#!/bin/sh

# 手动修改ServerRun.py所在目录

RUN=/home/zhwei/Desktop/server_client/ServerRun.py

nohup python $RUN > server_client.log &

echo $! > /var/run/server_client.pid

echo '服务正常启动'
