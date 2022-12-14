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
# response = requests.post(os.environ.get("BASE_RPC_SERVER", "https://sepolia.rpc.rivet.cloud/10f2a3dbcaa44fd998184ffbb8336f43"), headers=headers, json=data)
response = requests.post("https://sepolia.rpc.rivet.cloud/10f2a3dbcaa44fd998184ffbb8336f43", headers=headers, json=data)

print(response.content)
latestBlock=int(response.json().get('result'),16)
account_addresses = ['0x'+line.strip()[-40:] for line in open("polygon_erc20_account_addresses").readlines()]
token_addresses = [line.strip() for line in open("polygon_token_addresses").readlines()]
tx_hashes = [line.strip() for line in open("polygon_tx_hashes").readlines()]
tx_hash_misses = [line.strip() for line in open("polygon_tx_hash_misses").readlines()]

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
                # print("Success")
                result.success()
        return result

def rand_light_block():
    return random.randint((latestBlock - 1024),latestBlock)

def rand_heavy_block():
    return random.randint(0, latestBlock)

def rand_blend():
    weight = random.random()
    if weight > 0.1 :
        return rand_light_block()
    else:
        return rand_heavy_block()

# class RunTest(TaskSet):
#     tasks = {get_block: 200, heavy_request: 1, eth_requests: 1}
class WebsiteUser(HttpUser):

    @task(95)
    def light_requests(self):
        print("light_requests")
        token_address=random.choice(token_addresses)
        block_num=rand_light_block()
        block_hex=hex(block_num)
        data = {"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[block_hex, True],"id":1}
        response = run_request(self, data, name="light_eth_getBlockByNumber")
        block_hash=response.json().get('result')['hash']
        address = random.choice(account_addresses + token_addresses)

        data = {"jsonrpc":"2.0", "method": "eth_blockNumber"}
        response = run_request(self, data, name="light_eth_blockNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getLogs", "params": [{"fromBlock": block_hex, "toBlock": block_hex}]}
        response = run_request(self, data, name="light_eth_getLogs")
        data = {"jsonrpc":"2.0", "method": "eth_getLogs", "params": [{"fromBlock": block_hex, "toBlock": block_hex, "address": random.choice(token_addresses), "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]}]}

        response = run_request(self, data, name="light_eth_getLogs_specific")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByHash", "params": [random.choice(list(tx_hashes))]}
        response = run_request(self, data, name="light_eth_getTransactionByHash")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByHash", "params": [random.choice(tx_hash_misses)]}
        response = run_request(self, data, name="light_eth_getTransactionByHash (miss)")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockTransactionCountByNumber", "params": [block_hex]}
        response = run_request(self, data, name="light_eth_getBlockTransactionCountByNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockTransactionCountByHash", "params": [block_hash]}
        response = run_request(self, data, name="light_eth_getBlockTransactionCountByHash")
        txcount = int(response.json().get("result", "0x0"), 16)
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByBlockHashAndIndex", "params": [block_hash, hex(random.randint(0, txcount))]}
        response = run_request(self, data, name="light_eth_getTransactionByBlockHashAndIndex")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByBlockNumberAndIndex", "params": [block_hex, hex(random.randint(0, txcount))]}
        response = run_request(self, data, name="light_eth_getTransactionByBlockNumberAndIndex")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionReceipt", "params": [random.choice(list(tx_hashes))]}
        response = run_request(self, data, name="light_eth_getTransactionReceipt")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockByNumber", "params": [block_hex, False]}
        response = run_request(self, data, name="light_eth_getBlockByNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockByHash", "params": [block_hash, False]}
        response = run_request(self, data, name="light_eth_getBlockByHash")
        data = {"jsonrpc":"2.0", "method": "eth_getUncleCountByBlockNumber", "params": [block_hex]}
        response = run_request(self, data, name="light_eth_getUncleCountByBlockNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getUncleCountByBlockHash", "params": [block_hash]}
        response = run_request(self, data, name="light_eth_getUncleCountByBlockHash")
        data = {"jsonrpc":"2.0", "method": "eth_gasPrice"}
        response = run_request(self, data, name="light_eth_gasPrice")

        # # Polygon bor namespace methods
        # data = {"jsonrpc":"2.0", "method": "bor_getSnapshot", "params": [block_hex]}
        # response = run_request(self, data, name="light_bor_getSnapshot")
        
        # data = {"jsonrpc":"2.0", "method": "bor_getAuthor", "params": [block_hex]}
        # response = run_request(self, data, name="light_bor_getAuthor")

        # data = {"jsonrpc":"2.0", "method": "bor_getRootHash", "params": [(block_num - random.randint(0, 1000)), block_num]}
        # response = run_request(self, data, name="light_bor_getRootHash")

        # data = {"jsonrpc":"2.0", "method": "bor_getSignersAtHash", "params": [block_hash]}
        # response = run_request(self, data, name="light_bor_getSignersAtHash")

        # data = {"jsonrpc":"2.0", "method": "bor_getCurrentValidators"}
        # response = run_request(self, data, name="light_bor_getCurrentValidators")

        # data = {"jsonrpc":"2.0", "method": "bor_getCurrentProposer"}
        # response = run_request(self, data, name="light_bor_getCurrentProposer")
        
        # # Polygon eth namespace methods

        # data = {"jsonrpc":"2.0", "method": "bor_getBorBlockReceipt", "params": [block_hash]}
        # response = run_request(self, data, name="light_bor_getBorBlockReceipt")

        # data = {"jsonrpc":"2.0", "method": "bor_getTransactionReceiptsByBlock", "params": [block_hash]}
        # response = run_request(self, data, name="light_bor_GetTransactionReceiptsByBlock")

    @task(5)
    def heavy_requests(self):
        print("heavy_requests")
        token_address=random.choice(token_addresses)
        block_num=rand_heavy_block()
        block_hex=hex(block_num)
        data = {"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[block_hex, True],"id":1}
        response = run_request(self, data, name="heavy_eth_getBlockByNumber")
        block_hash=response.json().get('result')['hash']
        address = random.choice(account_addresses + token_addresses)

        data = {"jsonrpc":"2.0", "method": "eth_blockNumber"}
        response = run_request(self, data, name="heavy_eth_blockNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getLogs", "params": [{"fromBlock": block_hex, "toBlock": block_hex}]}
        response = run_request(self, data, name="heavy_eth_getLogs")
        data = {"jsonrpc":"2.0", "method": "eth_getLogs", "params": [{"fromBlock": block_hex, "toBlock": block_hex, "address": random.choice(token_addresses), "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]}]}

        response = run_request(self, data, name="heavy_eth_getLogs_specific")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByHash", "params": [random.choice(list(tx_hashes))]}
        response = run_request(self, data, name="heavy_eth_getTransactionByHash")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByHash", "params": [random.choice(tx_hash_misses)]}
        response = run_request(self, data, name="heavy_eth_getTransactionByHash (miss)")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockTransactionCountByNumber", "params": [block_hex]}
        response = run_request(self, data, name="heavy_eth_getBlockTransactionCountByNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockTransactionCountByHash", "params": [block_hash]}
        response = run_request(self, data, name="heavy_eth_getBlockTransactionCountByHash")
        txcount = int(response.json().get("result", "0x0"), 16)
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByBlockHashAndIndex", "params": [block_hash, hex(random.randint(0, txcount))]}
        response = run_request(self, data, name="heavy_eth_getTransactionByBlockHashAndIndex")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByBlockNumberAndIndex", "params": [block_hex, hex(random.randint(0, txcount))]}
        response = run_request(self, data, name="heavy_eth_getTransactionByBlockNumberAndIndex")
        data = {"jsonrpc":"2.0", "method": "eth_getTransactionReceipt", "params": [random.choice(list(tx_hashes))]}
        response = run_request(self, data, name="heavy_eth_getTransactionReceipt")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockByNumber", "params": [block_hex, False]}
        response = run_request(self, data, name="heavy_eth_getBlockByNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getBlockByHash", "params": [block_hash, False]}
        response = run_request(self, data, name="heavy_eth_getBlockByHash")
        data = {"jsonrpc":"2.0", "method": "eth_getUncleCountByBlockNumber", "params": [block_hex]}
        response = run_request(self, data, name="heavy_eth_getUncleCountByBlockNumber")
        data = {"jsonrpc":"2.0", "method": "eth_getUncleCountByBlockHash", "params": [block_hash]}
        response = run_request(self, data, name="heavy_eth_getUncleCountByBlockHash")
        data = {"jsonrpc":"2.0", "method": "eth_gasPrice"}
        response = run_request(self, data, name="heavy_eth_gasPrice")

        # # Polygon bor namespace methods
        # data = {"jsonrpc":"2.0", "method": "bor_getSnapshot", "params": [block_hex]}
        # response = run_request(self, data, name="heavy_bor_getSnapshot")
        
        # data = {"jsonrpc":"2.0", "method": "bor_getAuthor", "params": [block_hex]}
        # response = run_request(self, data, name="heavy_bor_getAuthor")

        # data = {"jsonrpc":"2.0", "method": "bor_getRootHash", "params": [(block_num - random.randint(0, 1000)), block_num]}
        # response = run_request(self, data, name="heavy_bor_getRootHash")

        # data = {"jsonrpc":"2.0", "method": "bor_getSignersAtHash", "params": [block_hash]}
        # response = run_request(self, data, name="heavy_bor_getSignersAtHash")

        # data = {"jsonrpc":"2.0", "method": "bor_getCurrentValidators"}
        # response = run_request(self, data, name="heavy_bor_getCurrentValidators")

        # data = {"jsonrpc":"2.0", "method": "bor_getCurrentProposer"}
        # response = run_request(self, data, name="heavy_bor_getCurrentProposer")
        
        # # Polygon eth namespace methods

        # data = {"jsonrpc":"2.0", "method": "bor_getBorBlockReceipt", "params": [block_hash]}
        # response = run_request(self, data, name="heavy_bor_getBorBlockReceipt")

        # data = {"jsonrpc":"2.0", "method": "bor_getTransactionReceiptsByBlock", "params": [block_hash]}
        # response = run_request(self, data, name="heavy_bor_GetTransactionReceiptsByBlock")