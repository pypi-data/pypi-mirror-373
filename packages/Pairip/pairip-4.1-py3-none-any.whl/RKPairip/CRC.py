from .C_M import CM; C = CM()

# ---------------- Format Time ----------------
def Format_Time(timestamp):
    return C.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

# ---------------- CRC Fix ----------------
def CRC_Fix(M_Skip, apk_path, build_dir, file_types):
    if M_Skip:
        with C.zipfile.ZipFile(build_dir, 'r') as zip_ref:
            LD = f'classes{int(sorted([f.filename for f in zip_ref.infolist() if f.filename.endswith(".dex")])[-1].split("classes")[1].split(".dex")[0])}.dex'
        input(f"\n{C.lb}[ {C.pr}FYI ! {C.lb}] {C.c} Now Script is Listen Mode, Cuz The value of your Last Dex {C.y}{LD} {C.c}Field/method is greater than 65536., So you can do Max Value Dex Redivision {C.pr}( like 65536 ) {C.g}using MT/ApkTool_M then correct the name of the APK again and then press enter in the script, which will bypass CRC )\n\n\n{C.lb}[ {C.pr}CRC Fix {C.lb}] {C.c} Press Enter to After Dex Redivision & Should Apk Name is {C.y}{C.os.path.basename(build_dir)} ...\n")

    Fix_Count, Logs = 0, []
    try:
        with C.zipfile.ZipFile(apk_path) as Zip_OR, C.zipfile.ZipFile(build_dir) as Zip_Fix:
            F = lambda Z: {i.filename: (i.CRC, i.date_time) for i in Z.infolist() if any(ft in i.filename for ft in file_types)}
            ORIGIN, Fix = F(Zip_OR), F(Zip_Fix)

        for filename, (OR_CRC, OR_Time) in ORIGIN.items():
            if filename in Fix and OR_CRC != Fix[filename][0]:
                with open(build_dir, "rb+") as f:
                    D = f.read().replace(Fix[filename][0].to_bytes(4, 'little'), OR_CRC.to_bytes(4, 'little'))
                    f.seek(0); f.write(D)
                Fix_Count += 1
                Logs.append((filename, f"{OR_CRC:08x}", f"{Fix[filename][0]:08x}", Format_Time(C.datetime(*OR_Time).timestamp()), Format_Time(C.datetime(*Fix[filename][1]).timestamp())))

    except Exception as e:
        print(f"{C.lb}[{C.rd}Error{C.lb}] {C.rd}{e}\n")
        return None

    print(f"\n{'':20}✨ {C.g}CRCFix by {C.rkj}Kirlif{C.g}' ✨\n")
    print(f"{C.c}{'File Name':<22}{'CRC':<12}{'FIX':<12}{'Modified'}")

    for e in Logs:
        print(f"\n{C.g}{e[0]:<22}{e[1]}{'':<4}{e[2]}{'':<4}{e[4]}\n")
    print(f"\n{C.lb}[{C.c}  INPUT  {C.lb}] {C.g}➸❥ {C.y}{apk_path}\n")
    print(f"{C.lb}[{C.c}  OUTPUT  {C.lb}] {C.g}➸❥ {C.y}{build_dir}\n")
    print(f"\n{C.lb}[{C.c}  CRCFix  {C.lb}] {C.g}➸❥ {C.pr}{Fix_Count}\n")
    return build_dir