import requests
import json
import sys
import time

coll_file, item_file = sys.argv[1:3]

service = "http://localhost:8000"

with open(coll_file) as f:
    collection = json.load(f)

collection_id = collection["id"]

with open(item_file) as f:
    item = json.load(f)

item_id = item["id"]

requests.delete(f"{service}/collections/{collection_id}/items/{item_id}")
time.sleep(1)
#resp = requests.post(f"{service}/collections", json=collection)
resp = requests.post(f"{service}/collections/{collection_id}/items", json=item)

#requests.delete(f"{service}/collections/{collection_id}")

from pystac_client import Client

cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
item = next(cat.search(ids="UKESM1-0-LL.ssp585.2100").items())
print(f"Properties: {item.properties}")


cat = Client.open(service)
#resp = cat.search(collections=collection_id) #, ids="ukcp-rcp85-tasmax")
#items = list(resp.items())
#print(f"Found {len(items)} items")

item = next(cat.search(ids=item_id).items())

print(f"Properties: {item.properties}")

