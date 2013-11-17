#!/bin/sh

kill `cat /var/run/server_client.pid`

echo 服务已停止
