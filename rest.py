'''

CVM$ python3 rest.py

'''
import requests
import json
import csv
import sys, os
from getpass import getpass
from datetime import datetime

url= "1"
cluster_ip = ""
port = "9440"
username = "admin"
password = ""
globNodeList=[]
globCluster=[]
globClusterName=""

def connectionSetting():
    global cluster_ip, password, url
    cluster_ip=input("1. cvm ip: ")
    password=getpass("2. Prism admin password: ")
    #password = input("2. Prism admin password: ")
    url = "https://" + cluster_ip + ":" + port + "/PrismGateway/services/rest/v2.0"


def call_api(endpoint, method, data=None):

    headers = {"Content-Type": "application/json"}
    response = requests.request(method, url + endpoint, headers=headers, auth=(username, password), verify=False, data=json.dumps(data))
    return json.loads(response.text)

def rest_hosts():
    hosts = call_api("/hosts/", "GET")
    nodeList = []
    for entitiy in hosts["entities"]:
        hostname = entitiy["name"]
        ipmiIp = entitiy["ipmi_address"]
        ahvIp = entitiy["hypervisor_address"]
        cvmIp = entitiy["service_vmexternal_ip"]
        cvmBackplaneIp = entitiy["controller_vm_backplane_ip"]
        blockSerial = entitiy["block_serial"]
        hardwareModel = entitiy["block_model_name"]
        nodeSerial = entitiy["serial"]
        cpuModel = entitiy["cpu_model"]
        cpuCores = entitiy["num_cpu_cores"]
        cpuSockets = entitiy["num_cpu_sockets"]
        numVms = entitiy["num_vms"]
        memory = str(int(entitiy["memory_capacity_in_bytes"] / 1024 / 1024 / 1024))  # Bytes -> GiB
        versionBios = entitiy["bios_version"]
        versionBmc = entitiy["bmc_version"]
        versionHba = entitiy["hba_firmwares_list"][0]["hba_version"]
        versionGpu = entitiy["gpu_driver_version"]
        storageTotal = entitiy["usage_stats"]["storage.capacity_bytes"]
        storageUsage = entitiy["usage_stats"]["storage.usage_bytes"]
        listDiskModel = []
        for diskSlotNumber in entitiy["disk_hardware_configs"]:
            if not entitiy["disk_hardware_configs"][diskSlotNumber] == None:
                listDiskModel.append(entitiy["disk_hardware_configs"][diskSlotNumber]["model"])

        nodeList.append({
            "hostname": hostname,
            "Model": hardwareModel,
            "Block Serial": blockSerial,
            "Node Serial": nodeSerial,
            "IPMI": ipmiIp,
            "CVM": cvmIp,
            "AHV": ahvIp,
            "CPU": cpuModel,
            "Socket": cpuSockets,
            "Total Cores": cpuCores,
            "Memory": memory,
            "Disks": listDiskModel
        })
    return nodeList

def rest_cluster():
    global globClusterName
    cluster = call_api("/cluster/", "GET")
    clusterList=[]
    globClusterName = cluster["name"]
    dataServiceIp = cluster["cluster_external_data_services_ipaddress"]
    vIp = cluster["cluster_external_ipaddress"]
    subnet = cluster["external_subnet"]
    storageType = cluster["storage_type"]
    aos = cluster["version"]
    ncc = cluster["ncc_version"]
    clusterList.append({
        "Cluster Name": globClusterName,
        "VIP": vIp,
        "Data service IP": dataServiceIp,
        "subnet": subnet,
        "AOS": aos,
        "NCC": ncc,
        "Stroage Type": storageType
    })
    return clusterList

def rest_vms():
    vms = call_api("/vms/", "GET")
    for vm in vms["entities"]:
        vmname = vm["name"]
        vmvcpus = vm["num_vcpus"]
        vmcorespervcpu = vm["num_cores_per_vcpu"]
        vmmem = vm["memory_mb"]
        vmtimezone = vm["timezone"] / 1024  # mb -> gb
        vmagent = vm["AGENT_VM"]
        vmpower = vm["power_state"]
        vmdescription = vm["description"]
        vmList.append({
            "VM name": vmname,
            "Power": vmpower,
            "vcpu": vmvcpus,
            "core per vcpu": vmcorespervcpu,
            "mem": vmmem,
            "agent vm": vmagent,
            "timezone": vmtimezone,
            "description": vmdescription
        })

def csvwriter(outfilename):
    global globNodeList, globCluster

    f = open(outfilename, 'a', newline='')
    wr = csv.writer(f)

    wr.writerow(globNodeList[0].keys())
    print(globNodeList[0].keys())
    for data in globNodeList:
        print(*data.values())
        wr.writerow(data.values())
    wr.writerow("")
    wr.writerow("")
    wr.writerow(globCluster[0].keys())
    for data in globCluster:
        print(*data.values())
        wr.writerow(data.values())

    f.close()

def main():
    global globNodeList, globCluster, globClusterName

    connectionSetting()
    globNodeList=rest_hosts()
    globCluster=rest_cluster()

    now=datetime.now()
    thisScriptName=os.path.splitext(os.path.basename(__file__))[0]
    outfilename=globClusterName+"_"+now.strftime('%y-%m-%d_%H%M%S')+".csv"

    csvwriter(outfilename)
    print("\n\n*** out file: ",outfilename)

if __name__ == "__main__":
    main()
