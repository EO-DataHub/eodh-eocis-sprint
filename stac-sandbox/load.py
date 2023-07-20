import requests
import json
import sys

coll_file, item_file = sys.argv[1:3]

service = "http://localhost:8000"

with open(coll_file) as f:
    collection = json.load(f)

collection_id = collection["id"]

with open(item_file) as f:
    item = json.load(f)

resp = requests.post(f"{service}/collections", json=collection)
resp = requests.post(f"{service}/collections/{collection_id}/items", json=item)

#import time
#time.sleep(1)

#requests.delete(f"{service}/collections/{collection_id}")

