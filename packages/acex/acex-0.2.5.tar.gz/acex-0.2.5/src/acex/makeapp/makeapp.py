from ace.constants import DEFAULT_INVENTORY_TYPE

class Make: 

    def __init__(self):
        self._inventory_type = DEFAULT_INVENTORY_TYPE

    @property
    def inventory_type(self):
        if self._inventory_type == None:
            return DEFAULT_INVENTORY_TYPE


    def build_skeleton(self):
        print(f"skapar nytt skelett för projekt. Inventory är av typen: {self.inventory_type}")