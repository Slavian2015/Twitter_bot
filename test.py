from collections import OrderedDict
import json

main_links_path = '.docker/data/my_links.json'

with open(main_links_path, "r") as fj:
    od = json.load(fj)

res = dict(reversed(list(OrderedDict(od).items())))

for key, value in OrderedDict(od).items():
    print(key, value)
