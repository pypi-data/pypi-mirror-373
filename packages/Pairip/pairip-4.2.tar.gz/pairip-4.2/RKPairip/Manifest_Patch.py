from .C_M import CM; C = CM()
from .Files_Check import FileCheck; F = FileCheck(); F.Set_Path();

# ---------------- Decode Manifest ----------------
def Decode_Manifest(manifest_path, d_manifest_path):
    try:
        process = C.subprocess.run(['java', '-jar', F.Axml2Xml_Path, 'd', manifest_path, d_manifest_path], check=True, capture_output=True, text=True)

        if process.returncode == 0:
            print(f"\n{C.lb}[ {C.c}Decoded Manifest {C.lb}] {C.pr}'{C.g}{C.os.path.basename(manifest_path)}{C.pr}' {C.g}➸❥ {C.pr}'{C.rkk}{C.os.path.basename(d_manifest_path)}{C.pr}' {C.g}✔\n")
            C.os.remove(manifest_path)
        else:
            print(f"\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} Decoding Failed  ✘\n")
    except Exception as e:
        print(f"\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} {e} ✘\n")

# ---------------- Generate ObjectLogger ----------------
def Generate_Objectlogger(decompile_dir, manifest_path, d_manifest_path, L_S_F):
    
    Target_Dest = C.os.path.join(L_S_F, 'RK_TECHNO_INDIA', 'ObjectLogger.smali')
    C.os.makedirs(C.os.path.dirname(Target_Dest), exist_ok=True)
    C.shutil.copy(F.Objectlogger, Target_Dest)
    
    print(f"\n{C.lb}[ {C.c}Generate {C.lb}] {C.g}ObjectLogger.smali {C.rkj}➸❥ {C.y}{C.os.path.relpath(Target_Dest, decompile_dir)}{C.g} ✔")

    # ---------------- Update Package Name ----------------
    PKG_Name = C.re.search(r'package="([^"]+)"', open(d_manifest_path, 'r', encoding='utf-8', errors='ignore').read())[1]
    content = open(Target_Dest, 'r', encoding='utf-8', errors='ignore').read()
    Update_PKG = content.replace('PACKAGENAME', PKG_Name)
    open(Target_Dest, 'w', encoding='utf-8', errors='ignore').write(Update_PKG)

    print(f"{C.g}     |\n     └──── {C.r}Package Name ~{C.g}$ {C.rkj}➸❥ {C.pn}'{C.g}{PKG_Name}{C.pn}' {C.g}✔\n")

# ---------------- Fix Manifest ----------------
def Fix_Manifest(d_manifest_path):

    patterns = [
        (r'\s+android:(splitTypes|requiredSplitTypes)="[^"]*?"', r'', 'Splits'),
        (r'(isSplitRequired=)"true"', r'\1"false"', 'isSplitRequired'),
        (r'\s+<meta-data\s+[^>]*"com.android.(vending.|stamp.|dynamic.apk.)[^"]*"[^>]*/>', r'', '<meta-data>'),
        (r'\s+<[^>]*"com.(pairip.licensecheck|android.vending.CHECK_LICENSE)[^"]*"[^>]*/>', r'', 'CHECK_LICENSE')
    ]

    for pattern, replacement, description in patterns:
        content = open(d_manifest_path, 'r', encoding='utf-8', errors='ignore').read()
        new_content = C.re.sub(pattern, replacement, content)
        if new_content != content:
            print(f"\n{C.lb}[ {C.c}Tag {C.lb}] {C.rkj}{description}\n\n{C.lb}[ {C.c}Pattern {C.lb}] {C.g}➸❥ {C.pr}{pattern}\n{C.g}     |\n     └──── {C.r}Patch Cleaned Up {C.rkj}➸❥ {C.pr}'{C.g}{C.os.path.basename(d_manifest_path)}{C.pr}' {C.g}✔\n")
        open(d_manifest_path, 'w', encoding='utf-8', errors='ignore').write(new_content)

