from pyswip import Prolog
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("Testiranje Prolog bridge-a...")
prolog = Prolog()
try:
    prolog_file = os.path.join("prolog", "dungeon_generator.pl").replace("\\", "/")
    print(f"Učitavam: {prolog_file}")
    prolog.consult(prolog_file)
    print("Consult uspješan.")
    
    list(prolog.query("clear_dungeon"))
    
    query = "generate_dungeon(42, 5)"
    print(f"Pokrećem query: {query}")
    
    res = list(prolog.query(query))
    print("Generiranje završeno (side-effects).")
    
    print("Dohvaćam sobe...")
    rooms_res = list(prolog.query("get_rooms(Rooms)"))
    if rooms_res:
        print(f"Sobe: {rooms_res[0]['Rooms']}")
    else:
        print("Nema soba!")

except Exception as e:
    print(f"Greška: {e}")
    import traceback
    traceback.print_exc()

