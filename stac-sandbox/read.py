from pystac_client import Client

# custom headers
headers = []

service = "http://localhost:8000"
cat = Client.open(service, headers=headers)

collection_id = "sentinel-s2-l2a-cogs"


