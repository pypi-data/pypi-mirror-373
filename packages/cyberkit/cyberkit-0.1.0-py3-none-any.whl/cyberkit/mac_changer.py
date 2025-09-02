import subprocess
import optparse
import re


def check_mac(interface):
    result = subprocess.check_output(['ifconfig', interface])
    search_result = re.search(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', str(result))
    if search_result:
        return search_result[0]
    else:
        print('/!/ Could not read MAC address')


def get_args():
    parser = optparse.OptionParser()
    parser.add_option('--interface',
                      '-i',
                      dest='interface',
                      help='Interface to change the MAC address of')
    parser.add_option('--new_mac',
                      '--newmac',
                      '--mac',
                      '-m',
                      dest='mac',
                      help='New MAC address to assign to the interface')
    (opts, args) = parser.parse_args()
    interface = opts.interface
    mac = opts.mac
    if not interface:
        interface = input(
            '/-/ Enter interface to change the MAC address of > ')
    if not mac:
        mac = input(
            f'/-/ Enter the new MAC address to assign to {interface} > ')
    return interface, mac


def change_mac(interface, mac):
    print(f'/+/ Changing MAC address of {interface} to {mac}')
    subprocess.call(['ifconfig', interface, 'down'])
    subprocess.call(['ifconfig', interface, 'hw', 'ether', mac])
    subprocess.call(['ifconfig', interface, 'up'])


def compare_mac(interface, mac):
    new_mac = check_mac(interface)
    if new_mac == mac:
        print(f'/+/ MAC address of {interface} successfully changed to {mac}')
    else:
        print(f'/!/ Failed to change MAC address of {interface} to {mac}')
        print(f'/-/ Actual MAC address of {interface} is {new_mac}')


def main():
    (interface, mac) = get_args()

    initial_mac = check_mac(interface)
    print(f'/-/ The current MAC address of {interface} is {initial_mac}')

    change_mac(interface, mac)

    compare_mac(interface, mac)

if __name__ == '__main__':
    main()