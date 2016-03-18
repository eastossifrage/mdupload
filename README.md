# mdupload —— 用Flask为gitblog开发一个上传文件的管理模块

> gitblog是个好东西，但是在实际应用中，还是有些不便之处，比如说还得自己上传md文件，而且上传之后还得修改权限，还得清空缓存，总之，为了解决这些不便之处，特用flask开发了一个管理模块，方便自己。

### 应用环境介绍

* Ubuntu 14.04
* 默认的python 2.7.6
* 默认安装的nginx 1.4.6

### 配置flask应用环境

```bash
os373/
    gitblog/
    mdupload/
```

以上是我的文件组织架构。
现在，你可以按照[《第一章 使用 flask 虚拟环境》](http://www.os373.cn/blog/flask001.html)来设置自己的flask应用环境。

```bash
$ sudo apt-get install python-virtualenv
$ cd mdupload
$ virtualenv flask
$ source flask/bin/activate
(flask)$
(flask)$ pip install -r requirements.txt
```
### 安装uWSGI

```bash
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install build-essential python python-dev
sudo pip install uwsgi
```

### 配置nginx

在原有的php环境的配置文件下进行配置。
```bash
sudo vi /etc/nginx/sites-available/default
```

新增一下内容：
```bash

server {
        listen 8888;
        server_name os373.cn;
        charset utf-8;
        client_max_body_size 75M;

        location / {
                try_files $uri @mdupload;
        }
        locahion @mdupload {
                include uwsgi_params;
                uwsgi_pass unix:/var/www/os373/mdupload/mdupload_uwsgi.sock;
        }
}


```

### 配置 uWSGI
创建一个新的uWSGI配置文件/var/www/os373/mdupload/mdupload_uwsgi.ini

```bash
[uwsgi]
base = /var/www/os373/mdupload
app = manage
module = %(app)

home = %(base)/flask
pythonpath = %(base)
socket = /var/www/os373/mdupload/%n.sock
master = true
processes = 8
workers = 2
chmod-socket = 644
callable = app
logto = /var/log/uwsgi/%n.log

```

执行uWSGI，用新创建的配置文件作为参数：

```bash
uwsgi --ini /var/www/os373/mdupload/mdupload_uwsgi.ini
```

我们的工作现在基本完成了，唯一剩下的事情是配置uWSGI在后台运行，这是uWSGI Emperor的职责。

### uWSGI Emperor

创建一个初始配置来运行emperor - `/etc/init/uwsgi.conf`：

```bash
description "uWSGI"
start on runlevel [2345]
stop on runlevel [06]
respawn
 
env UWSGI=/usr/local/bin/uwsgi
env LOGTO=/var/log/uwsgi/emperor.log
 
exec $UWSGI --master --emperor /etc/uwsgi/vassals --die-on-term --uid os373 --gid os373 --logto $LOGTO
```

最后一行运行uWSGI守护进程并让它到/etc/uwsgi/vassals文件夹查找配置文件。创建这个文件夹，在其中建立一个到链到我们刚创建配置文件的符号链接。

```bash
sudo mkdir /etc/uwsgi && sudo mkdir /etc/uwsgi/vassals
sudo ln -s /var/www/os373/mdupload/mdupload_uwsgi.ini /etc/uwsgi/vassals
```

### 设置进程用户权限
同时，最后一行说明用来运行守护进程的用户是os373。为简单起见，将这个用户设置成应用和日志文件夹的所有者。
#### 设置目录用户组

```bash
sudo chown -R os373:os373 /var/www/os373/
sudo chown -R os373:os373 /var/log/uwsgi/
```

#### 设置nginx用户组
修改nginx配置`/etc/nginx/nginx.conf`的启动用户

```bash
第1行 user os373
```

#### 设置php用户组
修改php配置`/etc/php5/fpm/pool.d/www.conf`的启动用户

```bash
第22行 user os373
第23行 group os373
.........
第44行 listen.owner = os373
第45行 listen.group = os373
```

修改'/var/run/php5-fpm.sock'的用户组

```bash
$ sudo chown os373:os373 /var/run/php5-fpm.sock
```

现在，flask应用就应该配置完成了。你可以查看`/var/log/uwsgi/`文件夹下的access.log和error.log内容，并根据提示来判断程序是否正常运行。

### 配置flask应用数据库

```bash
(flask)$ python manage.py db init
(flask)$ python manage.py db migrate -m "initial migration"
(flask)$ python manage.py db upgrade
```
配置好数据库之后，需要添加第一个用户。
```bash
(flask)$ python manage.py shell
>>>u = User(email=u'****************@gmail.com', username=u'###')
>>>db.session.add(u)
>>>u.password=u'***'
>>>db.session.commit()
```

最后的展示结果如下图：

登录界面：

![mdupload](http://www.os373.cn/blog/img/mdupload/01.png)

上传文件界面：

![mdupload](http://www.os373.cn/blog/img/mdupload/02.png)


### 程序下载

[<code class="pull-right">mdupload.tar.gz</code>](http://www.os373.cn/blog/mdupload.tar.gz)




