%% DUNGEON GENERATOR - Graph Grammar Edition
%% Uses Graph Grammars and L-System concepts to generate dungeon layout.

:- module(dungeon_generator, [
    generate_dungeon/2,
    get_rooms/1,
    get_connections/1,
    get_room_types/1,
    get_room_content/2,
    get_all_room_contents/1,
    clear_dungeon/0
]).

:- use_module(library(random)).
:- use_module(library(lists)).
:- use_module(library(pairs)).

:- dynamic room/3.
:- dynamic room_type/2.
:- dynamic connected/3.
:- dynamic room_content/2.
:- dynamic claimed_pos/2.

%% PROBABILISTIC GRAPH GRAMMAR RULES
%% weighted_rule(ParentType, ChildType, Weight)

weighted_rule(start, combat, 60).
weighted_rule(start, event, 40).

weighted_rule(combat, combat, 50).
weighted_rule(combat, treasure, 30).
weighted_rule(combat, shop, 10).
weighted_rule(combat, event, 10).

weighted_rule(event, treasure, 40).
weighted_rule(event, empty, 30).
weighted_rule(event, combat, 30).

weighted_rule(empty, combat, 70).
weighted_rule(empty, event, 30).

weighted_rule(shop, combat, 100).

weighted_rule(treasure, boss, 60).
weighted_rule(treasure, combat, 40).

weighted_rule(boss, _, 0).

get_weighted_types(ParentType, SelectedTypes) :-
    findall(Type-Weight, (weighted_rule(ParentType, Type, Weight), Weight > 0), Pairs),
    (   Pairs = []
    ->  SelectedTypes = []
    ;   select_multiple_weighted(Pairs, 2, SelectedTypes)
    ).

select_multiple_weighted(_, 0, []) :- !.
select_multiple_weighted(Pairs, N, [Type|Rest]) :-
    N > 0,
    select_by_weight(Pairs, Type),
    N1 is N - 1,
    select_multiple_weighted(Pairs, N1, Rest).

select_by_weight(Pairs, Selected) :-
    pairs_keys_values(Pairs, Types, Weights),
    sum_list(Weights, Total),
    random(0, Total, R),
    pick_by_accumulated(Types, Weights, R, 0, Selected).

pick_by_accumulated([Type|_], [Weight|_], Target, Acc, Type) :-
    NewAcc is Acc + Weight,
    Target < NewAcc, !.
pick_by_accumulated([_|Types], [Weight|Weights], Target, Acc, Selected) :-
    NewAcc is Acc + Weight,
    pick_by_accumulated(Types, Weights, Target, NewAcc, Selected).

grammar_rule(Type, Children) :-
    get_weighted_types(Type, Children).

generate_dungeon(Seed, NumRooms) :-
    clear_dungeon,
    set_random(seed(Seed)),
    assertz(claimed_pos(0, 0)),
    assertz(room(1, 0, 0)),
    assertz(room_type(1, start)),

    catch(
        expand_dungeon([room(1, start, 0, 0)], 1, NumRooms, 0),
        Error,
        (print_message(error, Error), true)
    ),
    
    ensure_boss_room,
    findall(ID, room(ID, _, _), AllIDs),
    sort(AllIDs, UniqueIDs),
    maplist(generate_room_content, UniqueIDs),
    !.

ensure_boss_room :-
    (   room_type(_, boss)
    ->  true
    ;   findall(ID, (
            room_type(ID, Type), 
            Type \= start,
            findall(N, connected(ID, N, _), Neighbors),
            length(Neighbors, 1)
        ), LeafRooms),
        
        (   LeafRooms = [BossID|_]
        ->  retract(room_type(BossID, _)),
            assertz(room_type(BossID, boss))
        ;   room_type(BossID, Type), Type \= start,
            retract(room_type(BossID, _)),
            assertz(room_type(BossID, boss)),
            !
        )
    ).

expand_dungeon([], _, _, _) :- !.
expand_dungeon(_, Count, Max, _) :- Count >= Max, !.

expand_dungeon(_, _, _, Iterations) :- 
    Iterations > 500, 
    print_message(warning, 'Safety break: Exceeded 500 iterations!'), 
    !.

expand_dungeon([room(ID, Type, X, Y) | RestQueue], Count, Max, Iterations) :-
    NewIterations is Iterations + 1,

    (   grammar_rule(Type, NextTypes) 
    ->  ShuffledTypes = NextTypes
    ;   ShuffledTypes = []
    ),
    
    spawn_neighbors(ID, X, Y, ShuffledTypes, RestQueue, NewQueue, Count, NewCount, Max),
    expand_dungeon(NewQueue, NewCount, Max, NewIterations).

