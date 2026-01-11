```mermaid
flowchart TB
    subgraph Python["Python (Frontend)"]
        direction TB
        main["main.py<br/>Game Loop"]
        renderer["renderer.py<br/>PyGame Vizualizacija"]
        player["player.py<br/>Stanje igrača"]
        bridge["prolog_bridge.py<br/>PySwip Sučelje"]
        
        main --> renderer
        main --> player
        main --> bridge
        renderer --> player
    end
    
    subgraph Prolog["Prolog (Backend)"]
        direction TB
        generator["dungeon_generator.pl"]
        
        subgraph Grammar["Gramatika Grafova"]
            rules["grammar_rule/2<br/>Pravila prepisivanja"]
            expand["expand_dungeon/4<br/>Algoritam ekspanzije"]
            spawn["spawn_neighbors/9<br/>Stvaranje soba"]
        end
        
        subgraph Content["Sadržaj Soba"]
            content["generate_room_content/1"]
            types["room_type/2"]
        end
        
        generator --> Grammar
        generator --> Content
        rules --> expand
        expand --> spawn
    end
    
    bridge <-->|"PySwip<br/>Query/Response"| generator
    
    subgraph Output["Izlaz"]
        rooms["Lista soba<br/>[ID, X, Y, Tip]"]
        connections["Veze<br/>[Od, Do, Smjer]"]
        contents["Sadržaj<br/>[Opis, Neprijatelji, Predmeti, Zlato]"]
    end
    
    generator --> rooms
    generator --> connections
    generator --> contents
    
    rooms --> bridge
    connections --> bridge
    contents --> bridge

    style Python fill:#3776ab,color:#fff
    style Prolog fill:#e34c26,color:#fff
    style Output fill:#2d5016,color:#fff
    style Grammar fill:#ff6b6b,color:#000
    style Content fill:#feca57,color:#000
```

## Objašnjenje arhitekture

### Python (Frontend)
- **main.py**: Glavna petlja igre, upravlja događajima i poziva renderer
- **renderer.py**: PyGame vizualizacija dungeona, soba i igrača
- **player.py**: Stanje igrača (HP, inventar, zlato)
- **prolog_bridge.py**: Most između Pythona i Prologa korištenjem PySwip biblioteke

### Prolog (Backend)
- **dungeon_generator.pl**: Glavni modul za generiranje
  - `grammar_rule/2`: Definira pravila gramatike grafova
  - `expand_dungeon/4`: BFS algoritam za ekspanziju grafa
  - `spawn_neighbors/9`: Stvara nove sobe na gridu
  - `generate_room_content/1`: Generira sadržaj za svaku sobu

### Komunikacija
Python poziva Prolog putem PySwip biblioteke. Prolog vraća:
1. **Sobe**: `[ID, X, Y, Tip]`
2. **Veze**: `[Od, Do, Smjer]`
3. **Sadržaj**: `[Opis, Neprijatelji, Predmeti, Zlato]`
