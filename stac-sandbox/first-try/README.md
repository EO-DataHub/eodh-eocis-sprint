# Some curl examples

curl "http://localhost:8000/collections"
curl "http://localhost:8000/collections/ag-test"
curl "http://localhost:8000/collections/agtest"
curl "http://localhost:8000/collections/sentinel-s2-l2a-cogs"
curl "http://localhost:8000/collections/sentinel-s2-l2a-cogs/items"
curl "http://localhost:8000/collections/sentinel-s2-l2a-cogsi/tems"
curl "http://localhost:8000/collections/sentinel-s2-l2a-cogsitems"
curl -XDELETE "http://localhost:8000/collections/sentinel-s2-l2a-cogs"

And with UKCP

curl "http://localhost:8000/collections"
curl "http://localhost:8000/collections/ukcp"

