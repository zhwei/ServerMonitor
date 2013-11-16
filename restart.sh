sudo kill `cat /var/run/gunicorn-server-monitor.pid`
echo ------------------ 
echo server monitor is stop
echo ------------------ 
sudo service server_monitor start
echo server monitor is start
echo ------------------ 
