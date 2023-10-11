import requests
import json
import sys
import time


service = "http://localhost:8000"
item_id = "UKESM1-0-LL.ssp585.2100"

from pystac_client import Client

cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
item = next(cat.search(ids=item_id).items())

print(f"Properties: {item.properties}")

cat = Client.open(service)
item = next(cat.search(ids=item_id).items())

print(f"Properties: {item.properties}")

