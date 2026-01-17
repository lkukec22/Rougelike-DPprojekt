"""
Unit testovi za Roguelike Dungeon Generator.

Pokreni s: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

# Dodaj src u path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from player import Player, ENEMY_DAMAGE, ITEM_HEAL


class TestPlayer:
    """Testovi za Player klasu."""
    
    def test_player_initialization(self):
        """Test inicijalizacije igrača."""
        player = Player()
        assert player.hp == 100
        assert player.max_hp == 100
        assert player.gold == 0
        assert player.inventory == []
        assert player.defeated_boss == False
    
    def test_take_damage(self):
        """Test primanja štete."""
        player = Player()
        result = player.take_damage(30)
        assert player.hp == 70
        assert result == True  # Još uvijek živ
    
    def test_take_fatal_damage(self):
        """Test smrtonosne štete."""
        player = Player()
        result = player.take_damage(150)
        assert player.hp == 0
        assert result == False  # Mrtav
    
    def test_heal(self):
        """Test liječenja."""
        player = Player()
        player.hp = 50
        player.heal(30)
        assert player.hp == 80
    
    def test_heal_max_cap(self):
        """Test da liječenje ne prelazi max HP."""
        player = Player()
        player.hp = 90
        player.heal(50)
        assert player.hp == 100  # Ne prelazi max
    
    def test_add_gold(self):
        """Test dodavanja zlata."""
        player = Player()
        player.add_gold(50)
        assert player.gold == 50
    
    def test_add_item(self):
        """Test dodavanja predmeta u inventar."""
        player = Player()
        player.add_item("health_potion")
        assert "health_potion" in player.inventory
    
    def test_add_item_excludes_common(self):
        """Test da se obični predmeti ne dodaju."""
        player = Player()
        player.add_item("torch")
        assert "torch" not in player.inventory
    
    def test_use_potion(self):
        """Test korištenja napitka."""
        player = Player()
        player.hp = 50
        player.add_item("health_potion")
        heal = player.use_potion()
        assert heal == 25
        assert player.hp == 75
        assert "health_potion" not in player.inventory
    
    def test_use_potion_empty(self):
        """Test korištenja napitka kad nema napitaka."""
        player = Player()
        heal = player.use_potion()
        assert heal == 0
    
    def test_is_alive(self):
        """Test provjere je li igrač živ."""
        player = Player()
        assert player.is_alive() == True
        player.hp = 0
        assert player.is_alive() == False


class TestEnemyDamage:
    """Testovi za ENEMY_DAMAGE konstantu."""
    
    def test_all_enemies_defined(self):
        """Test da su svi neprijatelji definirani."""
        expected_enemies = ['goblin', 'orc', 'skeleton', 'slime', 
                          'bat', 'spider', 'dragon', 'demon', 
                          'lich', 'golem', 'ghost']
        for enemy in expected_enemies:
            assert enemy in ENEMY_DAMAGE, f"Nedostaje: {enemy}"
    
    def test_damage_values_positive(self):
        """Test da su sve vrijednosti štete pozitivne."""
        for enemy, damage in ENEMY_DAMAGE.items():
            assert damage > 0, f"{enemy} ima nevažeću štetu: {damage}"


class TestItemHeal:
    """Testovi za ITEM_HEAL konstantu."""
    
    def test_heal_values(self):
        """Test vrijednosti liječenja."""
        assert ITEM_HEAL['health_potion'] == 25
        assert ITEM_HEAL['large_health_potion'] == 50
        assert ITEM_HEAL['elixir'] == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
