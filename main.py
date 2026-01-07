import platform
import os
import pygame
import chess
import chess.engine
import chess.pgn
import sys
import io
from pathlib import Path
import math
from datetime import datetime
from tkinter import filedialog
import tkinter as tk

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Load sounds
def load_sounds():
    sounds = {}
    try:
        sounds['move'] = pygame.mixer.Sound('sfx/move.wav')
        sounds['capture'] = pygame.mixer.Sound('sfx/capture.wav')
        # Adjust volume (0.0 to 1.0)
        sounds['move'].set_volume(0.5)
        sounds['capture'].set_volume(0.6)
        print("✓ Sounds loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load sounds - {e}")
        print("Playing without sound")
    return sounds

# Load sounds globally
SOUNDS = load_sounds()

# Constants
if os.name == "nt":
    is_windows = True
else: is_windows = False

if os.name == "posix" and platform.system() == "Linux":
    is_linux = True
else: is_linux = False

MENU_BAR_HEIGHT = 30
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
HIGHLIGHT = (255, 255, 0, 128)
MOVE_HINT = (0, 255, 0, 64)
ANIMATION_SPEED = 8  # Higher = faster animation
INFO_PANEL_WIDTH = 200
FULL_WIDTH = BOARD_SIZE + INFO_PANEL_WIDTH

# Menu colors
MENU_BG = (50, 50, 50)
MENU_HOVER = (80, 80, 80)
MENU_TEXT = (220, 220, 220)
MENU_BORDER = (30, 30, 30)
MENU_DROPDOWN_BG = (60, 60, 60)

# Difficulty settings
DIFFICULTY_SETTINGS = {
    "Beginner": {"time": 0.1, "depth": 3},
    "Easy": {"time": 0.3, "depth": 6},
    "Medium": {"time": 0.8, "depth": 10},
    "Hard": {"time": 1.5, "depth": 15},
    "Expert": {"time": 2.5, "depth": 20},
    "Master": {"time": 5.0, "depth": None},  # None = no depth limit
}

# Update screen initialization
screen = pygame.display.set_mode((FULL_WIDTH, BOARD_SIZE + MENU_BAR_HEIGHT))
pygame.display.set_caption("Chess vs Stockfish")

class MenuItem:
    def __init__(self, text, action=None, submenu=None, checkable=False, checked=False):
        self.text = text
        self.action = action
        self.submenu = submenu  # For nested menus
        self.checkable = checkable
        self.checked = checked
        self.rect = None

class Menu:
    def __init__(self, title, items):
        self.title = title
        self.items = items
        self.rect = None
        self.is_open = False
        self.dropdown_rect = None

