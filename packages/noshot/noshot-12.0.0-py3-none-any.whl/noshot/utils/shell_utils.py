import os
import shutil
import subprocess
import pathlib

def get_folder(folder_path, loc = False):
    src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", pathlib.Path(folder_path))
    try:
        dest = os.path.join(os.getcwd(), pathlib.Path(folder_path))
        shutil.copytree(src, dest, symlinks=False, copy_function = shutil.copy2,
                        ignore=shutil.ignore_patterns('.ipynb_checkpoints', '__init__.py', '__pycache__'),
                        ignore_dangling_symlinks=False, dirs_exist_ok=True)
    except:
        try:
            dest = os.path.join(os.path.expanduser('~'), "Downloads", pathlib.Path(folder_path))
            shutil.copytree(src, dest, symlinks=False, copy_function = shutil.copy2,
                            ignore=shutil.ignore_patterns('.ipynb_checkpoints', '__init__.py', '__pycache__'),
                            ignore_dangling_symlinks=False, dirs_exist_ok=True)
        except Exception as error:
            print(error)
            return
    finally:
        if loc:
            print("Path:",dest)

def get_file(file_path, loc = False, open = False):
    src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", pathlib.Path(file_path))
    try:
        dest = os.path.join(os.getcwd(), pathlib.Path(file_path).name)
        shutil.copy(src, dest)
        if open:
            subprocess.Popen(f"jupyter notebook {dest}")
    except:
        try:
            dest = os.path.join(os.path.expanduser('~'), "Downloads", pathlib.Path(file_path).name)
            shutil.copy(src, dest)
        except Exception as error:
            print(error)
    finally:
        if loc:
            print("Path:",dest)

def remove_folder(folder_path):
    try:
        src1 = os.path.join(os.getcwd(), pathlib.Path(folder_path))
        src2 = os.path.join(os.path.expanduser('~'), "Downloads", pathlib.Path(folder_path))
        if os.path.exists(src1) or os.path.exists(src2):
            shutil.rmtree(src1, ignore_errors =  True)
            shutil.rmtree(src2, ignore_errors =  True)
            if os.path.exists(src1) or os.path.exists(src2):
                print("Deletion Impossible [File Not Closed - Shutdown File Kernel]\nGo to Home page -> Running Tab -> Click Shut Down All")
            else:
                print(f"Folder({pathlib.Path(folder_path)}) Removed Successfully")
        else:
            print(f"Folder({pathlib.Path(folder_path)}) Not Found [Repeated Iteration | Probably Removed Manually]")
    except Exception as error:
        print(error)