from .CRC import CRC_Fix
from .Scan import Scan_Apk
from .C_M import CM;  C = CM()
from .Flutter_SO import Flutter_SO
from .Argparse import parse_arguments
from .Instruction_Credit import instruction
from .Anti_Splits import Anti_Split, Check_Split
from .Extract import Extract_Smali, Logs_Injected
from .Smali_Patch import Smali_Patch, Check_CoreX, Hook_Core
from .Files_Check import FileCheck; F = FileCheck(); F.Set_Path()
from .Fix_Dex import Scan_Application, Smali_Patcher, Replace_Strings
from .Decompile_Compile import Decompile_Apk, Recompile_Apk, FixSigBlock
from .Manifest_Patch import Patch_Manifest, Replace_Application, Encode_Manifest
from .Other_Patch import Application_Name, Translate_Smali_Name, Merge_Smali_Folders, UnMerge

def Clear(): C.os.system('cls' if C.os.name == 'nt' else 'clear')

Clear()

# ---------------- Install Require Module ---------------
required_modules = ['requests', 'multiprocess']
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        print(f"{C.lb}[ {C.pr}Installing {C.lb}] {C.c}{module} module...{C.g}\n")
        try:
            C.subprocess.check_call([C.sys.executable, "-m", "pip", "install", module])
            print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} {module} Installed Successfully.{C.g} ✔\n")
            Clear()
        except (C.subprocess.CalledProcessError, Exception):
            exit(f"\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} No Internet Connection. ✘\n\n{C.lb}[ {C.rd}INFO {C.lb}]{C.rd} Internet Connection is Required to Install {C.rd}'{C.g}pip install {module}{C.rd}' ✘\n")

# ---------------- Check Dependencies ----------------
def check_dependencies():
    try:
        C.subprocess.run(['java', '-version'], check=True, text=True, capture_output=True)
    except (C.subprocess.CalledProcessError, FileNotFoundError):
        if C.os.name == 'posix':
            install_package('openjdk-17')
        else:
            exit(f'\n\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} Java is not installed on Your System. ✘\n\n{C.lb}[ {C.y}INFO ! {C.lb}]{C.rd} Install Java and run script again in new CMD. ✘\n\n{C.lb}[ {C.y}INFO ! {C.lb}]{C.rd} Verify Java installation using {C.rd}"{C.g}java --version{C.rd}" command in CMD')

    if C.os.name == 'posix': install_package('aapt')

# ---------------- Install Package ----------------
def install_package(pkg):
    try:
        result = C.subprocess.run(['pkg', 'list-installed'], capture_output=True, text=True, check=True)
        if pkg not in result.stdout:
            print(f"{C.lb}[ {C.pr}Installing {C.lb}] {C.c}{pkg}...{C.g}\n")
            C.subprocess.check_call(['pkg', 'install', '-y', pkg])
            print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} {pkg} Installed Successfully.{C.g} ✔\n")
            Clear()
    except (C.subprocess.CalledProcessError, Exception) as e:
        exit(f"\n\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} No Internet Connection. ✘\n\n{C.lb}[ {C.rd}INFO {C.lb}]{C.rd} Internet Connection is Required to Installation {C.rd}'{C.g}pkg install {pkg}{C.rd}' ✘\n")

check_dependencies()

F.F_D();

ver = '2.0 𓄂 Ꭱꫝℑ 𓆐 ︻デ═一 ࿗ Я͓̽K͓̽ ࿗'
aaa = C.datetime.now().strftime(' %d/%m/%y')

