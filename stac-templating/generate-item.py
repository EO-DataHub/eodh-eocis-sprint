# write_messages.py
import random
from jinja2 import Environment, FileSystemLoader


collection = "Sentinel 2"


class ItemContent:
    def __init__(self, **props):
        self.props = props
        self.assets = [f"https://ceda.ac.uk/data/{x}.jpg" for x in random.sample(range(100, 200), k=10)]
        
    def variables(self):
        with open("variables.txt") as reader:
            return reader.read().strip().split()
        
    def bbox(self):
        return [-20., -20., 10., 15.]
    
        
        
content = ItemContent(
    sensor="s1str", platform="sentinel2a"
    )

environment = Environment(loader=FileSystemLoader("templates/"))
template = environment.get_template("stac-item.json")
filename = "outputs/output.json"


content = template.render(
        {"content": content, "collection": collection}
    )

with open(filename, mode="w", encoding="utf-8") as message:
    message.write(content)
    print(f"... wrote {filename}")
        

