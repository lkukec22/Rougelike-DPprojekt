# Roguelike Dungeon Generator - Projektna Dokumentacija

## Sadržaj

1. [Uvod](#1-uvod)
2. [Teorijski temelji](#2-teorijski-temelji)
3. [Arhitektura sustava](#3-arhitektura-sustava)
4. [Prolog implementacija](#4-prolog-implementacija)
5. [Python-Prolog sučelje](#5-python-prolog-sučelje)
6. [Pygame vizualizacija](#6-pygame-vizualizacija)
7. [Pokretanje aplikacije](#7-pokretanje-aplikacije)
8. [Zaključak](#8-zaključak)
9. [Literatura](#9-literatura)

---

## 1. Uvod

### 1.1 Motivacija

Proceduralno generiranje sadržaja (PCG - Procedural Content Generation) ključna je tehnika u razvoju modernih igara. Umjesto ručnog dizajniranja svakog levela, koriste se algoritmi koji automatski stvaraju sadržaj prema zadanim pravilima.

Ovaj projekt demonstrira **deklarativni pristup** generiranju dungeona za roguelike igru. Za razliku od imperativnog pristupa gdje programer specificira **kako** generirati dungeon korak po korak, deklarativni pristup omogućuje definiranje **što** želimo postići (constraints/ograničenja), a sustav sam pronalazi rješenje.

### 1.2 Cilj projekta

Cilj je implementirati generator dungeona koji:
- Koristi **Prolog** za deklarativno definiranje pravila i ograničenja
- Koristi **PySwip** za komunikaciju između Pythona i Prologa
- Koristi **Pygame** za vizualizaciju generiranog dungeona
- Demonstrira primjenu logičkog programiranja u domeni računalnih igara

### 1.3 Korištene tehnologije

| Tehnologija | Verzija | Namjena |
|-------------|---------|---------|
| SWI-Prolog | 9.x | Logičko programiranje, constraint solving |
| Python | 3.10+ | Glavna aplikacija |
| PySwip | 0.2.11 | Python-Prolog bridge |
| Pygame | 2.x | Grafičko sučelje i vizualizacija |

---

## 2. Teorijski temelji

### 2.1 Logičko programiranje

Logičko programiranje paradigma je programiranja temeljena na formalnoj logici. Program se sastoji od:
- **Činjenica** (facts) - tvrdnje koje su bezuvjetno istinite
- **Pravila** (rules) - uvjetne tvrdnje oblika "ako... onda..."
- **Upita** (queries) - pitanja koja postavljamo sustavu

#### 2.1.1 Hornove klauzule

Prolog koristi Hornove klauzule - podskup logike prvog reda. Opći oblik:

```
H :- B1, B2, ..., Bn.
```

Što znači: "H je istinito ako su B1 i B2 i ... i Bn istiniti."

#### 2.1.2 Unifikacija

Unifikacija je proces pronalaženja supstitucije varijabli koja čini dva izraza identičnima.

Primjer:
```prolog
room(X, 0, 0) = room(1, 0, 0)
% Unifikacija uspijeva s X = 1
```

#### 2.1.3 Backtracking

Prolog koristi backtracking za sistematsko pretraživanje prostora rješenja. Ako jedno rješenje ne zadovoljava sve uvjete, Prolog se vraća i pokušava alternativna rješenja.

### 2.2 Predikatni račun - Formalizacija

Formalna specifikacija predikata korištenih u projektu:

#### Osnovni predikati

| Predikat | Formalna definicija | Značenje |
|----------|---------------------|----------|
| `room(id, x, y)` | `room: ℕ × ℤ × ℤ` | Soba s ID-om na koordinatama (x,y) |
| `connected(a, b, dir)` | `connected: ℕ × ℕ × Dir` | Soba a povezana sa sobom b u smjeru dir |
| `room_type(id, type)` | `room_type: ℕ × Type` | Soba id ima tip type |

Gdje je:
- `Dir = {north, south, east, west}`
- `Type = {start, boss, combat, treasure, shop, event}`

#### Pravila u predikatnom računu

**Pravilo 1: Jedinstvenost start sobe**
```
∃!s ∈ Rooms: room_type(s, start)
```
Postoji točno jedna soba s tipom "start".

**Pravilo 2: Jedinstvenost boss sobe**
```
∃!b ∈ Rooms: room_type(b, boss)
```
Postoji točno jedna soba s tipom "boss".

**Pravilo 3: Povezanost grafa**
```
∀r₁, r₂ ∈ Rooms: path(r₁, r₂)
```
Za svake dvije sobe postoji put između njih.

**Pravilo 4: Minimalna udaljenost**
```
∀s,b: room_type(s, start) ∧ room_type(b, boss) → distance(s, b) ≥ 2
```
Udaljenost između start i boss sobe mora biti barem 2.

**Pravilo 5: Treasure u dead-end sobama**
```
∀r: room_type(r, treasure) → degree(r) = 1
```
Treasure sobe imaju točno jednu vezu (dead-end).

### 2.3 Constraint Satisfaction Problem (CSP)

Generator dungeona može se formalizirati kao CSP:

- **Varijable**: `X = {room₁_type, room₂_type, ..., roomₙ_type}`
- **Domene**: `D = {start, boss, combat, treasure, shop, event}`
- **Ograničenja**: `C = {C₁, C₂, ..., Cₘ}` (pravila iznad)

Prolog koristi backtracking za pronalaženje dodjele vrijednosti varijablama koja zadovoljava sva ograničenja.

### 2.4 Algoritmi

#### 2.4.1 Random Walk algoritam

Za generiranje topologije dungeona koristi se Random Walk algoritam:

```
ALGORITAM: RandomWalk(n)
ULAZ: n - broj soba
IZLAZ: Graf soba

1. Kreiraj početnu sobu na koordinatama (0, 0)
2. visited ← {(0, 0)}
3. Za i = 2 do n:
   a. Odaberi nasumičnu postojeću sobu S
   b. Odaberi nasumičan smjer D ∈ {N, S, E, W}
   c. Izračunaj nove koordinate (x', y') = S + offset(D)
   d. Ako (x', y') ∉ visited:
      - Kreiraj novu sobu na (x', y')
      - Poveži S s novom sobom
      - visited ← visited ∪ {(x', y')}
   e. Inače: ponovi od koraka b
4. Vrati graf
```

#### 2.4.2 BFS za računanje udaljenosti

Breadth-First Search koristi se za računanje udaljenosti između soba:

```
ALGORITAM: BFS_Distance(start, end)
ULAZ: start, end - ID-ovi soba
IZLAZ: udaljenost (broj koraka)

1. queue ← [[start]]
2. visited ← {}
3. Dok queue nije prazan:
   a. path ← queue.dequeue()
   b. current ← path[0]
   c. Ako current = end:
      - Vrati length(path) - 1
   d. Za svaki neighbor od current:
      - Ako neighbor ∉ visited:
        - queue.enqueue([neighbor] + path)
        - visited ← visited ∪ {neighbor}
4. Vrati ∞ (put ne postoji)
```

---

## 3. Arhitektura sustava

### 3.1 Pregled arhitekture

```
┌─────────────────────────────────────────────────────────────┐
│                      KORISNIK                                │
│                    (tipkovnica)                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   PYGAME RENDERER                            │
│                     (main.py)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Game Loop   │  │ Dungeon     │  │ Event Handler       │  │
│  │             │  │ Renderer    │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   PROLOG BRIDGE                              │
│                  (prolog_bridge.py)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ PySwip      │  │ Query       │  │ Result Parser       │  │
│  │ Interface   │  │ Builder     │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   PROLOG ENGINE                              │
│               (dungeon_generator.pl)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Room        │  │ Constraint  │  │ Validation          │  │
│  │ Generator   │  │ Solver      │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Tok podataka

1. **Inicijalizacija**: Python učitava Prolog modul putem PySwip
2. **Generacija**: Python poziva `generate_dungeon/3` s parametrima (seed, broj soba)
3. **Prolog procesiranje**:
   - Random Walk generira topologiju
   - Constraint solver dodjeljuje tipove soba
   - Validacija provjerava sva pravila
4. **Povratak**: Prolog vraća strukturu dungeona
5. **Parsiranje**: Python parsira Prolog strukturu u dict
6. **Vizualizacija**: Pygame renderira dungeon na ekran

### 3.3 Struktura projekta

```
Rougelike/
├── prolog/
│   └── dungeon_generator.pl    # Prolog modul (~550 linija)
│
├── src/
│   ├── main.py                 # Glavna aplikacija (~95 linija)
│   ├── player.py               # Player klasa i gameplay (~55 linija)
│   ├── renderer.py             # Dungeon renderer (~460 linija)
│   └── prolog_bridge.py        # PySwip sučelje (~200 linija)
│
├── predlozak/                  # LaTeX predložak
│   ├── Rad.tex
│   └── llncs.cls
│
├── dokumentacija.md            # Ovaj dokument
├── README.md                   # Kratke upute
└── .gitignore                  # Git ignore pravila
```

---

## 4. Prolog implementacija

### 4.1 Struktura modula

Datoteka: `prolog/dungeon_generator.pl`

```prolog
:- module(dungeon_generator, [
    generate_dungeon/3,
    get_rooms/1,
    get_connections/1,
    get_room_types/1,
    get_room_content/2,
    get_room_content/2,
    get_all_room_contents/1,
    clear_dungeon/0
]).
```

### 4.2 Dinamički predikati

```prolog
:- dynamic room/3.           % room(ID, X, Y)
:- dynamic connected/3.      % connected(RoomA, RoomB, Direction)
:- dynamic room_type/2.      % room_type(RoomID, Type)
:- dynamic room_content/2.   % room_content(RoomID, Content)
:- dynamic lsystem_rule/2.   % lsystem_rule(Symbol, Replacement)
```

Dinamički predikati omogućuju dodavanje i brisanje činjenica za vrijeme izvršavanja.

### 4.3 Glavni predikat (Graph Grammar Flow)

Naša implementacija koristi **gramatike grafova** kao glavni mehanizam generiranja. Umjesto da prvo generiramo sobe pa im dodijelimo tipove (kao u CSP pristupima), ovdje generiramo sobe *i* tipove istovremeno rekurzivnom ekspanzijom pravila.

```prolog
generate_dungeon(Seed, NumRooms, Result) :-
    clear_dungeon,
    set_random(seed(Seed)),
    
    % 1. Početno stanje grafa: samo 'start' čvor
    assertz(claimed_pos(0, 0)),
    assertz(room(1, 0, 0)),
    assertz(room_type(1, start)),
    
    % 2. Rekurzivna ekspanzija grafa pomoću gramatičkih pravila
    expand_dungeon([room(1, start, 0, 0)], 1, NumRooms),
    
    % 3. Generiranje internog sadržaja čvorova
    findall(ID, room(ID, _, _), IDs),
    maplist(generate_room_content, IDs),
    
    collect_result(Result).
```

### 4.4 Gramatička pravila (Production Rules)

Sustav koristi produkcijska pravila oblika `Tip -> [MogućiSljedećiTipovi]` s vjerojatnostima. Ovo definira topologiju grafa.

```prolog
%% grammar_rule(CurrentType, Probability, PossibleNextList)
grammar_rule(start,    1.0, [combat, event]).
grammar_rule(combat,   0.6, [combat, treasure]).
grammar_rule(combat,   0.4, [shop, empty]).
grammar_rule(event,    0.5, [combat, empty]).
grammar_rule(event,    0.5, [treasure]).
grammar_rule(empty,    0.7, [combat]).
grammar_rule(treasure, 1.0, [boss]).        % Treasure vodi do bossa
grammar_rule(boss,     1.0, []).            % Boss je terminalni simbol
```

### 4.5 Algoritam ekspanzije

Algoritam koristi red (queue) za BFS ekspanziju grafa:

1.  Uzmimo sobu s početka reda.
2.  Dohvatimo odgovarajuće gramatičko pravilo (`grammar_rule`).
3.  Za svaki tip sobe iz desne strane pravila (`PossibleNext`):
    *   Odredi nasumičan slobodan smjer (gore, dolje, lijevo, desno).
    *   Ako je mjesto slobodno, instanciraj novu sobu tog tipa.
    *   Poveži staru i novu sobu (dodaj brid u graf).
    *   Dodaj novu sobu u red za daljnju ekspanziju.

```prolog
spawn_neighbors(ParentID, X, Y, [NextType|Rest], QueueIn, QueueOut, ...) :-
    random_direction(DX, DY, Dir),
    NX is X + DX, NY is Y + DY,
    
    (   \+ claimed_pos(NX, NY)
    ->  % Validna ekspanzija gramatike
        assertz(room(NewID, NX, NY)),
        assertz(room_type(NewID, NextType)),
        assertz(connected(ParentID, NewID, Dir)),
        ...
    ;   % Sudar (kolizija), pokušaj drugo pravilo
        spawn_neighbors(...)
    ).
```

### 4.7 BFS algoritam

```prolog
bfs_distance(Start, End, Distance) :-
    bfs_search([[Start]], End, [], Distance).

bfs_search([[End|Path]|_], End, _, Distance) :-
    length(Path, Distance), !.

bfs_search([[Current|Path]|Queue], End, Visited, Distance) :-
    findall([Next, Current|Path], (
        connected(Current, Next, _),
        \+ member(Next, Visited),
        \+ member(Next, [Current|Path])
    ), NewPaths),
    append(Queue, NewPaths, NewQueue),
    bfs_search(NewQueue, End, [Current|Visited], Distance).
```

### 4.8 Generiranje sadržaja soba

Svaka soba dobiva generirani sadržaj ovisno o svom tipu. Koristi se predikat `room_content/2`.

#### Struktura sadržaja

```prolog
:- dynamic room_content/2.   % room_content(RoomID, Content)

% Struktura Content:
content(
    description(Desc),    % Tekstualni opis sobe
    enemies(EnemyList),   % Lista neprijatelja
    items(ItemList),      % Lista predmeta
    gold(Amount)          % Količina zlata
)
```

#### Primjer: Combat soba

```prolog
generate_content_for_type(RoomID, combat) :-
    random_between(1, 3, NumEnemies),
    generate_enemy_list(NumEnemies, Enemies),
    random_between(5, 25, Gold),
    random_member(Item, [nista, zdravlje_mala, strijele]),
    (Item = nista -> Items = [] ; Items = [Item]),
    random_member(Desc, [
        "Cujes korake u mraku...",
        "Neprijatelji te okruzuju!",
        "Sjene se pomicu oko tebe."
    ]),
    assertz(room_content(RoomID, content(
        description(Desc),
        enemies(Enemies),
        items(Items),
        gold(Gold)
    ))).
```

#### Sadržaj po tipu sobe

| Tip sobe | Neprijatelji | Predmeti | Zlato |
|----------|--------------|----------|-------|
| start | - | baklja | 0 |
| boss | zmaj/demon/lich/golem | legendarni_mac | 100-200 |
| combat | 1-3 (goblin/orc/skeleton...) | zdravlje/strijele | 5-25 |
| treasure | - | oklop/prsten/eliksir | 30-75 |
| shop | - | razni (za kupnju) | 0 |
| event | - | možda kljuc/zdravlje | 0 |

#### Generiranje liste neprijatelja

```prolog
generate_enemy_list(0, []) :- !.
generate_enemy_list(N, [Enemy|Rest]) :-
    N > 0,
    random_member(Enemy, [goblin, orc, skeleton, slime, bat, spider]),
    N1 is N - 1,
    generate_enemy_list(N1, Rest).
```

---

## 5. Python-Prolog sučelje

### 5.1 Klasa PrologBridge

Datoteka: `src/prolog_bridge.py`

```python
class PrologBridge:
    """Bridge klasa za komunikaciju između Pythona i Prologa."""
    
    def __init__(self):
        self.prolog = Prolog()
        self._load_prolog_files()
    
    def _load_prolog_files(self):
        """Učitava Prolog datoteke."""
        current_dir = Path(__file__).parent.parent
        prolog_dir = current_dir / "prolog"
        generator_path = prolog_dir / "dungeon_generator.pl"
        
        # PySwip zahtijeva forward slasheve
        path_str = str(generator_path).replace("\\", "/")
        self.prolog.consult(path_str)
```

### 5.2 Generiranje dungeona

```python
def generate_dungeon(self, seed: int = 42, num_rooms: int = 7) -> dict:
    """
    Generira dungeon s danim parametrima.
    
    Returns:
        dict sa strukturom:
        {
            'rooms': [{'id': 1, 'x': 0, 'y': 0, 'type': 'start'}, ...],
            'connections': [{'from': 1, 'to': 2, 'direction': 'east'}, ...]
        }
    """
    query = f"generate_dungeon({seed}, {num_rooms}, Result)"
    results = list(self.prolog.query(query))
    
    if not results:
        raise RuntimeError("Prolog nije uspio generirati dungeon")
    
    return self._parse_dungeon_result(results[0]['Result'])
```

### 5.3 Dohvaćanje podataka

```python
def _get_rooms(self) -> list:
    """Dohvaća listu soba iz Prologa."""
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
```

---

## 6. Pygame vizualizacija

### 6.1 Klasa DungeonRenderer

Datoteka: `src/main.py`

```python
class DungeonRenderer:
    """Klasa za renderiranje dungeona na ekran."""
    
    def __init__(self, screen, dungeon_data):
        self.screen = screen
        self.dungeon = dungeon_data
        self._calculate_offset()  # Centriraj dungeon
        self.current_room_id = self._find_start_room()
```

### 6.2 Boje tipova soba

```python
ROOM_COLORS = {
    'start': (50, 205, 50),      # Zelena
    'boss': (220, 20, 60),       # Crvena
    'combat': (255, 140, 0),     # Narančasta
    'treasure': (255, 215, 0),   # Zlatna
    'shop': (65, 105, 225),      # Plava
    'event': (148, 0, 211),      # Ljubičasta
    'empty': (128, 128, 128),    # Siva
}
```

### 6.3 Renderiranje soba

```python
def _render_rooms(self):
    """Renderira sve sobe."""
    for room in self.dungeon['rooms']:
        x, y = self._grid_to_screen(room['x'], room['y'])
        color = ROOM_COLORS.get(room['type'], ROOM_COLORS['empty'])
        
        # Pravokutnik sobe
        rect = pygame.Rect(x, y, ROOM_SIZE, ROOM_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, COLOR_TEXT, rect, 2)
        
        # ID sobe
        id_text = self.font.render(str(room['id']), True, (0, 0, 0))
        text_rect = id_text.get_rect(center=(x + ROOM_SIZE//2, y + ROOM_SIZE//2))
        self.screen.blit(id_text, text_rect)
```

### 6.4 Kretanje igrača

```python
def move_player(self, direction):
    """Pomiče igrača u zadanom smjeru ako postoji veza."""
    connected = self._get_connected_rooms(self.current_room_id)
    for room_id, conn_dir in connected:
        if conn_dir == direction:
            self.current_room_id = room_id
            return True
    return False
```

### 6.5 Glavna petlja

```python
def run(self):
    """Glavna petlja igre."""
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_w, pygame.K_UP):
                    self.renderer.move_player('north')
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    self.renderer.move_player('south')
                elif event.key == pygame.K_r:
                    self.seed += 1
                    self._generate_new_dungeon()
        
        self.renderer.render()
        pygame.display.flip()
        self.clock.tick(60)
```

---


---

## 7. Pokretanje aplikacije

### 7.1 Preduvjeti

1. **SWI-Prolog** instaliran i u PATH
   - Download: https://www.swi-prolog.org/download/stable

2. **Python paketi**:
```bash
pip install pyswip pygame
```

### 7.2 Pokretanje

```bash
cd src
python main.py
```

### 7.3 Kontrole

| Tipka | Akcija |
|-------|--------|
| W / ↑ | Kretanje gore (north) |
| S / ↓ | Kretanje dolje (south) |
| A / ← | Kretanje lijevo (west) |
| D / → | Kretanje desno (east) |
| H | Koristi health potion |
| R | Regeneriraj dungeon (novi seed) |
| ESC | Izlaz iz aplikacije |

### 7.4 Gameplay sustav

Igra uključuje jednostavan gameplay sustav:

**Player statistike:**
- **HP**: 100 (maksimalno)
- **Gold**: Skuplja se u sobama
- **Inventory**: Health potioni za liječenje

**Combat sustav:**
- Automatska borba pri ulasku u sobu
- Svaki neprijatelj nanosi štetu (goblin=5, orc=10, dragon=30...)
- Soba se "čisti" - neprijatelji nestaju

**Predmeti:**
| Predmet | Efekt |
|---------|-------|
| health_potion | +25 HP |
| large_health_potion | +50 HP |
| elixir | +100 HP |

**Uvjeti pobjede/poraza:**
- **Victory**: Pobijedi bossa i preživi
- **Game Over**: HP padne na 0

### 7.5 Primjer izlaza

```
============================================================
ROGUELIKE DUNGEON GENERATOR
Prolog + PySwip + Pygame
============================================================
Initializing Prolog bridge...
[PrologBridge] Loaded: dungeon_generator.pl

Generating dungeon (seed=42)...
Generated 7 rooms.
```

---

## 8. Zaključak

### 8.1 Postignuća

Projekt uspješno demonstrira:
- Primjenu **logičkog programiranja** u domeni računalnih igara
- **Deklarativni pristup** generiranju sadržaja (dungeon, room content)
- Integraciju **Prologa s Pythonom** putem PySwip
- Vizualizaciju generiranog sadržaja pomoću **Pygame**
- **Gameplay sustav** s HP, borbom i predmetima

### 8.2 Implementirane funkcionalnosti

1. **Dungeon generacija**: Random Walk algoritam s constraint validacijom
2. **Room content**: Prolog generira neprijatelje, predmete i opise
3. **Combat sustav**: Automatska borba s damage sustavom
4. **Inventory sustav**: Health potioni za liječenje
5. **Victory/Game Over**: Uvjeti pobjede i poraza

### 8.3 Prednosti deklarativnog pristupa

1. **Čitljivost**: Pravila su intuitivna i lako se mijenjaju
2. **Proširivost**: Dodavanje novih constrainta je trivijalno
3. **Odvojenost logike**: Generacija je odvojena od vizualizacije
4. **Formalizacija**: Pravila se mogu formalno verificirati

### 8.4 Nedostaci

1. **Performanse**: Prolog je sporiji od imperativnih jezika
2. **Debugging**: Teže pronalaženje grešaka u Prolog kodu
3. **Integracija**: PySwip može biti nezgodan za instalaciju

### 8.5 Mogući nastavak

- Implementacija lock-and-key mehanike
- Dinamičko podešavanje težine
- Turn-based combat sustav
- Vizualni prikaz neprijatelja (sprites)

---

## 9. Literatura

[1] Shaker, N., Togelius, J., & Nelson, M. J. (2016). *Procedural Content Generation in Games*. Springer.

[2] Smith, A. M., & Mateas, M. (2011). Answer Set Programming for Procedural Content Generation: A Design Space Approach. *IEEE Transactions on Computational Intelligence and AI in Games*, 3(3), 187-200.

[3] Smith, G., Whitehead, J., & Mateas, M. (2010). Tanagra: A Mixed-Initiative Level Design Tool. *Proceedings of the Fifth International Conference on the Foundations of Digital Games*, 209-216.

[4] Clocksin, W. F., & Mellish, C. S. (2003). *Programming in Prolog* (5th ed.). Springer.

[5] SWI-Prolog Documentation. https://www.swi-prolog.org/pldoc/

[6] PySwip Documentation. https://github.com/yuce/pyswip

---

*Dokumentacija generirana: 11. siječnja 2026.*
