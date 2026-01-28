# Ubuntu 常用命令行速查

## 📁 文件和目录操作

### 查看文件/目录
```bash
ls              # 列出当前目录文件
ls -la          # 详细列表（包含隐藏文件）
ls -lh          # 人类可读的文件大小
pwd             # 显示当前目录路径
tree            # 树形显示目录结构
tree -L 2       # 只显示2层
```

### 切换目录
```bash
cd /path/to/dir     # 切换到指定目录
cd ..               # 返回上级目录
cd ~                # 返回用户主目录
cd -                # 返回上一个目录
```

### 创建
```bash
touch file.txt          # 创建空文件
mkdir folder            # 创建文件夹
mkdir -p a/b/c          # 创建多级目录
echo "text" > file.txt  # 创建并写入内容
```

### 复制
```bash
cp file1.txt file2.txt      # 复制文件
cp -r folder1 folder2       # 复制文件夹
cp file.txt /path/to/       # 复制到指定目录
```

### 移动/重命名
```bash
mv old.txt new.txt          # 重命名文件
mv file.txt /path/to/       # 移动文件
mv old_folder new_folder    # 重命名文件夹
mv -i file.txt dest/        # 询问是否覆盖
```

### 删除
```bash
rm file.txt             # 删除文件
rm -f file.txt          # 强制删除
rm -r folder            # 删除文件夹
rm -rf folder           # 强制删除文件夹（危险！）
rmdir empty_folder      # 删除空文件夹
```

## 📝 文件查看和编辑

### 查看文件内容
```bash
cat file.txt            # 显示全部内容
less file.txt           # 分页查看（空格翻页，q退出）
head file.txt           # 显示前10行
head -n 20 file.txt     # 显示前20行
tail file.txt           # 显示后10行
tail -f log.txt         # 实时查看日志
```

### 编辑文件
```bash
nano file.txt           # 简单编辑器（推荐新手）
vim file.txt            # 强大编辑器
gedit file.txt          # GUI编辑器
code file.txt           # VS Code
```

### 搜索文件内容
```bash
grep "keyword" file.txt         # 搜索关键词
grep -r "keyword" .             # 递归搜索当前目录
grep -i "keyword" file.txt      # 忽略大小写
grep -n "keyword" file.txt      # 显示行号
```

## 🔍 查找文件

```bash
find . -name "*.py"             # 查找所有.py文件
find . -type f -name "test*"    # 查找以test开头的文件
find . -type d -name "folder"   # 查找文件夹
find . -mtime -7                # 查找7天内修改的文件
locate filename                 # 快速查找（需要updatedb）
which python3                   # 查找命令位置
```

## 📦 压缩和解压

### tar
```bash
tar -czf archive.tar.gz folder/     # 压缩
tar -xzf archive.tar.gz             # 解压
tar -xzf archive.tar.gz -C /path/   # 解压到指定目录
tar -tzf archive.tar.gz             # 查看内容
```

### zip
```bash
zip -r archive.zip folder/      # 压缩
unzip archive.zip               # 解压
unzip -l archive.zip            # 查看内容
```

## 🔐 权限管理

```bash
chmod +x script.sh          # 添加执行权限
chmod 755 file              # rwxr-xr-x
chmod 644 file              # rw-r--r--
chmod -R 755 folder/        # 递归修改
chown user:group file       # 修改所有者
sudo command                # 以管理员权限执行
```

## 💻 进程管理

```bash
ps aux                      # 查看所有进程
ps aux | grep python        # 查找python进程
top                         # 实时进程监控
htop                        # 更好的进程监控
kill PID                    # 终止进程
kill -9 PID                 # 强制终止
killall python3             # 终止所有python3进程
```

## 🌐 网络相关

```bash
ping google.com             # 测试网络连接
curl https://api.com        # 发送HTTP请求
wget https://file.com       # 下载文件
ifconfig                    # 查看网络配置
ip addr                     # 查看IP地址
netstat -tuln               # 查看端口占用
```

## 📊 系统信息

```bash
df -h                       # 查看磁盘使用
du -sh folder/              # 查看文件夹大小
free -h                     # 查看内存使用
uname -a                    # 系统信息
lsb_release -a              # Ubuntu版本
uptime                      # 运行时间
date                        # 当前日期时间
```

