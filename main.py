import pygame
import chess
import chess.engine
import sys
from pathlib import Path

# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
HIGHLIGHT = (255, 255, 0, 128)
MOVE_HINT = (0, 255, 0, 64)

# Initialize display
screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
pygame.display.set_caption("Chess vs Stockfish")

def load_pieces():
    pieces = {}
    piece_map = {
        'P': '♟', 'N': '♞', 'B': '♝', 'R': '♜', 'Q': '♛', 'K': '♚',
        'p': '♙', 'n': '♘', 'b': '♗', 'r': '♖', 'q': '♕', 'k': '♔'
    }
    
    # Try different fonts that support Unicode chess symbols
    fonts_to_try = [
        pygame.font.SysFont('segoeuisymbol', 60),  # Windows
        pygame.font.SysFont('arial', 60),
        pygame.font.SysFont('courier', 60),
        pygame.font.Font(None, 60)  # Default
    ]
    
    font = None
    for test_font in fonts_to_try:
        if test_font:
            font = test_font
            break
    
    if not font:
        font = pygame.font.Font(None, 60)
    
    for key, unicode_char in piece_map.items():
        color = (255, 255, 255) if key.isupper() else (0, 0, 0)
        text_surface = font.render(unicode_char, True, color)
        pieces[key] = text_surface
    
    return pieces


# Draw the board
def draw_board(surface):
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, 
                              SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(surface, color, rect)

# Draw pieces
def draw_pieces(surface, board, pieces):
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)  # Flip board vertically
            piece = board.piece_at(square)
            if piece:
                piece_image = pieces[piece.symbol()]
                x = col * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_width()) // 2
                y = row * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_height()) // 2
                surface.blit(piece_image, (x, y))

# Convert pixel coordinates to chess square
def get_square_from_mouse(pos):
    col = pos[0] // SQUARE_SIZE
    row = 7 - (pos[1] // SQUARE_SIZE)  # Flip vertically
    return chess.square(col, row)

# Highlight selected square
def draw_selection(surface, square):
    if square is not None:
        col = chess.square_file(square)
        row = 7 - chess.square_rank(square)
        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(HIGHLIGHT)
        surface.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Show possible moves
def draw_possible_moves(surface, board, square):
    if square is not None:
        for move in board.legal_moves:
            if move.from_square == square:
                col = chess.square_file(move.to_square)
                row = 7 - chess.square_rank(move.to_square)
                hint_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                hint_surface.fill(MOVE_HINT)
                surface.blit(hint_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Main game class
class ChessGame:
    def __init__(self, stockfish_path):
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.pieces = load_pieces()
        self.selected_square = None
        self.player_color = chess.WHITE  # Player is white
        self.game_over = False
        
    def handle_click(self, pos):
        if self.game_over or self.board.turn != self.player_color:
            return
        
        square = get_square_from_mouse(pos)
        
        if self.selected_square is None:
            # Select a piece
            piece = self.board.piece_at(square)
            if piece and piece.color == self.player_color:
                self.selected_square = square
        else:
            # Try to make a move
            move = chess.Move(self.selected_square, square)
            
            # Check for pawn promotion
            if (self.board.piece_at(self.selected_square).piece_type == chess.PAWN and
                chess.square_rank(square) in [0, 7]):
                move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
            
            if move in self.board.legal_moves:
                self.board.push(move)
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
        if not self.game_over and self.board.turn != self.player_color:
            result = self.engine.play(self.board, chess.engine.Limit(time=1.0))
            self.board.push(result.move)
            
            if self.board.is_game_over():
                self.game_over = True
                print("Game Over!", self.get_result())
    
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
        draw_board(surface)
        draw_selection(surface, self.selected_square)
        draw_possible_moves(surface, self.board, self.selected_square)
        draw_pieces(surface, self.board, self.pieces)
    
    def cleanup(self):
        self.engine.quit()

# Main game loop
def main():
    # CHANGE THIS PATH to where you extracted stockfish.exe
    STOCKFISH_PATH = r"C:\Users\woland\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"  # Update this!
    
    # Check if stockfish exists
    if not Path(STOCKFISH_PATH).exists():
        print(f"Stockfish not found at {STOCKFISH_PATH}")
        print("Please download Stockfish from https://stockfishchess.org/download/")
        print("And update the STOCKFISH_PATH variable in the code")
        return
    
    clock = pygame.time.Clock()
    game = ChessGame(STOCKFISH_PATH)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    game.handle_click(event.pos)
        
        # Make engine move if it's the engine's turn
        if not game.game_over and game.board.turn != game.player_color:
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
