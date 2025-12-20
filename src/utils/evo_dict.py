

class EvoDict:
    def __init__(self):
        self._evo_dict = {
            # name: (new_name, new_sprite, lev_req, money_req, max_hp+)
            "Pikachu": ("Charizard", "menu_sprites/menusprite2.png", 20, 200, 15),
            "Charizard": ("Blastoise", "menu_sprites/menusprite3.png", 30, 400, 25),
            "Venusaur": ("idk the name", "menu_sprites/menusprite7.png", 15, 150, 12),
            "idk the name": ("Donald Trump", "menu_sprites/menusprite8.png", 25, 260, 18),
            "Donald Trump": ("sans undertale", "menu_sprites/menusprite9.png", 35, 620, 35),
        }

    @property
    def evo_dict(self):
        return self._evo_dict

    @evo_dict.setter
    def evo_dict(self, value):
        if not isinstance(value, dict):
            raise TypeError("evo_dict must be a dict")
        self._evo_dict = value
# monsters": [
#       { "name": "Pikachu",   "hp": 85,  "max_hp": 100, "level": 25, "sprite_path": "menu_sprites/menusprite1.png", "element": "nature", "exp": 0 },
#       { "name": "Charizard", "hp": 150, "max_hp": 200, "level": 36, "sprite_path": "menu_sprites/menusprite2.png", "element": "nature", "exp": 0 },
#       { "name": "Blastoise", "hp": 120, "max_hp": 180, "level": 32, "sprite_path": "menu_sprites/menusprite3.png", "element": "nature", "exp": 0 },
#       { "name": "Venusaur",  "hp": 90,  "max_hp": 160, "level": 30, "sprite_path": "menu_sprites/menusprite4.png", "element": "fire", "exp": 0 },
#       { "name": "Gengar",    "hp": 110, "max_hp": 140, "level": 28, "sprite_path": "menu_sprites/menusprite5.png", "element": "fire", "exp": 0 },
#       { "name": "Dragonite", "hp": 180, "max_hp": 220, "level": 40, "sprite_path": "menu_sprites/menusprite6.png", "element": "water", "exp": 0 }
#     ],