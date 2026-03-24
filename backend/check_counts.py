import requests

r = requests.get('http://localhost:8000/api/datasets')
datasets = r.json()

print("Unit Counts:")
for d in sorted(datasets, key=lambda x: x['tag']):
    print(f"{d['tag']:40} : {d['unit_count']} unit(s)")
