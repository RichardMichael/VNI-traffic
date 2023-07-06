#!/isan/bin/python

from cli import *
import sys, time
import json
import re
from tabulate import tabulate 

interface = input("Enter the interface number(Eg:Ethernet1/1):"  )
index = json.loads(clid('sh system internal access-list interface ' + interface + ' input entries detail'))
iter_in = index['TABLE_module']['ROW_module']['TABLE_instance']['ROW_instance']


index = []
rule =[]
stats = []
final = []

for i in iter_in:
    final.append(i['TABLE_tcam_resource_usage']['ROW_tcam_resource_usage']['TABLE_bank']['ROW_bank']['TABLE_class']['ROW_class']['TABLE_tcam_entry']['ROW_tcam_entry']) 

for j in final:
    for k in j:
        index.append(k['tcam-index'])
        rule.append(k['tcam-rule'])
        stats.append(k['tcam-stats'])

# Extracting Index from the system internal access-list 
pattern = r':0x[0-9a-fA-F]{4}:0x([0-9a-fA-F]{4})'
third_hex_values = [re.search(pattern, element).group(1) for element in index]
third_hex_values = ['0x' + value for value in third_hex_values]

#Extracting the VNI values from the access-list rules
vni = []
for line in rule:
    hex_values = re.findall(r'val\s(0x\w+)', line)
    if hex_values:
        merged_value = ''.join(hex_values).replace('0x', '')
        decimal_value = int(merged_value, 16)
        vni.append(decimal_value)

#Extracting the Bytes from the TCAM index
pkts = []
for i in third_hex_values:
    byte_count = cli('show system internal access-list tcam ingress start-idx ' + i + ' count 1 | i pkts|bytes').strip()
    pkts.append(byte_count)


#Merge the VNI/Pkts
final_output = dict(zip(vni, pkts))

#Final Tabulation
table_data = [] 
for vni, value in final_output.items():
    packets, bytes = value.split(', ')
    packets = packets.split(': ')[1]
    bytes = bytes.split(': ')[1]
    table_data.append([vni, packets, bytes])

table_headers = ["VNI", "Packets", "Bytes"]
table = tabulate(table_data, headers=table_headers, tablefmt="fancy_grid")
print(table)

