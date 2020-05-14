import json

if __name__ == '__main__':
    f = open('scan_ip.txt')
    lines = f.readlines()
    ip_list = list()
    for line in lines:
        address, port = line.split(":")
        ip_info = {'address': address, 'port': port.replace("\n","")}
        ip_list.append(ip_info)
    with open('ip.txt', 'w') as file:
        json.dump(ip_list, file)
