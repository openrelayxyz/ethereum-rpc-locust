from locust import HttpLocust, TaskSet, task
import requests
import json
import random
import argparse
import sys
import os

headers = {
    'Content-Type': 'application/json',
}
data={"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}
if os.environ.get("BASE_RPC_SERVER"):
    response = requests.post(os.environ.get("BASE_RPC_SERVER"), headers=headers, json=data)
else:
    response = l.client.post("", json=data)

print(response.content)
latestBlock=int(response.json().get('result'),16)
account_addresses = open("erc20_account_addresses").readlines()
token_addresses = open("erc20_token_addresses").readlines()
if os.environ.get("BASE_RPC_SERVER"):
    def run_request(l, data, name):
        baseserv=os.environ.get("BASE_RPC_SERVER")
        # data["id"] = random.randint(0, sys.maxsize)
        result =  l.client.post("", name=name, json=data, catch_response=True)
        base_res=requests.post(os.environ.get("BASE_RPC_SERVER"), json=data)
        try:
            response = json.loads(result.content)
            base_response = json.loads(base_res.content)

        except json.decoder.JSONDecodeError:
            print(data)
            result.failure("Invalid JSON")
        if response != base_response:
            if name != "eth_blockNumber":
                result.failure("Nonmatched Response:\nGot: %s \nexpected: %s" % (response,base_response))
            else:
                result.failure("DifferenceResponse: %d" % (int(response['result'], 16) - int(base_response['result'], 16)))
        else: result.success()

        if name != "eth_blockNumber":
            old_result = requests.post(os.environ.get("BASE_RPC_SERVER"), json=data)
            for x in range(1,5):
                try:
                    old_response = json.loads(old_result.content)
                except:
                    print("breaking try 1")
                    old_result = requests.post(os.environ.get("BASE_RPC_SERVER"), json=data)
                    break
                try:
                    result=l.client.post("", name="%s_consistency" % name, json=data, catch_response=True)
                    response =  json.loads(result.content)
                except:
                    print("breaking try2")
                    result.failure("Invalid JSON")
                    break
                if response != old_response:
                    result.failure("DifferenceResponse: %d" % (int(response['result'], 16) - int(base_response['result'], 16)))
                else: result.success()

        return result
else:
    def run_request(l, data, name):
        data["id"] = random.randint(0, sys.maxsize)
        result =  l.client.post("", name=name, json=data, catch_response=True)
        try:
            response = json.loads(result.content)
        except json.decoder.JSONDecodeError:
            print(data)
            result.failure("Invalid JSON")
        else:
            if response.get("error", False):
                # print(data)
                result.failure("Payload error: %s" % response.get("error"))
            elif response.get("id") != data["id"]:
                # print(data)
                # print(response)
                # print(response.get("id"),data["id"])
                # print(type(response.get("id")),type(data["id"]))
                result.failure("Mismatched IDs")
            else: result.success()
        return result
def rand_block():
    return random.randint(1024,latestBlock)
@task(200)
def get_block(l):
    run_request(l,  {"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}, name="eth_blockNumber")
@task(1)
def heavy_request(l):
        account_address1=random.choice(account_addresses)
        account_address2=random.choice(account_addresses)
        token_address=random.choice(token_addresses)
        block_num=rand_block()
        block_hex=hex(block_num)
        data = {"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[block_hex, True],"id":1}
        response = run_request(l, data, name="eth_getBlockByNumber")
        block_hash=response.json().get('result')['hash']
        data = {"jsonrpc":"2.0","method":"eth_getTransactionByBlockHashAndIndex","params":[block_hash, "0x0"],"id":1}
        response = run_request(l, data, name="eth_getTransactionByBlockHashAndIndex")
        data = {"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[block_hex, True],"id":1}
        run_request(l, data, name="eth_getBlockByNumber")
        data = {"jsonrpc":"2.0","method":"eth_getBlockByHash","params":[block_hash, False],"id":1}
        run_request(l, data, name="eth_getBlockByHash")
        data = {"jsonrpc":"2.0","method":"eth_getBlockTransactionCountByHash","params":[block_hash],"id":1}
        run_request(l, data, name="eth_getBlockTransactionCountByHash")
        data = {"jsonrpc":"2.0","method":"eth_getTransactionByBlockHashAndIndex","params":[block_hash, "0x0"],"id":1}
        run_request(l, data, name="eth_getTransactionByBlockHashAndIndex")
        data = {"jsonrpc":"2.0","method":"eth_call","params":[{"to": token_address.strip(), "data": f"0x70a08231000000000000000000000000{account_address1.strip()[2:]}"}, "latest"],"id":1}
        run_request(l, data, name="eth_call1")
        data = {"jsonrpc":"2.0","method":"eth_call","params":[{"to": token_address.strip(), "data": "0x18160ddd"}, "latest"],"id":1}
        run_request(l, data, name="eth_call2")
        data = {"jsonrpc":"2.0","method":"eth_call","params":[{"to": token_address.strip(), "data": f"0xdd62ed3e000000000000000000000000{account_address1.strip()[2:]}000000000000000000000000{account_address2.strip()[2:]}"}, "latest"],"id":1}
        run_request(l, data, name="eth_call3")
        data = {"jsonrpc":"2.0","method":"eth_estimateGas","params":[{"to": token_address.strip(), "data": f"0x70a08231000000000000000000000000{account_address1.strip()[2:]}"}],"id":1}
        run_request(l, data, name="eth_estimateGas1")
        data = {"jsonrpc":"2.0","method":"eth_estimateGas","params":[{"to": token_address.strip(), "data": "0x18160ddd"}],"id":1}
        run_request(l, data, name="eth_estimateGas2")
        data = {"jsonrpc":"2.0","method":"eth_estimateGas","params":[{"to": token_address.strip(), "data": f"0xdd62ed3e000000000000000000000000{account_address1.strip()[2:]}000000000000000000000000{account_address2.strip()[2:]}"}],"id":1}
        run_request(l, data, name="eth_estimateGas3")
        data = {"jsonrpc":"2.0","method":"eth_getBalance","params":[account_address1.strip(), "latest"],"id":1}
        run_request(l, data, name="eth_getBalance")
        data = {"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}
        run_request(l, data, name="eth_gasPrice")
        data = {"jsonrpc":"2.0","method":"eth_getBlockTransactionCountByNumber","params":[block_hex],"id":1}
        run_request(l, data, name="eth_getBlockTransactionCountByNumber")
class RunTest(TaskSet):
    tasks = {get_block: 200, heavy_request: 1}
class WebsiteUser(HttpLocust):
    task_set = RunTest
    min_wait = 50
    max_wait = 100
