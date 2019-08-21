import asyncio
import json
from collections import Counter

import websockets
import logging

logging.basicConfig(level=logging.INFO,)
# logger = logging.getLogger('websockets')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())
log = logging.getLogger(__name__)


async def watch_primary(primary, collectables, subscriptions):
    async with websockets.connect(primary) as websocket:
        sends = []
        for i, sub in enumerate(subscriptions):
            sends.append(websocket.send(json.dumps(
                {"jsonrpc":"2.0", "id": i, "method": "eth_subscribe", "params": sub}
            )))
        await asyncio.wait(sends)
        log.info("Primary initialized")
        sub_mapping = {}
        while True:
            message = json.loads(await websocket.recv())
            try:
                sub_id = message["id"]
            except KeyError:
                pass
            else:
                if sub_id < len(subscriptions):
                    try:
                        sub_mapping[message["result"]] = sub_id
                        continue
                    except KeyError:
                        pass
            try:
                message["params"]["subscription"] = sub_mapping[message["params"]["subscription"]]
            except KeyError:
                log.warning("Mapping missing for %s", message["params"]["subscription"])
            message_string = json.dumps(message, sort_keys=True)
            for collectable in collectables:
                collectable[message_string] += 1

async def watch_secondary(secondary, collectable, subscriptions):
    log.info("Initializing secondary %s", secondary)
    async with websockets.connect(secondary) as websocket:
        log.info("Connected %s", secondary)
        # log.info("%s", list(enumerate(subscriptions)))
        sends = []
        for i, sub in enumerate(subscriptions):
            sends.append(websocket.send(json.dumps(
                {"jsonrpc":"2.0", "id": i, "method": "eth_subscribe", "params": sub}
            )))
        await asyncio.wait(sends)
        log.info("Secondary initialized")
        sub_mapping = {}
        while True:
            # log.info("Getting message on %s", secondary)
            try:
                raw_message = await websocket.recv()
            except:
                log.exception("Error receiving message")
                break
            # log.info("Parsing message on %s", secondary)
            message = json.loads(raw_message)
            log.info("Got message on %s", secondary)
            try:
                sub_id = message["id"]
            except KeyError:
                pass
            else:
                if sub_id < len(subscriptions):
                    try:
                        sub_mapping[message["result"]] = sub_id
                        continue
                    except KeyError:
                        pass
            try:
                message["params"]["subscription"] = sub_mapping[message["params"]["subscription"]]
            except KeyError:
                log.warning("Mapping missing for %s", message["params"]["subscription"])
            message_string = json.dumps(message, sort_keys=True)
            collectable[message_string] -= 1
            log.info("Done with loop %s", secondary)

async def report(collectables):
    while True:
        print("Report: %s" % max(len(c) for c in collectables))
        for i, c in enumerate(collectables):
            counter = 0
            for k, v in c.items():
                if v:
                    counter += 1
                    # print("\t", i, v, k)
            if counter > 0:
                print("\t", i, counter)
        await asyncio.sleep(30)

async def run_test():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("primary")
    parser.add_argument("secondary", nargs="+")
    parser.add_argument("--subscriptions")
    args = parser.parse_args()
    subscriptions = [
        ["logs", {}],
        # ["newHeads"],
        # ["logs", {"topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]}],
    ]
    if args.subscriptions:
        with open(args.subscription) as fd:
            subscriptions = json.load(fd)
    collectables = [Counter() for _ in args.secondary]
    actions = [watch_primary(args.primary, collectables, subscriptions), report(collectables)]
    for secondary, collectable in zip(args.secondary, collectables):
        actions.append(watch_secondary(secondary, collectable, subscriptions))
    await asyncio.wait(actions)


asyncio.get_event_loop().run_until_complete(run_test())