# ---------------- Patch Manifest ----------------
def Patch_Manifest(decompile_dir, manifest_path, d_manifest_path, isAPKTool, L_S_F, CoreX_Hook, isFlutter, isCoreX):
    if isAPKTool:
        Decode_Manifest(manifest_path, d_manifest_path)
    Fix_Manifest(d_manifest_path)
    if not (CoreX_Hook or isCoreX):
        Generate_Objectlogger(decompile_dir, manifest_path, d_manifest_path, L_S_F)

    if not CoreX_Hook:
        content = open(d_manifest_path, 'r', encoding='utf-8', errors='ignore').read()

        application_tag = C.re.search(r'<application\s+[^>]*>', content)[0]
        
        if isCoreX or isFlutter:
            cleaned_tag = C.re.sub(r'\s+android:extractNativeLibs="[^"]*?"', '', application_tag)
            content = content.replace(application_tag, C.re.sub(r'>', '\n\tandroid:extractNativeLibs="true">', cleaned_tag))
        else:
            new_permissions = '''\t<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>\n\t<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>\n\t<uses-permission android:name="android.permission.MANAGE_EXTERNAL_STORAGE"/>'''

            content = C.re.sub(r'\s+<uses-permission[^>]*android:name="(android.permission.((READ|WRITE|MANAGE)_EXTERNAL_STORAGE))"[^>]*>', '', content)
        
            #content = C.re.sub(r'android:targetSdkVersion="\d+"', 'android:targetSdkVersion="28"', content)

            content = C.re.sub(r'(<uses-sdk\s+[^>]*>)', r'\1\n' + new_permissions, content)

            cleaned_tag = C.re.sub(r'\s+android:(request|preserve)LegacyExternalStorage="[^"]*?"', '', application_tag)
            content = content.replace(application_tag, C.re.sub(r'>','\n\tandroid:requestLegacyExternalStorage="true"\n\tandroid:preserveLegacyExternalStorage="true">', cleaned_tag))
        
        open(d_manifest_path, 'w', encoding='utf-8', errors='ignore').write(content)
        
        print(f"\n{C.lb}[ {C.c}Storage Permission {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}AndroidManifest.xml{C.pr}' {C.g}✔\n")

    if (isCoreX or isFlutter) and isAPKTool:
        Encode_Manifest(decompile_dir, manifest_path, d_manifest_path)

# ---------------- Replace Application ----------------
def Replace_Application(manifest_path, d_manifest_path, Super_Value, App_Name, isAPKTool, Fix_Dex):
    if isAPKTool or Fix_Dex:
        Decode_Manifest(manifest_path, d_manifest_path)
        manifest_path = d_manifest_path
    f = open(manifest_path, 'r', encoding='utf-8', errors='ignore').read()
    updated = f.replace(App_Name, Super_Value)
    print(f"\n{C.lb}[ {C.c}Replaced {C.lb}] {C.pr}'{C.g}{App_Name}{C.pr}' {C.g}➸❥ {C.pr}'{C.c}{Super_Value}{C.pr}' {C.g}✔\n")
    open(manifest_path, 'w', encoding='utf-8', errors='ignore').write(updated)

# ---------------- Encoded Mainfest ----------------
def Encode_Manifest(decompile_dir, manifest_path, d_manifest_path):
    try:
        process = C.subprocess.run(['java', '-jar', F.Axml2Xml_Path, 'e', d_manifest_path, manifest_path], check=True, capture_output=True, text=True)
        if process.returncode == 0:
            print(f"\n{C.lb}[ {C.c}Encoded Manifest {C.lb}] {C.pr}'{C.rkk}{C.os.path.basename(d_manifest_path)}{C.pr}' {C.g}➸❥ {C.pr}'{C.g}{C.os.path.basename(manifest_path)}{C.pr}' {C.g}✔\n")
            C.os.remove(d_manifest_path)
        else:
            print(f"\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} Encoding Failed  ✘\n")
    except Exception as e:
        print(f"\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} {e} ✘\n")