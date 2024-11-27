#!/usr/bin/python
import psutil

def main():
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'username','name'])
        except psutil.NoSuchProcess:
            pass
        else:
            print("%s\t%s\t%s" % (pinfo['pid'],pinfo['username'],pinfo['name']))

if __name__ == '__main__':
    main()