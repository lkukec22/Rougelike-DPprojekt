"""
Prolog Bridge - PySwip sučelje za komunikaciju s Prolog generatorom dungeona.

Ovaj modul pruža Python sučelje za pozivanje Prolog predikata
i parsiranje rezultata u Python strukture podataka.
"""


from pathlib import Path
from pyswip import Prolog


class PrologBridge:
    
    def __init__(self):
        self.prolog = Prolog()
        self._load_prolog_files()
    
    def _load_prolog_files(self):

        current_dir = Path(__file__).parent.parent
        prolog_dir = current_dir / "prolog"
        

        generator_path = prolog_dir / "dungeon_generator.pl"
        if generator_path.exists():

            path_str = str(generator_path).replace("\\", "/")
            self.prolog.consult(path_str)
            print(f"[PrologBridge] Učitan: {generator_path.name}")
        else:
            raise FileNotFoundError(f"Prolog datoteka nije pronađena: {generator_path}")
    
    def generate_dungeon(self, seed: int = 42, num_rooms: int = 7) -> dict:
        """
        Generira dungeon s danim parametrima.
        """
        query = f"generate_dungeon({seed}, {num_rooms})"
        print(f"[DEBUG] Running query: {query}")
        
        try:
            results = list(self.prolog.query(query))
            print(f"[DEBUG] Prolog generation finished.")
        except Exception as e:
            print(f"[ERROR] Prolog query failed: {e}")
            return {'rooms': [], 'connections': [], 'room_contents': {}}
            
        return {
            'rooms': self._get_rooms(),
            'connections': self._get_connections(),
            'room_contents': self._get_all_room_contents()
        }
    
    def _get_rooms(self) -> list:
        rooms = []
        query_results = list(self.prolog.query("get_rooms(Rooms)"))
        
        if query_results:
            room_list = query_results[0]['Rooms']
            for room_data in room_list:
                rooms.append({
                    'id': int(room_data[0]),
                    'x': int(room_data[1]),
                    'y': int(room_data[2]),
                    'type': str(room_data[3])
                })
        
        return rooms
    
    def _get_connections(self) -> list:
        connections = []
        query_results = list(self.prolog.query("get_connections(Connections)"))
        
        if query_results:
            conn_list = query_results[0]['Connections']
            for conn_data in conn_list:
                connections.append({
                    'from': int(conn_data[0]),
                    'to': int(conn_data[1]),
                    'direction': str(conn_data[2])
                })
        
        return connections
    
    def _decode_prolog_string(self, value) -> str:
        if isinstance(value, bytes):
            return value.decode('utf-8')
        s = str(value)
        if s.startswith("b'") and s.endswith("'"):
            return s[2:-1]
        if s.startswith('b"') and s.endswith('"'):
            return s[2:-1]
        return s
    
    def _get_all_room_contents(self) -> dict:
        """Dohvaća sadržaj svih soba iz Prologa."""
        contents = {}
        query_results = list(self.prolog.query("get_all_room_contents(Contents)"))
        
        if query_results:
            content_list = query_results[0]['Contents']
            for content_data in content_list:
                room_id = int(content_data[0])
                contents[room_id] = {
                    'description': self._decode_prolog_string(content_data[1]),
                    'enemies': [self._decode_prolog_string(e) for e in content_data[2]],
                    'items': [self._decode_prolog_string(i) for i in content_data[3]],
                    'gold': int(content_data[4])
                }
        
        return contents
    
    def get_room_content(self, room_id: int) -> dict:
        """Dohvaća sadržaj specifične sobe."""
        query = f"get_room_content({room_id}, Content)"
        query_results = list(self.prolog.query(query))
        
        if query_results:
            content = query_results[0]['Content']
            return {
                'description': str(content[0]),
                'enemies': [str(e) for e in content[1]],
                'items': [str(i) for i in content[2]],
                'gold': int(content[3])
            }
        return None
    
    def clear(self):
        """Briše trenutni dungeon iz Prologa."""
        list(self.prolog.query("clear_dungeon"))



