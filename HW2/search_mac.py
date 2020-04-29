from datetime import datetime
from pathlib import Path
from nornir import InitNornir
from nornir.plugins.tasks.networking import napalm_get
from nornir_scrapli.tasks import send_command
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir_scrapli.tasks import send_command as scrapli_send_command

def get_interfaces_trunk(task):

    int_trunk=list()
    output = task.run(napalm_get, getters=["interfaces"])
    for interface in output.result['interfaces']:
        output = task.run(scrapli_send_command, command=f'sh run int {interface}')
        # Вытащим все интерфейсы сконфигурированные как trunk
        if 'trunk' in output.result:
            int_trunk.append(interface)

    return int_trunk

def get_mac_address_table(task):

    output = task.run(napalm_get, getters=["get_mac_address_table"])

    return output.result['get_mac_address_table']


def get_interfaces_svi(task):

    interfaces_svi=list()
    output = task.run(napalm_get, getters=["get_arp_table"])
    for item in output.result['get_arp_table']:
        # Вытащим все локальные интерфейсы у которых age = 0.0
        if item['age'] == 0.0:
            interfaces_svi.append(item)

    return interfaces_svi

def search_mac(task):

    found = False

    interfaces_svi = get_interfaces_svi(task)
    if interfaces_svi:
        # Ищем в SVI интерфейсах наш мак, если он есть дальше не ищем.
        for item in interfaces_svi:
            if item['mac'] == MAC:
                found = True
                print (f'MAC={MAC},{task.host.name}, {item["interface"]}')
                break
    if found == False:
        interfaces_trunk = get_interfaces_trunk(task)
        mac_address_table = get_mac_address_table(task)
        if mac_address_table:
            n_interface = ''
            for n_mac in mac_address_table:
            # Ищем наш мак в таблице, запоминаем его интерфейс
                if n_mac['mac'] == MAC:
                    n_interface = n_mac['interface']
                    break
            if n_interface:
            # Если наш найденный интерфейс не входит в группу trunk интерфейсов, значит это искомый интерфейс.
                if n_interface not in interfaces_trunk:
                    print (f'MAC={MAC},{task.host.name}, {n_interface}')

# Вставить мак тут
MAC = '00:1C:58:29:4A:C1'

def main():
    with InitNornir(config_file="nr-config-local.yaml") as nr:
        nr.run(search_mac)

if __name__ == '__main__':
    main()
