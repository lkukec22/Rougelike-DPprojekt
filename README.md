# Roguelike Dungeon Generator

Deklarativni generator dungeona za roguelike igru koristeći **Prolog** za constraint solving i **Pygame** za vizualizaciju.

## 🎯 Opis projekta

Ovaj projekt demonstrira upotrebu deklarativnog programiranja (Prolog) za proceduralno generiranje sadržaja u igrama. Umjesto imperativnog pristupa, definiramo **što** želimo (constrainte), a Prolog sam pronalazi rješenje.

## 🛠️ Tehnologije

- **SWI-Prolog** - Logičko programiranje, constraint solving
- **PySwip** - Python-Prolog bridge
- **Pygame** - Vizualizacija i gameplay

## 📁 Struktura projekta

```
Rougelike/
├── prolog/
│   └── dungeon_generator.pl   # Prolog generator s constraintima
├── src/
│   ├── main.py                # Pygame aplikacija
│   └── prolog_bridge.py       # PySwip sučelje
├── predlozak/                 # LaTeX dokumentacija
└── README.md
```

## 🚀 Pokretanje

### Preduvjeti

```bash
# Instaliraj SWI-Prolog (mora biti u PATH)
# https://www.swi-prolog.org/download/stable

# Instaliraj Python pakete
pip install pyswip pygame
```

### Pokretanje aplikacije

```bash
cd src
python main.py
```

## 🎮 Kontrole

| Tipka | Akcija |
|-------|--------|
| W / ↑ | Gore (North) |
| S / ↓ | Dolje (South) |
| A / ← | Lijevo (West) |
| D / → | Desno (East) |
| R | Regeneriraj dungeon |
| ESC | Izlaz |

## 🧠 Prolog predikati

### Glavni predikati

| Predikat | Opis |
|----------|------|
| `generate_dungeon/3` | Generira dungeon (Seed, NumRooms, Result) |
| `room/3` | Definicija sobe (ID, X, Y) |
| `connected/3` | Veza između soba (From, To, Direction) |
| `room_type/2` | Tip sobe (RoomID, Type) |

### Constraint pravila

1. **Točno jedna start soba**
2. **Točno jedna boss soba**
3. **Postoji put od start do boss**
4. **Minimalna udaljenost start-boss ≥ 2**
5. **Treasure sobe su u dead-end pozicijama**

## 📊 Tipovi soba

| Tip | Boja | Opis |
|-----|------|------|
| start | 🟢 Zelena | Početna soba |
| boss | 🔴 Crvena | Boss soba |
| combat | 🟠 Narančasta | Borbena soba |
| treasure | 🟡 Zlatna | Soba s blagom |
| shop | 🔵 Plava | Trgovina |
| event | 🟣 Ljubičasta | Event soba |

## 📝 Licenca

GPL-3.0
