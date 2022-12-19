from locust import HttpUser, TaskSet, task
import requests
import json
import random
import sys
from weights import *

headers = {
    'Content-Type': 'application/json',
}
data={"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest", False],"id":1}
response = requests.post("https://sepolia.rpc.stage.rivet.cloud/43b33061f60445c2a74ac62fd904ed29", headers=headers, json=data)
block_number = response.json().get('result')['number']
block_hash = response.json().get('result')['hash']


print(response.content)
latestBlock=int(block_number,16)
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
                result.success()
        return result

def rand_light_block():
    return random.randint((latestBlock - 1024),latestBlock)

def rand_heavy_block():
    return random.randint(0, latestBlock)


weight_object = get_weight_object()

light_coefficient = 9
heavy_coefficient = 1

class WebsiteUser(HttpUser):
    def __init__(self, *args, **kwargs):
        self.light_session_tx_hashes = [*tx_hashes]
        self.light_session_senders = []
        self.light_session_recipients = []
        self.light_block_num = latestBlock
        self.light_block_hex = block_number
        self.light_block_hash = block_hash
        self.light_64block_hash = ""

        self.heavy_session_tx_hashes = [*tx_hashes]
        self.heavy_session_senders = []
        self.heavy_session_recipients = []
        self.heavy_block_num = latestBlock
        self.heavy_block_hex = block_number
        self.heavy_block_hash = block_hash
        self.heavy_64block_hash = ""
        super(WebsiteUser, self).__init__(*args, **kwargs)

    ## flume standard eth methods

    @task(weight=weight_object["eth_chainId"] * light_coefficient) # default light
    def light_chainId(self):
        method = "eth_chainId"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    @task(weight=weight_object["eth_blockNumber"] * light_coefficient) # default light
    def blockNumber(self):
        method = "eth_blockNumber"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    # @task(weight=weight_object["eth_getBlockByNumber"] * light_coefficient)
    @task(1000)
    def light_blockByNumber(self):
        method = "eth_getBlockByNumber"
        print(method)
        self.light_block_num=rand_light_block()
        self.light_block_hex=hex(self.light_block_num)
        data = {"jsonrpc":"2.0","method":f"{method}","params":[self.light_block_hex, True],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")
        if self.light_block_num % 64 == 0:
            self.light_64block_hash = response.json().get('result')['hash']
        else:
            self.light_block_hash = response.json().get('result')['hash']
        transaction_hashes = [tx['hash'] for tx in response.json().get('result')['transactions']]
        recepients = [tx['to'] for tx in response.json().get('result')['transactions']]
        senders = [tx['from'] for tx in response.json().get('result')['transactions']]
        self.light_session_tx_hashes.extend(transaction_hashes)
        self.light_session_recipients.extend(recepients)
        self.light_session_senders.extend(senders)
    
    @task(weight=weight_object["eth_getBlockByHash"] * light_coefficient)
    def light_blockByHash(self):
        method = "eth_getBlockByHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hash, True],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    @task(weight=weight_object["eth_getLogs"] * light_coefficient)
    def light_getLogs(self):
        method = "eth_getLogs"
        print(method)
        data = {"jsonrpc":"2.0", "method": "eth_getLogs", "params": [{"fromBlock": hex(self.light_block_num - random.randint(0, 3)), "toBlock": hex(self.light_block_num), "address": random.choice(token_addresses), "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]}],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    @task(weight=weight_object["eth_getTransactionByHash"] * light_coefficient)
    def light_transactionByHash(self):
        method = "eth_getTransactionByHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(self.light_session_tx_hashes)],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByHash", "params": [random.choice(tx_hash_misses)]}
        response = run_request(self, data, name="light_eth_getTransactionByHash (miss)")

    @task(weight=weight_object["eth_getBlockTransactionCountByNumber"] * light_coefficient)
    def light_blockTransactionCountByNumber(self):
        print(len(self.light_transaction_hashes))
        method = "eth_getBlockTransactionCountByNumber"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hex],"id":random.randint(0, 9999)}
        print(self.light_block_hex)
        response = run_request(self, data, name=f"light_{method}")
        self.light_txcount_and_number = (self.light_block_hex, int(response.json().get("result", "0x0"), 16))

    @task(weight=weight_object["eth_getBlockTransactionCountByHash"] * light_coefficient)
    def light_blockTransactionCountByHash(self):
        print(len(self.light_transaction_hashes))
        method = "eth_getBlockTransactionCountByHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hash],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")
        self.light_txcount_and_hash = (self.light_block_hash, int(response.json().get("result", "0x0"), 16))

    @task(weight=weight_object["eth_getTransactionReceipt"] * light_coefficient)
    def light_transactionReceipt(self):
        method = "eth_getTransactionReceipt"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(self.light_session_tx_hashes)],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

        data = {"jsonrpc":"2.0", "method": "eth_getTransactionReceipt", "params": [random.choice(tx_hash_misses)]}
        response = run_request(self, data, name="light_eth_getTransactionReceipt (miss)")

    @task(weight=weight_object["eth_getUncleCountByBlockNumber"] * light_coefficient)
    def light_uncleCountByBlockNumber(self):
        method = "eth_getUncleCountByBlockNumber"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hex],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    @task(weight=weight_object["eth_getUncleCountByBlockHash"] * light_coefficient)
    def light_uncleCountByBlockHash(self):
        method = "eth_getUncleCountByBlockHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hash],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    @task(weight=weight_object["eth_gasPrice"] * light_coefficient)
    def light_gasPrice(self):
        method = "eth_gasPrice"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    @task(weight=weight_object["eth_maxPriorityFeePerGas"] * light_coefficient)
    def light_maxPriorityFeePerGas(self):
        method = "eth_maxPriorityFeePerGas"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    @task(weight=weight_object["eth_feeHistory"] * light_coefficient)
    def light_feeHistory(self):
        method = "eth_feeHistory"
        print(method) ## TODO float params
        data = {"jsonrpc":"2.0","method": f"{method}","params":[hex(random.randint(0, 10)), self.light_block_hex, [random.random(), random.random(), random.random()]], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")    

    ## flume name space methods 

    @task(weight=weight_object["flume_getTransactionReceiptsByBlockNumber"] * light_coefficient) 
    def light_transactionReceiptsByBlockNumber(self):
        method = "flume_getTransactionReceiptsByBlockNumber"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hex], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    @task(weight=weight_object["flume_getTransactionReceiptsByBlockHash"] * light_coefficient) 
    def light_transactionReceiptsByBlockHash(self):
        method = "flume_getTransactionReceiptsByBlockHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hash], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    # # Polygon bor namespace methods

    # @task(weight=weight_object["bor_getSnapshot"] * light_coefficient)
    @task(weight=2000)
    def light_snapshot(self):
        method = "bor_getSnapshot"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hex], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method} block")

        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hash], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method} hash")

    # @task(weight=weight_object["bor_getAuthor"] * light_coefficient)
    @task(weight=2000)
    def light_author(self):
        method = "bor_getAuthor"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hex], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    # @task(weight=weight_object["bor_getRootHash"] * light_coefficient)
    @task(weight=2000)
    def light_rootHash(self):
        method = "bor_getRootHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[(self.light_block_num - random.randint(0, 1000)), self.light_block_num], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    @task(weight=weight_object["bor_getSignersAtHash"] * light_coefficient)
    @task(weight=2000)
    def light_signersAtHash(self):
        method = "bor_getSignersAtHash"
        print(method)

        if len(self.light_64block_hash) > 0:
            data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_64block_hash], "id":random.randint(0, 9999)}
            response = run_request(self, data, name=f"light_{method}")
        else:
            data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hash], "id":random.randint(0, 9999)}
            response = run_request(self, data, name=f"light_{method} error")

    # @task(weight=weight_object["bor_getCurrentValidators"] * light_coefficient)
    @task(weight=2000)
    def light_currentValidators(self):
        method = "bor_getCurrentValidators"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    # @task(weight=weight_object["bor_getCurrentProposer"] * light_coefficient)
    @task(weight=2000)
    def light_currentProposer(self):
        method = "bor_getCurrentProposer"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")
        
    # # Polygon eth namespace methods

    # @task(weight=weight_object["eth_getBorBlockReceipt"] * light_coefficient)
    @task(weight=2000)
    def light_borBlockReceipt(self):
        method = "eth_getBorBlockReceipt"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hash], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method}")

    # @task(weight=weight_object["eth_getTransactionReceiptsByBlock"] * light_coefficient)
    @task(weight=2000)
    def light_transactionReceiptsByBlock(self):
        method = "eth_getTransactionReceiptsByBlock"
        print(method)

        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hex], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method} block")

        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.light_block_hash], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"light_{method} hash")

    # Heavy calls

    @task(weight=weight_object["eth_getBlockByNumber"] * heavy_coefficient)
    @task(1000)
    def heavy_blockByNumber(self):
        method = "eth_getBlockByNumber"
        print(method)
        self.heavy_block_num=rand_heavy_block()
        self.heavy_block_hex=hex(self.heavy_block_num)
        data = {"jsonrpc":"2.0","method":f"{method}","params":[self.heavy_block_hex, True],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")
        if self.heavy_block_num % 64 == 0:
            self.heavy_65block_hash = response.json().get('result')['hash']
        else:
            self.heavy_block_hash = response.json().get('result')['hash']
        self.heavy_block_hash = response.json().get('result')['hash']
        transaction_hashes = [tx['hash'] for tx in response.json().get('result')['transactions']]
        recepients = [tx['to'] for tx in response.json().get('result')['transactions']]
        senders = [tx['from'] for tx in response.json().get('result')['transactions']]
        self.heavy_session_tx_hashes.extend(transaction_hashes)
        self.heavy_session_recipients.extend(recepients)
        self.heavy_session_senders.extend(senders)
    
    @task(weight=weight_object["eth_getBlockByHash"] * heavy_coefficient)
    def heavy_blockByHash(self):
        method = "eth_getBlockByHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hash, True],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["eth_getLogs"] * heavy_coefficient)
    def heavy_getLogs(self):
        method = "eth_getLogs"
        print(method)
        data = {"jsonrpc":"2.0", "method": "eth_getLogs", "params": [{"fromBlock": hex(self.heavy_block_num - random.randint(0, 3)), "toBlock": hex(self.heavy_block_num), "address": random.choice(token_addresses), "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]}],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["eth_getTransactionByHash"] * heavy_coefficient)
    def heavy_transactionByHash(self):
        method = "eth_getTransactionByHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(self.heavy_session_tx_hashes)],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

        data = {"jsonrpc":"2.0", "method": "eth_getTransactionByHash", "params": [random.choice(tx_hash_misses)]}
        response = run_request(self, data, name="light_eth_getTransactionByHash (miss)")

    @task(weight=weight_object["eth_getBlockTransactionCountByNumber"] * heavy_coefficient)
    def heavy_blockTransactionCountByNumber(self):
        print(len(self.heavy_transaction_hashes))
        method = "eth_getBlockTransactionCountByNumber"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hex],"id":random.randint(0, 9999)}
        print(self.heavy_block_hex)
        response = run_request(self, data, name=f"heavy_{method}")
        self.heavy_txcount_and_number = (self.heavy_block_hex, int(response.json().get("result", "0x0"), 16))

    @task(weight=weight_object["eth_getBlockTransactionCountByHash"] * heavy_coefficient)
    def heavy_blockTransactionCountByHash(self):
        print(len(self.heavy_transaction_hashes))
        method = "eth_getBlockTransactionCountByHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hash],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")
        self.heavy_txcount_and_hash = (self.heavy_block_hash, int(response.json().get("result", "0x0"), 16))

    @task(weight=weight_object["eth_getTransactionReceipt"] * heavy_coefficient)
    def heavy_transactionReceipt(self):
        method = "eth_getTransactionReceipt"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(self.heavy_session_tx_hashes)],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

        data = {"jsonrpc":"2.0", "method": "eth_getTransactionReceipt", "params": [random.choice(tx_hash_misses)]}
        response = run_request(self, data, name="light_eth_getTransactionReceipt (miss)")

    @task(weight=weight_object["eth_getUncleCountByBlockNumber"] * heavy_coefficient)
    def heavy_uncleCountByBlockNumber(self):
        method = "eth_getUncleCountByBlockNumber"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hex],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["eth_getUncleCountByBlockHash"] * heavy_coefficient)
    def heavy_uncleCountByBlockHash(self):
        method = "eth_getUncleCountByBlockHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hash],"id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["eth_gasPrice"] * heavy_coefficient)
    def heavy_gasPrice(self):
        method = "eth_gasPrice"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["eth_maxPriorityFeePerGas"] * heavy_coefficient)
    def heavy_maxPriorityFeePerGas(self):
        method = "eth_maxPriorityFeePerGas"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["eth_feeHistory"] * heavy_coefficient)
    def heavy_feeHistory(self):
        method = "eth_feeHistory"
        print(method) ## TODO float params
        data = {"jsonrpc":"2.0","method": f"{method}","params":[hex(random.randint(0, 10)), self.heavy_block_hex, [random.random(), random.random(), random.random()]], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")    

    ## flume name space methods 

    @task(weight=weight_object["flume_getTransactionsBySender"] * heavy_coefficient) ## default heavy
    def heavy_transactionsBySender(self):
        method = "flume_getTransactionsBySender"
        print(method) 
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(self.heavy_session_senders)], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["flume_getTransactionsByRecipient"] * heavy_coefficient) ## default heavy
    def heavy_transactionsByRecipient(self):
        method = "flume_getTransactionsByRecipient"
        print(method) 
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(self.heavy_session_recipients)], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["flume_getTransactionsByParticipant"] * heavy_coefficient) ## default heavy
    def heavy_transactionsByParticipant(self):
        method = "flume_getTransactionsByParticipant"
        print(method) 
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(account_addresses)], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["flume_getTransactionReceiptsBySender"] * heavy_coefficient) ## default heavy
    def heavy_transactionReceiptsBySender(self):
        method = "flume_getTransactionReceiptsBySender"
        print(method) 
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(self.heavy_session_senders)], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["flume_getTransactionReceiptsByRecipient"] * heavy_coefficient) ## default heavy
    def heavy_transactionReceiptsByRecipient(self):
        method = "flume_getTransactionReceiptsByRecipient"
        print(method) 
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(self.heavy_session_recipients)], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["flume_getTransactionReceiptsByParticipant"] * heavy_coefficient) ## default heavy
    def heavy_transactionReceiptsByParticipant(self):
        method = "flume_getTransactionReceiptsByParticipant"
        print(method) 
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(account_addresses)], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")


    @task(weight=weight_object["flume_getTransactionReceiptsByBlockNumber"] * heavy_coefficient) 
    def heavy_transactionReceiptsByBlockNumber(self):
        method = "flume_getTransactionReceiptsByBlockNumber"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hex], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["flume_getTransactionReceiptsByBlockHash"] * heavy_coefficient) 
    def heavy_transactionReceiptsByBlockHash(self):
        method = "flume_getTransactionReceiptsByBlockHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hash], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["flume_getERC20ByAccount"] * heavy_coefficient) ## default heavy
    def heavy_eRC20ByAccount(self):
        method = "flume_getERC20ByAccount"
        print(method) 
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(account_addresses)], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["flume_getERC20Holders"] * heavy_coefficient) ## default heavy
    def heavy_eRC20Holders(self):
        method = "flume_getERC20Holders"
        print(method) 
        data = {"jsonrpc":"2.0","method": f"{method}","params":[random.choice(account_addresses)], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    # # # Polygon bor namespace methods

    # @task(weight=weight_object["bor_getSnapshot"] * heavy_coefficient)
    @task(weight=2000)
    def heavy_snapshot(self):
        method = "bor_getSnapshot"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hex], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method} block")

        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hash], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method} hash")

    # @task(weight=weight_object["bor_getAuthor"] * heavy_coefficient)
    @task(weight=2000)
    def heavy_author(self):
        method = "bor_getAuthor"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hex], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    # @task(weight=weight_object["bor_getRootHash"] * heavy_coefficient)
    @task(weight=2000)
    def heavy_rootHash(self):
        method = "bor_getRootHash"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[(self.heavy_block_num - random.randint(0, 1000)), self.heavy_block_num], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    @task(weight=weight_object["bor_getSignersAtHash"] * heavy_coefficient)
    @task(weight=2000)
    def heavy_getSignersAtHash(self):
        method = "bor_getSignersAtHash"
        print(method)

        if len(self.heavy_64block_hash) > 0:
            data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_64block_hash], "id":random.randint(0, 9999)}
            response = run_request(self, data, name=f"heavy_{method}")
        else:
            data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hash], "id":random.randint(0, 9999)}
            response = run_request(self, data, name=f"heavy_{method} error")

    # @task(weight=weight_object["bor_getCurrentValidators"] * heavy_coefficient)
    @task(weight=2000)
    def heavy_currentValidators(self):
        method = "bor_getCurrentValidators"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    # @task(weight=weight_object["bor_getCurrentProposer"] * heavy_coefficient)
    @task(weight=2000)
    def heavy_currentProposer(self):
        method = "bor_getCurrentProposer"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")
        
    # # Polygon eth namespace methods

    # @task(weight=weight_object["eth_getBorBlockReceipt"] * heavy_coefficient)
    @task(weight=2000)
    def heavy_borBlockReceipt(self):
        method = "eth_getBorBlockReceipt"
        print(method)
        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hash], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method}")

    # @task(weight=weight_object["eth_getTransactionReceiptsByBlock"] * heavy_coefficient)
    @task(weight=2000)
    def heavy_transactionReceiptsByBlock(self):
        method = "eth_getTransactionReceiptsByBlock"
        print(method)

        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hex], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method} block")

        data = {"jsonrpc":"2.0","method": f"{method}","params":[self.heavy_block_hash], "id":random.randint(0, 9999)}
        response = run_request(self, data, name=f"heavy_{method} hash")