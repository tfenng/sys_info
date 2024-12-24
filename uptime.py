import psutil,datetime

if __name__ == '__main__':
    bt=psutil.boot_time()
    print(datetime.datetime.fromtimestamp(bt).strftime("%Y-%m-%d %H:%M:%S"))
