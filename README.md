# PowersiFscTaskSync

#### 介绍

创智和宇信息管理平台基金安全任务处理器

1. 因上周开会提到其它省份内外网不互通问题，因此已改造此工具，可以选择连接SQLite数据库，也可以选择直接连接postresql数据库

   工具主要功能是从信息管理平台下拉同步待处理任务，结合基金安全检查执行器，执行完毕后，编辑检查说明，将任务提交至信息管理平台

2. 此工具还需要结合基金安全检查配合使用，执行器的主要功能是运行SQL语句，将SQL语句结果更新至数据库。执行器只能在内网连接数据库运行，目前还在改造中。

#### 软件依赖

Pyqt5+requests+sqlalchemy+ddddocr

Pyqt5：界面开发
requests：网络请求
sqlalchemy：数据库连接
ddddocr：验证码识别

```shell
pip install PyQt5==5.15.4
pip install ddddocr==1.4.7
pip install requests==2.28.2
pip install SQLAlchemy==1.3.22
pip install psycopg2==2.7.7
pip install pydantic==1.10.6
pip install pyinstaller==5.8.0
```

#### 启动步骤

##### 1.配置文件

```ini
[User]
username = username
password = password
login_timer_minutes = 10

[Database]
url = postgresql://user:password@host:port/database
echo = True

```

| 变量类别            | 变量名              | 注释                                                         |
| ------------------- | ------------------- | ------------------------------------------------------------ |
| User                | username            | 信息管理平台账号                                             |
| User                | password            | 信息管理平台密码                                             |
| User                | login_timer_minutes | 每隔login_timer_minutes分钟登录一次信息管理平台，防止session失效 |
| Database            | url                 | sqlalchemy数据库连接地址                                     |
| Database            | echo                | 是否开启数据库日志                                           |

如果内网不通无法连接postgresql，可以连接sqlite，可进行如下配置：
```ini
[Database]
url = sqlite:///powersi.db?check_same_thread=False
echo = True
```

##### 2.打包exe

1.如果要打包exe，则安装以下依赖：

```
pip install pyinstaller
pip install auto-py-to-exe
```

2.打包命令：

```
pyinstaller --noconfirm --onefile --console --icon "C:/Users/Admin/PycharmProjects/powersi-fsc-task-sync/resource/ico/agt utilities.ico" --add-data "C:/Users/Admin/PycharmProjects/powersi-fsc-task-sync/resource/data/onnxruntime/capi/onnxruntime_providers_shared.dll;." --add-data "C:/Users/Admin/PycharmProjects/powersi-fsc-task-sync/resource/data/ddddocr;ddddocr/"  "C:/Users/Admin/PycharmProjects/powersi-fsc-task-sync/main.py"
```
使用auto-py-to-exe打包:

![打包界面.png](resource/images/打包界面.png)

（1）选择脚本位置：项目路径/powersi-fsc-task-sync/main.py

（2）选择单文件模式

（3）选择基于控制台的

（4）图标：项目路径/powersi-fsc-task-sync/resource/ico/agt utilities.ico

（5）附加文件：
   - 添加文件 python环境/Lib/site-packages/onnxruntime/capi/onnxruntime_providers_shared.dll
   - 添加目录 python环境/Lib/site-packages/ddddocr

（6）点击底部蓝色按钮开始打包

使用auto-py-to-exe打包，博客参考：https://zhuanlan.zhihu.com/p/487007957

##### 3.网络配置
打开创智和宇VPN

##### 4.启动
如果不选择打包，直接运行main.py进行启动 ,也可以双击运行打包后的main.exe文件

#### 使用说明

1.工具启动时会自动创建任务表：powersi_fsc_task

2.启动后点击 ，同步脚本开始从信息管理平台同步待办任务到数据库![工具界面](resource/images/工具界面.png)

3.脚本同步完毕后，运行基金安全检查执行器，待所有任务SQL执行完毕后再次打开此工具。（目前执行器还在改造当中）
