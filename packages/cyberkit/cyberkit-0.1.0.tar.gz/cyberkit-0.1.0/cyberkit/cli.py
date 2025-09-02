import sys
import subprocess
import os

tools = {
    'arp_spoofer': 'arp_spoofer.py',
    'dns_spoofer': 'dns_spoofer.py',
    'mac_changer': 'mac_changer.py',
    'network_scanner': 'network_scanner.py',
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in tools:
        print("Usage: cyberkit <tool> [arguments]")
        print("Run cyberkit <tool> --help for arguments.")
        print("Available tools:", ", ".join(tools.keys()))
        sys.exit(1)

    tool_name = sys.argv[1]
    script_path = tools[tool_name]

    script_full_path = os.path.join(os.path.dirname(__file__), script_path)
    subprocess.run([sys.executable, script_full_path] + sys.argv[2:])

if __name__ == "__main__":
    main()
