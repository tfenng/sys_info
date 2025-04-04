import psutil
from datetime import datetime
import uptime
import users

kb=1024
mb=kb * kb
gb=mb * kb

def format_datetime(dt):
    return datetime.fromtimestamp(dt).strftime("%Y-%m-%d %H:%M:%S")

def print_split_line():
    print("-" * 80)

if __name__ == '__main__':
    #### CPU ####
    print('Cpu Count: %s Cores , %s Threads ' %(psutil.cpu_count(logical=False),psutil.cpu_count()))
    print(psutil.cpu_freq(percpu=False))
    print(psutil.cpu_times())

    #### Memory ####
    print_split_line()
    mem=psutil.virtual_memory()
    print(f'Mem: {mem.used/gb:.2f} / {mem.total/gb:.2f}')

    #### Disk ####
    print_split_line()
    for dp in psutil.disk_partitions():
        if not dp.device.startswith('/dev/loop'):
            print(dp)
    print()
    print(psutil.disk_usage('/'))
    #### NetIO ####
    print_split_line()
    net = psutil.net_io_counters()
    bytes_sent = '{0:.2f} M'.format(net.bytes_sent / mb)
    bytes_rcvd = '{0:.2f} M'.format(net.bytes_recv / mb)
    print("Net IO: Recv %s Send %s"%(bytes_rcvd, bytes_sent))

    #### Users Online ####
    print_split_line()
    users.online()

    #### uptime ####
    print_split_line()
    uptime.show()