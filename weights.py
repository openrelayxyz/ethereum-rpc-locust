import json
from collections import Counter


def extract_flume_methods():
    f = open('flume-methods.json')
    l = json.load(f)
    mets = [*l[0], *l[1], *l[2], *l[3]]
    return mets

def get_weight_object():
    methods = []
    f = open('kafka.txt').readlines()
    for item in f:
        d = json.loads(item)
        b = json.loads(d['b'])
        m = b['method']
        methods.append(m)

    c = Counter(methods)

    total = sum(dict(c).values())

    print(total)

    dist = {}

    for k, v in dict(c).items():
        dist[k] = int((v / total) * 10000)

    low = min(dist.values())

    flume_methods = extract_flume_methods()

    for item in flume_methods:
        if item not in list(dist):
            dist[item] = low

    return dist

def main():
    x = get_weight_object()
    print(x)

if __name__ == '__main__':
    main()