import psutil,datetime

from uptime import uptime

kb=1024
mb=kb * kb
gb=mb * kb

def format_datetime(dt):
    return datetime.datetime.fromtimestamp(dt).strftime("%Y-%m-%d %H:%M:%S")

def print_split_line():
    print("-" * 80)

if __name__ == '__main__':
    #### CPU ####
    print('Cpu Count: %s Cores , %s Threads ' %(psutil.cpu_count(logical=False),psutil.cpu_count()))
    print(psutil.cpu_times())

    #### Memory ####
    print_split_line()
    mem=psutil.virtual_memory()
    print(f'Mem: {mem.used/gb:.2f} / {mem.total/gb:.2f}')


    #### NetIO ####
    print_split_line()
    net = psutil.net_io_counters()
    bytes_sent = '{0:.2f} M'.format(net.bytes_sent / mb)
    bytes_rcvd = '{0:.2f} M'.format(net.bytes_recv / mb)
    print("Net IO: Recv %s Send %s"%(bytes_rcvd, bytes_sent))

    #### Users Online ####
    print_split_line()
    users_count = len(psutil.users())
    users_list = ",".join([u.name for u in psutil.users()])
    print("%s users online : %s"%(users_count, users_list))

    #### uptime ####
    print_split_line()
    uptime()