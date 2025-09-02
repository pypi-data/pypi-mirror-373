import netfilterqueue as nfq


def process_packet(packet):
    print(packet)
    packet.drop()


queue = nfq.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()
