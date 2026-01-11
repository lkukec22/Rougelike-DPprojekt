"""
Dungeon Renderer module - Handles all Pygame rendering and game logic.
"""

import pygame
from player import Player, ENEMY_DAMAGE, ITEM_HEAL



WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768


ROOM_SIZE = 80
ROOM_MARGIN = 20
CORRIDOR_WIDTH = 8


ROOM_COLORS = {
    'start': (50, 205, 50),      # Zelena
    'boss': (220, 20, 60),       # Crvena
    'combat': (255, 140, 0),     # Narančasta
    'treasure': (255, 215, 0),   # Zlatna
    'shop': (65, 105, 225),      # Plava
    'event': (148, 0, 211),      # Ljubičasta
    'empty': (128, 128, 128),    # Siva
}


COLOR_BG = (20, 20, 30)
COLOR_CORRIDOR = (100, 100, 120)
COLOR_TEXT = (255, 255, 255)
COLOR_PLAYER = (0, 255, 255)     # Cyan
COLOR_HP_BAR = (50, 205, 50)     # Green
COLOR_HP_BG = (100, 0, 0)        # Dark red


class DungeonRenderer:
    
    def __init__(self, screen, dungeon_data, player):
        self.screen = screen
        self.dungeon = dungeon_data
        self.player = player
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        self.cleared_rooms = set()
        
        self.combat_message = ""
        self.message_timer = 0
        
        self._calculate_offset()
        
        self.current_room_id = self._find_start_room()
        self.cleared_rooms.add(self.current_room_id)
    
    def _calculate_offset(self):
        if not self.dungeon['rooms']:
            self.offset_x = WINDOW_WIDTH // 2
            self.offset_y = WINDOW_HEIGHT // 2
            return
        
        min_x = min(r['x'] for r in self.dungeon['rooms'])
        max_x = max(r['x'] for r in self.dungeon['rooms'])
        min_y = min(r['y'] for r in self.dungeon['rooms'])
        max_y = max(r['y'] for r in self.dungeon['rooms'])
        
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        self.offset_x = WINDOW_WIDTH // 2 - center_x * (ROOM_SIZE + ROOM_MARGIN)
        self.offset_y = WINDOW_HEIGHT // 2 - center_y * (ROOM_SIZE + ROOM_MARGIN)
    
    def _find_start_room(self) -> int:
        for room in self.dungeon['rooms']:
            if room['type'] == 'start':
                return room['id']
        return 1
    
    def _grid_to_screen(self, grid_x, grid_y):
        """Pretvara grid koordinate u screen koordinate."""
        screen_x = self.offset_x + grid_x * (ROOM_SIZE + ROOM_MARGIN)
        screen_y = self.offset_y + grid_y * (ROOM_SIZE + ROOM_MARGIN)
        return int(screen_x), int(screen_y)
    
    def _get_room_by_id(self, room_id):
        """Pronalazi sobu po ID-u."""
        for room in self.dungeon['rooms']:
            if room['id'] == room_id:
                return room
        return None
    
    def _get_connected_rooms(self, room_id):
        connected = []
        for conn in self.dungeon['connections']:
            if conn['from'] == room_id:
                connected.append((conn['to'], conn['direction']))
        return connected
    
    def render(self):
        """Renderira cijeli dungeon."""
        self.screen.fill(COLOR_BG)
        
        # Check game state
        if not self.player.is_alive():
            self._render_game_over()
            return
        
        if self.player.defeated_boss:
            self._render_victory()
            return
        
        title = self.title_font.render("Roguelike Dungeon Generator", True, COLOR_TEXT)
        self.screen.blit(title, (20, 20))
        
        subtitle = self.font.render("Prolog + PySwip + Pygame", True, (150, 150, 150))
        self.screen.blit(subtitle, (20, 55))
        
        self._render_corridors()
        
        self._render_rooms()
        
        self._render_player()
        
        self._render_legend()
        
        self._render_room_content()
        
        self._render_player_stats()
        
        if self.message_timer > 0:
            self._render_combat_message()
            self.message_timer -= 1
        
        self._render_controls()
    
    def _render_corridors(self):
        """Renderira koridore između soba kao jednostavne linije."""
        line_color = COLOR_CORRIDOR
        line_width = CORRIDOR_WIDTH
        
        for conn in self.dungeon['connections']:
            room_from = self._get_room_by_id(conn['from'])
            room_to = self._get_room_by_id(conn['to'])
            
            if room_from and room_to:
                x1, y1 = self._grid_to_screen(room_from['x'], room_from['y'])
                x2, y2 = self._grid_to_screen(room_to['x'], room_to['y'])
                
                start_pos = (x1 + ROOM_SIZE // 2, y1 + ROOM_SIZE // 2)
                end_pos = (x2 + ROOM_SIZE // 2, y2 + ROOM_SIZE // 2)
                
                pygame.draw.line(self.screen, line_color, start_pos, end_pos, line_width)
    
    def _render_rooms(self):
        """Renderira sve sobe."""
        for room in self.dungeon['rooms']:
            x, y = self._grid_to_screen(room['x'], room['y'])
            color = ROOM_COLORS.get(room['type'], ROOM_COLORS['empty'])
            
            rect = pygame.Rect(x, y, ROOM_SIZE, ROOM_SIZE)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, COLOR_TEXT, rect, 2)
            
            id_text = self.font.render(str(room['id']), True, (0, 0, 0))
            text_rect = id_text.get_rect(center=(x + ROOM_SIZE // 2, y + ROOM_SIZE // 2))
            self.screen.blit(id_text, text_rect)
            
            type_text = self.font.render(room['type'], True, COLOR_TEXT)
            type_rect = type_text.get_rect(center=(x + ROOM_SIZE // 2, y + ROOM_SIZE + 12))
            self.screen.blit(type_text, type_rect)
    
    def _render_player(self):
        """Renderira igrača u trenutnoj sobi."""
        current_room = self._get_room_by_id(self.current_room_id)
        if current_room:
            x, y = self._grid_to_screen(current_room['x'], current_room['y'])
            center = (x + ROOM_SIZE // 2, y + ROOM_SIZE // 2)
            
            pygame.draw.circle(self.screen, COLOR_PLAYER, center, 15)
            pygame.draw.circle(self.screen, COLOR_TEXT, center, 15, 2)
    
    def _render_legend(self):
        """Renderira legendu boja."""
        legend_x = WINDOW_WIDTH - 150
        legend_y = 20
        
        title = self.font.render("Legend:", True, COLOR_TEXT)
        self.screen.blit(title, (legend_x, legend_y))
        
        for i, (room_type, color) in enumerate(ROOM_COLORS.items()):
            y = legend_y + 30 + i * 25
            pygame.draw.rect(self.screen, color, (legend_x, y, 20, 20))
            text = self.font.render(room_type, True, COLOR_TEXT)
            self.screen.blit(text, (legend_x + 30, y + 2))
    
    def _render_room_content(self):
        """Renderira panel sa sadržajem trenutne sobe."""
        room_contents = self.dungeon.get('room_contents', {})
        content = room_contents.get(self.current_room_id, None)
        
        if not content:
            return
        
        current_room = self._get_room_by_id(self.current_room_id)
        room_type = current_room['type'] if current_room else "unknown"
        room_color = ROOM_COLORS.get(room_type, ROOM_COLORS['empty'])
        
        text_x = 20
        text_y = 90
        max_text_width = 400
        
        title_text = f"[ {room_type.upper()} ]"
        title_surf = self.title_font.render(title_text, True, room_color)
        self.screen.blit(title_surf, (text_x, text_y))
        
        def truncate_text(text, font, max_width):
            if font.size(text)[0] <= max_width:
                return text
            while font.size(text + "...")[0] > max_width and len(text) > 0:
                text = text[:-1]
            return text + "..."
        
        desc = content.get('description', '')
        desc_truncated = truncate_text(desc, self.font, max_text_width)
        desc_surf = self.font.render(desc_truncated, True, (200, 200, 200))
        self.screen.blit(desc_surf, (text_x, text_y + 35))
        
        enemies = content.get('enemies', [])
        if enemies and self.current_room_id not in self.cleared_rooms:
            enemy_text = f"Enemies: {', '.join(enemies)}"
            enemy_color = (255, 100, 100)
        else:
            enemy_text = "Enemies: Cleared"
            enemy_color = (100, 200, 100)
        enemy_truncated = truncate_text(enemy_text, self.font, max_text_width)
        enemy_surf = self.font.render(enemy_truncated, True, enemy_color)
        self.screen.blit(enemy_surf, (text_x, text_y + 60))
        
        items = content.get('items', [])
        if items:
            item_text = f"Items: {', '.join(items)}"
        else:
            item_text = "Items: None"
        item_truncated = truncate_text(item_text, self.font, max_text_width)
        item_surf = self.font.render(item_truncated, True, (255, 215, 0))
        self.screen.blit(item_surf, (text_x, text_y + 85))
        
        gold = content.get('gold', 0)
        if gold > 0:
            gold_text = f"Gold: {gold}"
            gold_surf = self.font.render(gold_text, True, (255, 215, 0))
            self.screen.blit(gold_surf, (text_x, text_y + 110))
    
    def _render_controls(self):
        """Renderira kontrole."""
        controls = [
            "Controls:",
            "WASD / Arrows - Move",
            "H - Use health potion",
            "R - New dungeon",
            "ESC - Exit"
        ]
        
        y = WINDOW_HEIGHT - len(controls) * 25 - 20
        for line in controls:
            text = self.font.render(line, True, (150, 150, 150))
            self.screen.blit(text, (20, y))
            y += 25
    
    def _render_player_stats(self):
        """Render HP bar and player stats."""
        # HP Bar position
        bar_x = WINDOW_WIDTH - 220
        bar_y = WINDOW_HEIGHT - 100
        bar_width = 200
        bar_height = 25
        
        pygame.draw.rect(self.screen, COLOR_HP_BG, (bar_x, bar_y, bar_width, bar_height))
        
        hp_ratio = self.player.hp / self.player.max_hp
        fill_width = int(bar_width * hp_ratio)
        pygame.draw.rect(self.screen, COLOR_HP_BAR, (bar_x, bar_y, fill_width, bar_height))
        
        pygame.draw.rect(self.screen, COLOR_TEXT, (bar_x, bar_y, bar_width, bar_height), 2)
        
        hp_text = f"HP: {self.player.hp}/{self.player.max_hp}"
        hp_surf = self.font.render(hp_text, True, COLOR_TEXT)
        self.screen.blit(hp_surf, (bar_x + 5, bar_y + 5))
        
        gold_text = f"Gold: {self.player.gold}"
        gold_surf = self.font.render(gold_text, True, (255, 215, 0))
        self.screen.blit(gold_surf, (bar_x, bar_y + 30))
        
        potions = [i for i in self.player.inventory if i in ITEM_HEAL]
        potion_text = f"Potions: {len(potions)}"
        potion_surf = self.font.render(potion_text, True, (100, 200, 100))
        self.screen.blit(potion_surf, (bar_x, bar_y + 55))
    
    def _render_combat_message(self):
        """Render combat message."""
        msg_surf = self.title_font.render(self.combat_message, True, (255, 100, 100))
        msg_rect = msg_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(msg_surf, msg_rect)
    
    def _render_game_over(self):
        """Render game over screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        go_text = self.big_font.render("GAME OVER", True, (220, 20, 60))
        go_rect = go_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        self.screen.blit(go_text, go_rect)
        
        hint = self.font.render("Press R to restart", True, COLOR_TEXT)
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
        self.screen.blit(hint, hint_rect)
    
    def _render_victory(self):
        """Render victory screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((50, 50, 0))
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))
        
        vic_text = self.big_font.render("VICTORY!", True, (255, 215, 0))
        vic_rect = vic_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(vic_text, vic_rect)
        
        stats = f"Gold collected: {self.player.gold}  |  HP remaining: {self.player.hp}"
        stats_surf = self.title_font.render(stats, True, COLOR_TEXT)
        stats_rect = stats_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(stats_surf, stats_rect)
        
        hint = self.font.render("Press R to play again", True, COLOR_TEXT)
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        self.screen.blit(hint, hint_rect)
    
    def move_player(self, direction):
        """Move player and trigger room events."""
        connected = self._get_connected_rooms(self.current_room_id)
        for room_id, conn_dir in connected:
            if conn_dir == direction:
                self.current_room_id = room_id
                self._enter_room(room_id)
                return True
        return False
    
    def _enter_room(self, room_id):
        """Handle entering a room - combat, loot, etc."""
        if room_id in self.cleared_rooms:
            return
        
        room_contents = self.dungeon.get('room_contents', {})
        content = room_contents.get(room_id, {})
        
        enemies = content.get('enemies', [])
        items = content.get('items', [])
        gold = content.get('gold', 0)
        
        room = self._get_room_by_id(room_id)
        room_type = room['type'] if room else 'empty'
        
        if enemies:
            total_damage = 0
            for enemy in enemies:
                damage = ENEMY_DAMAGE.get(enemy, 5)
                total_damage += damage
            
            self.player.take_damage(total_damage)
            self.combat_message = f"Took {total_damage} damage from {', '.join(enemies)}!"
            self.message_timer = 120
            
            if room_type == 'boss' and self.player.is_alive():
                self.player.defeated_boss = True
        
        for item in items:
            self.player.add_item(item)
        
        if gold > 0:
            self.player.add_gold(gold)
        
        self.cleared_rooms.add(room_id)