class MenuBar:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 22)
        self.menus = []
        self.active_menu = None
        self.setup_menus()
        
    def setup_menus(self):
        # Game menu
        game_menu = Menu("Game", [
            MenuItem("New Game", action="new_game"),
            MenuItem("Undo Move", action="undo"),
            MenuItem("separator"),
            MenuItem("Flip Board", action="flip_board", checkable=True),
            MenuItem("separator"),
            MenuItem("Exit", action="exit"),
        ])
        
        # Difficulty menu
        difficulty_items = []
        for diff_name in DIFFICULTY_SETTINGS.keys():
            difficulty_items.append(MenuItem(diff_name, action=f"difficulty_{diff_name}", checkable=True, checked=(diff_name == "Medium")))
        difficulty_menu = Menu("Difficulty", difficulty_items)
        
        # Options menu
        options_menu = Menu("Options", [
            MenuItem("Sound Effects", action="toggle_sound", checkable=True, checked=True),
            MenuItem("Show Coordinates", action="toggle_coords", checkable=True, checked=True),
            MenuItem("separator"),
            MenuItem("Reset Settings", action="reset_settings"),
        ])
        
        # File menu (import/export)
        file_menu = Menu("File", [
            MenuItem("Load PGN...", action="load_pgn"),
            MenuItem("Load FEN...", action="load_fen"),
            MenuItem("separator"),
            MenuItem("Export PGN...", action="export_pgn"),
            MenuItem("Copy PGN to Clipboard", action="copy_pgn"),
            MenuItem("separator"),
            MenuItem("Export FEN...", action="export_fen"),
            MenuItem("Copy FEN to Clipboard", action="copy_fen"),
        ])
        
        # Help menu
        help_menu = Menu("Help", [
            MenuItem("Controls", action="show_controls"),
            MenuItem("About", action="show_about"),
        ])
        
        self.menus = [game_menu, file_menu, difficulty_menu, options_menu, help_menu]
        self._calculate_menu_positions()
    
    def _calculate_menu_positions(self):
        x = 10
        for menu in self.menus:
            text_width = self.font.size(menu.title)[0] + 20
            menu.rect = pygame.Rect(x, 0, text_width, MENU_BAR_HEIGHT)
            x += text_width
    
    def draw(self, surface):
        # Draw menu bar background and titles
        pygame.draw.rect(surface, MENU_BG, (0, 0, FULL_WIDTH, MENU_BAR_HEIGHT))
        pygame.draw.line(surface, MENU_BORDER, (0, MENU_BAR_HEIGHT - 1), (FULL_WIDTH, MENU_BAR_HEIGHT - 1))
        
        # Draw menu titles
        for menu in self.menus:
            bg_color = MENU_HOVER if (self.active_menu == menu or menu.rect.collidepoint(pygame.mouse.get_pos())) else MENU_BG
            pygame.draw.rect(surface, bg_color, menu.rect)
            text = self.font.render(menu.title, True, MENU_TEXT)
            text_rect = text.get_rect(center=menu.rect.center)
            surface.blit(text, text_rect)
    
    def draw_dropdowns(self, surface):
        # Draw active dropdown (called last so it appears on top)
        if self.active_menu:
            self._draw_dropdown(surface, self.active_menu)
    
    def _draw_dropdown(self, surface, menu):
        if not menu.items:
            return
        
        # Ensure rects are calculated
        self._calculate_dropdown_rects(menu)
        
        max_width = 180
        item_height = 28
        dropdown_x = menu.dropdown_rect.left
        dropdown_y = menu.dropdown_rect.top
        
        # Draw dropdown background with shadow
        shadow_rect = menu.dropdown_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(surface, (20, 20, 20), shadow_rect)
        pygame.draw.rect(surface, MENU_DROPDOWN_BG, menu.dropdown_rect)
        pygame.draw.rect(surface, MENU_BORDER, menu.dropdown_rect, 1)
        
        # Draw items
        y = dropdown_y
        mouse_pos = pygame.mouse.get_pos()
        for item in menu.items:
            if item.text == "separator":
                pygame.draw.line(surface, MENU_BORDER, (dropdown_x + 5, y + 4), (dropdown_x + max_width - 5, y + 4))
                y += 8
            else:
                # Hover effect
                if item.rect and item.rect.collidepoint(mouse_pos):
                    pygame.draw.rect(surface, (70, 130, 180), item.rect)
                
                # Checkmark for checkable items
                text_x = dropdown_x + 10
                if item.checkable:
                    if item.checked:
                        check = self.font.render("✓", True, (100, 200, 100))
                        surface.blit(check, (dropdown_x + 8, y + 5))
                    text_x = dropdown_x + 28
                
                # Item text
                text = self.font.render(item.text, True, MENU_TEXT)
                surface.blit(text, (text_x, y + 5))
                y += item_height
    
    def _calculate_dropdown_rects(self, menu):
        """Calculate rectangles for dropdown and its items"""
        if not menu.items:
            return
            
        max_width = 180
        item_height = 28
        total_height = 0
        for item in menu.items:
            if item.text == "separator":
                total_height += 8
            else:
                total_height += item_height
        
        dropdown_x = menu.rect.left
        dropdown_y = MENU_BAR_HEIGHT
        
        # Keep dropdown on screen
        if dropdown_x + max_width > FULL_WIDTH:
            dropdown_x = FULL_WIDTH - max_width
        
        menu.dropdown_rect = pygame.Rect(dropdown_x, dropdown_y, max_width, total_height)
        
        # Calculate item rects
        y = dropdown_y
        for item in menu.items:
            if item.text == "separator":
                item.rect = None
                y += 8
            else:
                item.rect = pygame.Rect(dropdown_x, y, max_width, item_height)
                y += item_height
    
    def handle_click(self, pos):
        # Check if clicked on menu title
        for menu in self.menus:
            if menu.rect.collidepoint(pos):
                if self.active_menu == menu:
                    self.active_menu = None
                else:
                    self.active_menu = menu
                    # Calculate dropdown rects immediately when menu opens
                    self._calculate_dropdown_rects(menu)
                return True
        
        # Check if clicked on dropdown item
        if self.active_menu:
            # Ensure rects are calculated
            self._calculate_dropdown_rects(self.active_menu)
            
            if self.active_menu.dropdown_rect and self.active_menu.dropdown_rect.collidepoint(pos):
                for item in self.active_menu.items:
                    if item.rect and item.rect.collidepoint(pos) and item.text != "separator":
                        self._execute_action(item)
                        self.active_menu = None
                        return True
        
        # Clicked outside - close menu
        if self.active_menu:
            self.active_menu = None
            return True
        
        return False
    
    def handle_hover(self, pos):
        # If a menu is open, switch to hovered menu
        if self.active_menu:
            for menu in self.menus:
                if menu.rect.collidepoint(pos) and menu != self.active_menu:
                    self.active_menu = menu
                    return
    
    def _execute_action(self, item):
        action = item.action
        if not action:
            return
        
        # Handle checkable items
        if item.checkable:
            # For difficulty, only one can be checked
            if action.startswith("difficulty_"):
                for menu in self.menus:
                    if menu.title == "Difficulty":
                        for diff_item in menu.items:
                            diff_item.checked = (diff_item == item)
                        break
            else:
                item.checked = not item.checked
        
        # Execute the action
        if action == "new_game":
            self.game.new_game()
        elif action == "undo":
            self.game.undo_move()
        elif action == "flip_board":
            self.game.flip_board()
        elif action == "exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif action == "toggle_sound":
            self.game.toggle_sound(item.checked)
        elif action == "toggle_coords":
            self.game.toggle_coordinates(item.checked)
        elif action == "reset_settings":
            self.game.reset_settings()
        elif action == "load_pgn":
            self.game.load_pgn()
        elif action == "load_fen":
            self.game.load_fen()
        elif action == "export_pgn":
            self.game.export_pgn()
        elif action == "copy_pgn":
            self.game.copy_pgn()
        elif action == "export_fen":
            self.game.export_fen()
        elif action == "copy_fen":
            self.game.copy_fen()
        elif action == "show_controls":
            self.game.show_controls()
        elif action == "show_about":
            self.game.show_about()
        elif action.startswith("difficulty_"):
            diff_name = action.replace("difficulty_", "")
            self.game.set_difficulty(diff_name)
    
    def is_menu_area(self, pos):
        """Check if position is in menu bar or active dropdown"""
        if pos[1] < MENU_BAR_HEIGHT:
            return True
        if self.active_menu and self.active_menu.dropdown_rect:
            return self.active_menu.dropdown_rect.collidepoint(pos)
        return False

