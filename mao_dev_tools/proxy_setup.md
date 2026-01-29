# Ubuntu 代理设置指南

## 📋 目录
1. [常用代理软件](#常用代理软件)
2. [系统代理设置](#系统代理设置)
3. [终端代理设置](#终端代理设置)
4. [应用程序代理](#应用程序代理)
5. [常见问题](#常见问题)

---

## 🔧 常用代理软件

### 1. Clash for Linux (推荐)
```bash
# 下载 Clash
wget https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-linux-amd64-v1.18.0.gz
gunzip clash-linux-amd64-v1.18.0.gz
chmod +x clash-linux-amd64-v1.18.0
sudo mv clash-linux-amd64-v1.18.0 /usr/local/bin/clash

# 创建配置目录
mkdir -p ~/.config/clash

# 下载配置文件（从你的代理服务商获取）
# 将配置文件保存为 ~/.config/clash/config.yaml

# 启动 Clash
clash -d ~/.config/clash

# 后台运行
nohup clash -d ~/.config/clash > /dev/null 2>&1 &
```

### 2. V2Ray
```bash
# 安装 V2Ray
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)

# 配置文件位置
sudo nano /usr/local/etc/v2ray/config.json

# 启动服务
sudo systemctl start v2ray
sudo systemctl enable v2ray

# 查看状态
sudo systemctl status v2ray
```

### 3. Qv2ray (图形界面)
```bash
# 下载 AppImage
wget https://github.com/Qv2ray/Qv2ray/releases/download/v2.7.0/Qv2ray-v2.7.0-linux-x64.AppImage
chmod +x Qv2ray-v2.7.0-linux-x64.AppImage

# 运行
./Qv2ray-v2.7.0-linux-x64.AppImage
```

### 4. Shadowsocks
```bash
# 安装
sudo apt install shadowsocks-libev

# 配置文件
sudo nano /etc/shadowsocks-libev/config.json

# 配置示例
{
    "server": "服务器地址",
    "server_port": 8388,
    "local_port": 1080,
    "password": "密码",
    "timeout": 60,
    "method": "aes-256-gcm"
}

# 启动
sudo systemctl start shadowsocks-libev
sudo systemctl enable shadowsocks-libev
```

### 5. Clash Verge (类似小火箭的图形界面，推荐！)
```bash
# 下载最新版本
wget https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v1.5.11/clash-verge_1.5.11_amd64.deb

# 安装
sudo dpkg -i clash-verge_1.5.11_amd64.deb
sudo apt install -f  # 修复依赖

# 启动
clash-verge

# 特点：
# ✅ 图形界面，操作简单（类似小火箭）
# ✅ 支持订阅链接一键导入
# ✅ 支持规则切换、节点测速
# ✅ 系统托盘图标，方便开关
# ✅ 内置规则编辑器
```

### 6. NekoRay / NekoBox (另一个图形界面选择)
```bash
# 下载
wget https://github.com/MatsuriDayo/nekoray/releases/download/3.26/nekoray-3.26-2023-12-09-linux64.zip

# 解压
unzip nekoray-3.26-2023-12-09-linux64.zip
cd nekoray

# 运行
./nekoray

# 特点：
# ✅ 支持多种协议（SS、SSR、V2Ray、Trojan等）
# ✅ 图形界面友好
# ✅ 支持订阅和分组
# ✅ 跨平台（Windows/Linux/macOS）
```

---

## ⚙️ 系统代理设置

### 方法1: 图形界面设置
```bash
# 打开系统设置
gnome-control-center

# 导航到：设置 -> 网络 -> 网络代理
# 选择"手动"，填入：
# HTTP代理: 127.0.0.1:7890
# HTTPS代理: 127.0.0.1:7890
# Socks代理: 127.0.0.1:7891
```

### 方法2: 命令行设置（临时）
```bash
# 设置HTTP/HTTPS代理
export http_proxy="http://127.0.0.1:7890"
export https_proxy="http://127.0.0.1:7890"
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"

# 设置SOCKS代理
export all_proxy="socks5://127.0.0.1:7891"
export ALL_PROXY="socks5://127.0.0.1:7891"

# 设置不走代理的地址
export no_proxy="localhost,127.0.0.1,192.168.*,10.*"
export NO_PROXY="localhost,127.0.0.1,192.168.*,10.*"

# 取消代理
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
```

### 方法3: 永久设置
```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
nano ~/.bashrc

# 添加以下内容
export http_proxy="http://127.0.0.1:7890"
export https_proxy="http://127.0.0.1:7890"
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
export all_proxy="socks5://127.0.0.1:7891"
export ALL_PROXY="socks5://127.0.0.1:7891"
export no_proxy="localhost,127.0.0.1,192.168.*,10.*"

# 重新加载配置
source ~/.bashrc
```

---

## 💻 终端代理设置

### 快速开关代理（推荐）
```bash
# 编辑 ~/.bashrc
nano ~/.bashrc

# 添加代理函数
# 开启代理
proxy_on() {
    export http_proxy="http://127.0.0.1:7890"
    export https_proxy="http://127.0.0.1:7890"
    export HTTP_PROXY="http://127.0.0.1:7890"
    export HTTPS_PROXY="http://127.0.0.1:7890"
    export all_proxy="socks5://127.0.0.1:7891"
    export ALL_PROXY="socks5://127.0.0.1:7891"
    echo "✅ 代理已开启"
}

# 关闭代理
proxy_off() {
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
    echo "❌ 代理已关闭"
}

# 查看代理状态
proxy_status() {
    if [ -n "$http_proxy" ]; then
        echo "✅ 代理已开启"
        echo "HTTP Proxy: $http_proxy"
        echo "HTTPS Proxy: $https_proxy"
        echo "ALL Proxy: $all_proxy"
    else
        echo "❌ 代理未开启"
    fi
}

# 重新加载
source ~/.bashrc

# 使用
proxy_on      # 开启代理
proxy_off     # 关闭代理
proxy_status  # 查看状态
```

### 测试代理是否生效
```bash
# 测试HTTP代理
curl -I https://www.google.com

# 查看当前IP
curl https://ipinfo.io
curl https://api.ip.sb/ip

# 测试速度
curl -o /dev/null -s -w "time_total: %{time_total}s\n" https://www.google.com
```

---

## 📦 应用程序代理

### Git 代理
```bash
# 设置Git代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 只对GitHub设置代理
git config --global http.https://github.com.proxy http://127.0.0.1:7890

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy

# 查看配置
git config --global --list | grep proxy
```

### APT 代理
```bash
# 临时使用
sudo apt -o Acquire::http::proxy="http://127.0.0.1:7890" update

# 永久设置
sudo nano /etc/apt/apt.conf.d/proxy.conf

# 添加内容
Acquire::http::Proxy "http://127.0.0.1:7890";
Acquire::https::Proxy "http://127.0.0.1:7890";

# 删除代理
sudo rm /etc/apt/apt.conf.d/proxy.conf
```

### Snap 代理
```bash
# 设置代理
sudo snap set system proxy.http="http://127.0.0.1:7890"
sudo snap set system proxy.https="http://127.0.0.1:7890"

# 查看配置
sudo snap get system proxy

# 取消代理
sudo snap unset system proxy.http
sudo snap unset system proxy.https
```

### Docker 代理
```bash
# 创建配置目录
sudo mkdir -p /etc/systemd/system/docker.service.d

# 创建代理配置文件
sudo nano /etc/systemd/system/docker.service.d/http-proxy.conf

# 添加内容
[Service]
Environment="HTTP_PROXY=http://127.0.0.1:7890"
Environment="HTTPS_PROXY=http://127.0.0.1:7890"
Environment="NO_PROXY=localhost,127.0.0.1"

# 重启Docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证
sudo systemctl show --property=Environment docker
```

### Python pip 代理
```bash
# 临时使用
pip install package_name --proxy http://127.0.0.1:7890

# 永久设置
mkdir -p ~/.pip
nano ~/.pip/pip.conf

# 添加内容
[global]
proxy = http://127.0.0.1:7890

# 或使用环境变量
export PIP_PROXY=http://127.0.0.1:7890
```

### npm 代理
```bash
# 设置代理
npm config set proxy http://127.0.0.1:7890
npm config set https-proxy http://127.0.0.1:7890

# 取消代理
npm config delete proxy
npm config delete https-proxy

# 查看配置
npm config list
```

### wget 代理
```bash
# 编辑配置文件
nano ~/.wgetrc

# 添加内容
http_proxy = http://127.0.0.1:7890
https_proxy = http://127.0.0.1:7890
use_proxy = on

# 或临时使用
wget -e use_proxy=yes -e http_proxy=127.0.0.1:7890 URL
```

---

## 🔍 常见问题

### 1. 如何查看代理是否运行？
```bash
# 查看端口占用
netstat -tlnp | grep 7890
ss -tlnp | grep 7890

# 查看进程
ps aux | grep clash
ps aux | grep v2ray
```

### 2. 代理不生效？
```bash
# 检查代理软件是否运行
systemctl status clash
systemctl status v2ray

# 检查端口是否监听
curl -I http://127.0.0.1:7890

# 检查环境变量
echo $http_proxy
echo $https_proxy

# 测试连接
curl -x http://127.0.0.1:7890 https://www.google.com
```

### 3. 开机自启动
```bash
# Clash 开机自启
sudo nano /etc/systemd/system/clash.service

# 添加内容
[Unit]
Description=Clash daemon
After=network.target

[Service]
Type=simple
User=你的用户名
ExecStart=/usr/local/bin/clash -d /home/你的用户名/.config/clash
Restart=on-failure

[Install]
WantedBy=multi-user.target

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable clash
sudo systemctl start clash
```

### 4. 局域网共享代理
```bash
# 修改 Clash 配置
nano ~/.config/clash/config.yaml

# 修改绑定地址
mixed-port: 7890
allow-lan: true
bind-address: 0.0.0.0

# 重启 Clash
pkill clash
clash -d ~/.config/clash

# 其他设备使用
# 代理地址: 你的电脑IP:7890
```

### 5. 透明代理（高级）
```bash
# 使用 iptables 实现透明代理
# 需要配合 Clash TUN 模式或 V2Ray 透明代理

# 启用 IP 转发
sudo sysctl -w net.ipv4.ip_forward=1

# 配置 iptables 规则（示例）
sudo iptables -t nat -A OUTPUT -p tcp -j REDIRECT --to-ports 12345
```

---

## 📝 推荐配置

### 🔥 最推荐：Clash Verge（最接近小火箭体验）
1. 下载安装 Clash Verge
   ```bash
   wget https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v1.5.11/clash-verge_1.5.11_amd64.deb
   sudo dpkg -i clash-verge_1.5.11_amd64.deb
   ```
2. 启动软件，导入订阅链接
3. 选择节点，开启系统代理
4. 完成！（和小火箭一样简单）

### 最简单方案：Clash 命令行
1. 下载 Clash
2. 导入订阅配置
3. 开启系统代理
4. 完成！

### 命令行方案：Clash + 终端代理函数
1. 安装 Clash
2. 配置 config.yaml
3. 添加 proxy_on/proxy_off 函数到 ~/.bashrc
4. 使用 `proxy_on` 开启，`proxy_off` 关闭

### 全局方案：V2Ray + 透明代理
1. 安装 V2Ray
2. 配置透明代理
3. 所有流量自动走代理
4. 无需手动设置

---

## 🔗 相关链接

- **Clash Verge** (推荐): https://github.com/clash-verge-rev/clash-verge-rev
- Clash: https://github.com/Dreamacro/clash
- V2Ray: https://www.v2ray.com
- Qv2ray: https://github.com/Qv2ray/Qv2ray
- NekoRay: https://github.com/MatsuriDayo/nekoray
- Shadowsocks: https://shadowsocks.org

## 📱 小火箭替代品对比

| 软件 | 图形界面 | 易用性 | 功能 | 推荐度 |
|------|---------|--------|------|--------|
| **Clash Verge** | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🔥🔥🔥 最推荐 |
| NekoRay | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🔥🔥 推荐 |
| Qv2ray | ✅ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 🔥 可选 |
| Clash 命令行 | ❌ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 适合开发者 |
| V2Ray | ❌ | ⭐⭐ | ⭐⭐⭐⭐⭐ | 高级用户 |

**结论**：如果你习惯用小火箭，在Linux上用 **Clash Verge** 最合适！

---

## ⚠️ 注意事项

1. **端口号**：默认 Clash 使用 7890(HTTP) 和 7891(SOCKS)，根据实际情况修改
2. **防火墙**：确保防火墙允许代理端口
3. **安全性**：不要在公共网络上开启局域网共享
4. **合法性**：仅用于访问正常网站，遵守当地法律法规
5. **订阅链接**：妥善保管，不要泄露

