import scapy.all as scapy
import optparse


def get_args():
    parser = optparse.OptionParser()
    parser.add_option('--target',
                      '-t',
                      dest='target',
                      help='IP address/range to scan')
    (opts, args) = parser.parse_args()
    target = opts.target

    if not target:
        target = input('/-/ Enter IP address/range to scan > ')

    return target


def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    arp_request_broadcast = broadcast / arp_request
    ans_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    clients = []
    for entry in ans_list:
        client_dict = {'ip': entry[1].psrc, 'mac': entry[1].hwsrc}
        clients.append(client_dict)
    return clients


def print_results(results):
    print(
        'IP Address \t | MAC Address\n--------------------------------------')
    for client in results:
        print(f'{client['ip']} \t | {client['mac']}')

def main():
    target = get_args()
    scan_result = scan(target)
    print_results(scan_result)

main()