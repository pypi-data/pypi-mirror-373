from .C_M import CM; C = CM()
from .Files_Check import FileCheck; F = FileCheck(); F.Set_Path()

C_Line = f"{C.r}{'_' * 61}"

# ---------------- Decompile APK ----------------
def Decompile_Apk(apk_path, decompile_dir, isAPKTool, Fix_Dex):

    AA = f"{'APKTool' if isAPKTool else 'APKEditor'}"
    print(f"\n{C_Line}\n\n\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Decompile APK with {AA}...")

    if isAPKTool or Fix_Dex:
        cmd = ["java", "-jar", F.APKTool_Path, "d", "-f", "-r", '--only-main-classes', apk_path, "-o", decompile_dir]

        print(f"{C.g}  |\n  └──── {C.r}Decompiling ~{C.g}$ java -jar {C.os.path.basename(F.APKTool_Path)} d -f -r --only-main-classes {apk_path} -o {C.os.path.basename(decompile_dir)}\n\n{C_Line}{C.g}\n")

    else:
        cmd = ["java", "-jar", F.APKEditor_Path, "d", "-f", "-no-dex-debug", "-i", apk_path, "-o", decompile_dir]

        print(f"{C.g}  |\n  └──── {C.r}Decompiling ~{C.g}$ java -jar {C.os.path.basename(F.APKEditor_Path)} d -f -no-dex-debug -i {apk_path} -o {C.os.path.basename(decompile_dir)}\n\n{C_Line}{C.g}\n")

    try:
        C.subprocess.run(cmd, check=True)
        print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Decompile APK Successful  {C.g}✔\n\n{C_Line}\n")
    except C.subprocess.CalledProcessError:
        C.shutil.rmtree(decompile_dir)
        exit(f"\n{C.lb}[ {C.rd}Error ! {C.lb}] {C.rd} Decompile APK Failed with {AA} ✘\n")

# ---------------- Recompile APK ----------------
def Recompile_Apk(decompile_dir, isAPKTool, build_dir, isFlutter):

    AA = f"{'APKTool' if isAPKTool else 'APKEditor'}"
    print(f"{C_Line}\n\n\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Recompile APK with {AA}...")

    if isAPKTool:
        cmd = ["java", "-jar", F.APKTool_Path, "b", "-f", decompile_dir, "-o", build_dir]

        print(f"{C.g}  |\n  └──── {C.r}Recompiling ~{C.g}$ java -jar {C.os.path.basename(F.APKTool_Path)} b -f {C.os.path.basename(decompile_dir)} -o {C.os.path.basename(build_dir)}\n\n{C_Line}{C.g}\n")

    else:
        cmd = ["java", "-jar", F.APKEditor_Path, "b", "-i", decompile_dir, "-o", build_dir, "-f"]
        
        if isFlutter: cmd += ["-extractNativeLibs", "true"]

        print(f"{C.g}  |\n  └──── {C.r}Recompiling ~{C.g}$ java -jar {C.os.path.basename(F.APKEditor_Path)} b -i {C.os.path.basename(decompile_dir)} -o {C.os.path.basename(build_dir)} -f" + (" -extractNativeLibs true" if isFlutter else "") + f"\n\n{C_Line}{C.g}\n")

    try:
        C.subprocess.run(cmd, check=True)
        print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Recompile APK Successful  {C.g}✔\n\n{C_Line}\n")
    except C.subprocess.CalledProcessError:
        C.shutil.rmtree(decompile_dir)
        exit(f"\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} Recompile APK Failed with {AA} ✘\n")

    if C.os.path.exists(build_dir): print(f"\n{C.lb}[ {C.c}APK Created {C.lb}] {C.g}➸❥ {C.y}{build_dir} {C.g}✔\n\n{C_Line}\n")

# ---------------- FixSigBlock ----------------
def FixSigBlock(decompile_dir, apk_path, build_dir, rebuild_dir):
    C.os.rename(build_dir, rebuild_dir)
    sig_dir = decompile_dir.replace('_decompiled', '_SigBlock')
    for operation in ["d", "b"]:
        cmd = ["java", "-jar", F.APKEditor_Path, operation, "-t", "sig", "-i", (apk_path if operation == "d" else rebuild_dir), "-f", "-sig", sig_dir]
        if operation == "b":
            cmd.extend(["-o", build_dir])
        C.subprocess.run(cmd, check=True, text=True, capture_output=True)
    C.shutil.rmtree(sig_dir); C.os.remove(rebuild_dir)