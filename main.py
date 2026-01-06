import pygame
import chess
import chess.engine
import sys
from pathlib import Path
import math

# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
HIGHLIGHT = (255, 255, 0, 128)
MOVE_HINT = (0, 255, 0, 64)
ANIMATION_SPEED = 8  # Higher = faster animation
INFO_PANEL_WIDTH = 200
FULL_WIDTH = BOARD_SIZE + INFO_PANEL_WIDTH


# Update screen initialization
screen = pygame.display.set_mode((FULL_WIDTH, BOARD_SIZE))
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
		pygame.font.Font(None, 60)	# Default
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

# Draw pieces (modified to handle animations)
def draw_pieces(surface, board, pieces, animating_piece=None, animated_squares=None):
	for row in range(8):
		for col in range(8):
			square = chess.square(col, 7 - row)  # Flip board vertically
			
			# Skip drawing piece if it's being animated
			if animated_squares and square in animated_squares:
				continue
				
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
				# Draw a circle in the center of valid move squares
				center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
				center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
				
				# Check if there's a piece to capture
				if board.piece_at(move.to_square):
					pygame.draw.circle(surface, (255, 0, 0, 100), (center_x, center_y), 20, 3)
				else:
					pygame.draw.circle(surface, (0, 150, 0, 150), (center_x, center_y), 10)

# Draw hint arrow
def draw_hint(surface, move):
	if move:
		# Get coordinates for from and to squares
		from_col = chess.square_file(move.from_square)
		from_row = 7 - chess.square_rank(move.from_square)
		to_col = chess.square_file(move.to_square)
		to_row = 7 - chess.square_rank(move.to_square)
		
		# Calculate center points of squares
		from_x = from_col * SQUARE_SIZE + SQUARE_SIZE // 2
		from_y = from_row * SQUARE_SIZE + SQUARE_SIZE // 2
		to_x = to_col * SQUARE_SIZE + SQUARE_SIZE // 2
		to_y = to_row * SQUARE_SIZE + SQUARE_SIZE // 2
		
		# Draw arrow for hint
		pygame.draw.line(surface, (255, 0, 255), (from_x, from_y), (to_x, to_y), 5)
		
		# Draw arrow head
		pygame.draw.circle(surface, (255, 0, 255), (to_x, to_y), 10)
		
		# Highlight the squares
		hint_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
		hint_surface.fill((255, 0, 255, 100))
		surface.blit(hint_surface, (from_col * SQUARE_SIZE, from_row * SQUARE_SIZE))
		surface.blit(hint_surface, (to_col * SQUARE_SIZE, to_row * SQUARE_SIZE))

# Draw hint button
def draw_hint_button(surface):
	button_rect = pygame.Rect(BOARD_SIZE - 100, 10, 90, 30)
	pygame.draw.rect(surface, (100, 200, 100), button_rect)
	pygame.draw.rect(surface, (0, 0, 0), button_rect, 2)
	
	font = pygame.font.Font(None, 24)
	text = font.render("Hint (H)", True, (0, 0, 0))
	text_rect = text.get_rect(center=button_rect.center)
	surface.blit(text, text_rect)

# Draw hint text
def draw_hint_text(surface):
	font = pygame.font.Font(None, 20)
	text = font.render("Best move shown in purple", True, (255, 0, 255))
	surface.blit(text, (10, 10))

def draw_last_move(surface, move):
	if move:
		# Highlight the last move squares with subtle color
		from_col = chess.square_file(move.from_square)
		from_row = 7 - chess.square_rank(move.from_square)
		to_col = chess.square_file(move.to_square)
		to_row = 7 - chess.square_rank(move.to_square)
		
		# Draw with a subtle yellow highlight
		last_move_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
		last_move_surface.fill((255, 255, 100, 50))
		surface.blit(last_move_surface, (from_col * SQUARE_SIZE, from_row * SQUARE_SIZE))
		surface.blit(last_move_surface, (to_col * SQUARE_SIZE, to_row * SQUARE_SIZE))

