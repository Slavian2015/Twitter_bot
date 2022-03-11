import json

main_path = '.docker/data/users.json'

# with open(main_path, "r") as fj:
#     data = json.load(fj)
#
#     print(len(data))
#     for k, v in data.items():
#         print(v)
#
# with open(main_path, 'w', encoding='utf-8') as f:
#     data = json.load(fj)
#     data[f"user{len(data) + 1}"] = {"UNAME": "slava2", "UPASS": "1112", "EMAIL": "1112"}
#     json.dump(data, f, ensure_ascii=False, indent=4)

email = "slavaku2014@gmail.com"

with open(main_path, "r") as fj:
    data_full = json.load(fj)

data = data_full.get(email, None)

print(data)
