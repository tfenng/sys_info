import psutil

kb=1024
mb=kb * kb
gb=mb * kb

if __name__ == '__main__':
    net = psutil.net_io_counters()
    bytes_sent = '{0:.2f} M'.format(net.bytes_sent / mb)
    bytes_rcvd = '{0:.2f} M'.format(net.bytes_recv / mb)
    print("Net IO: Recv %s Send %s" % (bytes_rcvd, bytes_sent))
    print()
    for nc in psutil.net_connections():
        print(nc)
    net = psutil.net_io_counters()
