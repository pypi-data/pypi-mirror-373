from noshot.utils.shell_utils import get_folder
from noshot.utils.shell_utils import get_file
from noshot.utils.shell_utils import remove_folder

available = {'-1  ' : "ML TS XAI(Folder)",
             '0   ' : "Remove Folder"}

def get(name = None, open = False):
    try:
        if name is not None:
            name = str(name)
        if name in ['-1']   :   get_folder("ML TS XAI", loc = True)
        elif name in ['0']  :   remove_folder("ML TS XAI")
        else:
            for k, v in available.items():
                sep = " : " if v else ""
                print(k,v,sep = sep)
    except Exception as error:
        print(error)