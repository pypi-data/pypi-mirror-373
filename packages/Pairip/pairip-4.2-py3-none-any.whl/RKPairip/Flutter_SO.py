from .C_M import CM; C = CM()

# ---------------- Download libflutter.so ----------------
def Flutter_SO(apk_path, isFlutter):

    import requests

    Arch, Flutter_Libs = set(), []
    
    with C.zipfile.ZipFile(apk_path, 'r') as zip_ref:
        for item in zip_ref.infolist():
            if item.filename.startswith('lib/'):
                if item.filename.endswith('libflutter.so'):
                    Flutter_Libs.append(item.filename)
                if "arm64-v8a" in item.filename:
                    Arch.add("arm64-v8a")
                elif "armeabi-v7a" in item.filename:
                    Arch.add("armeabi-v7a")

        if isFlutter:
            print(f"\n{C.r}{'_' * 61}\n\n\n{C.lb}[ {C.y}WARN ! {C.lb}] {C.cb}This is {C.g}Flutter + Pairip {C.cb}APK, So For Pairip Bypass, Need Replace {C.pr}'{C.g}libflutter.so{C.pr}' {C.cb}in Your APK Arch")

            for lib in Flutter_Libs:
                with zip_ref.open(lib) as so_file:
                    read = so_file.read().decode('ascii', errors='ignore').replace('\x00', '')
                    if " (stable)" in read:
                        version_code = C.re.findall(r'\d+\.\d+\.\d+', read[:read.find(" (stable)")])[-1]
                    else:
                        version_code = "Unknown"

                    print(f"\n\n{C.lb}[ {C.pr}Flutter Dart Version {C.lb}]  {C.g}➸❥  {version_code}  ✔")
                    break

            if version_code == "Unknown":
                print(f"\n\n{C.lb}[ {C.y}Info {C.lb}] {C.rd}Version Not Founded in {C.pr}'{C.g}libflutter.so{C.pr}'")
                return

            URLS = []

            if "arm64-v8a" in Arch:
                URLS.append((f"https://github.com/TechnoIndian/Flutter-SO-Build/releases/download/v{version_code}/libflutter_so_arm64.zip", C.os.path.join(C.os.path.dirname(apk_path), "libflutter_so_arm64.zip")))

            if "armeabi-v7a" in Arch:
                URLS.append((f"https://github.com/TechnoIndian/Flutter-SO-Build/releases/download/v{version_code}/libflutter_so_armeabi_v7a.zip", C.os.path.join(C.os.path.dirname(apk_path), "libflutter_so_armeabi_v7a.zip")))

            for File_URL, File_Path in URLS:
                File_Name = C.os.path.basename(File_Path)

                try:
                    print(f'\n\n{C.lb}[ {C.pr}Downloading {C.lb}] {C.c}{File_Name}')
                    with requests.get(File_URL, stream=True) as response:
                        if response.status_code == 200:
                            total_size = int(response.headers.get('content-length', 0))
                            with open(File_Path, 'wb') as f:
                                print(f'       |')
                                for data in response.iter_content(1024 * 64):
                                    f.write(data)

                                    print(f"\r       {C.r}╰┈ PS {C.rkj}➸❥ {C.g}{f.tell()/(1024*1024):.2f}/{total_size/(1024*1024):.2f} MB ({f.tell()/total_size*100:.1f}%)", end='', flush=True)

                            print('  ✔')

                        else:
                            print(f'\n\n{C.lb}[ {C.y}Warn ! {C.lb}]{C.rd} Download Failed {C.y}{File_Name} {C.rd}| Status Code: {response.status_code}\n\n{C.lb}[ {C.y}INFO ! {C.lb}]{C.rd} {C.c}Please Download Manually\n    |\n    {C.r}╰┈ URL {C.rkj}➸❥ {C.g}{File_URL}')

                except requests.exceptions.RequestException:
                    print(f'\n\n{C.lb}[ {C.y}Warn ! {C.lb}]{C.rd} No Internet Connection\n\n{C.lb}[ {C.y}INFO ! {C.lb}]{C.cb} Internet Connection is Required to Download\n    |\n    {C.r}╰┈ URL {C.rkj}➸❥ {C.g}{File_URL}')