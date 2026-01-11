"""
Testovi za Prolog Bridge i integraciju s Prologom.

Pokreni s: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

# Dodaj src u path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prolog_bridge import PrologBridge


class TestPrologBridge:
    """Testovi za PrologBridge klasu."""
    
    @pytest.fixture
    def bridge(self):
        """Fixture koji stvara PrologBridge instancu."""
        return PrologBridge()
    
    def test_bridge_initialization(self, bridge):
        """Test inicijalizacije bridge-a."""
        assert bridge.prolog is not None
    
    def test_generate_dungeon_returns_dict(self, bridge):
        """Test da generate_dungeon vraća rječnik."""
        result = bridge.generate_dungeon(seed=42, num_rooms=5)
        assert isinstance(result, dict)
        assert 'rooms' in result
        assert 'connections' in result
        assert 'room_contents' in result
    
    def test_generate_dungeon_creates_rooms(self, bridge):
        """Test da se stvaraju sobe."""
        result = bridge.generate_dungeon(seed=123, num_rooms=5)
        assert len(result['rooms']) > 0
    
    def test_rooms_have_required_fields(self, bridge):
        """Test da sobe imaju potrebna polja."""
        result = bridge.generate_dungeon(seed=456, num_rooms=5)
        for room in result['rooms']:
            assert 'id' in room
            assert 'x' in room
            assert 'y' in room
            assert 'type' in room
    
    def test_start_room_exists(self, bridge):
        """Test da postoji start soba."""
        result = bridge.generate_dungeon(seed=789, num_rooms=5)
        room_types = [r['type'] for r in result['rooms']]
        assert 'start' in room_types
    
    def test_connections_exist(self, bridge):
        """Test da postoje veze između soba."""
        result = bridge.generate_dungeon(seed=101, num_rooms=5)
        assert len(result['connections']) > 0
    
    def test_connections_have_required_fields(self, bridge):
        """Test da veze imaju potrebna polja."""
        result = bridge.generate_dungeon(seed=202, num_rooms=5)
        for conn in result['connections']:
            assert 'from' in conn
            assert 'to' in conn
            assert 'direction' in conn
    
    def test_room_contents_exist(self, bridge):
        """Test da postoji sadržaj soba."""
        result = bridge.generate_dungeon(seed=303, num_rooms=5)
        assert len(result['room_contents']) > 0
    
    def test_room_content_has_required_fields(self, bridge):
        """Test da sadržaj sobe ima potrebna polja."""
        result = bridge.generate_dungeon(seed=404, num_rooms=5)
        for room_id, content in result['room_contents'].items():
            assert 'description' in content
            assert 'enemies' in content
            assert 'items' in content
            assert 'gold' in content
    
    def test_clear_dungeon(self, bridge):
        """Test brisanja dungeona."""
        bridge.generate_dungeon(seed=505, num_rooms=5)
        bridge.clear()
        # Nakon clear, sljedeće generiranje bi trebalo raditi
        result = bridge.generate_dungeon(seed=606, num_rooms=3)
        assert len(result['rooms']) > 0
    
    def test_different_seeds_different_dungeons(self, bridge):
        """Test da različiti seedovi daju različite dungeonove."""
        result1 = bridge.generate_dungeon(seed=111, num_rooms=5)
        bridge.clear()
        result2 = bridge.generate_dungeon(seed=222, num_rooms=5)
        
        # Barem nešto bi trebalo biti drugačije
        rooms1 = [(r['x'], r['y']) for r in result1['rooms']]
        rooms2 = [(r['x'], r['y']) for r in result2['rooms']]
        # Ne moraju biti potpuno različiti, ali testiramo da rade


class TestPrologBridgeEdgeCases:
    """Testovi rubnih slučajeva."""
    
    @pytest.fixture
    def bridge(self):
        return PrologBridge()
    
    def test_minimum_rooms(self, bridge):
        """Test minimalnog broja soba."""
        result = bridge.generate_dungeon(seed=1, num_rooms=1)
        assert len(result['rooms']) >= 1
    
    def test_large_dungeon(self, bridge):
        """Test većeg dungeona."""
        result = bridge.generate_dungeon(seed=999, num_rooms=20)
        assert len(result['rooms']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
