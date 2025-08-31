from .C_M import CM; C = CM();

# ---------------- Application Name ----------------
def Application_Name(L_S_F):
    pattern = C.re.compile(r'\.class public Lcom/pairip/application/Application;\s+\.super L([^;\s]+)', C.re.DOTALL)
    super_value = None
    for root, _, files in C.os.walk(L_S_F):
        for file in files:
            if file == 'Application.smali':
                smali_file_path = C.os.path.join(root, file)
                content = open(smali_file_path, 'r', encoding='utf-8', errors='ignore').read()
                match = pattern.search(content)
                if match:
                    super_value = match[1].replace(C.os.sep, ".")
                    break
        if super_value:
            break
    return super_value

# ---------------- Translate Smali Name ----------------
def Translate_Smali_Name(folder_name, isAPKTool):
    if isAPKTool:
        if folder_name == "smali":
            return "classes.dex"
        elif folder_name.startswith("smali_classes"):
            number = folder_name.replace("smali_classes", "")
            return f"classes{number}.dex" if number else "classes.dex"
    else:
        if folder_name == "classes":
            return "classes.dex"
        elif folder_name.startswith("classes"):
            number = folder_name.replace("classes", "")
            return f"classes{number}.dex" if number else "classes.dex"
    return folder_name

moved_files = []; smali_folders = []

# ---------------- Merge Smali Folders ----------------
def Merge_Smali_Folders(decompile_dir, isAPKTool, L_S_F):
    global moved_files, smali_folders
    moved_files = []; smali_folders = []
    smali_path = decompile_dir if isAPKTool else C.os.path.join(decompile_dir, "smali")
    prefix = "smali_classes" if isAPKTool else "classes"
    smali_folder = sorted([f for f in C.os.listdir(smali_path) if f == "smali" or f.startswith(prefix)], key=lambda x: int(x.split(prefix)[-1]) if x.split(prefix)[-1].isdigit() else 0)
    
    smali_folders = [C.os.path.join(smali_path, f) for f in smali_folder]
    last_path, prev_path = smali_folders[-1], smali_folders[-2]

    if C.os.path.isdir(last_path) and C.os.path.isdir(prev_path):
        for root, _, files in C.os.walk(last_path):
            for file in files:
                src = C.os.path.join(root, file)
                dest = C.os.path.join(prev_path, C.os.path.relpath(src, last_path))
                C.os.makedirs(C.os.path.dirname(dest), exist_ok=True)
                C.shutil.move(src, dest)
                moved_files.append((src, dest))
        print(f"\n{C.lb}[ {C.c}Merge {C.lb}] {C.rkj}➸❥ {C.pn}'{C.g}{C.os.path.basename(last_path)}{C.pn}' {C.c}& {C.pn}'{C.g}{C.os.path.basename(prev_path)}{C.pn}' {C.g}✔\n")
        C.shutil.rmtree(L_S_F)
    return moved_files

# ---------------- UnMerge Smali Folder ----------------
def UnMerge():
    global moved_files, smali_folders
    for src, dest in moved_files:
        C.os.makedirs(C.os.path.dirname(src), exist_ok=True)
        C.shutil.move(dest, src)
    print(f"\n\n{C.lb}[ {C.c}Reverse Merge {C.lb}] {C.rkj}➸❥ {C.pn}'{C.g}{C.os.path.basename(smali_folders[-2])}{C.pn}' {C.c}& {C.pn}'{C.g}{C.os.path.basename(smali_folders[-1])}{C.pn}' {C.g}✔\n")