def load_pieces():
    pieces = {}
    piece_map = {
        'P': '♟', 'N': '♞', 'B': '♝', 'R': '♜', 'Q': '♛', 'K': '♚',
        'p': '♙', 'n': '♘', 'b': '♗', 'r': '♖', 'q': '♕', 'k': '♔'
    }

    fonts_to_try = []

    if is_windows:
        fonts_to_try = [
            pygame.font.Font(r"C:\Windows\Fonts\seguisym.ttf", 60),
            pygame.font.Font(None, 60),
        ]

    elif is_linux:
        fonts_to_try = [
            pygame.font.Font("/usr/share/fonts/TTF/DejaVuSans.ttf", 60),
            pygame.font.Font("/usr/share/fonts/noto/NotoSansSymbols-Regular.ttf", 60),
            pygame.font.Font(None, 60),
        ]

    font = None
    for f in fonts_to_try:
        try:
            f.render("♔", True, (255, 255, 255))
            font = f
            break
        except Exception:
            pass

    if font is None:
        font = pygame.font.Font(None, 60)


    for key, unicode_char in piece_map.items():
        is_white = key.isupper()
        
        if is_white:
            # White pieces: cream/ivory color with dark outline
            main_color = (255, 248, 220)  # Cream/cornsilk color
            outline_color = (60, 40, 20)  # Dark brown outline
            
            # Render the outline first (slightly larger or offset)
            outline_surface = font.render(unicode_char, True, outline_color)
            main_surface = font.render(unicode_char, True, main_color)
            
            # Create a surface large enough for the outline effect
            padding = 3
            w = main_surface.get_width() + padding * 2
            h = main_surface.get_height() + padding * 2
            piece_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            
            # Draw outline by rendering at offsets
            offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2),
                       (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for ox, oy in offsets:
                piece_surface.blit(outline_surface, (padding + ox, padding + oy))
            
            # Draw main piece on top
            piece_surface.blit(main_surface, (padding, padding))
            pieces[key] = piece_surface
        else:
            # Black pieces: Solid black with light internal detail lines
            # Black fill at offsets for size, light details only on top (no glow)
            
            # Map outline symbols to their filled counterparts
            filled_map = {'♙': '♟', '♘': '♞', '♗': '♝', '♖': '♜', '♕': '♛', '♔': '♚'}
            filled_char = filled_map.get(unicode_char, unicode_char)
            
            # Colors
            fill_color = (0, 0, 0)  # Black fill
            detail_color = (200, 200, 200)  # Light gray for internal details
            
            # Render surfaces
            fill_surface = font.render(filled_char, True, fill_color)
            detail_surface = font.render(unicode_char, True, detail_color)
            
            # Match the padding of white pieces for consistent sizing
            padding = 3
            w = fill_surface.get_width() + padding * 2
            h = fill_surface.get_height() + padding * 2
            piece_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            
            # Draw BLACK fill at offsets (makes piece fuller, no glow)
            offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2),
                       (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for ox, oy in offsets:
                piece_surface.blit(fill_surface, (padding + ox, padding + oy))
            
            # Draw black filled center
            piece_surface.blit(fill_surface, (padding, padding))
            
            # Draw light detail lines ONCE on top (internal details only, no outer glow)
            piece_surface.blit(detail_surface, (padding, padding))
            
            pieces[key] = piece_surface
    
    # return pieces
    return pieces

# Draw the board
def draw_board(surface, flipped=False, show_coords=True):
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE + MENU_BAR_HEIGHT, 
                              SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(surface, color, rect)
    
    # Draw coordinates if enabled
    if show_coords:
        coord_font = pygame.font.Font(None, 18)
        for i in range(8):
            # File letters (a-h) at bottom
            file_letter = chr(ord('a') + i) if not flipped else chr(ord('h') - i)
            file_text = coord_font.render(file_letter, True, (100, 100, 100))
            surface.blit(file_text, (i * SQUARE_SIZE + SQUARE_SIZE - 12, BOARD_SIZE + MENU_BAR_HEIGHT - 14))
            
            # Rank numbers (1-8) on left
            rank_num = str(8 - i) if not flipped else str(i + 1)
            rank_text = coord_font.render(rank_num, True, (100, 100, 100))
            surface.blit(rank_text, (4, i * SQUARE_SIZE + MENU_BAR_HEIGHT + 4))

# Draw pieces (modified to handle animations)
def draw_pieces(surface, board, pieces, animating_piece=None, animated_squares=None, flipped=False):
    for row in range(8):
        for col in range(8):
            if flipped:
                square = chess.square(7 - col, row)
            else:
                square = chess.square(col, 7 - row)
            
            # Skip drawing piece if it's being animated
            if animated_squares and square in animated_squares:
                continue
                
            piece = board.piece_at(square)
            if piece:
                piece_image = pieces[piece.symbol()]
                x = col * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_width()) // 2
                y = row * SQUARE_SIZE + MENU_BAR_HEIGHT + (SQUARE_SIZE - piece_image.get_height()) // 2
                surface.blit(piece_image, (x, y))

# Convert pixel coordinates to chess square
def get_square_from_mouse(pos, flipped=False):
    col = pos[0] // SQUARE_SIZE
    row = (pos[1] - MENU_BAR_HEIGHT) // SQUARE_SIZE
    if flipped:
        return chess.square(7 - col, row)
    else:
        return chess.square(col, 7 - row)

# Highlight selected square
def draw_selection(surface, square, flipped=False):
    if square is not None:
        if flipped:
            col = 7 - chess.square_file(square)
            row = chess.square_rank(square)
        else:
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(HIGHLIGHT)
        surface.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE + MENU_BAR_HEIGHT))

# Show possible moves
def draw_possible_moves(surface, board, square, flipped=False):
    if square is not None:
        for move in board.legal_moves:
            if move.from_square == square:
                if flipped:
                    col = 7 - chess.square_file(move.to_square)
                    row = chess.square_rank(move.to_square)
                else:
                    col = chess.square_file(move.to_square)
                    row = 7 - chess.square_rank(move.to_square)
                # Draw a circle in the center of valid move squares
                center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2 + MENU_BAR_HEIGHT
                
                # Check if there's a piece to capture
                if board.piece_at(move.to_square):
                    pygame.draw.circle(surface, (255, 0, 0, 100), (center_x, center_y), 20, 3)
                else:
                    pygame.draw.circle(surface, (0, 150, 0, 150), (center_x, center_y), 10)

# Draw hint arrow
def draw_hint(surface, move, flipped=False):
    if move:
        # Get coordinates for from and to squares
        if flipped:
            from_col = 7 - chess.square_file(move.from_square)
            from_row = chess.square_rank(move.from_square)
            to_col = 7 - chess.square_file(move.to_square)
            to_row = chess.square_rank(move.to_square)
        else:
            from_col = chess.square_file(move.from_square)
            from_row = 7 - chess.square_rank(move.from_square)
            to_col = chess.square_file(move.to_square)
            to_row = 7 - chess.square_rank(move.to_square)
        
        # Calculate center points of squares
        from_x = from_col * SQUARE_SIZE + SQUARE_SIZE // 2
        from_y = from_row * SQUARE_SIZE + SQUARE_SIZE // 2 + MENU_BAR_HEIGHT
        to_x = to_col * SQUARE_SIZE + SQUARE_SIZE // 2
        to_y = to_row * SQUARE_SIZE + SQUARE_SIZE // 2 + MENU_BAR_HEIGHT
        
        # Draw arrow for hint
        pygame.draw.line(surface, (255, 0, 255), (from_x, from_y), (to_x, to_y), 5)
        
        # Draw arrow head
        pygame.draw.circle(surface, (255, 0, 255), (to_x, to_y), 10)
        
        # Highlight the squares
        hint_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        hint_surface.fill((255, 0, 255, 100))
        surface.blit(hint_surface, (from_col * SQUARE_SIZE, from_row * SQUARE_SIZE + MENU_BAR_HEIGHT))
        surface.blit(hint_surface, (to_col * SQUARE_SIZE, to_row * SQUARE_SIZE + MENU_BAR_HEIGHT))

