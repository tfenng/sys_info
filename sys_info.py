#!/usr/bin/python

import psutil,datetime

kb=1024
mb=kb * kb

def format_datetime(dt):
    return datetime.datetime.fromtimestamp(dt).strftime("%Y-%m-%d %H:%M:%S")

def print_split_line():
    print("-" * 32)

if __name__ == '__main__':
    users_count = len(psutil.users())
    users_list = ",".join([u.name for u in psutil.users()])
    print("%s users online : %s"%(users_count, users_list))
    print_split_line()

    mem=psutil.virtual_memory()
    print('Mem: %s / %s ' % (mem.used / mb,mem.total / mb))
    print('Cpu Count: %s , %s ' %(psutil.cpu_count(), psutil.cpu_count(logical=False)))

    print(psutil.cpu_times())

    net = psutil.net_io_counters()
    bytes_sent = '{0:.2f} M'.format(net.bytes_sent / mb)
    bytes_rcvd = '{0:.2f} M'.format(net.bytes_recv / mb)
    print("Recv %s Send %s"%(bytes_rcvd, bytes_sent))

    print_split_line()
    print("OS started at %s\n" % format_datetime(psutil.boot_time()))
