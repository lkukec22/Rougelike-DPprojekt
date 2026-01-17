%% DUNGEON GENERATOR TESTS
%% Unit testovi za dungeon_generator.pl
%% Pokreni s: swipl -s tests/test_dungeon_generator.pl -g run_all_tests -t halt

:- use_module(library(plunit)).

%% Učitaj dungeon generator - koristimo consult umjesto use_module
:- consult('../prolog/dungeon_generator').

%% ============================================
%% TEST SUITE: Grammar Rules
%% ============================================

:- begin_tests(grammar_rules).

test(start_rule_exists) :-
    dungeon_generator:grammar_rule(start, Children),
    is_list(Children).

test(boss_is_terminal) :-
    dungeon_generator:grammar_rule(boss, Children),
    Children = [].

test(combat_rule_exists) :-
    dungeon_generator:grammar_rule(combat, Children),
    is_list(Children),
    length(Children, L),
    L > 0.

:- end_tests(grammar_rules).

%% ============================================
%% TEST SUITE: Dungeon Generation
%% ============================================

:- begin_tests(dungeon_generation).

test(generate_creates_rooms) :-
    dungeon_generator:clear_dungeon,
    dungeon_generator:generate_dungeon(42, 5),
    dungeon_generator:get_rooms(Rooms),
    length(Rooms, N),
    N > 0.

test(generate_creates_connections) :-
    dungeon_generator:clear_dungeon,
    dungeon_generator:generate_dungeon(123, 5),
    dungeon_generator:get_connections(Connections),
    length(Connections, N),
    N > 0.

test(start_room_always_exists) :-
    dungeon_generator:clear_dungeon,
    dungeon_generator:generate_dungeon(456, 5),
    dungeon_generator:get_room_types(Types),
    member([_, start], Types).

test(clear_dungeon_works) :-
    dungeon_generator:generate_dungeon(789, 5),
    dungeon_generator:clear_dungeon,
    dungeon_generator:get_rooms(Rooms),
    Rooms = [].

:- end_tests(dungeon_generation).

%% ============================================
%% TEST SUITE: Room Content
%% ============================================

:- begin_tests(room_content).

test(rooms_have_content) :-
    dungeon_generator:clear_dungeon,
    dungeon_generator:generate_dungeon(101, 5),
    dungeon_generator:get_all_room_contents(Contents),
    length(Contents, N),
    N > 0.

:- end_tests(room_content).

%% ============================================
%% TEST SUITE: Direction Utilities
%% ============================================

:- begin_tests(directions).

test(opposite_north_south) :-
    dungeon_generator:opposite_dir_val(north, south).

test(opposite_south_north) :-
    dungeon_generator:opposite_dir_val(south, north).

test(opposite_east_west) :-
    dungeon_generator:opposite_dir_val(east, west).

test(opposite_west_east) :-
    dungeon_generator:opposite_dir_val(west, east).

:- end_tests(directions).

%% ============================================
%% Run all tests
%% ============================================

run_all_tests :-
    run_tests(grammar_rules),
    run_tests(dungeon_generation),
    run_tests(room_content),
    run_tests(directions).
