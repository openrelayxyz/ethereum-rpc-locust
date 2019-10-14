from locust import HttpLocust, TaskSet, task
from locust.events import request_success, request_failure

import json
import uuid
import time
import gevent
import logging
import random
import websocket
import six
import sys

# account_addresses = open("erc20_account_addresses").readlines()
token_addresses = open("erc20_token_addresses").readlines()

logging.basicConfig(level=logging.INFO,)

log = logging.getLogger(__name__)
websocket.setdefaulttimeout(120)


class EchoTaskSet(TaskSet):
    def on_start(self):
        sends = []
        self.sends = sends
        ws = websocket.create_connection('ADDERSS', timeout=120)
        self.ws = ws
        ws2 = websocket.create_connection('ADDERSS', timeout=120)
        self.ws2 = ws2
        output = random.randint(1,5000) >= 4999

        def _receive():
            sub_mapping = {}
            while True:
                start_time = time.time()
                try:
                    res = ws.recv()
                except:
                    log.exception("Error receiving message")
                    break
                message = json.loads(res)
                try:
                    sub_id = message["id"]
                except KeyError:
                    pass
                else:
                    try:
                        sub_mapping[message["result"]] = sub_id
                        continue
                    except KeyError:
                        pass
                    # except TypeError:
                    #     print(sub_mapping)
                    #     print(message)
                    #     print(sub_id)

                end_time = time.time()
                # if output:
                   # print(message)
                try:
                    message["params"]["subscription"] = sub_mapping[message["params"]["subscription"]]
                except KeyError:
                    log.warning("Mapping missing for %s", message["params"]["subscription"])
                    end_at = time.time()
                    response_time = int(round((end_time - start_time) * 1000))
                    num=len(self.sends)//10
                    request_failure.fire(
                        request_type='WebSocket Recv',
                        name=f'gotsomething{num}',
                        response_time=1,
                        response_length=len(res),
                        exception="Mapping missing for %s" % message["params"]["subscription"]
                    )

                end_at = time.time()
                num=len(self.sends)//10
                # print("recv")
                # print(message)
                # if num == 0:
                    # print(len(self.sends))
                    # print(self.sends)
                response_time = int(round((end_time - start_time) * 1000))
                request_success.fire(
                    request_type='WebSocket Recv',
                    name=f'gotsomething{num}',
                    response_time=response_time,
                    response_length=len(res),
                )

        def _receive2():
            while True:
                try:
                    res = ws2.recv()
                except:
                    log.exception("Error receiving message")
                    break

                end_time = time.time()
                response_time = int(round((end_time - self.check_start_time) * 1000))
                request_success.fire(
                    request_type='WebSocket Recv',
                    name=f'eth_blockNumberRPC',
                    response_time=response_time,
                    response_length=len(res),
                )

        gevent.spawn(_receive2)
        gevent.spawn(_receive)
        subscription=[
        {"jsonrpc":"2.0", "method": "eth_subscribe", "params": ["newHeads"]},
        {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["logs", {"topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]}]}
        ]
        for sub in subscription:
            sub['id'] = random.randint(0,sys.maxsize)
            self.sends.append(self.ws.send(json.dumps(sub)))

    def on_quit(self):
        self.ws.close()
        self.ws2.close()

    @task
    def wait(self):
        time.sleep(10)
        # print("RUnninTAsk")
        resp=self.ws.send(json.dumps({"jsonrpc":"2.0", "id": random.randint(0,sys.maxsize), "method": "eth_subscribe", "params": ["logs", {"topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"], "address": random.choice(token_addresses).strip()}]}))
        self.sends.append(resp)
        # print(resp)
        # print(self.sends)

    @task
    def query(self):
        time.sleep(random.randint(5,20))
        # print("RUnninTAsk2")
        self.check_start_time = time.time()
        data={"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":000000000000000000000000}
        self.ws2.send(json.dumps(data))
class EchoLocust(HttpLocust):
    task_set = EchoTaskSet
    min_wait = 1000
    max_wait = 5000
