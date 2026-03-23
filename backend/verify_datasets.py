import requests
import json

# Check the /datasets endpoint
print("=" * 80)
print("BACKEND API RESPONSE - /api/datasets")
print("=" * 80)
response = requests.get('http://localhost:8000/api/datasets')
datasets = response.json()

print(f'\nTotal datasets: {len(datasets)}\n')

for i, dataset in enumerate(sorted(datasets, key=lambda x: x['tag']), 1):
    print(f"{i}. {dataset['tag']}")
    print(f"   - ID: {dataset['id']}")
    print(f"   - Month: {dataset.get('month_label', 'N/A')}")
    print(f"   - Units: {dataset['unit_count']}")
    print(f"   - Upload Date: {dataset['upload_date']}")
    print()

print("=" * 80)
print("EXPECTED IN FRONTEND DROPDOWN:")
print("=" * 80)
for dataset in sorted(datasets, key=lambda x: x['tag']):
    print(f"  {dataset['tag']} ({dataset['month_label']}) - {dataset['unit_count']} unit(s)")
