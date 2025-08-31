from .C_M import CM; C = CM()
G = "\n" * 3

class CustomArgumentParser(C.argparse.ArgumentParser):
    # ---------------- Error Handling ----------------
    def error(self, message):
        suggestion = ""
        for action in self._actions:
            if action.option_strings and any(option in message for option in action.option_strings):
                if action.dest == 'input':
                    suggestion = f'\n{C.lb}[ {C.y}FYI ! {C.lb}] {C.g}Make Sure There Is "No Extra Space" In The Folder/Apk Name In The Input Text. If Yes, Then Remove Extra Space & Correct It By Renaming It.{G}{C.lb}[ {C.pr}* {C.lb}] {C.c}With APKEditor ( Default ){G}{C.lb}[ {C.y}Ex. {C.lb}] {C.g}RKPairip -i YourApkPath.apk{G}{C.lb}[ {C.pr}* {C.lb}] {C.c}With APKTool Use {C.rkj}-a {C.c}Flag{G}{C.lb}[ {C.y}Ex. {C.lb}] {C.g}RKPairip -i YourApkPath.apk {C.rkj}-a{G}{C.lb}[ {C.pr}* {C.lb}] {C.c}Merge Skip Use {C.rkj}-s {C.c}Flag ( Do U Want Last Dex Add Seprate For Dex Redivision ){G}{C.lb}[ {C.y}Ex. {C.lb}] {C.g}RKPairip -i YourApkPath.apk {C.rkj}-s{G}{C.lb}[ {C.pr}* {C.lb}] {C.c}Pairip Dex Fix Use {C.rkj}-r {C.c}Flag ( Try After Translate String to MT ){G}{C.lb}[ {C.y}Ex. {C.lb}] {C.g}RKPairip -i YourApkPath.apk {C.rkj}-r{G}{C.lb}[ {C.pr}* {C.lb}] {C.c}Hook CoreX ( For Unity / Flutter & Crashed Apk Apk ) {C.rkj}-x {C.y}/ {C.rkj}-a -x {G}{C.lb}[ {C.y}Ex. {C.lb}] {C.g}RKPairip -i YourApkPath.apk {C.rkj}-x\n'
                elif action.dest == 'Merge':
                    suggestion = f'\n{C.lb}[ {C.y}INFO {C.lb}] {C.c}Only Merge Apk{G}{C.lb}[ {C.y}INFO {C.lb}] {C.c}Merge Extension {C.y}( .apks/.xapk/.apkm ){G}{C.lb}[ {C.y}Ex. {C.lb}] {C.g}RKPairip {C.rkj}-m {C.g}Your_Apk_Path.apks\n'
                break

        exit(f'\n{C.lb}[ {C.rd}Error ! {C.lb}] {C.rd} {message}\n\n{suggestion}')

# ---------------- Parse Arguments ----------------
def parse_arguments():
    parser = CustomArgumentParser(description=f'{C.c}RKPairip Script v4.2') if any(arg.startswith('-') for arg in C.sys.argv[1:]) else C.argparse.ArgumentParser(description=f'{C.c}RKPairip Script v4.2')

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-i', dest='input', help=f'{C.y}➸ {C.g}Input APK Path...{C.c}')
    group.add_argument('-m', dest='Merge', help=f'{C.y}➸ {C.g}Anti-Split ( Only Merge Apk ){C.c}')
    group.add_argument('-C', dest='Credits_Instruction', action='store_true', help=f'{C.y}➸ {C.g}Show Instructions & Credits{C.c}')

    additional = parser.add_argument_group(f'{C.rkj}[ * ] Additional Flags{C.c}')

    additional.add_argument('-a', '--ApkTool', action='store_true', help=f'{C.y}➸ {C.g}ApkTool ( Fast, But Not Stable Comparison To APKEditor ){C.c}')
    additional.add_argument('-s', '--MergeSkip', action='store_true', help=f'{C.y}➸ {C.g}Do U Want Last Dex Add Seprate ( For Dex Redivision & The script will be in listen mode, so you can do Max Value Dex Redivision {C.pr}( like 65536 ) {C.g}using MT/ApkTool_M and correct the name of the APK again and then press enter in the script, which will bypass CRC ){C.c}')
    additional.add_argument('-r', '--Repair_Dex', action='store_true', help=f'{C.y}➸ {C.g}Pairip Dex Fix ( Try After Translate String to MT ){C.c}')
    additional.add_argument('-x', '--Hook_CoreX', action='store_true', help=f'{C.y}➸{C.g} Hook CoreX ( For Unity / Flutter & Crashed Apk ){C.r}')

    args = C.sys.argv[1:]
    Ext = ('.apk', '.apks', '.apkm', '.xapk')
    fixed = []; start = None; Valid_Ext = False

    for i, a in enumerate(args):
        if a in ['-i', '-m', '-C']:
            start, fixed = i + 1, fixed + [a]
        elif start and (a.endswith(Ext) or C.os.path.isdir(a)):
            fixed, start = fixed + [' '.join(args[start:i+1])], None
            Valid_Ext = True
        elif not start:
            fixed.append(a)

    if not Valid_Ext and C.sys.argv[1:2] != ['-C']:
        print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Only Supported Extensions {C.g}{Ext}\n")

    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Input Path {C.g}➸❥{C.y}", *fixed, f"{C.r}\n")

    return parser.parse_args(fixed)