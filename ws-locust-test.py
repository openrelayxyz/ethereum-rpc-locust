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
        ws = websocket.create_connection('ADDRESS', timeout=120)
        self.ws = ws
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
                end_time = time.time()
                if output:
                   print(message)
                try:
                    message["params"]["subscription"] = sub_mapping[message["params"]["subscription"]]
                except KeyError:
                    log.warning("Mapping missing for %s", message["params"]["subscription"])
                    end_at = time.time()
                    response_time = int(round((end_time - start_time) * 1000))
                    request_failure.fire(
                        request_type='WebSocket Recv',
                        name='gotsomething',
                        response_time=1,
                        response_length=len(res),
                        exception="Mapping missing for %s" % message["params"]["subscription"]
                    )

                end_at = time.time()
                response_time = int(round((end_time - start_time) * 1000))
                request_success.fire(
                    request_type='WebSocket Recv',
                    name='gotsomething',
                    response_time=response_time,
                    response_length=len(res),
                )

        sends = []
        subscription=[
        {"jsonrpc":"2.0", "method": "eth_subscribe", "params": ["newHeads"]}
        # {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["logs", {"topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]}]},
        ]
        for sub in subscription:
            sub['id'] = random.randint(0,sys.maxsize)
            sends.append(self.ws.send(json.dumps(sub)))
        gevent.spawn(_receive)


    def on_quit(self):
        self.ws.close()

    @task
    def wait(self):
        while True:
            time.sleep(random.randint(5,125))




class EchoLocust(HttpLocust):
    task_set = EchoTaskSet
    min_wait = 0
    max_wait = 100
