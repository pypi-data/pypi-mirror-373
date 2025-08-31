from .C_M import CM;  C = CM()
from .Files_Check import FileCheck; F = FileCheck(); F.Set_Path()

# ---------------- Scan APK ----------------
def Scan_Apk(apk_path):
    print(f"\n{C.r}{'_' * 61}\n")
    isPairip = License_Check = App_Name = False; Package_Name = ''

    # ---------------- Extract Package Name with AAPT ----------------
    if C.os.name == 'posix':
        Package_Name = C.subprocess.run(['aapt', 'dump', 'badging', apk_path], capture_output=True, text=True).stdout.split("package: name='")[1].split("'")[0]
        if Package_Name:
            print(f"\n{C.lb}[ {C.c}Package Name {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{Package_Name}{C.pr}' {C.g} ✔")
 
        # ---------------- Match Application & License  ----------------
        A_N, L_C = '"com.pairip.application.Application"', '"com.pairip.licensecheck.LicenseActivity"'
        manifest = C.subprocess.run(['aapt', 'dump', 'xmltree', apk_path, 'AndroidManifest.xml'], capture_output=True, text=True).stdout

        App_Name = A_N in manifest
        if App_Name:
            print(f"\n\n{C.lb}[ {C.c}Application Name {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{A_N[1:-1]}{C.pr}' {C.g} ✔")
        else:
            License_Check = L_C in manifest
            if License_Check:
                print(f"\n\n{C.lb}[ {C.c}License Check {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{L_C[1:-1]}{C.pr}' {C.g} ✔")

    # ---------------- Extract Package Name with APKEditor ----------------
    if not Package_Name:
        Package_Name = C.subprocess.run(["java", "-jar", F.APKEditor_Path, "info", "-package", "-i", apk_path], capture_output=True, text=True).stdout.split('"')[1]
        print(f"\n{C.lb}[ {C.c}Package Name {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{Package_Name}{C.pr}'{C.g}  ✔")

    # ---------------- Check for APK protections ----------------
    Detect_Protection = []
    with C.zipfile.ZipFile(apk_path, 'r') as zip_ref:
        for item in zip_ref.infolist():
            if item.filename.startswith('lib/'):
                if item.filename.endswith('libpairipcore.so'):
                    print(f"\n\n{C.lb}[ {C.c}Pairip Protection {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}Google加固{C.pr}' {C.g} ✔")
                    isPairip = True
                    break
        
    if not any([App_Name, isPairip, License_Check]): exit(f"{C.rd} Your APK Has No Pairip Protection ✘\n")

    # ---------------- Check Flutter / Unity Protection ----------------
    isUnity = isFlutter = False; isDex = []

    with C.zipfile.ZipFile(apk_path, 'r') as zip_ref:
        for item in zip_ref.infolist():
            if item.filename.startswith('lib/'):
                if item.filename.endswith('libunity.so'):
                    isUnity = True
                if item.filename.endswith('libflutter.so'):
                    isFlutter = True

            elif item.filename.startswith("classes") and item.filename.endswith('.dex'):
                isDex.append(item.filename)

        Methods = Fields = 0

        if isDex:
            try:
                data = zip_ref.open(isDex[-1], 'r').read()
                Methods = int.from_bytes(data[88:91], "little")
                Fields = int.from_bytes(data[80:83], "little")
            except (OSError, ValueError, KeyError, C.zipfile.BadZipFile) as e:
                print(f"\n\n{C.lb}[ {C.y}WARN ! {C.lb}] {C.rd}{e}, Skipping Methods & Fields Count.")

    if isUnity:
        print(f"\n\n{C.lb}[ {C.c}Unity Protection {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}libunity.so{C.pr}' {C.g} ✔\n\n{C.lb}[ {C.y}WARN ! {C.lb}] {C.cb}This is {C.g}Unity + Pairip {C.cb}APK. Completely removing Pairip may not be possible unless you can bypass the libpairipcore.so check from Unity libraries.")
    if isFlutter:
        print(f"\n\n{C.lb}[ {C.c}Flutter Protection {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}libflutter.so{C.pr}' {C.g} ✔")
    if Methods and Fields:
        print(f"\n\n{C.lb}[{C.y} Last Dex Total {C.lb}] {C.c}Methods: {C.rkj}{Methods} {C.g}➸❥ {C.c}Field: {C.rkj}{Fields}  {C.g}✔")
    else:
        pass

    return Package_Name, License_Check, isFlutter