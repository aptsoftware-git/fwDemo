import requests
import json

# Test the datasets API endpoint
response = requests.get('http://localhost:8000/api/datasets')
datasets = response.json()

print(f'Total datasets returned: {len(datasets)}')
print('=' * 80)

for i, dataset in enumerate(sorted(datasets, key=lambda x: x['tag']), 1):
    print(f"{i}. {dataset['tag']}")
    print(f"   ID: {dataset['id']}")
    print(f"   Month: {dataset.get('month_label', 'N/A')}")
    print(f"   Units: {dataset['unit_count']}")
    print()
