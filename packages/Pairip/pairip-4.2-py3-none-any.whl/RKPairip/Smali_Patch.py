from .C_M import CM; C = CM()
from .Files_Check import FileCheck; F = FileCheck(); F.Set_Path()

# ---------------- Smali Patch ----------------
def Smali_Patch(smali_folders, CoreX_Hook, isCoreX):
    target_files = ["SignatureCheck.smali", "LicenseClientV3.smali", "LicenseClient.smali", "Application.smali"]
    if CoreX_Hook or isCoreX: target_files.append("VMRunner.smali")

    patterns = []

    if not (isCoreX and not CoreX_Hook):
        patterns.extend([
            (r'invoke-static \{[^\}]*\}, Lcom/pairip/SignatureCheck;->verifyIntegrity\(Landroid/content/Context;\)V', r'#', "VerifyIntegrity"),
            (r'(\.method [^(]*verifyIntegrity\(Landroid/content/Context;\)V\s+.locals \d+)[\s\S]*?(\s+return-void\n.end method)', r'\1\2', "VerifyIntegrity"),
            (r'(\.method [^(]*verifySignatureMatches\(Ljava/lang/String;\)Z\s+.locals \d+\s+)[\s\S]*?(\s+return ([pv]\d+)\n.end method)', r'\1const/4 \3, 0x1\2', "verifySignatureMatches"),
            (r'(\.method [^(]*connectToLicensingService\(\)V\s+.locals \d+)[\s\S]*?(\s+return-void\n.end method)', r'\1\2', "connectToLicensingService"),
            (r'(\.method [^(]*initializeLicenseCheck\(\)V\s+.locals \d+)[\s\S]*?(\s+return-void\n.end method)', r'\1\2', "initializeLicenseCheck"),
            (r'(\.method [^(]*processResponse\(ILandroid/os/Bundle;\)V\s+.locals \d+)[\s\S]*?(\s+return-void\n.end method)', r'\1\2', "processResponse")
        ])

    # ---------------- loadLibrary ➢ '_Pairip_CoreX' ----------------
    if CoreX_Hook or isCoreX:
        patterns.append((r'(\.method [^<]*<clinit>\(\)V\s+.locals \d+\n)', r'\1\tconst-string v0, "_Pairip_CoreX"\n\tinvoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n', f'CoreX_Hook ➸❥ {C.rkj}"lib_Pairip_CoreX.so"'))

    Smali_Files = []
    for smali_folder in smali_folders:
        for root, _, files in C.os.walk(smali_folder):
            for file in files:
                if file in target_files:
                    Smali_Files.append(C.os.path.join(root, file))

    for pattern, replacement, description in patterns:
        for Smali_File in Smali_Files:
            try:
                if description.startswith("CoreX_Hook") and not Smali_File.endswith("VMRunner.smali"): continue

                content = open(Smali_File, 'r', encoding='utf-8', errors='ignore').read()
                new_content = C.re.sub(pattern, replacement, content)
                if new_content != content:
                    print(f"\n{C.lb}[ {C.c}Patch {C.lb}] {C.g}{description} {C.rkj}➸❥ {C.y}{C.os.path.basename(Smali_File)}")
                    print(f"{C.g}    |\n    └── {C.r}Pattern {C.g}➸❥ {C.pr}{pattern}")
                    open(Smali_File, 'w', encoding='utf-8', errors='ignore').write(new_content)
            except Exception as e:
                pass
    print(f"\n{C.r}{'_' * 61}\n")

# ---------------- Check CoreX ----------------
def Check_CoreX(decompile_dir, isAPKTool):
    lib_paths = C.os.path.join(decompile_dir, *(['lib'] if isAPKTool else ['root', 'lib']))
    Lib_CoreX = []

    for arch in C.os.listdir(lib_paths):
        for root, _, files in C.os.walk(C.os.path.join(lib_paths, arch)):
            for target_file in ['lib_Pairip_CoreX.so', 'libFirebaseCppApp.so']:
                if target_file in files:
                    Lib_CoreX.append(f"{C.g}{target_file} ➸❥ {C.rkk}{arch}")
    if Lib_CoreX:
        print(f"\n\n{C.lb}[ {C.y}Info {C.lb}] {C.c}Already Added {C.rkj}➸❥ {f' {C.rkj}& '.join(Lib_CoreX)}{C.c} {C.g}✔")
        return True
    return False

# ---------------- HooK CoreX ----------------
def Hook_Core(apk_path, decompile_dir, isAPKTool, Package_Name):
    with C.zipfile.ZipFile(apk_path, 'r') as zf:
        base_apk = "base.apk" if "base.apk" in zf.namelist() else f"{Package_Name}.apk"

    try:
        if C.os.name == 'nt' and C.shutil.which("7z"):
            C.subprocess.run(["7z", "e", apk_path, base_apk, "-y"], text=True, capture_output=True)
            with C.zipfile.ZipFile(apk_path) as zf:
                zf.extract(base_apk)
        else:
            if C.shutil.which("unzip"):
                C.subprocess.run(["unzip", "-o", apk_path, base_apk], text=True, capture_output=True)
                with C.zipfile.ZipFile(apk_path) as zf:
                    zf.extract(base_apk)
        print(f'\n{C.lb}[ {C.c}Dump {C.lb}] {C.g}➸❥ {C.rkj}{base_apk}\n')
        Dump_Apk = "libFirebaseCppApp.so"
        C.os.rename(base_apk, Dump_Apk)
        lib_paths = C.os.path.join(decompile_dir, *(['lib'] if isAPKTool else ['root', 'lib']))
        Arch_Paths = []
        for lib in C.os.listdir(lib_paths):
            for root, _, files in C.os.walk(C.os.path.join(lib_paths, lib)):
                if 'libpairipcore.so' in files:
                    Arch_Paths.append(root)

        for Arch in Arch_Paths:
            print(f"\n{C.lb}[ {C.c}Arch {C.lb}] {C.g}➸❥ {C.os.path.basename(Arch)}\n")
            C.shutil.move(Dump_Apk, Arch); C.shutil.copy(F.Pairip_CoreX, Arch);
        print(f'\n{C.lb}[ {C.c}HooK {C.lb}] {C.g}➸❥ {C.rkj}libFirebaseCppApp.so {C.g}✔\n\n{C.lb}[ {C.c}HooK {C.lb}] {C.g}➸❥ {C.rkj}lib_Pairip_CoreX.so {C.g}✔\n')

        return True
    except Exception as e:
        print(f"\n{C.lb}[ {C.rd}Hook_Core Error ! {C.lb}] {C.rd}{e} ✘")