# Animation class for smooth piece movement
class PieceAnimation:
	def __init__(self, piece, from_square, to_square, piece_image):
		self.piece = piece
		self.from_square = from_square
		self.to_square = to_square
		self.piece_image = piece_image
		
		# Calculate pixel positions
		from_col = chess.square_file(from_square)
		from_row = 7 - chess.square_rank(from_square)
		to_col = chess.square_file(to_square)
		to_row = 7 - chess.square_rank(to_square)
		
		self.start_x = from_col * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_width()) // 2
		self.start_y = from_row * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_height()) // 2
		self.end_x = to_col * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_width()) // 2
		self.end_y = to_row * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_height()) // 2
		
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
		self.board = chess.Board()
		self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
		self.pieces = load_pieces()
		self.selected_square = None
		self.player_color = chess.WHITE  # Player is white
		self.game_over = False
		self.hint_move = None  # Store the hint move
		self.show_hint = False	# Toggle hint display
		self.last_move = None  # Store last move for highlighting
		self.engine_thinking = False  # Flag for when engine is thinking
		self.engine_move_pending = None  # Store pending engine move
		self.engine_move_timer = 0	# Timer for delayed move
		self.current_animation = None  # Current piece animation
		self.animation_board = None  # Board state during animation
	
		self.move_history = []

	# # Add this method to ChessGame class
	# def add_to_history(self, move):
	#	  # Convert to algebraic notation
	#	  san = self.board.san(move)
	#	  move_number = (len(self.move_history) // 2) + 1
		
	#	  if self.board.turn == chess.BLACK:  # Just made white's move
	#		  self.move_history.append(f"{move_number}. {san}")
	#	  else:  # Just made black's move
	#		  if self.move_history and not self.move_history[-1].endswith("..."):
	#			  self.move_history[-1] += f" {san}"
	#		  else:
	#			  self.move_history.append(f"{move_number}... {san}")
	
	def add_to_history(self, move):
	# Get the move in SAN before pushing it
		san = self.board.san(move)
		move_number = len(self.move_history) // 2 + 1
	
		if self.board.turn == chess.WHITE:	# Black just moved
			if self.move_history and "..." not in self.move_history[-1]:
				self.move_history[-1] += f" {san}"
			else:
				self.move_history.append(f"{move_number}... {san}")
		else:  # White just moved
			self.move_history.append(f"{move_number}. {san}")

	
	def draw_info_panel(self, surface):
		# Draw panel background
		panel_rect = pygame.Rect(BOARD_SIZE, 0, INFO_PANEL_WIDTH, BOARD_SIZE)
		pygame.draw.rect(surface, (40, 40, 40), panel_rect)
		
		# Title
		font_title = pygame.font.Font(None, 28)
		title = font_title.render("Move History", True, (255, 255, 255))
		surface.blit(title, (BOARD_SIZE + 10, 10))
		
		# Draw moves
		font_moves = pygame.font.Font(None, 20)
		y_offset = 50
		for i, move_text in enumerate(self.move_history[-15:]):  # Show last 15 moves
			color = (255, 255, 255) if i == len(self.move_history) - 1 else (180, 180, 180)
			text = font_moves.render(move_text, True, color)
			surface.blit(text, (BOARD_SIZE + 10, y_offset + i * 25))
		
		# Show current turn
		turn_text = "White to move" if self.board.turn == chess.WHITE else "Black to move"
		turn_color = (255, 255, 255) if self.board.turn == chess.WHITE else (100, 100, 100)
		turn_surface = font_title.render(turn_text, True, turn_color)
		surface.blit(turn_surface, (BOARD_SIZE + 10, BOARD_SIZE - 100))
		
		# Show game status
		if self.game_over:
			result_text = self.get_result()
			result_surface = font_moves.render(result_text, True, (255, 100, 100))
			surface.blit(result_surface, (BOARD_SIZE + 10, BOARD_SIZE - 50))
		
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
			self.current_animation = PieceAnimation(piece, move.from_square, move.to_square, piece_image)
			# Store board state before move for drawing
			self.animation_board = self.board.copy()
	
	def handle_click(self, pos):
			# Ignore clicks outside the board
		if pos[0] >= BOARD_SIZE:
			return
		if self.game_over or self.board.turn != self.player_color or self.current_animation:
			return
		
		# Clear hint when making a move
		self.show_hint = False
		self.hint_move = None
		
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
				# Start animation
				self.start_animation(move)
				self.add_to_history(move)  # ADD THIS LINE
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
				# Start thinking
				self.engine_thinking = True
				result = self.engine.play(self.board, chess.engine.Limit(time=1.0))
				self.engine_move_pending = result.move
				self.engine_move_timer = pygame.time.get_ticks() + 500	# 0.5 second delay before moving
				
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
				
				print(f"🤖 Stockfish: {piece_name} {from_square} → {to_square}")
				self.engine_thinking = False
			
			# Check if it's time to make the pending move
			if self.engine_move_pending and pygame.time.get_ticks() >= self.engine_move_timer:
				# Start animation for engine move
				self.start_animation(self.engine_move_pending)
				self.add_to_history(self.engine_move_pending)  # ADD THIS LINE
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
		draw_board(surface)
		
		# Draw last move highlight
		if self.last_move and not self.current_animation:
			draw_last_move(surface, self.last_move)
		
		draw_selection(surface, self.selected_square)
		
		# Only show possible moves when not animating
		if not self.current_animation:
			draw_possible_moves(surface, self.board, self.selected_square)
		
		# Draw hint if active
		if self.show_hint and self.hint_move:
			draw_hint(surface, self.hint_move)
			
		self.draw_info_panel(surface)
		
		# Draw pieces
		if self.current_animation:
			# Draw board without the animating piece
			animated_squares = [self.current_animation.from_square, self.current_animation.to_square]
			draw_pieces(surface, self.animation_board, self.pieces, animating_piece=self.current_animation, animated_squares=animated_squares)
			# Draw the animating piece
			self.current_animation.draw(surface)
		else:
			draw_pieces(surface, self.board, self.pieces)
		
		# Draw hint button
		draw_hint_button(surface)
		if self.show_hint:
			draw_hint_text(surface)
	
	def cleanup(self):
		self.engine.quit()
	
# Main game loop
def main():
	# CHANGE THIS PATH to where you extracted stockfish.exe
	STOCKFISH_PATH = r"C:\Users\woland\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"
	
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
	print("=========================")
	
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:  # Left click
					# Check if hint button clicked
					button_rect = pygame.Rect(BOARD_SIZE - 100, 10, 90, 30)
					if button_rect.collidepoint(event.pos):
						game.get_hint()
					else:
						game.handle_click(event.pos)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_h:  # Press H for hint
					game.get_hint()
		
		# Update animation
		game.update_animation()
		
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
