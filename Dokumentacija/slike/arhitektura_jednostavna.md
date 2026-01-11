```mermaid
flowchart LR
    subgraph Frontend["Python / PyGame"]
        main["main.py"]
        renderer["Vizualizacija"]
        player["Stanje Igrača"]
    end
    
    subgraph Backend["Prolog"]
        generator["dungeon_generator.pl"]
        grammar["Graf Gramatika"]
    end
    
    main --> renderer
    main --> player
    main <-->|"PySwip"| generator
    generator --> grammar
    
    generator -->|"Sobe, Veze, Sadržaj"| main
```

## Opis

**Python (Frontend)**
- Vizualizacija dungeona pomoću PyGame
- Upravljanje stanjem igrača (HP, inventar)
- Kontrola igre i korisničkog unosa

**Prolog (Backend)**  
- Generiranje strukture dungeona pomoću graf gramatike
- Ekspanzija soba prema pravilima prepisivanja
- Generiranje sadržaja soba (neprijatelji, predmeti)

**Komunikacija**
- Python poziva Prolog putem PySwip biblioteke
- Prolog vraća podatke o sobama, vezama i sadržaju
