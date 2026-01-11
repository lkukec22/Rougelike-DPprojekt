"""
Roguelike Dungeon Generator - Main Application

Pygame application using Prolog for dungeon generation.
"""

import pygame
import sys
import random
from prolog_bridge import PrologBridge
from player import Player
from renderer import DungeonRenderer, WINDOW_WIDTH, WINDOW_HEIGHT


class Game:
    """
    Main game class.
    """
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Roguelike Dungeon Generator")
        self.clock = pygame.time.Clock()
        

        self.bridge = PrologBridge()
        

        self.seed = random.randint(1, 100000)
        self.player = None
        self._generate_new_dungeon()
    
    def _generate_new_dungeon(self):
        print(f"\nGenerating dungeon (seed={self.seed})...")
        self.bridge.clear()
        self.player = Player()
        dungeon_data = self.bridge.generate_dungeon(seed=self.seed, num_rooms=7)
        self.renderer = DungeonRenderer(self.screen, dungeon_data, self.player)
        print(f"Generated {len(dungeon_data['rooms'])} rooms.")
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    elif self.player.is_alive() and not self.player.defeated_boss:
                        if event.key in (pygame.K_w, pygame.K_UP):
                            self.renderer.move_player('north')
                        elif event.key in (pygame.K_s, pygame.K_DOWN):
                            self.renderer.move_player('south')
                        elif event.key in (pygame.K_d, pygame.K_RIGHT):
                            self.renderer.move_player('east')
                        elif event.key in (pygame.K_a, pygame.K_LEFT):
                            self.renderer.move_player('west')
                        elif event.key == pygame.K_h:
                            heal = self.player.use_potion()
                            if heal > 0:
                                self.renderer.combat_message = f"Healed for {heal} HP!"
                                self.renderer.message_timer = 90
                    
                    if event.key == pygame.K_r:
                        self.seed = random.randint(1, 100000)
                        self._generate_new_dungeon()
            
            self.renderer.render()
            pygame.display.flip()
            
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    """Application entry point."""
    print("=" * 60)
    print("ROGUELIKE DUNGEON GENERATOR")
    print("Prolog + PySwip + Pygame")
    print("=" * 60)
    
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
