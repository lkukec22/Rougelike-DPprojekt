ENEMY_DAMAGE = {
    'goblin': 5, 'orc': 10, 'skeleton': 8, 'slime': 3,
    'bat': 4, 'spider': 6, 'dragon': 30, 'demon': 25,
    'lich': 35, 'golem': 20, 'ghost': 7
}

ITEM_HEAL = {
    'health_potion': 25, 'large_health_potion': 50, 'elixir': 100
}


class Player:
    """
    Klasa koja predstavlja igrača u igri.
    
    Attributes:
        max_hp (int): Maksimalni HP igrača.
        hp (int): Trenutni HP igrača.
        gold (int): Količina zlata.
        inventory (list): Lista predmeta u inventaru.
        defeated_boss (bool): Je li igrač pobijedio bossa.
    """
    
    def __init__(self):
        self.max_hp = 100
        self.hp = 100
        self.gold = 0
        self.inventory = []
        self.defeated_boss = False
    
    def take_damage(self, amount):
        """Take damage and return True if still alive."""
        self.hp = max(0, self.hp - amount)
        return self.hp > 0
    
    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
    
    def add_gold(self, amount):
        self.gold += amount
    
    def add_item(self, item):
        if item not in ['nothing', 'torch', 'arrows', 'bomb', 'armor', 'magic_ring', 'key']:
            self.inventory.append(item)
    
    def use_potion(self):
        """Use first available healing potion. Returns heal amount or 0."""
        for item in self.inventory:
            if item in ITEM_HEAL:
                heal = ITEM_HEAL[item]
                self.inventory.remove(item)
                self.heal(heal)
                return heal
        return 0
    
    def is_alive(self):
        return self.hp > 0
