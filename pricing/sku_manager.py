import os
import csv
import json

BASE = os.path.dirname(os.path.abspath(__file__))
SKU_FILE = os.path.join(BASE, "skus.json")

def load_skus():
    if os.path.exists(SKU_FILE):
        with open(SKU_FILE, 'r') as f:
            return json.load(f)
    return []

def save_skus(skus):
    with open(SKU_FILE, 'w') as f:
        json.dump(skus, f, indent=4)

def add_sku(sku, name, description, materials):
    skus = load_skus()
    skus.append({
        'sku': sku,
        'name': name,
        'description': description,
        'materials': materials
    })
    save_skus(skus)
    print(f"Added SKU: {sku}")

def list_skus():
    skus = load_skus()
    if not skus:
        print("No SKUs found.")
        return
    print("Current SKUs:")
    for sku in skus:
        print(f"- {sku['sku']}: {sku['name']}")
        print(f"  Description: {sku['description']}")
        print(f"  Materials: {', '.join(sku['materials'])}")
        print()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'add':
            if len(sys.argv) >= 6:
                sku = sys.argv[2]
                name = sys.argv[3]
                description = sys.argv[4]
                materials = sys.argv[5:]
                add_sku(sku, name, description, materials)
            else:
                print("Usage: python sku_manager.py add <sku> <name> <description> <material1> <material2> ...")
        elif command == 'list':
            list_skus()
        else:
            print("Commands: add, list")
    else:
        list_skus()