# Logo ( 🙏 )
b64 = """eJyNUz9Lw0AUn3NfocvjyGqJEVHpYrsFl2BFkU5SAwqmnd7gJlrsJpUiTiLOgg4uBRG/gIIfQauTi/0I3l3uLu+SCL4judz7/e73/twFQFmtM5/WOgvLjcVGGITp7Hp4J54H2EoOuv00cfCltHWoHSthupF093p9iHq7+zvCG9i9jHkeYGYMqCH6uTmgg5RwCRYSBR1+jiQgNzl7qswyMoItB+JmtB7F0NqOm+220Svx/yHpc/HJyUwp3BAUHbVXOW3qkg9FitSuYKD7mbeUZz0UL81HN4hNjabp4HnJdi4cp8/JkKA48TxF9EEPVElk5yxoSo6UIqnoY+5UBGYwdNM17TNXhrmXSlGl6XAEZWoz55SO4Fy+DBVd0AJSy5UXa4HRRsggUFBl+mSIdIGkMVOlic6JsENXITmpv2QZ3eT2Nw/MffOqQftLrG7WIawHMBsPjuHj7Ob79mo6OBfL0xH8TB4/T4bTi9HX5Ajeny/h7f7l6XW8Jl9yLf8f9guAzed1"""
print(C.zlib.decompress(C.base64.b64decode(b64)).decode('utf-8'))
print(f'''————————|——————————————————|—————————————————|——————————————|————
      {C.c}Name{C.r}       |     {C.c}Telegram{C.r}     |      {C.c}OWNER{C.r}       |   {C.c}Date{C.r}
————————|——————————————————|—————————————————|——————————————|————
{C.rkj}「Techno India」{C.r} | {C.pr}@rktechnoindians{C.r} | {C.pr}@RK_TECHNO_INDIA{C.r} |{C.lb}{aaa
}{C.r}
————————|——————————————————|—————————————————|——————————————|————\n''')

# ---------------- enable_wake_lock ----------------
def enable_wake_lock():
    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Acquiring Wake Lock...\r")

# ---------------- Target All Classes Folder ----------------
def Find_Smali_Folders(decompile_dir, isAPKTool, Fix_Dex):
    smali_path = decompile_dir if isAPKTool or Fix_Dex else C.os.path.join(decompile_dir, "smali")
    prefix = "smali_classes" if isAPKTool or Fix_Dex else "classes"
    folders = sorted([f for f in C.os.listdir(smali_path) if f == "smali" or f.startswith(prefix)], key=lambda x: int(x.split(prefix)[-1]) if x.split(prefix)[-1].isdigit() else 0)
    
    return [C.os.path.join(smali_path, f) for f in folders]

# ---------------- Target Last Classes Folder ----------------
def L_S_C_F(decompile_dir, isAPKTool, Fix_Dex):
    smali_folders = Find_Smali_Folders(decompile_dir, isAPKTool, Fix_Dex)
    return smali_folders[-1] if smali_folders else None

