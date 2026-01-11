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

:- use_module(library(random)).  % CRITICAL: Needed for random_permutation, random_member
:- use_module(library(lists)).   % Needed for append, member

%% Dynamic predicates



%% GRAPH GRAMMAR RULES
%% Defines how room types expand into other room types.


grammar_rule(start,    [combat, event]).
grammar_rule(combat,   [combat, treasure]).
grammar_rule(event,    [treasure, empty]).
grammar_rule(empty,    [combat]).
grammar_rule(shop,     [combat]).
grammar_rule(treasure, [boss]).        
grammar_rule(boss,     []).            


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
    
    % 3. Ensure boss room existence
    ensure_boss_room,

    % 4. Generate content for all created rooms
    findall(ID, room(ID, _, _), AllIDs),
    sort(AllIDs, UniqueIDs),  % Remove duplicates
    maplist(generate_room_content, UniqueIDs),
    !.

ensure_boss_room :-
    (   room_type(_, boss)
    ->  true  % Boss already exists
    ;   % Find a leaf node (only 1 connection) that is not start
        findall(ID, (
            room_type(ID, Type), 
            Type \= start,
            findall(N, connected(ID, N, _), Neighbors),
            length(Neighbors, 1)
        ), LeafRooms),
        
        (   LeafRooms = [BossID|_]  % Pick first leaf
        ->  retract(room_type(BossID, _)),
            assertz(room_type(BossID, boss))
        ;   % Fallback: Pick ANY non-start room
            room_type(BossID, Type), Type \= start,
            retract(room_type(BossID, _)),
            assertz(room_type(BossID, boss)),
            !
        )
    ).

%% expand_dungeon(Queue, CurrentCount, MaxRooms, Iterations)
expand_dungeon([], _, _, _) :- !.
expand_dungeon(_, Count, Max, _) :- Count >= Max, !.
% Safety break: Stop after 500 iterations
expand_dungeon(_, _, _, Iterations) :- 
    Iterations > 500, 
    print_message(warning, 'Safety break: Exceeded 500 iterations!'), 
    !.

expand_dungeon([room(ID, Type, X, Y) | RestQueue], Count, Max, Iterations) :-
    NewIterations is Iterations + 1,

    % Get production rule for this type
    (   grammar_rule(Type, NextTypes) 
    ->  ShuffledTypes = NextTypes % random_permutation(NextTypes, ShuffledTypes) 
    ;   ShuffledTypes = []
    ),
    
    % Try to spawn neighbors
    spawn_neighbors(ID, X, Y, ShuffledTypes, RestQueue, NewQueue, Count, NewCount, Max),
    
    % Continue with new queue
    expand_dungeon(NewQueue, NewCount, Max, NewIterations).

%% spawn_neighbors(...)
spawn_neighbors(_, _, _, [], Queue, Queue, Count, Count, _) :- !.
spawn_neighbors(_, _, _, _, Queue, Queue, Count, Count, Max) :- Count >= Max, !.

spawn_neighbors(ParentID, X, Y, [NextType|RestTypes], QueueIn, QueueOut, Count, FinalCount, Max) :-
    % Get random available direction
    get_random_direction(DX, DY, Dir),
    NX is X + DX,
    NY is Y + DY,
    
    % Check collision
    (   \+ claimed_pos(NX, NY)
    ->  % Valid spot! Create room
        NewCount is Count + 1,
        NewID = NewCount, 
        
        assertz(room(NewID, NX, NY)),
        assertz(room_type(NewID, NextType)),
        assertz(connected(ParentID, NewID, Dir)),
        assertz(claimed_pos(NX, NY)),
        
        % Add reciprocal connection
        opposite_dir_val(Dir, OppDir),
        assertz(connected(NewID, ParentID, OppDir)),
        
        NewQueueIn = [room(NewID, NextType, NX, NY) | QueueIn],
        spawn_neighbors(ParentID, X, Y, RestTypes, NewQueueIn, QueueOut, NewCount, FinalCount, Max)
    ;   % Spot taken
        spawn_neighbors(ParentID, X, Y, RestTypes, QueueIn, QueueOut, Count, FinalCount, Max)
    ).

%% Utilities
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

% Start Room
generate_content_for_type(ID, start) :-
    assertz(room_content(ID, content(
        description("A quiet room. Your journey begins here."),
        enemies([]),
        items([torch, health_potion]),
        gold(0)
    ))).

% Boss Room
generate_content_for_type(ID, boss) :-
    assertz(room_content(ID, content(
        description("A massive chamber filled with dread."),
        enemies([dragon]),
        items([ancient_crown]),
        gold(500)
    ))).

% Treasury
generate_content_for_type(ID, treasure) :-
    random(0, 100, R),
    (   R < 50 -> Item = magic_sword ; Item = heavy_armor ),
    assertz(room_content(ID, content(
        description("A glittering room full of riches!"),
        enemies([]),
        items([Item, large_health_potion]),
        gold(100)
    ))).

% Shop
generate_content_for_type(ID, shop) :-
    assertz(room_content(ID, content(
        description("A merchant greets you from the shadows."),
        enemies([]),
        items([elixir, map]),
        gold(0)
    ))).

% Combat (Standard)
generate_content_for_type(ID, combat) :-
    random_member(Enemy, [goblin, orc, skeleton, slime]),
    assertz(room_content(ID, content(
        description("You hear growling from the shadows."),
        enemies([Enemy]),
        items([health_potion]),
        gold(10)
    ))).

% Event
generate_content_for_type(ID, event) :-
    assertz(room_content(ID, content(
        description("A strange statue stands in the center."),
        enemies([ghost]),
        items([mysterious_scroll]),
        gold(5)
    ))).

% Empty
generate_content_for_type(ID, empty) :-
    assertz(room_content(ID, content(
        description("An empty, dusty room."),
        enemies([]),
        items([]),
        gold(1)
    ))).

% Fallback
generate_content_for_type(ID, _) :-
    generate_content_for_type(ID, empty).


get_rooms(Rooms) :-
    % Merge room position and type into a single list [ID, X, Y, Type]
    findall([ID, X, Y, Type], (room(ID, X, Y), room_type(ID, Type)), Rooms).

get_connections(Connections) :-
    % Return connections as lists [From, To, Direction]
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

collect_result(Result) :-
    get_rooms(Rooms),
    get_connections(Connections),
    get_room_types(Types),
    Result = [rooms(Rooms), connections(Connections), types(Types)].

clear_dungeon :-
    retractall(room(_, _, _)),
    retractall(connected(_, _, _)),
    retractall(room_type(_, _)),
    retractall(room_content(_, _)),
    retractall(claimed_pos(_, _)).