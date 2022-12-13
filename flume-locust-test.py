from locust import HttpUser, TaskSet, task
import requests
import json
import random
import argparse
import sys
import os
import time

headers = {
    'Content-Type': 'application/json',
}
data={"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}
response = requests.post(os.environ.get("BASE_RPC_SERVER", "https://sepolia.rpc.rivet.cloud/10f2a3dbcaa44fd998184ffbb8336f43"), headers=headers, json=data)

print(response.content)
latestBlock=int(response.json().get('result'),16)
account_addresses = ['0x'+line.strip()[-40:] for line in open("polygon_erc20_account_addresses").readlines()]
token_addresses = [line.strip() for line in open("polygon_token_addresses").readlines()]
tx_hashes = [line.strip() for line in open("polygon_tx_hashes").readlines()]
tx_hash_misses = [line.strip() for line in open("polygon_tx_hash_misses").readlines()]

if os.environ.get("BASE_RPC_SERVER"):
    def run_request(l, data, name):
        print("Running request")
        baseserv=os.environ.get("BASE_RPC_SERVER")
        # data["id"] = random.randint(0, sys.maxsize)
        with l.client.post("", name=name, json=data, catch_response=True) as result:
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
                    with l.client.post("", name="%s_consistency" % name, json=data, catch_response=True) as result:
                        try:
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
                elif response.get("id") != data["id"]:
                    print(data)
                    # print(response)
                    # print(response.get("id"),data["id"])
                    print(type(response.get("id")),type(data["id"]))
                    result.failure("Mismatched IDs")
                else:
                    # print("Success")
                    result.success()
            return result
def rand_block():
    return random.randint(1024,latestBlock)


# class RunTest(TaskSet):
#     tasks = {get_block: 200, heavy_request: 1, eth_requests: 1}
class WebsiteUser(HttpUser):
    # @task(1)
    # def heavy_request(self):
    #     print("heavy_request")
    #     token_address=random.choice(token_addresses)
    #     block_num=rand_block()
    #     block_hex=hex(block_num)
    #     data = {"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[block_hex, True],"id":1}
    #     response = run_request(self, data, name="eth_getBlockByNumber")
    #     try:
    #         block_hash=response.json().get('result')['hash']
    #     except Exception:
    #         print("Could not get hash from %s" % response.text)
    #     address = random.choice(account_addresses + token_addresses)
    #
    #     data = {"jsonrpc":"2.0", "method": "flume_erc20ByAccount", "params": [random.choice(account_addresses)]}
    #     response = run_request(self, data, name="flume_erc20ByAccount")
    #     data = {"jsonrpc":"2.0", "method": "flume_erc20Holders", "params": [random.choice(token_addresses)]}
    #     response = run_request(self, data, name="flume_erc20Holders")
    #     data = {"jsonrpc":"2.0", "method": "flume_getTransactionsBySender", "params": [random.choice(account_addresses)]}
    #     response = run_request(self, data, name="flume_getTransactionsBySender")
    #     data = {"jsonrpc":"2.0", "method": "flume_getTransactionReceiptsBySender", "params": [random.choice(account_addresses)]}
    #     response = run_request(self, data, name="flume_getTransactionReceiptsBySender")
    #     data = {"jsonrpc":"2.0", "method": "flume_getTransactionsByRecipient", "params": [random.choice(account_addresses + token_addresses)]}
    #     response = run_request(self, data, name="flume_getTransactionsByRecipient")
    #     data = {"jsonrpc":"2.0", "method": "flume_getTransactionReceiptsByRecipient", "params": [random.choice(account_addresses + token_addresses)]}
    #     response = run_request(self, data, name="flume_getTransactionReceiptsByRecipient")
    #     data = {"jsonrpc":"2.0", "method": "flume_getTransactionsByParticipant", "params": [random.choice(account_addresses + token_addresses)]}
    #     response = run_request(self, data, name="flume_getTransactionsByParticipant")
    #     data = {"jsonrpc":"2.0", "method": "flume_getTransactionReceiptsByParticipant", "params": [random.choice(account_addresses + token_addresses)]}
    #     response = run_request(self, data, name="flume_getTransactionReceiptsByParticipant")
    #     data = {"jsonrpc":"2.0", "method": "flume_getTransactionReceiptsByBlockHash", "params": [block_hash]}
    #     response = run_request(self, data, name="flume_getTransactionReceiptsByBlockHash")
    #     data = {"jsonrpc":"2.0", "method": "flume_getTransactionReceiptsByBlockNumber", "params": [block_hex]}
    #     response = run_request(self, data, name="flume_getTransactionReceiptsByBlockNumber")
    #     print("/heavy_request")

    @task(1)
    def eth_requests(self):
        print("eth_requests")
        token_address=random.choice(token_addresses)
        block_num=rand_block()
        block_hex=hex(block_num)
        data = {"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[block_hex, True],"id":1}
        response = run_request(self, data, name="eth_getBlockByNumber")
        block_hash=response.json().get('result')['hash']
        address = random.choice(account_addresses + token_addresses)

        data = {"jsonrpc":"2.0", "method": "eth_blockNumber"}
        response = run_request(self, data, name="eth_blockNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getLogs", "params": [{"fromBlock": block_hex, "toBlock": block_hex}]}
        response = run_request(self, data, name="eth_getLogs")
        data = {"jsonrpc":"2.0", "method": "eth_getLogs", "params": [{"fromBlock": block_hex, "toBlock": block_hex, "address": random.choice(token_addresses), "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]}]}

        response = run_request(self, data, name="eth_getLogs_specific")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByHash", "params": [random.choice(list(tx_hashes))]}
        response = run_request(self, data, name="eth_getTransactionByHash")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByHash", "params": [random.choice(tx_hash_misses)]}
        response = run_request(self, data, name="eth_getTransactionByHash (miss)")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockTransactionCountByNumber", "params": [block_hex]}
        response = run_request(self, data, name="eth_getBlockTransactionCountByNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockTransactionCountByHash", "params": [block_hash]}
        response = run_request(self, data, name="eth_getBlockTransactionCountByHash")
        txcount = int(response.json().get("result", "0x0"), 16)
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByBlockHashAndIndex", "params": [block_hash, hex(random.randint(0, txcount))]}
        response = run_request(self, data, name="eth_getTransactionByBlockHashAndIndex")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByBlockNumberAndIndex", "params": [block_hex, hex(random.randint(0, txcount))]}
        response = run_request(self, data, name="eth_getTransactionByBlockNumberAndIndex")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionReceipt", "params": [random.choice(list(tx_hashes))]}
        response = run_request(self, data, name="eth_getTransactionReceipt")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockByNumber", "params": [block_hex, False]}
        response = run_request(self, data, name="eth_getBlockByNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockByHash", "params": [block_hash, False]}
        response = run_request(self, data, name="eth_getBlockByHash")
        data = {"jsonrpc":"2.0", "method": "eth_getUncleCountByBlockNumber", "params": [block_hex]}
        response = run_request(self, data, name="eth_getUncleCountByBlockNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getUncleCountByBlockHash", "params": [block_hash]}
        response = run_request(self, data, name="eth_getUncleCountByBlockHash")
        data = {"jsonrpc":"2.0", "method": "eth_gasPrice"}
        response = run_request(self, data, name="eth_gasPrice")

    # @task(200)
    # def get_block(self):
    #     run_request(self,  {"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}, name="eth_blockNumber")
