"""
=====简介=====
模块名称:pythonlinux
作者:qimomo
实现python中运行简单命令
"""
__help__ ="""
模块名称:pythonlinux
作者:qimomo
pythonlinux:help
    class linux:
        run() : 执行命令
命令:
    return ~~~ : 将命令 ~~~ 返回输出
    linux-system ~~~ : 向系统发送 ~~~
clear_screen : 用于清屏
calculate_folder_depth : 用于查看文件夹最深深度(几个文件夹)
get_folder_size_getsize : 获取文件，文件夹大小
download_file   : 用于下载文件
"""


print("pythonlinux:正在导入模块... \n    Importing module...")
import time
import os
import shutil
import subprocess
import sys
import time
import requests
from tqdm import tqdm
from getpass import getpass#password = getpass("请输入密码")  输入时不会显示内容


print("pythonlinux:模块导入:ok \n    Importing module:ok\npythonlinux:正在准备函数... \n    Preparing the function...")
linux_file_path = None
def calculate_folder_depth(path):#深度
    if not os.path.isdir(path):
        return 0
    max_depth = 0
    for root, dirs, files in os.walk(path):
        current_depth = len(root.split(os.sep)) - len(path.split(os.sep)) - 1  # 减去1因为path本身不计入深度
        max_depth = max(max_depth, current_depth)
    return max_depth + 1 if max_depth > 0 else 0 