spawn_neighbors(_, _, _, [], Queue, Queue, Count, Count, _) :- !.
spawn_neighbors(_, _, _, _, Queue, Queue, Count, Count, Max) :- Count >= Max, !.

spawn_neighbors(ParentID, X, Y, [NextType|RestTypes], QueueIn, QueueOut, Count, FinalCount, Max) :-
    get_random_direction(DX, DY, Dir),
    NX is X + DX,
    NY is Y + DY,
    (   \+ claimed_pos(NX, NY)
    ->  NewCount is Count + 1,
        NewID = NewCount, 
        assertz(room(NewID, NX, NY)),
        assertz(room_type(NewID, NextType)),
        assertz(connected(ParentID, NewID, Dir)),
        assertz(claimed_pos(NX, NY)),
        opposite_dir_val(Dir, OppDir),
        assertz(connected(NewID, ParentID, OppDir)),
        NewQueueIn = [room(NewID, NextType, NX, NY) | QueueIn],
        spawn_neighbors(ParentID, X, Y, RestTypes, NewQueueIn, QueueOut, NewCount, FinalCount, Max)
    ;   spawn_neighbors(ParentID, X, Y, RestTypes, QueueIn, QueueOut, Count, FinalCount, Max)
    ).

get_random_direction(DX, DY, Dir) :-
    Directions = [[0,-1,north], [0,1,south], [1,0,east], [-1,0,west]],
    random_permutation(Directions, Shuffled),
    member([DX, DY, Dir], Shuffled).

opposite_dir_val(north, south).
opposite_dir_val(south, north).
opposite_dir_val(east, west).
opposite_dir_val(west, east).

generate_room_content(ID) :-
    room_type(ID, Type),
    generate_content_for_type(ID, Type).

generate_content_for_type(ID, start) :-
    assertz(room_content(ID, content(
        description("A quiet room. Your journey begins here."),
        enemies([]),
        items([torch, health_potion]),
        gold(0)
    ))).

generate_content_for_type(ID, boss) :-
    assertz(room_content(ID, content(
        description("A massive chamber filled with dread."),
        enemies([dragon]),
        items([ancient_crown]),
        gold(500)
    ))).

generate_content_for_type(ID, treasure) :-
    random(0, 100, R),
    (   R < 50 -> Item = magic_sword ; Item = heavy_armor ),
    assertz(room_content(ID, content(
        description("A glittering room full of riches!"),
        enemies([]),
        items([Item, large_health_potion]),
        gold(100)
    ))).

generate_content_for_type(ID, shop) :-
    assertz(room_content(ID, content(
        description("A merchant greets you from the shadows."),
        enemies([]),
        items([elixir, map]),
        gold(0)
    ))).

generate_content_for_type(ID, combat) :-
    random_member(Enemy, [goblin, orc, skeleton, slime]),
    assertz(room_content(ID, content(
        description("You hear growling from the shadows."),
        enemies([Enemy]),
        items([health_potion]),
        gold(10)
    ))).

generate_content_for_type(ID, event) :-
    assertz(room_content(ID, content(
        description("A strange statue stands in the center."),
        enemies([ghost]),
        items([mysterious_scroll]),
        gold(5)
    ))).

generate_content_for_type(ID, empty) :-
    assertz(room_content(ID, content(
        description("An empty, dusty room."),
        enemies([]),
        items([]),
        gold(1)
    ))).

generate_content_for_type(ID, _) :-
    generate_content_for_type(ID, empty).

get_rooms(Rooms) :-
    findall([ID, X, Y, Type], (room(ID, X, Y), room_type(ID, Type)), Rooms).

get_connections(Connections) :-
    findall([ID1, ID2, Dir], connected(ID1, ID2, Dir), Connections).

get_room_types(Types) :-
    findall([ID, Type], room_type(ID, Type), Types).

get_room_content(ID, [Desc, Enemies, Items, Gold]) :-
    room_content(ID, content(
        description(Desc),
        enemies(Enemies),
        items(Items),
        gold(Gold)
    )).

get_all_room_contents(Contents) :-
    findall([ID, Desc, Enemies, Items, Gold], (
        room_content(ID, content(
            description(Desc),
            enemies(Enemies),
            items(Items),
            gold(Gold)
        ))
    ), Contents).

clear_dungeon :-
    retractall(room(_, _, _)),
    retractall(connected(_, _, _)),
    retractall(room_type(_, _)),
    retractall(room_content(_, _)),
    retractall(claimed_pos(_, _)).