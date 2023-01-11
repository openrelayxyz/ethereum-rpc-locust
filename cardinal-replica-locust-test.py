from locust import HttpUser, TaskSet, task
import requests
import json
import random
import sys

headers = {
    'Content-Type': 'application/json',
}
data={"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest", False],"id":1}
response = requests.post("https://eth.rpc.rivet.cloud/baea23955a9a48a68bc75879b67e05e0", headers=headers, json=data)
block_number = response.json().get('result')['number']

account_addresses = open("erc20_account_addresses").readlines()
token_addresses = open("erc20_token_addresses").readlines()

def run_request(l, data, name):
    data["id"] = random.randint(0, sys.maxsize)
    with l.client.post("", name=name, json=data, catch_response=True) as result:
        try:
            response = json.loads(result.content)
        except json.decoder.JSONDecodeError:
            print(data)
            print(result.content)
            result.failure("Invalid JSON")
        else:
            if response.get("error", False):
                print(data)
                print(response.get("error"))
                result.failure("Payload error: %s" % response.get("error"))
            else:
                result.success()
        return result

def rand_block(block_number):
    blocks = [hex(random.randint(block_number - 120, block_number)), "latest"]
    return blocks[random.randint(0, 1)]

weight_coefficient = 100

class WebsiteUser(HttpUser):
    def __init__(self, *args, **kwargs):
        self.block_num = block_number
        super(WebsiteUser, self).__init__(*args, **kwargs)

    @task(weight_coefficient * 3) # increased weight coefficient here will mean greater variation in block numbers as well as ensure that we stay current with the network 
    def block_number(self):
        method = "eth_blockNumber"
        data = {"jsonrpc":"2.0","method":f"{method}","params":[],"id":1}
        response = run_request(self, data, name=f"{method}")
        self.block_num = int(response["response"]["number"], 16)

    @task(weight_coefficient) 
    def call_1(self):
        method = "eth_call"
        token_address=random.choice(token_addresses)
        print(method + "1")
        data = {"jsonrpc":"2.0","method":"eth_call","params":[{"to": token_address.strip(), "data": "0x18160ddd"}, rand_block(self.block_num)],"id":1}
        response = run_request(self, data, name=f"{method}_1")
        
    @task(weight_coefficient) 
    def call_2(self):
        method = "eth_call"
        token_address=random.choice(token_addresses)
        account_address1=random.choice(account_addresses)
        account_address2=random.choice(account_addresses)
        print(method + "2")
        data = {"jsonrpc":"2.0","method":f"{method}","params":[{"to": token_address.strip(), "data": f"0xdd62ed3e000000000000000000000000{account_address1.strip()[2:]}000000000000000000000000{account_address2.strip()[2:]}"}, rand_block(self.block_num)],"id":1}
        response = run_request(self, data, name=f"{method}_2")

    @task(weight_coefficient) 
    def estimateGas_1(self):
        method = "eth_estimateGas"
        token_address=random.choice(token_addresses)
        account_address1=random.choice(account_addresses)
        print(method + "1")
        data = {"jsonrpc":"2.0","method":f"{method}","params":[{"to": token_address.strip(), "data": f"0x70a08231000000000000000000000000{account_address1.strip()[2:]}"}],"id":1}
        response = run_request(self, data, name=f"{method}_1")

    @task(weight_coefficient) 
    def estimateGas_2(self):
        method = "eth_estimateGas"
        token_address=random.choice(token_addresses)
        print(method + "2")
        data = {"jsonrpc":"2.0","method":f"{method}","params":[{"to": token_address.strip(), "data": "0x18160ddd"}],"id":1}
        response = run_request(self, data, name=f"{method}_2")

    @task(weight_coefficient) 
    def estimateGas_3(self):
        method = "eth_estimateGas"
        token_address=random.choice(token_addresses)
        account_address1=random.choice(account_addresses)
        account_address2=random.choice(account_addresses)
        print(method + "3")
        data = {"jsonrpc":"2.0","method":f"{method}","params":[{"to": token_address.strip(), "data": f"0xdd62ed3e000000000000000000000000{account_address1.strip()[2:]}000000000000000000000000{account_address2.strip()[2:], rand_block(self.block_num)}"}],"id":1}
        response = run_request(self, data, name=f"{method}_3")

    @task(weight_coefficient) 
    def estimateGasList(self):
        method = "ethercattle_estimateGasList"
        token_address=random.choice(token_addresses)
        account_address1=random.choice(account_addresses)
        account_address2=random.choice(account_addresses)
        print(method)
        data = {"jsonrpc":"2.0","method":"ethercattle_estimateGasList","params":[[{"to": token_address.strip(), "data": f"0xdd62ed3e000000000000000000000000{account_address1.strip()[2:]}000000000000000000000000{account_address2.strip()[2:]}"}, {"to": token_address.strip(), "data": f"0x70a08231000000000000000000000000{account_address1.strip()[2:]}"}]],"id":1}
        response = run_request(self, data, name=f"{method}")

    @task(weight_coefficient * 2) 
    def getBalance(self):
        method = "eth_getBalance"
        account_address1=random.choice(account_addresses)
        print(method)
        data = {"jsonrpc":"2.0","method":"eth_getBalance","params":['0x'+account_address1.strip()[-40:], rand_block(self.block_num)],"id":1}
        response = run_request(self, data, name=f"{method}")




    # run_request(l, data, name="eth_call1")
    # data = {"jsonrpc":"2.0","method":"eth_call","params":[{"to": token_address.strip(), "data": "0x18160ddd"}, "latest"],"id":1}
    # run_request(l, data, name="eth_call2")
    # data = {"jsonrpc":"2.0","method":"eth_call","params":[{"to": token_address.strip(), "data": f"0xdd62ed3e000000000000000000000000{account_address1.strip()[2:]}000000000000000000000000{account_address2.strip()[2:]}"}, "latest"],"id":1}
    # run_request(l, data, name="eth_call3")
    # data = {"jsonrpc":"2.0","method":"eth_estimateGas","params":[{"to": token_address.strip(), "data": f"0x70a08231000000000000000000000000{account_address1.strip()[2:]}"}],"id":1}
    # run_request(l, data, name="eth_estimateGas1")
    # data = {"jsonrpc":"2.0","method":"eth_estimateGas","params":[{"to": token_address.strip(), "data": "0x18160ddd"}],"id":1}
    # run_request(l, data, name="eth_estimateGas2")
    # data = {"jsonrpc":"2.0","method":"eth_estimateGas","params":[{"to": token_address.strip(), "data": f"0xdd62ed3e000000000000000000000000{account_address1.strip()[2:]}000000000000000000000000{account_address2.strip()[2:]}"}],"id":1}
    # run_request(l, data, name="eth_estimateGas3")
    # data = {"jsonrpc":"2.0","method":"ethercattle_estimateGasList","params":[[{"to": token_address.strip(), "data": f"0xdd62ed3e000000000000000000000000{account_address1.strip()[2:]}000000000000000000000000{account_address2.strip()[2:]}"}, {"to": token_address.strip(), "data": f"0x70a08231000000000000000000000000{account_address1.strip()[2:]}"}]],"id":1}
    # run_request(l, data, name="ethercattle_estimateGasList")
    # data = {"jsonrpc":"2.0","method":"eth_getBalance","params":['0x'+account_address1.strip()[-40:], "latest"],"id":1}
    


