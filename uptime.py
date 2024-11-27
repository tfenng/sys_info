#!/usr/bin/python3

import psutil,datetime
bt=psutil.boot_time()
print(datetime.datetime.fromtimestamp(bt).strftime("%Y-%m-%d %H:%M:%S"))
