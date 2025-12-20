

class DestinationDict:
    def __init__(self):
        self._destination_dict = {
            # name: (map, (x, y))
            "gym": ("map.tmx", (24, 23)),
            "desert": ("map.tmx", (1, 31))
        }

    @property
    def destination_dict(self):
        return self._destination_dict

    @destination_dict.setter
    def destination_dict(self, value):
        if not isinstance(value, dict):
            raise TypeError("destination_dict must be a dict")
        self._destination_dict = value