# ---------------- disable_wake_lock ----------------
def disable_wake_lock():
    exit(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Releasing Wake Lock...\n")

# ---------------- Execute Main Function ----------------
def RK_Techno_IND():
    args = parse_arguments()
    M_Skip=args.MergeSkip
    CoreX_Hook=args.Hook_CoreX; isCoreX=False
    Credit=args.Credits_Instruction; instruction(Credit)
    isAPKTool=args.ApkTool; Fix_Dex=args.Repair_Dex
    if isAPKTool or Fix_Dex: F.F_D_A()
    
    apk_path = args.input or args.Merge

    if not C.os.path.isfile(apk_path): exit(f"\n{C.lb}[ {C.rd}Error ! {C.lb}] {C.rd} APK file '{apk_path}' not found. ✘\n")

    apk_path = Anti_Split(apk_path, args.Merge, CoreX_Hook)

    # ---------------- Set All Paths Directory ----------------
    decompile_dir = C.os.path.join(C.os.path.expanduser("~"), f"{C.os.path.splitext(C.os.path.basename(apk_path))[0]}_decompiled")
    build_dir = C.os.path.abspath(C.os.path.join(C.os.path.dirname(apk_path), f"{C.os.path.splitext(C.os.path.basename(apk_path))[0]}_Pairip.apk"))
    rebuild_dir = build_dir.replace('_Pairip.apk', '_Patched.apk')
    manifest_path = C.os.path.join(decompile_dir, 'AndroidManifest.xml')
    d_manifest_path = C.os.path.join(decompile_dir, 'AndroidManifest_d.xml')
    mtd_path = "/sdcard/MT2/dictionary/"
    C_Line = f"{C.r}{'_' * 61}"
    Logo = f'\n🚩 {C.r}࿗ {C.rkj}Jai Shree Ram {C.r}࿗ 🚩\n     🛕🛕🙏🙏🙏🛕🛕\n'
    START = f'\n{C.lb}[{C.c}  Time Spent  {C.lb}] {C.g}︻デ═一 {C.y}'; END=f'{C.r} Seconds\n'

    if C.os.name == 'posix': (C.subprocess.run(['termux-wake-lock']), enable_wake_lock())

    start_time = C.time.time()

    # ---------------- Scan & Decompile APK ---------------
    Package_Name, License_Check, isFlutter = Scan_Apk(apk_path)
    if input and isFlutter: Flutter_SO(apk_path, isFlutter)
    Decompile_Apk(apk_path, decompile_dir, isAPKTool, Fix_Dex)

    # ---------------- Last Smali Folder & All Smali Folder ---------------
    L_S_F = L_S_C_F(decompile_dir, isAPKTool, Fix_Dex)
    smali_folders = Find_Smali_Folders(decompile_dir, isAPKTool, Fix_Dex)

    # ---------------- Fix Dex Flag: -r ---------------
    if Fix_Dex:
        try:
            App_Name = Scan_Application(apk_path, manifest_path, d_manifest_path, Fix_Dex)
            if App_Name:
                Super_Value = Application_Name(L_S_F)
                print(f'\n{C.lb}[{C.c}  APPLICATION  {C.lb}] {C.g}︻デ═一 {Super_Value}  ✔\n')
                Replace_Application(manifest_path, d_manifest_path, Super_Value, App_Name, isAPKTool, Fix_Dex)
                Encode_Manifest(decompile_dir, manifest_path, d_manifest_path)
            else:
                C.os.remove(d_manifest_path)
                pass

            Smali_Patcher(smali_folders, L_S_F); build_dir = rebuild_dir
            Recompile_Apk(decompile_dir, Fix_Dex, build_dir); C.shutil.rmtree(decompile_dir)
            elapsed_time = C.time.time() - start_time
            print(START + f'{elapsed_time:.2f}' + END)
            print(Logo)
            if C.os.name == 'posix': (C.subprocess.run(['termux-wake-unlock']), disable_wake_lock())
            exit(0)
        except Exception as e:
            exit(f"\n{C.lb}[ {C.rd}Error ! {C.lb}] {C.rd}{e} ✘\n")

    # ---------------- Extract Target Smali & Logs Inject ---------------
    if not (CoreX_Hook or License_Check): Extract_Smali(decompile_dir, smali_folders, isAPKTool)
    L_S_F = L_S_C_F(decompile_dir, isAPKTool, Fix_Dex)
    if not (CoreX_Hook or License_Check):
        Logs_Injected(L_S_F)
        Super_Value = Application_Name(L_S_F)
        OR_App=f'\n{C.lb}[{C.c}  APPLICATION  {C.lb}] {C.g}︻デ═一 {Super_Value}  ✔\n'
        smali_folders = Find_Smali_Folders(decompile_dir, isAPKTool, Fix_Dex)

    # ---------------- Hook CoreX ---------------
    if CoreX_Hook and Check_CoreX(decompile_dir, isAPKTool): C.shutil.rmtree(decompile_dir); exit(0)
    Smali_Patch(smali_folders, CoreX_Hook, isCoreX)
    if CoreX_Hook or isCoreX: Hook_Core(args.input, decompile_dir, isAPKTool, Package_Name)
    if not isAPKTool: d_manifest_path = manifest_path

    # ---------------- Patch Manifest ---------------
    Patch_Manifest(decompile_dir, manifest_path, d_manifest_path, isAPKTool, L_S_F, CoreX_Hook, isCoreX)
    if isAPKTool: Encode_Manifest(decompile_dir, manifest_path, d_manifest_path)
    
    if not (CoreX_Hook or License_Check): 
        # ---------------- Merge Smali ---------------
        if M_Skip:
            print(f"\n{C.lb}[ {C.y}INFO ! {C.lb}] {C.g} Skip Merge Last Dex {C.y}{C.os.path.basename(L_S_F)} {C.g} & Add Seprate (For Dex Redivision)\n")
            pass
        else:
            Merge_Smali_Folders(decompile_dir, isAPKTool, L_S_F)

        Translate_Smali = Translate_Smali_Name(C.os.path.basename(L_S_C_F(decompile_dir, isAPKTool, Fix_Dex)), isAPKTool) if L_S_C_F(decompile_dir, isAPKTool, Fix_Dex) else "No Smali classes folder found."

    # ---------------- Recompile APK ---------------
    Recompile_Apk(decompile_dir, isAPKTool, build_dir)
    if CoreX_Hook or License_Check:
        CRC_Fix(M_Skip, apk_path, build_dir, ["AndroidManifest.xml", ".dex"])
        C.shutil.rmtree(decompile_dir)
        print(f"{C_Line}\n\n" + START + f'{C.time.time() - start_time:.2f}' + END + f'\n{Logo}')
        C.os.name == 'posix' and (C.subprocess.run(['termux-wake-unlock']), disable_wake_lock()); exit(0)

    # ---------------- CRCFix ---------------
    Final_Apk = CRC_Fix(M_Skip, apk_path, build_dir, ["AndroidManifest.xml", ".dex"])
    if isAPKTool: FixSigBlock(decompile_dir, apk_path, build_dir, rebuild_dir)

    print(f'\n{C.lb}[{C.c}  Final APK  {C.lb}] {C.g}︻デ═一 {C.y} {Final_Apk}  {C.g}✔\n')
    elapsed_time = C.time.time() - start_time
    print(f"{C_Line}\n\n\n{C.lb}[{C.c}  Last Dex  {C.lb}] {C.g}︻デ═一 {C.pr}'{C.g}{C.os.path.basename(Translate_Smali)}{C.pr}' {C.y}( Translate with MT )  {C.g}✔\n")

    # ---------------- APPLICATION NAME ---------------
    print(OR_App)
    print(START + f'{elapsed_time:.2f}' + END + f"\n{C_Line}\n")
    if C.os.path.exists(mtd_path):
        mtd_files = [file for file in C.os.listdir(mtd_path) if file.startswith(Package_Name) and file.endswith('.mtd')]
        for mtd_file in mtd_files:
            C.os.remove(C.os.path.join(mtd_path, mtd_file))
    print(f'\n{C.lb}[ {C.y}INFO {C.lb}] {C.g} If U Want Repair Dex Without Translate, So Generate .mtd First & put the .mtd in the path of {C.y}"/sdcard/MT2/dictionary/"{C.g}, if .mtd available in target path then The Script will handle Automatically, So Press Enter 🤗🤗\n')

    while True:
        UnMerge_input = input(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Do U Want Repair Dex (Press Enter To Proceed or 'q' to exit or 'm' to More Info) | Hook If Apk Crash Then Try with 'x'\n{C.g}  |\n  └──── {C.r}~{C.g}$ : {C.y}").strip().lower()
        if UnMerge_input == 'q':
            C.shutil.rmtree(decompile_dir)
            print(f"\n{C_Line}\n\n\n{C.lb}[{C.y} INFO ! {C.lb}] {C.c} Now you have to manually Translate the Last Dex with MT & again input with -r Flag the Command {C.g}( Copy Below Command & Run After Translate Dex )\n{C.g}  |\n  └──── {C.r}~{C.g}${C.y}  RKPairip -i {build_dir} -r\n\n{C_Line}\n")
            break
        elif UnMerge_input == 'm':
            print(f'\n{C_Line}\n\n\n{C.lb}[{C.y} MORE INFO {C.lb}] {C.g} - To generate .mtd file, first install the {C.rkj}“{C.os.path.basename(apk_path)}”{C.g} in Multi App/Dual Space and save the .mtd in "/sdcard/MT2/dictionary/"\n\n{C.lb}[{C.y} NOTE {C.lb}] {C.g} - if u use root or VM so .mtd will save path of {C.y}"/data/data/{Package_Name}/dictionary/" {C.g}& then u just move .mtd file to path of {C.y}"/sdcard/MT2/dictionary/"\n\n{C.lb}[{C.y} FYI {C.lb}] {C.g} - Make sure you have generated a new .mtd before pressing enter as using the old .mtd may cause a apk crash\n\n{C.lb}[{C.y} INFO {C.lb}] {C.g} - The script will handle it automatically if the .mtd file exists in the target path.\n')
            continue
        elif UnMerge_input == 'x' and not (CoreX_Hook or Check_CoreX(decompile_dir, isAPKTool) or Check_Split(args.input, isCoreX=True)):
            print(f"\n{C_Line}\n\n\n{C.lb}[{C.y} Info {C.lb}] {C.c}Hook lib_Pairip_CoreX.so & loadLibrary in VMRunner Class.{C.g}\n    |\n    └──── {C.r}~{C.g}${C.y} This Hook Work in Some Apk Like Flutter/Unity & Try on Crash Apk.{C.g}\n    |\n    └──── {C.r}~{C.g}${C.y} Note Some Time This Apk Working Directly with Sign When Directly Working Hook Then why need Bypass Pairip, because u can also modify dex in Apk.{C.g}\n    |\n    └──── {C.r}~{C.g}${C.y} Still U want Bypass Pairip then Dump '.mtd' & Press Enter ( for mtd dump Use  Multi_App cuz Storage Permission not added in Apk )\n\n{C_Line}\n")
            
            Smali_Patch(smali_folders, CoreX_Hook, isCoreX=True)
            Patch_Manifest(decompile_dir, manifest_path, d_manifest_path, isAPKTool, L_S_F, CoreX_Hook, isCoreX=True)
            Hook_Core(args.input, decompile_dir, isAPKTool, Package_Name)
            Recompile_Apk(decompile_dir, isAPKTool, build_dir)
            # ---------------- CRCFix ---------------
            CRC_Fix(M_Skip, apk_path, build_dir, ["AndroidManifest.xml", ".dex"])
            if isAPKTool: FixSigBlock(decompile_dir, apk_path, build_dir, rebuild_dir)
            continue
        else:
            print(f"\n{C_Line}")
            if UnMerge:
                mtd_files = None
                while True:
                    if C.os.path.exists(mtd_path):
                        mtd_files = [file for file in C.os.listdir(mtd_path) if file.startswith(Package_Name) and file.endswith('.mtd')]
                        if not mtd_files: print(f"\n\n{C.lb}[{C.y} Warn ! {C.lb}] {C.rd} No {C.g}{Package_Name}..... .mtd {C.g}file found in {C.y}{mtd_path}\n")
                        else:
                            if not M_Skip: UnMerge()
                            mtd_file = max(mtd_files, key=lambda file: C.os.path.getmtime(C.os.path.join(mtd_path, file)))
                            print(f"\n{C.lb}[{C.y} INFO ! {C.lb}] {C.c}Founded {C.g}➸❥ {mtd_file} ✔\n\n{C_Line}\n")
                            break
                    else:
                        print(f"\n\n{C.lb}[{C.y} Warn ! {C.lb}] {C.rd} No such directory found: {C.y}{mtd_path}\n")
                    user_input = input(f"\n{C.lb}[{C.y} Input {C.lb}] {C.c}If You Want To Retry, Press Enter & Exit To Script {C.pr}'q' : {C.y}")
                    if user_input.lower() == 'q': break

                # ---------------- Restore Strings ---------------
                if mtd_files:
                    fix_time = C.time.time()
                    Smali_Patcher(smali_folders, L_S_F)
                    Replace_Strings(L_S_F, C.os.path.join(mtd_path, mtd_file))
                    if not M_Skip: Merge_Smali_Folders(decompile_dir, isAPKTool, L_S_F)
                    App_Name = Scan_Application(apk_path, manifest_path, d_manifest_path, isAPKTool)
                    print(OR_App)
                    Replace_Application(manifest_path, d_manifest_path, Super_Value, App_Name, isAPKTool, Fix_Dex)
                    if isAPKTool: Encode_Manifest(decompile_dir, manifest_path, d_manifest_path)
                    Recompile_Apk(decompile_dir, isAPKTool, build_dir)
                    C.shutil.rmtree(decompile_dir)
                    elapsed_time = C.time.time() - fix_time
                    print(START + f'{elapsed_time:.2f}' + END)
                    break
                else:
                    C.shutil.rmtree(decompile_dir)
                    print(f"\n{C_Line}\n\n\n{C.lb}[{C.y} INFO ! {C.lb}] {C.rd} No Valid .mtd File Found. ✘\n\n\n{C.lb}[{C.y} INFO ! {C.lb}] {C.c} Now you have to manually Translate the Last Dex with MT & again input with -r Flag the Command {C.g}( Copy Below Command & Run After Translate Dex )\n{C.g}  |\n  └──── {C.r}~{C.g}${C.y}  RKPairip -i {build_dir} -r\n\n{C_Line}\n")
                    break

    print(Logo)
    if C.os.name == 'posix': (C.subprocess.run(['termux-wake-unlock']), disable_wake_lock())
    exit(0)