## 🐍 Python开发

```bash
python3 --version           # 查看Python版本
python3 script.py           # 运行脚本
pip3 install package        # 安装包
pip3 list                   # 查看已安装的包
pip3 freeze > requirements.txt  # 导出依赖
python3 -m venv venv        # 创建虚拟环境
source venv/bin/activate    # 激活虚拟环境
deactivate                  # 退出虚拟环境
```

## 📦 包管理

```bash
sudo apt update             # 更新包列表
sudo apt upgrade            # 升级所有包
sudo apt install package    # 安装包
sudo apt remove package     # 卸载包
sudo apt autoremove         # 清理无用包
apt search keyword          # 搜索包
```

## 🔄 后台运行

```bash
command &                   # 后台运行
nohup command &             # 后台运行（不挂断）
nohup python3 main.py > log.txt 2>&1 &  # 后台运行并记录日志
jobs                        # 查看后台任务
fg %1                       # 将任务调到前台
bg %1                       # 继续后台任务
```

## 🔗 快捷操作

```bash
Ctrl + C                    # 终止当前命令
Ctrl + Z                    # 暂停当前命令
Ctrl + D                    # 退出终端
Ctrl + L                    # 清屏（或输入 clear）
Ctrl + R                    # 搜索历史命令
Tab                         # 自动补全
↑ ↓                         # 浏览历史命令
!!                          # 执行上一条命令
sudo !!                     # 以sudo执行上一条命令
```

## 📝 文本处理

```bash
echo "text"                 # 输出文本
echo "text" > file.txt      # 写入文件（覆盖）
echo "text" >> file.txt     # 追加到文件
cat file1.txt file2.txt     # 合并文件
wc -l file.txt              # 统计行数
sort file.txt               # 排序
uniq file.txt               # 去重
sed 's/old/new/g' file.txt  # 替换文本
```

## 🔧 实用技巧

### 管道和重定向
```bash
command1 | command2         # 管道：将输出传给下一个命令
command > file.txt          # 重定向输出到文件
command >> file.txt         # 追加输出到文件
command 2> error.log        # 重定向错误到文件
command &> all.log          # 重定向所有输出
```

### 批量操作
```bash
# 批量重命名
for file in *.txt; do
    mv "$file" "${file%.txt}.md"
done

# 批量处理
for file in *.py; do
    python3 "$file"
done

# 查找并删除
find . -name "*.pyc" -delete
```

### 别名设置
```bash
# 临时别名
alias ll='ls -la'
alias gs='git status'

# 永久别名（添加到 ~/.bashrc）
echo "alias ll='ls -la'" >> ~/.bashrc
source ~/.bashrc
```

## 🚀 项目开发常用

```bash
# 克隆项目
git clone https://github.com/user/repo.git

# 进入项目
cd repo

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip3 install -r requirements.txt

# 运行项目
python3 main.py

# 后台运行
nohup python3 main.py > logs/app.log 2>&1 &

# 查看日志
tail -f logs/app.log

# 停止进程
ps aux | grep python3
kill PID
```

## 💡 常见问题

### 权限不足
```bash
# 使用sudo
sudo command

# 修改文件权限
chmod +x file
```

### 命令未找到
```bash
# 安装命令
sudo apt install package-name

# 查找命令位置
which command
```

### 端口被占用
```bash
# 查找占用端口的进程
sudo lsof -i :8080
sudo netstat -tuln | grep 8080

# 终止进程
kill -9 PID
```

## 📚 学习资源

- `man command` - 查看命令手册
- `command --help` - 查看命令帮助
- `tldr command` - 简化的命令示例（需安装tldr）

## ⚠️ 危险命令（慎用）

```bash
rm -rf /                    # 删除所有文件（永远不要执行！）
rm -rf /*                   # 同上
chmod -R 777 /              # 修改所有文件权限（危险）
dd if=/dev/zero of=/dev/sda # 清空硬盘（危险）
```

---

**提示**：
- 使用Tab键自动补全，提高效率
- 使用↑↓键浏览历史命令
- 不确定的命令先加 `--help` 查看帮助
- 重要操作前先备份