# Draw hint button in menu bar (rightmost corner)
def draw_hint_button(surface, hint_active=False):
    # Position in the right corner of menu bar
    button_size = MENU_BAR_HEIGHT - 4
    button_rect = pygame.Rect(FULL_WIDTH - button_size - 8, 2, button_size, button_size)
    
    # Button background - highlight if hint is active
    if hint_active:
        bg_color = (255, 200, 50)  # Golden yellow when active
    else:
        mouse_pos = pygame.mouse.get_pos()
        bg_color = MENU_HOVER if button_rect.collidepoint(mouse_pos) else MENU_BG
    
    pygame.draw.rect(surface, bg_color, button_rect, border_radius=4)
    pygame.draw.rect(surface, MENU_BORDER, button_rect, 1, border_radius=4)
    
    # Draw lightbulb icon using Unicode character
    font = pygame.font.SysFont('segoeuisymbol', 18)
    icon = font.render("💡", True, (255, 220, 50) if not hint_active else (80, 60, 0))
    icon_rect = icon.get_rect(center=button_rect.center)
    surface.blit(icon, icon_rect)
    
    return button_rect

# Draw hint text overlay on board
def draw_hint_text(surface):
    font = pygame.font.Font(None, 20)
    # Semi-transparent background for text
    text = font.render("Best move shown in purple (H to toggle)", True, (255, 0, 255))
    text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 6), pygame.SRCALPHA)
    text_bg.fill((0, 0, 0, 150))
    surface.blit(text_bg, (5, MENU_BAR_HEIGHT + 5))
    surface.blit(text, (10, MENU_BAR_HEIGHT + 8))

def draw_last_move(surface, move, flipped=False):
    if move:
        # Highlight the last move squares with subtle color
        if flipped:
            from_col = 7 - chess.square_file(move.from_square)
            from_row = chess.square_rank(move.from_square)
            to_col = 7 - chess.square_file(move.to_square)
            to_row = chess.square_rank(move.to_square)
        else:
            from_col = chess.square_file(move.from_square)
            from_row = 7 - chess.square_rank(move.from_square)
            to_col = chess.square_file(move.to_square)
            to_row = 7 - chess.square_rank(move.to_square)
        
        # Draw with a subtle yellow highlight
        last_move_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        last_move_surface.fill((255, 255, 100, 50))
        surface.blit(last_move_surface, (from_col * SQUARE_SIZE, from_row * SQUARE_SIZE + MENU_BAR_HEIGHT))
        surface.blit(last_move_surface, (to_col * SQUARE_SIZE, to_row * SQUARE_SIZE + MENU_BAR_HEIGHT))

# Animation class for smooth piece movement
class PieceAnimation:
    def __init__(self, piece, from_square, to_square, piece_image, flipped=False):
        self.piece = piece
        self.from_square = from_square
        self.to_square = to_square
        self.piece_image = piece_image
        self.flipped = flipped
        
        # Calculate pixel positions
        if flipped:
            from_col = 7 - chess.square_file(from_square)
            from_row = chess.square_rank(from_square)
            to_col = 7 - chess.square_file(to_square)
            to_row = chess.square_rank(to_square)
        else:
            from_col = chess.square_file(from_square)
            from_row = 7 - chess.square_rank(from_square)
            to_col = chess.square_file(to_square)
            to_row = 7 - chess.square_rank(to_square)
        
        self.start_x = from_col * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_width()) // 2
        self.start_y = from_row * SQUARE_SIZE + MENU_BAR_HEIGHT + (SQUARE_SIZE - piece_image.get_height()) // 2
        self.end_x = to_col * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_width()) // 2
        self.end_y = to_row * SQUARE_SIZE + MENU_BAR_HEIGHT + (SQUARE_SIZE - piece_image.get_height()) // 2
        
        self.current_x = float(self.start_x)
        self.current_y = float(self.start_y)
        
        # Calculate distance and speed
        self.dx = self.end_x - self.start_x
        self.dy = self.end_y - self.start_y
        self.distance = math.sqrt(self.dx ** 2 + self.dy ** 2)
        self.progress = 0.0
        
    def update(self):
        if self.progress < 1.0:
            # Smooth easing function (ease-in-out)
            self.progress = min(1.0, self.progress + ANIMATION_SPEED / 60.0)
            
            # Use sine function for smooth acceleration/deceleration
            eased_progress = (math.sin((self.progress - 0.5) * math.pi) + 1) / 2
            
            self.current_x = self.start_x + self.dx * eased_progress
            self.current_y = self.start_y + self.dy * eased_progress
            return False  # Animation not complete
        return True  # Animation complete
    
    def draw(self, surface):
        surface.blit(self.piece_image, (int(self.current_x), int(self.current_y)))

