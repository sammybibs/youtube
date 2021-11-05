#!/usr/bin/python3.8
__author__ = 'sabibby'

import sys

user_inputs = sys.argv


##This is the DNAC and varibles info needed

DNAC_IP_PORT ='192.0.0.1:50002'
DNAC_USER='mcmouse'
DNAC_PASSWORD='Password1!'



########First we setup the required imports (requests) and the URL for authentication along with the header.
########sys is used to allow for exit codes in the pocedure.
import sys
import requests
from requests.auth import HTTPBasicAuth
import json
import urllib3
import re
import time
urllib3.disable_warnings()
url = "https://"+DNAC_IP_PORT+"/api/system/v1/auth/token"
headers = {'content-type': 'application/json','__persistbapioutput': "true" }



#######We can now make a POST API call, using basic authentication and then print out the token.
resp = requests.post(url, auth=HTTPBasicAuth(username=DNAC_USER, password=DNAC_PASSWORD), headers=headers,verify=False)
token = resp.json()['Token']
#print (f"YOUR TOKEN IS: \n {token}")

######This token will be required in a header for future API calls. It needs to be used in a header called x-auth-token.
######I add the token to the header and I can now make authenticated API calls.
######This token is valid for sixty minutes, then you will need to repeat the step above.
headers['x-auth-token'] = token


######Now we make our call to DNAC API and etun the data to the BN_DATA dictinay (yes its a disctinarty type)
#To have a look at the exiting IP pools if we want to use the follwing function.
def get_pools(DNAC_IP_PORT, headers):
        POOLS = requests.get('https://'+DNAC_IP_PORT+'/api/v2/ippool', headers=headers, verify=False)
        IP_POOLS = POOLS.json()
        MY_DATA = IP_POOLS['response']
        for ENTRY in MY_DATA:
                if type(ENTRY) == dict:
                        print(f"Found pool {ENTRY['ipPoolName']} subnet {ENTRY['ipPoolCidr']} on DNAC")
                else:
                        print('no pools found')


def delete_all_pools(DNAC_IP_PORT, headers):
        POOLS = requests.get('https://'+DNAC_IP_PORT+'/api/v2/ippool', headers=headers, verify=False)
        IP_POOLS = POOLS.json()
        MY_DATA = IP_POOLS['response']
        for ENTRY in MY_DATA:
                if type(ENTRY) == dict:
                        key_str = ENTRY['id']
                        requests.delete('https://'+DNAC_IP_PORT+'/dna/intent/api/v1/global-pool/'+key_str, headers=headers, verify=False)
                        print(f"Deleted pool {ENTRY['ipPoolName']} subnet {ENTRY['ipPoolCidr']} from DNAC")
                        time.sleep(0.100)
                else:
                        print('no pools found')


#This function takes the adress/mask and gives back wehat you need as slash notation
def subnet_mask(input):
        s = input
        final_ips = ['{}/{}'.format(a, sum([bin(int(x)).count('1') for x in b.split('.')])) for a, b in map(lambda x:re.findall('[\d\.]+', x), s)]
        return final_ips[0]



#To push an IP Pool use the following API
#https://10.53.254.20:50002/dna/intent/api/v1/global-pool

#Def to setup the ppools where we need to glean
#name, subnet_size, address from the file that we need  open.
def IP_POOL_DICT(DNAC_IP_PORT, headers):
        DNAC_API_Dic = {
                "ipPoolCidr":"IP-SLASH-SUBNET",
                "ipPoolName":"NAME",
                "gateways":[],
                "dhcpServerIps":[],
                "dnsServerIps":[],
                "context":[
                        {"contextKey":"type",
                        "contextValue":"generic",
                        "owner":"DNAC"}]}

        file = open('DHCP_POOLS.csv','rt')

        dhcp_list = []

        for line in file:
                dhcp_list.append(line.split(','))

        qty_of_data = len(dhcp_list)

        for value in range(1,qty_of_data):
                named, addd, subd = dhcp_list[value][1:4]
                convert = [addd+'/'+subd]
                ippoolcidr = subnet_mask(convert)

                DNAC_API_Dic['ipPoolName'] = named
                DNAC_API_Dic['ipPoolCidr'] = ippoolcidr
                IP_POOL_NEW = json.dumps(DNAC_API_Dic)

                requests.post('https://'+DNAC_IP_PORT+'/api/v2/ippool', headers=headers, verify=False, data=IP_POOL_NEW)
                print(f'Pushed pool {named} subnet {ippoolcidr} to DNAC')
                time.sleep(0.100)


#Use this to push the pools to DNAC (its default)
if len(user_inputs) == 1:
        IP_POOL_DICT(DNAC_IP_PORT, headers)
#Use this to view all subnets:
elif len(user_inputs) == 2 and user_inputs[1].lower() == 'check':
        get_pools(DNAC_IP_PORT, headers)
#Use this to purge all subnets:
elif len(user_inputs) == 2 and user_inputs[1].lower() == 'delete':
        delete_all_pools(DNAC_IP_PORT, headers)
else:
        print('\nNo action defined, please call the script via: \n')
        print('To create IP Pools: python Add_pools_to_DNAC.py ')
        print('To create IP Pools: python Add_pools_to_DNAC.py ')
        print('To view IP Pools: python Add_pools_to_DNAC.py check')
        print('To delete IP Pools: python Add_pools_to_DNAC.py delete \n')
  
#


#

