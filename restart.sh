. venv/bin/activate
kill `ps aux | grep "python python-backups.py" | grep -v grep | awk '{print $2}'`
nohup python python-backups.py > /dev/null 2>&1 &