# Main game class
class ChessGame:
    def __init__(self, stockfish_path):
        self.stockfish_path = stockfish_path
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.pieces = load_pieces()
        self.selected_square = None
        self.player_color = chess.WHITE  # Player is white
        self.game_over = False
        self.hint_move = None  # Store the hint move
        self.show_hint = False  # Toggle hint display
        self.last_move = None  # Store last move for highlighting
        self.engine_thinking = False  # Flag for when engine is thinking
        self.engine_move_pending = None  # Store pending engine move
        self.engine_move_timer = 0  # Timer for delayed move
        self.current_animation = None  # Current piece animation
        self.animation_board = None  # Board state during animation
        self.move_history = []
        self.sounds = SOUNDS
        
        # Menu-related settings
        self.menu_bar = MenuBar(self)
        self.board_flipped = False
        self.show_coordinates = True
        self.sound_enabled = True
        self.difficulty = "Medium"
        self.engine_time = DIFFICULTY_SETTINGS["Medium"]["time"]
        self.engine_depth = DIFFICULTY_SETTINGS["Medium"]["depth"]
        
        # For PGN export
        self.game_moves = []  # Store moves in UCI format for PGN
        self.game_start_time = datetime.now()
        
        # Dialog/overlay state
        self.showing_dialog = False
        self.dialog_text = []
        self.dialog_title = ""
        
        # Hint button rect (updated during draw)
        self.hint_button_rect = None

    # # Add this method to ChessGame class
    # def add_to_history(self, move):
    #     # Convert to algebraic notation
    #     san = self.board.san(move)
    #     move_number = (len(self.move_history) // 2) + 1
        
    #     if self.board.turn == chess.BLACK:  # Just made white's move
    #         self.move_history.append(f"{move_number}. {san}")
    #     else:  # Just made black's move
    #         if self.move_history and not self.move_history[-1].endswith("..."):
    #             self.move_history[-1] += f" {san}"
    #         else:
    #             self.move_history.append(f"{move_number}... {san}")
    
    def add_to_history(self, move):
    # Get the move in SAN before pushing it
        san = self.board.san(move)
        move_number = len(self.move_history) // 2 + 1
    
        if self.board.turn == chess.WHITE:  # Black just moved
            if self.move_history and "..." not in self.move_history[-1]:
                self.move_history[-1] += f" {san}"
            else:
                self.move_history.append(f"{move_number}... {san}")
        else:  # White just moved
            self.move_history.append(f"{move_number}. {san}")
            
    def play_move_sound(self, move):
        if self.sounds and self.sound_enabled:
            if self.board.is_capture(move):
                if 'capture' in self.sounds:
                    self.sounds['capture'].play()
            else:
                if 'move' in self.sounds:
                    self.sounds['move'].play()
    
    # ========== Menu Action Methods ==========
    
    def new_game(self):
        """Start a new game"""
        self.board = chess.Board()
        self.selected_square = None
        self.game_over = False
        self.hint_move = None
        self.show_hint = False
        self.last_move = None
        self.engine_thinking = False
        self.engine_move_pending = None
        self.engine_move_timer = 0
        self.current_animation = None
        self.animation_board = None
        self.move_history = []
        self.game_moves = []
        self.game_start_time = datetime.now()
        print("=== New Game Started ===")
    
    def undo_move(self):
        """Undo the last move (player's move + engine's response)"""
        if len(self.board.move_stack) >= 2 and not self.current_animation:
            # Undo engine's move
            self.board.pop()
            if self.game_moves:
                self.game_moves.pop()
            if self.move_history:
                # Remove from display history
                if self.move_history[-1].count(' ') > 0:
                    # Both moves on same line, just remove black's move
                    parts = self.move_history[-1].split(' ')
                    self.move_history[-1] = parts[0] + ' ' + parts[1]
                else:
                    self.move_history.pop()
            
            # Undo player's move
            self.board.pop()
            if self.game_moves:
                self.game_moves.pop()
            if self.move_history:
                self.move_history.pop()
            
            self.selected_square = None
            self.last_move = self.board.move_stack[-1] if self.board.move_stack else None
            self.game_over = False
            print("⟲ Undo: Reverted last move pair")
        elif len(self.board.move_stack) == 1:
            # Only one move made (player's first move)
            self.board.pop()
            if self.game_moves:
                self.game_moves.pop()
            if self.move_history:
                self.move_history.pop()
            self.last_move = None
            print("⟲ Undo: Reverted opening move")
    
    def flip_board(self):
        """Flip the board view"""
        self.board_flipped = not self.board_flipped
        print(f"Board {'flipped' if self.board_flipped else 'normal'}")
    
    def toggle_sound(self, enabled):
        """Toggle sound effects"""
        self.sound_enabled = enabled
        print(f"Sound {'enabled' if enabled else 'disabled'}")
    
    def toggle_coordinates(self, enabled):
        """Toggle coordinate display"""
        self.show_coordinates = enabled
    
    def reset_settings(self):
        """Reset all settings to default"""
        self.board_flipped = False
        self.show_coordinates = True
        self.sound_enabled = True
        self.set_difficulty("Medium")
        # Update menu checkboxes
        for menu in self.menu_bar.menus:
            if menu.title == "Options":
                for item in menu.items:
                    if item.action == "toggle_sound":
                        item.checked = True
                    elif item.action == "toggle_coords":
                        item.checked = True
            elif menu.title == "Difficulty":
                for item in menu.items:
                    item.checked = (item.text == "Medium")
            elif menu.title == "Game":
                for item in menu.items:
                    if item.action == "flip_board":
                        item.checked = False
        print("Settings reset to defaults")
    
    def set_difficulty(self, difficulty_name):
        """Set the engine difficulty"""
        if difficulty_name in DIFFICULTY_SETTINGS:
            self.difficulty = difficulty_name
            settings = DIFFICULTY_SETTINGS[difficulty_name]
            self.engine_time = settings["time"]
            self.engine_depth = settings["depth"]
            print(f"Difficulty set to {difficulty_name} (time: {self.engine_time}s, depth: {self.engine_depth or 'unlimited'})")
    
    def get_pgn(self):
        """Generate PGN string for the current game"""
        pgn_lines = []
        
        # Headers
        pgn_lines.append(f'[Event "Casual Game"]')
        pgn_lines.append(f'[Site "PyChess"]')
        pgn_lines.append(f'[Date "{self.game_start_time.strftime("%Y.%m.%d")}"]')
        pgn_lines.append(f'[Round "?"]')
        pgn_lines.append(f'[White "Player"]')
        pgn_lines.append(f'[Black "Stockfish ({self.difficulty})"]')
        
        # Result
        if self.game_over:
            if self.board.is_checkmate():
                result = "1-0" if self.board.turn == chess.BLACK else "0-1"
            else:
                result = "1/2-1/2"
        else:
            result = "*"
        pgn_lines.append(f'[Result "{result}"]')
        pgn_lines.append('')
        
        # Moves
        temp_board = chess.Board()
        move_text = []
        for i, move in enumerate(self.game_moves):
            if i % 2 == 0:
                move_text.append(f"{i // 2 + 1}.")
            move_text.append(temp_board.san(move))
            temp_board.push(move)
        
        move_text.append(result)
        pgn_lines.append(' '.join(move_text))
        
        return '\n'.join(pgn_lines)
    
    def export_pgn(self):
        """Export game to PGN file"""
        # Hide pygame window temporarily for file dialog
        root = tk.Tk()
        root.withdraw()
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pgn",
            filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")],
            title="Export Game as PGN",
            initialfile=f"chess_game_{self.game_start_time.strftime('%Y%m%d_%H%M%S')}.pgn"
        )
        
        root.destroy()
        
        if filename:
            pgn = self.get_pgn()
            with open(filename, 'w') as f:
                f.write(pgn)
            print(f"✓ Game exported to {filename}")
    
    def copy_pgn(self):
        """Copy PGN to clipboard"""
        pgn = self.get_pgn()
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(pgn)
        root.update()
        root.destroy()
        print("✓ PGN copied to clipboard")
    
    def export_fen(self):
        """Export current position as FEN"""
        root = tk.Tk()
        root.withdraw()
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".fen",
            filetypes=[("FEN files", "*.fen"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Position as FEN",
            initialfile=f"position_{datetime.now().strftime('%Y%m%d_%H%M%S')}.fen"
        )
        
        root.destroy()
        
        if filename:
            with open(filename, 'w') as f:
                f.write(self.board.fen())
            print(f"✓ Position exported to {filename}")
    
    def load_pgn(self):
        """Load a game from PGN file"""
        root = tk.Tk()
        root.withdraw()
        
        filename = filedialog.askopenfilename(
            filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")],
            title="Load PGN Game"
        )
        
        root.destroy()
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    pgn_text = f.read()
                
                # Parse PGN using chess library
                pgn_io = io.StringIO(pgn_text)
                game = chess.pgn.read_game(pgn_io)
                
                if game is None:
                    print("✗ Error: Could not parse PGN file")
                    return
                
                # Reset the board
                self.board = chess.Board()
                self.move_history = []
                self.game_moves = []
                self.selected_square = None
                self.last_move = None
                self.game_over = False
                self.hint_move = None
                self.show_hint = False
                
                # Play through all the moves
                for move in game.mainline_moves():
                    self.add_to_history(move)
                    self.game_moves.append(move)
                    self.board.push(move)
                    self.last_move = move
                
                # Check if game is over
                if self.board.is_game_over():
                    self.game_over = True
                
                print(f"✓ Loaded game from {filename}")
                print(f"  {len(self.game_moves)} moves loaded")
                
                # Show headers if available
                if game.headers.get("White"):
                    print(f"  White: {game.headers.get('White')}")
                if game.headers.get("Black"):
                    print(f"  Black: {game.headers.get('Black')}")
                if game.headers.get("Result"):
                    print(f"  Result: {game.headers.get('Result')}")
                    
            except Exception as e:
                print(f"✗ Error loading PGN: {e}")
    
    def load_fen(self):
        """Load a position from FEN string or file"""
        root = tk.Tk()
        root.withdraw()
        
        # First try to get from clipboard
        try:
            clipboard_text = root.clipboard_get()
        except:
            clipboard_text = ""
        
        root.destroy()
        
        # Check if clipboard contains a valid FEN
        fen_to_load = None
        if clipboard_text:
            try:
                test_board = chess.Board(clipboard_text.strip())
                fen_to_load = clipboard_text.strip()
                print(f"Found FEN in clipboard")
            except:
                pass
        
        # If no valid FEN in clipboard, open file dialog
        if not fen_to_load:
            root = tk.Tk()
            root.withdraw()
            
            filename = filedialog.askopenfilename(
                filetypes=[("FEN files", "*.fen"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Load FEN Position"
            )
            
            root.destroy()
            
            if filename:
                try:
                    with open(filename, 'r') as f:
                        fen_to_load = f.read().strip()
                except Exception as e:
                    print(f"✗ Error reading file: {e}")
                    return
        
        if fen_to_load:
            try:
                self.board = chess.Board(fen_to_load)
                self.move_history = []
                self.game_moves = []
                self.selected_square = None
                self.last_move = None
                self.game_over = self.board.is_game_over()
                self.hint_move = None
                self.show_hint = False
                self.game_start_time = datetime.now()
                
                print(f"✓ Position loaded from FEN")
                print(f"  {fen_to_load}")
            except Exception as e:
                print(f"✗ Invalid FEN: {e}")
    
    def copy_fen(self):
        """Copy FEN to clipboard"""
        fen = self.board.fen()
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(fen)
        root.update()
        root.destroy()
        print(f"✓ FEN copied to clipboard: {fen}")
    
    def show_controls(self):
        """Show controls dialog"""
        self.dialog_title = "Controls"
        self.dialog_text = [
            "Mouse Controls:",
            "  Click piece to select",
            "  Click destination to move",
            "",
            "Keyboard Shortcuts:",
            "  H - Show hint",
            "  Ctrl+Z - Undo move",
            "  Ctrl+N - New game",
            "  F - Flip board",
            "  Esc - Close dialog",
        ]
        self.showing_dialog = True
    
    def show_about(self):
        """Show about dialog"""
        self.dialog_title = "About PyChess"
        self.dialog_text = [
            "PyChess v1.0",
            "",
            "A chess game powered by",
            "Stockfish engine",
            "",
            "Built with Python & Pygame",
            "",
            "Press Esc to close",
        ]
        self.showing_dialog = True
    
    def _draw_menu_bar_background(self, surface):
        """Draw just the menu bar (dropdowns drawn later)"""
        self.menu_bar.draw(surface)
    
    def draw_dialog(self, surface):
        """Draw modal dialog overlay"""
        if not self.showing_dialog:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((FULL_WIDTH, BOARD_SIZE + MENU_BAR_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_width = 300
        dialog_height = 50 + len(self.dialog_text) * 25
        dialog_x = (FULL_WIDTH - dialog_width) // 2
        dialog_y = (BOARD_SIZE + MENU_BAR_HEIGHT - dialog_height) // 2
        
        pygame.draw.rect(surface, (50, 50, 50), (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=8)
        pygame.draw.rect(surface, (100, 100, 100), (dialog_x, dialog_y, dialog_width, dialog_height), 2, border_radius=8)
        
        # Title
        title_font = pygame.font.Font(None, 28)
        title = title_font.render(self.dialog_title, True, (255, 255, 255))
        surface.blit(title, (dialog_x + 15, dialog_y + 15))
        
        # Content
        content_font = pygame.font.Font(None, 22)
        y = dialog_y + 45
        for line in self.dialog_text:
            text = content_font.render(line, True, (200, 200, 200))
            surface.blit(text, (dialog_x + 15, y))
            y += 25


    def draw_info_panel(self, surface):
        # Draw panel background
        panel_rect = pygame.Rect(BOARD_SIZE, MENU_BAR_HEIGHT, INFO_PANEL_WIDTH, BOARD_SIZE)
        pygame.draw.rect(surface, (40, 40, 40), panel_rect)
        
        # Title
        font_title = pygame.font.Font(None, 28)
        title = font_title.render("Move History", True, (255, 255, 255))
        surface.blit(title, (BOARD_SIZE + 10, MENU_BAR_HEIGHT + 10))
        
        # Show difficulty
        font_small = pygame.font.Font(None, 18)
        diff_text = font_small.render(f"Difficulty: {self.difficulty}", True, (150, 150, 150))
        surface.blit(diff_text, (BOARD_SIZE + 10, MENU_BAR_HEIGHT + 35))
        
        # Draw moves
        font_moves = pygame.font.Font(None, 20)
        y_offset = MENU_BAR_HEIGHT + 60
        for i, move_text in enumerate(self.move_history[-12:]):  # Show last 12 moves
            color = (255, 255, 255) if i == len(self.move_history[-12:]) - 1 else (180, 180, 180)
            text = font_moves.render(move_text, True, color)
            surface.blit(text, (BOARD_SIZE + 10, y_offset + i * 25))
        
        # Show current turn
        turn_text = "White to move" if self.board.turn == chess.WHITE else "Black to move"
        turn_color = (255, 255, 255) if self.board.turn == chess.WHITE else (100, 100, 100)
        turn_surface = font_title.render(turn_text, True, turn_color)
        surface.blit(turn_surface, (BOARD_SIZE + 10, BOARD_SIZE + MENU_BAR_HEIGHT - 100))
        
        # Show game status
        if self.game_over:
            result_text = self.get_result()
            result_surface = font_moves.render(result_text, True, (255, 100, 100))
            surface.blit(result_surface, (BOARD_SIZE + 10, BOARD_SIZE + MENU_BAR_HEIGHT - 50))
        
    def get_hint(self):
        """Get the best move suggestion from Stockfish"""
        if not self.game_over and self.board.turn == self.player_color and not self.current_animation:
            # Get Stockfish's recommendation
            result = self.engine.play(self.board, chess.engine.Limit(time=0.5))
            self.hint_move = result.move
            self.show_hint = True
            
            # Print hint to console as well
            from_square = chess.square_name(result.move.from_square)
            to_square = chess.square_name(result.move.to_square)
            
            # Get piece name for clearer hint
            piece = self.board.piece_at(result.move.from_square)
            piece_name = {
                chess.PAWN: "Pawn",
                chess.KNIGHT: "Knight", 
                chess.BISHOP: "Bishop",
                chess.ROOK: "Rook",
                chess.QUEEN: "Queen",
                chess.KING: "King"
            }.get(piece.piece_type, "Piece")
            
            print(f"💡 Hint: Move {piece_name} from {from_square} to {to_square}")
            return result.move
        return None
    
    def start_animation(self, move):
        """Start animating a piece move"""
        piece = self.board.piece_at(move.from_square)
        if piece:
            piece_image = self.pieces[piece.symbol()]
            self.current_animation = PieceAnimation(piece, move.from_square, move.to_square, piece_image, self.board_flipped)
            # Store board state before move for drawing
            self.animation_board = self.board.copy()
    
    def handle_click(self, pos):
        # Ignore clicks outside the board or in menu area
        if pos[0] >= BOARD_SIZE or pos[1] < MENU_BAR_HEIGHT:
            return
        if self.game_over or self.board.turn != self.player_color or self.current_animation:
            return
        if self.showing_dialog:
            return
        
        # Clear hint when making a move
        self.show_hint = False
        self.hint_move = None
        
        square = get_square_from_mouse(pos, self.board_flipped)
        
        if self.selected_square is None:
            # Select a piece
            piece = self.board.piece_at(square)
            if piece and piece.color == self.player_color:
                self.selected_square = square
        else:
            # Try to make a move
            move = chess.Move(self.selected_square, square)
            
            # Check for pawn promotion
            piece_at_selected = self.board.piece_at(self.selected_square)
            if (piece_at_selected and piece_at_selected.piece_type == chess.PAWN and
                chess.square_rank(square) in [0, 7]):
                move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
            
            if move in self.board.legal_moves:
                # Start animation
                self.start_animation(move)
                self.add_to_history(move)
                self.game_moves.append(move)  # Track for PGN export
                self.play_move_sound(move)
                self.board.push(move)
                self.last_move = move
                self.selected_square = None
                
                # Check game over
                if self.board.is_game_over():
                    self.game_over = True
                    print("Game Over!", self.get_result())
            else:
                # Select new piece or deselect
                piece = self.board.piece_at(square)
                if piece and piece.color == self.player_color:
                    self.selected_square = square
                else:
                    self.selected_square = None
    
    def make_engine_move(self):
        if not self.game_over and self.board.turn != self.player_color and not self.current_animation:
            if not self.engine_thinking and self.engine_move_pending is None:
                # Start thinking with difficulty-based limits
                self.engine_thinking = True
                
                # Build limit based on difficulty settings
                if self.engine_depth:
                    limit = chess.engine.Limit(time=self.engine_time, depth=self.engine_depth)
                else:
                    limit = chess.engine.Limit(time=self.engine_time)
                
                result = self.engine.play(self.board, limit)
                self.engine_move_pending = result.move
                self.engine_move_timer = pygame.time.get_ticks() + 500  # 0.5 second delay before moving
                
                # Show what piece will be moved
                from_square = chess.square_name(result.move.from_square)
                to_square = chess.square_name(result.move.to_square)
                piece = self.board.piece_at(result.move.from_square)
                piece_name = {
                    chess.PAWN: "Pawn",
                    chess.KNIGHT: "Knight", 
                    chess.BISHOP: "Bishop",
                    chess.ROOK: "Rook",
                    chess.QUEEN: "Queen",
                    chess.KING: "King"
                }.get(piece.piece_type, "Piece")
                
                print(f"🤖 Stockfish ({self.difficulty}): {piece_name} {from_square} → {to_square}")
                self.engine_thinking = False
            
            # Check if it's time to make the pending move
            if self.engine_move_pending and pygame.time.get_ticks() >= self.engine_move_timer:
                # Start animation for engine move
                self.start_animation(self.engine_move_pending)
                self.play_move_sound(self.engine_move_pending)
                self.add_to_history(self.engine_move_pending)
                self.game_moves.append(self.engine_move_pending)  # Track for PGN export
                self.board.push(self.engine_move_pending)
                self.last_move = self.engine_move_pending
                self.engine_move_pending = None
                
                # Clear any hint after engine moves
                self.show_hint = False
                self.hint_move = None
                
                if self.board.is_game_over():
                    self.game_over = True
                    print("Game Over!", self.get_result())
    
    def update_animation(self):
        """Update current animation"""
        if self.current_animation:
            if self.current_animation.update():
                # Animation complete
                self.current_animation = None
                self.animation_board = None
    
    def get_result(self):
        if self.board.is_checkmate():
            return "Checkmate! " + ("White wins!" if self.board.turn == chess.BLACK else "Black wins!")
        elif self.board.is_stalemate():
            return "Stalemate!"
        elif self.board.is_insufficient_material():
            return "Draw - Insufficient material!"
        elif self.board.is_fifty_moves():
            return "Draw - 50 move rule!"
        else:
            return "Draw!"
    
    def draw(self, surface):
        # Draw menu bar background (but not dropdowns yet)
        self._draw_menu_bar_background(surface)
        
        draw_board(surface, self.board_flipped, self.show_coordinates)
        
        # Draw last move highlight
        if self.last_move and not self.current_animation:
            draw_last_move(surface, self.last_move, self.board_flipped)
        
        draw_selection(surface, self.selected_square, self.board_flipped)
        
        # Only show possible moves when not animating
        if not self.current_animation:
            draw_possible_moves(surface, self.board, self.selected_square, self.board_flipped)
        
        # Draw hint if active
        if self.show_hint and self.hint_move:
            draw_hint(surface, self.hint_move, self.board_flipped)
            
        self.draw_info_panel(surface)
        
        # Draw pieces
        if self.current_animation:
            # Draw board without the animating piece
            animated_squares = [self.current_animation.from_square, self.current_animation.to_square]
            draw_pieces(surface, self.animation_board, self.pieces, animating_piece=self.current_animation, animated_squares=animated_squares, flipped=self.board_flipped)
            # Draw the animating piece
            self.current_animation.draw(surface)
        else:
            draw_pieces(surface, self.board, self.pieces, flipped=self.board_flipped)
        
        # Draw hint button in menu bar
        self.hint_button_rect = draw_hint_button(surface, self.show_hint)
        # if self.show_hint:
            # draw_hint_text(surface)
        
        # Draw menu dropdowns LAST so they appear on top of everything
        self.menu_bar.draw_dropdowns(surface)
        
        # Draw dialog if showing
        self.draw_dialog(surface)
    
    def cleanup(self):
        self.engine.quit()
    
# Main game loop
def main():
    # CHANGE THIS PATH to where you extracted stockfish.exe
    if is_windows:
        STOCKFISH_PATH = r"C:\Users\woland\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"
    elif is_linux:
        STOCKFISH_PATH = "/home/woland/pychess/stockfish/stockfish-ubuntu-x86-64-avx2"
    
    # Check if stockfish exists
    if not Path(STOCKFISH_PATH).exists():
        print(f"Stockfish not found at {STOCKFISH_PATH}")
        print("Please download Stockfish from https://stockfishchess.org/download/")
        print("And update the STOCKFISH_PATH variable in the code")
        return
    
    clock = pygame.time.Clock()
    game = ChessGame(STOCKFISH_PATH)
    running = True
    
    print("=== Chess Game Started ===")
    print("Press 'H' for hint")
    print("Click pieces to move")
    print("Use menu bar for options")
    print("=========================")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if hint button clicked (in menu bar)
                    if hasattr(game, 'hint_button_rect') and game.hint_button_rect and game.hint_button_rect.collidepoint(event.pos):
                        game.get_hint()
                        continue
                    
                    # First check if clicking in menu area
                    if game.menu_bar.handle_click(event.pos):
                        continue
                    
                    # Close dialog on click
                    if game.showing_dialog:
                        game.showing_dialog = False
                        continue
                    
                    # Handle board clicks
                    game.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                # Handle menu hover for switching between open menus
                game.menu_bar.handle_hover(event.pos)
            elif event.type == pygame.KEYDOWN:
                # Close dialog on Escape
                if event.key == pygame.K_ESCAPE:
                    if game.showing_dialog:
                        game.showing_dialog = False
                    elif game.menu_bar.active_menu:
                        game.menu_bar.active_menu = None
                elif event.key == pygame.K_h:  # Press H for hint
                    if not game.showing_dialog:
                        game.get_hint()
                elif event.key == pygame.K_f:  # Press F to flip board
                    if not game.showing_dialog:
                        game.flip_board()
                        # Update menu checkbox
                        for menu in game.menu_bar.menus:
                            if menu.title == "Game":
                                for item in menu.items:
                                    if item.action == "flip_board":
                                        item.checked = game.board_flipped
                elif event.key == pygame.K_n and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Ctrl+N for new game
                    game.new_game()
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Ctrl+Z for undo
                    game.undo_move()
        
        # Update animation
        game.update_animation()
        
        # Make engine move if it's the engine's turn (and no dialog open)
        if not game.game_over and game.board.turn != game.player_color and not game.showing_dialog:
            game.make_engine_move()
        
        # Draw everything
        game.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    # Cleanup
    game.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
