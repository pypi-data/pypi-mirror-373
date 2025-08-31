from .C_M import CM; C = CM()

class FileCheck:
    # ---------------- Set Jar & Files Paths ----------------
    def Set_Path(self):
        run_dir = C.os.path.dirname(C.os.path.abspath(C.sys.argv[0]))
        script_dir = C.os.path.dirname(C.os.path.abspath(__file__))
        self.APKEditor_Path = C.os.path.join(run_dir, "APKEditor.jar")
        self.APKTool_Path = C.os.path.join(run_dir, "APKTool_OR.jar")
        self.Axml2Xml_Path = C.os.path.join(run_dir, "Axml2Xml.jar")
        self.Objectlogger = C.os.path.join(script_dir, "Objectlogger.smali")
        self.Pairip_CoreX = C.os.path.join(script_dir, "lib_Pairip_CoreX.so")

    # ---------------- SHA-256 CheckSum ----------------
    def Calculate_CheckSum(self, file_path):
        sha256_hash = C.hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return None

    # ---------------- Download Files ----------------
    def Download_Files(self, Jar_Files):
        import requests
        downloaded_urls = set()
        for File_URL, File_Path, Expected_CheckSum in Jar_Files:
            File_Name = C.os.path.basename(File_Path)

            if C.os.path.exists(File_Path):
                if self.Calculate_CheckSum(File_Path) == Expected_CheckSum:
                    continue
                else:
                    print(f"{C.rd}[ {C.pr}File {C.rd}] {C.c}{File_Name} {C.rd}is Corrupt (Checksum Mismatch).\n\n{C.lb}[ {C.y}INFO ! {C.lb}]{C.rd} Re-Downloading, Need Internet Connection.\n")
                    C.os.remove(File_Path)
            try:
                Version = C.re.findall(r'version = "([^"]+)"', requests.get("https://raw.githubusercontent.com/TechnoIndian/RKPairip/main/pyproject.toml").text)[0]
                if Version != "4.1":
                    print(f"\n{C.lb}[ {C.y}Update {C.lb}]{C.c} Updating RKPairip ➸❥ {C.g}{Version}...\n\n")
                    cmd = (["pip", "install", "git+https://github.com/TechnoIndian/RKPairip.git"] if C.os.name == "nt" else "pip install --force-reinstall https://github.com/TechnoIndian/RKPairip/archive/refs/heads/main.zip")
                    C.subprocess.run(cmd, shell=isinstance(cmd, str), check=True)

                print(f'\n{C.lb}[ {C.pr}Downloading {C.lb}] {C.c}{File_Name}')
                with requests.get(File_URL, stream=True) as response:
                    if response.status_code == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        with open(File_Path, 'wb') as f:
                            print(f'       |')
                            for data in response.iter_content(1024 * 64):
                                f.write(data)

                                print(f"\r       {C.r}╰┈ PS {C.rkj}➸❥ {C.g}{f.tell()/(1024*1024):.2f}/{total_size/(1024*1024):.2f} MB ({f.tell()/total_size*100:.1f}%)", end='', flush=True)

                        print(' ✔\n')

                    else:
                        exit(f'\n\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} Failed to download {C.y}{File_Name} {C.rd}Status Code: {response.status_code}\n\n{C.lb}[ {C.y}INFO ! {C.lb}]{C.rd} Restart Script...\n')

            except requests.exceptions.RequestException:
                exit(f'\n\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} Got an error while Fetching {C.y}{File_Path}\n\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} No internet Connection\n\n{C.lb}[ {C.y}INFO ! {C.lb}]{C.rd} Internet Connection is Required to Download {C.y}{File_Name}\n')

    # ---------------- Files Download Link ----------------
    def F_D(self):

        self.Download_Files([
            ("https://github.com/TechnoIndian/Tools/releases/download/Tools/APKEditor.jar", self.APKEditor_Path, "c242f5fc4591667a0084668320d0016a20e7c2abae102c1bd4d640e11d9f60ee"),
            ("https://raw.githubusercontent.com/TechnoIndian/Objectlogger/main/Objectlogger.smali", self.Objectlogger, "ff31dd1f55d95c595b77888b9606263256f1ed151a5bf5706265e74fc0b46697"),
            ("https://github.com/TechnoIndian/Tools/releases/download/Tools/lib_Pairip_CoreX.so", self.Pairip_CoreX, "22a7954092001e7c87f0cacb7e2efb1772adbf598ecf73190e88d76edf6a7d2a")
        ])

        C.os.system('cls' if C.os.name == 'nt' else 'clear')

    # ---------------- Files Download Link ----------------
    def F_D_A(self):

        self.Download_Files([
            ("https://github.com/TechnoIndian/Tools/releases/download/Tools/APKTool.jar", self.APKTool_Path, "effb69dab2f93806cafc0d232f6be32c2551b8d51c67650f575e46c016908fdd"),
            ("https://github.com/TechnoIndian/Tools/releases/download/Tools/Axml2Xml.jar", self.Axml2Xml_Path, "e3a09af1255c703fc050e17add898562e463c87bb90c085b4b4e9e56d1b5fa62")
        ])