def get_folder_size_getsize(file_path):#大小
    total_size = 0
    if os.path.isdir(file_path):
        for dirpath, dirnames, filenames in os.walk(file_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
    else:
        total_size=os.path.getsize(file_path)
    return total_size

def download_file(url, filename=None):
    if not filename:
        filename = url.split('/')[-1]
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    with open(filename, 'wb') as f, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            size = f.write(chunk)
            bar.update(size)
    print(f"\nDownload completed: {filename}")


# 检查是否授予存储权限（仅限部分设备）
def check():
    result = os.popen("pm list permissions").read()
    if "android.permission.WRITE_EXTERNAL_STORAGE" in result:
        print("已授予存储权限")
    if "MANAGE_EXTERNAL_STORAGE" in result:
        print("已授予MANAGE_EXTERNAL_STORAGE权限")


def clear_screen():
    # 对于 Windows 系统
    if os.name == 'nt':
        os.system('cls')
    # 对于 Linux 和 macOS 系统
    else:
        os.system('clear')





class linux():
    def __init__(Linux):
        
        print("pythonlinux:正在初始化... \n    Initializing...")
        #Linux.time=time;Linux.os=os;Linux.shutil=shutil;Linux.subprocess=subprocess;Linux.sys=sys
        Linux.access = os.getcwd() # "#/*/" #默认权限
        Linux.user = "" #默认用户
        Linux.default_access = os.getcwd() #Default 默认
        Linux.login_tf = False
        Linux.工作路径=os.getcwd()
        Linux.history_temp="";Linux.str_input=""
        print("pythonlinux:正在读取history.txt文件... \n    Reading the history.txt file...")
        try:
            if linux_file_path:
                os.chdir(linux_file_path)
                with open("history.txt") as open_history:
                    Linux.history_temp+=open_history.read()
                    open_history.close()
                    print("pythonlinux:读取history.txt:ok\n    Reading the history.txt file:ok")
            else :
                print(f"pythonlinux:读取history.txt文件失败\n    pythonlinux: Failed to read the history.txt file \n    [请先设置文件存放地(linux_file_path)] \npythonlinux: 已跳过 Skipped ")
        except Exception as Ex:
            print(f"pythonlinux:读取history.txt文件失败\n    pythonlinux: Failed to read the history.txt file \n    [{Ex}] \npythonlinux: 已跳过 Skipped ")
        Linux.print=""
        os.chdir(Linux.default_access)
        Linux.linux_help =[[
            ["cd"+" "*8+":更换目录位置如果路径中有空格请用'\-'取代空格",
            "history"+" "*3+":查看写过的命令",
            "ls"+" "*8+":查看目录下的文件",
            "pwd"+" "*7+":查看此目录的路径",
            "cat"+" "*7+":查看文件内容",
            "\033[91mfind\033[0m"+" "*6+"\033[91m查看某个文件的位置[find / -name ]\033[0m",
            "rm"+" "*8+":删除文件(夹)[rm -r]",
            "mkdir"+" "*5+":创建文件夹",
            "touch"+" "*5+":创建文件",
            "bash"+" "*6+":执行bash脚本"],
            ["clear"+" "*6+":清屏",
             "su"+" "*8+":登录用户",
             "linux-wget"+":pythonlinux下载工具",
             "return ~~~ : 将命令 ~~~ 返回输出",
             "linux-system ~~~ : 向系统发送 ~~~"
            ]
            ]]
        Linux.run = Linux.执行命令
        print("pythonlinux:初始化:ok\n    Initializing:ok")
        if not linux_file_path:
            print("如果使用'su'请先设置文件存放地(linux_file_path)\n   请使用'pythonlinux-file-path  [you path file]'设置")
    def 执行命令(Linux,*命令):
        命令= str(*命令) if 命令 else False 
        if 命令=="\n":
            return None
        Linux.命令_列表=[]
        路径_print='..'+Linux.工作路径[-10:] if len(Linux.工作路径)>10 else Linux.工作路径
        Linux.str_input=str(input(f"\033[92m(Linux)-[{Linux.print}{路径_print}]$\033[0m") if not 命令 else 命令)
        ##################################
        if Linux.str_input:
            Linux.history_temp+=Linux.str_input+"\n"
            Linux.命令_列表=Linux.str_input.split(" ")#分割字符
            Linux.命令_列表 = [data.replace("/-"," ") for data in Linux.命令_列表 if data != ""]
            Linux.命令长度=len(Linux.命令_列表)
            print(f"\033[92m>\033[0m\033[94m{Linux.str_input}\033[0m\033[92m>\033[0m")
            if Linux.命令_列表[0]=="cd":#
                LJ_temp=Linux.工作路径
                """
                if ((Linux.命令_列表[1][-1]=="\\"  ) and (Linux.命令_列表[1]!="/")) if len(Linux.命令_列表[1])>1 else False:
                    jio=Linux.命令_列表[1][:-1]
                else:
                    jio=Linux.命令_列表[1]
                """
                if len(Linux.命令_列表[1])>1 :
                    if Linux.access != "#/*/" :
                        if Linux.access in Linux.命令_列表[1] or Linux.access == "0" :#and Linux.access != Linux.命令_列表[1]:
                            Linux.工作路径=Linux.命令_列表[1]
                        else:
                            print("\033[91m您没有足够的权限访问\033[0m")
                            Linux.工作路径=LJ_temp
                try:
                    os.listdir(Linux.工作路径)
                except PermissionError :
                    print("\033[91m您没有足够的权限访问\033[0m")
                    Linux.工作路径=LJ_temp
                except Exception as Ex:
                    print(f"\033[91m错误{[Ex]}\033[0m")
                    Linux.工作路径=LJ_temp
                os.chdir(Linux.工作路径)
                Linux.工作路径=os.getcwd() if ( os.getcwd()[-1]=="/" or os.getcwd()[-1]==r"\\") else (os.getcwd() + "/"  if ( "/" in os.getcwd() )  else os.getcwd()+"\\")
            elif Linux.命令_列表[0]=="ls":
                if Linux.access in Linux.工作路径 or Linux.access == "0" :
                    try:
                        #os.path.isdir()如果是文件夹则返回True  isfile
                        if Linux.命令长度 == 1 or ( Linux.命令长度 == 2 and Linux.命令_列表[1] not in ["-t","-b","-l"] and (Linux.access in Linux.命令_列表[1] or Linux.access == "0")):
                            for i in os.listdir(os.getcwd() if Linux.命令长度 != 2 else Linux.命令_列表[1]):
                                print("\033[94m"+i+"\033[0m" if os.path.isdir(i) else i)
                        elif Linux.命令长度==2:
                            if Linux.命令_列表[1]=="-t":
                                for i in os.listdir(Linux.工作路径):
                                    print(f"\033[94m{i} -- "+str(calculate_folder_depth(i))+"\033[0m" if os.path.isdir(i) else i)
                            elif Linux.命令_列表[1]=="-l":
                                for i in os.listdir(Linux.工作路径):
                                    print(f"\033[94m{i} -- "+str(get_folder_size_getsize(i))+"\033[0m" if os.path.isdir(i) else f"{i} -- "+str(get_folder_size_getsize(i))+"B")
                        else:
                            print("错误还没有此功能")
                    except PermissionError:
                        print(f"\033[91m您没有足够的权限\033[0m")
                    except Exception as Ex:
                        print(f"错误{Ex}")
                else:
                    print(f"\033[91m您没有足够的权限查看\033[0m")
            elif Linux.命令_列表[0]=="history":
                try :
                    
                    Linux.history_temp= "" if ( Linux.命令_列表[1]=="-c" if len(Linux.命令_列表)>1 else False) else Linux.history_temp
                    if (Linux.命令_列表[1]=="-a" if len(Linux.命令_列表)>1 else False) :
                        if linux_file_path:
                            temp_path = Linux.工作路径
                            Linux.执行命令(f'cd {linux_file_path}')
                            if "su" in os.listdir():
                                lk_history=open("histort.txt","a")
                                lk_history.write(Linux.history_temp+"\n")
                                lk_history.close()
                            else:
                                print(f"在{linux_file_path}中没有histort.txt文件")
                            Linux.执行命令(f"cd {temp_path}")
                        else:
                            print("还没有设置linux_file_path,请使用'pythonlinux-file-path  [you path file]'设置命令设置文件位置")
                    elif Linux.命令_列表[1]=="-c" if len(Linux.命令_列表)>1 else False:
                        Linux.history_temp = ""
                    else :
                        print(Linux.history_temp)
                except Exception as Ex:
                    print(f"错误[{Ex}]")
            elif Linux.命令_列表[0]=="pwd":
                print(os.getcwd())
            elif Linux.命令_列表[0]=="cat":
                    if Linux.命令长度>1:
                        if Linux.access in Linux.工作路径 or Linux.access == "0" :
                            try:
                                预处理=open(Linux.命令_列表[1],"r")
                                print(预处理.read())
                                预处理.close()
                            except Exception as Ex:
                                print(f"没有\"{Linux.命令_列表[1]}\"文件")
                        else:
                            print(f"\033[91m您没有足够的权限查看\033[0m")
                    else:
                        print("没有要打开的文件")
            elif Linux.命令_列表[0]=="rm":
                if Linux.命令长度>2:
                    #os.path.exists(路径) 用于判断是否为有效路径不区分文件或目录
                    if (Linux.access in Linux.工作路径 or Linux.access == "0") and os.path.exists(Linux.命令_列表[2]) :
                        if Linux.命令_列表[1]=="-r":
                            # 递归删除目录及其内容shutil.rmtree()
                            #删除文件os.remove()
                            try:
                                if os.path.isdir(Linux.命令_列表[2]):
                                    shutil.rmtree(Linux.命令_列表[2])
                                else:
                                    os.remove(Linux.命令_列表[2]) #os.remove(临时路径) if os.path.isfile(临时路径) else shutil.rmtree(临时路径)
                            except Exception as Ex:
                                print(f"\033[91m删除失败[{Ex}]\033[0m")
                    else:
                        print(f"\033[91m您没有足够的权删除{Linux.命令_列表[2]}\033[0m")
            elif Linux.命令_列表[0]=="find":
                if Linux.命令长度>3:
                    if Linux.命令_列表[1]=="/":
                        if Linux.命令_列表[2]=="-name":
                            try:
                                print(Linux.命令_列表[3],":[",os.path.dirname(Linux.命令_列表[3]),"]")
                            except FileNotFoundError :
                                print("\033[91m{Linux.命令_列表[3]}不存在\033[0m")
                            except Exception as Ex:
                                print("请检查名称是否正确")
                else :
                    print("\033[91m请写完整指令\033[0m")
            elif Linux.命令_列表[0]=="mkdir":#创建文件夹
                if Linux.命令长度>1:
                    if (Linux.access in Linux.工作路径 or Linux.access == "0") and ((Linux.access in Linux.命令_列表[1]) if os.path.exists(Linux.命令_列表[1]) else True):
                        try:
                            os.makedirs(Linux.命令_列表[1])
                        except Exception as Ex:
                            print(f"\033[91m创建失败{Ex}\033[0m")
                    else:
                        print(f"\033[91m您没有足够的权限创建{Linux.命令_列表[1]}文件夹\033[0m")
                else:
                    print("\033[91m请把命令写完整\033[0m")
            elif Linux.命令_列表[0]=="touch":#创建文件
                if 1 < Linux.命令长度 <= 2:
                    if (Linux.access in Linux.工作路径 or Linux.access == "0") and ((Linux.access in Linux.命令_列表[1]) if os.path.exists(Linux.命令_列表[1]) else True) :
                        try:
                            with open(Linux.命令_列表[1],"w") as open_:
                                open_.close()
                        except PermissionError:
                            print("\033[91m你没有足够的权限\033[0m")
                        except Exception as Ex:
                            print(f"\033[91m创建{Linux.命令_列表[1]}失败[{Ex}]\033[0m")
                    else:
                        print(f"\033[91m您没有足够的权限创建{Linux.命令_列表[1]}文件\033[0m")
                else:
                    print("\033[91m请把命令写完整\033[0m")
            elif Linux.命令_列表[0]=="bash":
                if Linux.命令长度==2:
                    try:
                        print(">bash>开始执行:")
                        #with open(Linux.工作路径+Linux.命令_列表[1] if "//" not in Linux.命令_列表[1] and "\\" not in Linux.命令_列表[1] else Linux.命令_列表[1],"r") as 预处理: 
                        with open(Linux.命令_列表[1] if "//" not in Linux.命令_列表[1] and "\\" not in Linux.命令_列表[1] else Linux.命令_列表[1],"r") as 预处理: 
                            for 文件命令 in 预处理:
                                Linux.执行命令(文件命令.rstrip("\n"))
                            预处理.close()
                        print("执行结束")
                    except FileNotFoundError :
                        print(f"没有{Linux.命令_列表[1]}文件")
                    except Exception as Ex:
                        print(f"执行时出现错误[错误{Ex}]")
            elif Linux.命令_列表[0].upper() in  ["PYTHON","PY"]:
                if Linux.命令长度==2 :
                    执行文件路径=Linux.命令_列表[1]
                    """
                    if ("/" not in Linux.命令_列表[1]) or ("\\" not in Linux.命令_列表[1]):
                        执行文件路径=Linux.工作路径+Linux.命令_列表[1]
                        print(执行文件路径)
                    """
                    try:
                        try:
                            预处理=open(执行文件路径,"r")
                        except Exception as Ex:
                            print("\033[91m请检查路径或者文件名称是否正确\033[0m")
                        print("\033[91m>开始执行>\033[0m");exec(预处理.read());print("\033[91m执行结束\033[0m")
                        预处理.close()
                    except Exception as Ex:
                        print(f"\033[91m执行文件时发生错误[{Ex}]\033[0m")
                elif  Linux.命令长度>=5 or Linux.命令长度==7:
                        安装命令列表=[]
                        print(Linux.命令长度)
                        if Linux.命令长度==5:
                            #执行安装命令
                            安装命令列表=[sys.executable,Linux.命令_列表[1],Linux.命令_列表[2],Linux.命令_列表[3],Linux.命令_列表[4]]
                        elif Linux.命令长度==7:
                            安装命令列表=[sys.executable,*Linux.命令_列表[1:].extend(" ","")]
                        try:
                            subprocess.check_call(安装命令列表)
                        except Exception as Ex:
                            print(f"\033[91m命令书写错误[错误{Ex}]\033[0m")
                elif len(Linux.命令_列表)==1:
                    print("\033[92m>>开始执行\033[0m");tf_py=True
                    while tf_py:
                        执行=input(">>>")
                        if 执行 !="f":
                            try:
                                exec(执行)
                            except Exception as Ex:
                                print(f"错误{Ex}")
                        else :
                            tf_py=False
                    print(f"\033[91m{Linux.str_input}结束>\033[0m")
            elif Linux.命令_列表[0]=="cp":
                if len(Linux.命令_列表)>2:
                    if (Linux.access in Linux.工作路径 or Linux.access == "0") and (((Linux.access in  Linux.命令_列表[2]) if ("./" not in Linux.命令_列表[2] or ".\\" not in Linux.命令_列表[2]) else (Linux.access in Linux.工作路径 or Linux.access == "0") ) if os.path.exists(Linux.命令_列表[2]) else os.path.isfile(Linux.命令_列表[2])) :
                        try:
                            if os.path.isfile(Linux.命令_列表[1]):
                                shutil.copy(Linux.命令_列表[1], Linux.命令_列表[2])
                            else:
                                shutil.copytree(Linux.命令_列表[1], Linux.命令_列表[2])
                        except FileExistsError as File:
                           print(f"\033[91m[错误{Linux.命令_列表[1]}在{Linux.命令_列表[2]}中存在][详细:{File}]\033[0m")
                           if input(f"请问您要覆盖{Linux.命令_列表[2]}中{Linux.命令_列表[1]}吗(Y/n/是/否)").upper() in ["Y","N","是","否"]:
                               shutil.copytree(Linux.命令_列表[1], Linux.命令_列表[2],dirs_exist_ok=True)
                        except Exception as Ex:
                            print(f"\033[91m[错误{Ex}]\033[0m")
                    else:
                        print(f"\033[91m您没有足够的权限复制{Linux.命令_列表[1]}到{Linux.命令_列表[2]}\033[0m")
                else:
                    print("还没有此功能或查看命令是否正确")
            #[@_&]
            #
            elif Linux.命令_列表[0]=="su":
                if linux_file_path :
                    if 2 <= Linux.命令长度  <= 3 :
                        TF = False
                        TF_user = False
                        if Linux.命令_列表[1] == "-" and Linux.命令长度 == 3:
                            sequence = 2
                        else:
                            sequence = 1
                        temp_path = Linux.工作路径
                        Linux.执行命令(f'cd {pythonlinux_file_path}')
                        if "su" in os.listdir():
                            with open("su") as open_su:
                                for i in open_su.read().split("\n"):
                                    list_i=i.split("#*$")
                                    if Linux.命令_列表[sequence] == list_i[0] :
                                        #getpass.getpass
                                        TF_user = True
                                        if (getpass("输入密码: ") == list_i[2] ) if list_i[2] != "0" else True :
                                            Linux.access=list_i[1]
                                            TF = True;Linux.login_tf = True
                                        else:
                                            print("密码错误")
                                        break
                                open_su.close()
                        else:
                            print(f"没有'su'文件")
                        if TF:
                            Linux.print=f"@{Linux.命令_列表[sequence]}: "
                        elif TF_user :
                            pass
                        else:
                            print(f"\033[91m没有用户{Linux.命令_列表[1]}\033[0m")
                        Linux.执行命令(f"cd {temp_path}")
                else:
                    print("还没有设置pythonlinux_file_path,请使用'pythonlinux-file-path  [you path file]'设置命令设置文件位置")
            elif Linux.命令_列表[0] == "clear":
                clear_screen()
            elif Linux.命令_列表[0]=="linux-wget":
                if 2 <= Linux.命令长度  < 4 :
                    print("正在下载")
                    download_file(Linux.命令_列表[1],filename= Linux.命令_列表[2] if Linux.命令长度 == 3 else None )
                    print("下载完成")
            elif Linux.命令_列表[0].upper() in ["EXIT","F"]:
                if Linux.命令长度 == 2:
                    if Linux.命令_列表[1] == "-l":
                        return "exit"
                if Linux.login_tf :
                    Linux.print = ""
                    Linux.user = ""
                    Linux.access = Linux.default_access
                    Linux.login_tf=False
                    return None
                else:
                    return "exit"
            elif Linux.命令_列表[0] == "return":
                return_str = ""
                for i in Linux.命令_列表[1:]:
                        return_str += i +" "
                return return_str
            elif Linux.命令_列表[0] == "linux-system":
                return_str = ""
                for i in Linux.命令_列表[1:]:
                        return_str += i +" "
                os.system(return_str)
            elif Linux.命令_列表[0] == "pythonlinux-file-path":
                if Linux.命令长度 >1 :
                    linux_file_path = Linux.命令_列表[1]
                else:
                    print("命令不正确")
            else :
                try :
                    subprocess.run([*Linux.命令_列表])#os.system()
                except Exception as Ex:
                    print(Ex)
                    for i_cmd_ml_ in Linux.linux_help [0]:
                        for ii_cmd_ml_ in i_cmd_ml_:
                            print(ii_cmd_ml_)
                        if input(">")=='f':
                            break
        if 命令:
            return "exit"
print("pythonlinux:函数准备:ok \n    Preparing the function:ok")