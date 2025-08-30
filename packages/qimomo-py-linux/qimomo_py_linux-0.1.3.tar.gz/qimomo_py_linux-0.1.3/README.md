## Author
**七魔陌** 
- Email: qimomo.17@qq.com
0.1.3 ：
- 前面几个版本有重大问题请不要使用\n
本模块是在Python中执行简单Linux命令(实现方法)
主要是作者不会Windows上cmd命令而制作的一个模块
\n里面有一个su  :
      su qi  #登录用户qi
用之前使用命令
pythonlinux-file-path you_path_file
设置su与histort.txt的位置
比如在 /data/data/pythonlinux/里面有su与histort.txt
命令就是:
pythonlinux-file-path /data/data/pythonlinux/

import pythonlinux
a=linux()
a.run('pythonlinux-file-path /data/data/pythonlinux/')
#或者直接指定
linux_file_path='/data/data/pythonlinux/'
'''
'''python    
import pylinux
a=linux()
a.run('pylinux-file-path /data/data/pythonlinux/')
#或者直接指定
pylinux_file_path='/data/data/pythonlinux/'
'''
su文件：
用户名#*$权限路径#*$密码
比如:
     用户名： qi
     密码 ：  123
     访问路径： /data/data/pythonlinux/
就写成
qi#*$/data/data/pythonlinux/#*$123
没密码：
qi#*$/data/data/pythonlinux/#*$0
程序最高访问权限:
qi#*$0#*$123
多个：
qi#*$/data/data/pythonlinux/#*$123
ii#*$0#*$0

![使用例子1:模块版本0.1.3](./images/1.PNG)
![使用例子2:模块版本0.1.3](./images/2.PNG)