# 部署
## 安装osmo-trx
```javascript
#安装uhd
apt install libuhd-dev libuhd3.15.0 uhd-host terminator

#配置编译环境
apt install build-essential libtool libtalloc-dev libsctp-dev shtool autoconf automake git-core gcc make pkg-config gnutls-dev libusb-1.0-0-dev sqlite3 libpcsclite-dev libnml-dev

#编译libosmocore
git clone https://github.com/osmocom/libosomcore.git
cd libosmocore
git checkout 1.5.1
autoreconf -i
./configure
make
make install

#编译osmotrx
git clone https://github.com/osmocom/osmo-trx.git
cd osmo-trx
git checkout 1.3.1
./configure
make
make install
```
## 配置OpenBTS与osmocombb环境
```javascript
cp lib/* /usr/lib
mkdir -p /etc/OpenBTS
mkdir -p /var/lib/asterisk/sqlite3dir
sqlite3 -init OpenBTS/OpenBTS.exmaple.sql /etc/OpenBTS/OpenBTS.db ".quit"
sqlite3 -init OpenBTS/subscriberRegistry.example.sql /etc/OpenBTS/sipauthserve.db ".quit"
```
## 配置服务器脚本
blacklist.json       --      黑名单与imsi上限数量  
config.json          --      服务器端口配置  
OpenBTS的端口可以有多个，需要不同的rhost和lhost以应对多设备,mobile端口仅需一个

# 使用
## 运行服务器脚本
```javascript
#在服务器上
python3 main_server.py

#在OpenBTS所在设备上
python3 OpenBTS_relay_server [服务器IP] [配置的OpenBTS端口]

#在C118所在设备上
python3 mobile_relay_server [服务器IP] [配置的mobile端口]
```
## 运行osmotrx
```javascript
uhd_usrp_probe
cd osmo-trx/doc/examples/osmo-trx-uhd
osmo-trx-uhd -C osmo-trx-usrp_b200.cfg -f
```
## 运行OpenBTS
```javascript
cd OpenBTS
./sipauthserse
./OpenBTS
```
## 运行mobile
```javascript
```







```
