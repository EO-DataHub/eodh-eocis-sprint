import json, sys

f = sys.argv[1]

data = json.load(open(f))

with open(f, "w") as w:
    json.dump(data, w, indent=3)

