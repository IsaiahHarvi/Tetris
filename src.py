

import pygame 
import random

# Constants
SCREEN_X = 800
SCREEN_Y = 600
WIDTH, HEIGHT = 300, 600  # This gives each block a size of 30x30
ROWS, COLS = 20, 10
BLOCK_SIZE = WIDTH // COLS
DROP_INTERVAL = 1000  # Drop every second


# Start the game grid at the center of the screen
GRID_OFFSET_X = (SCREEN_X - WIDTH) // 2
GRID_OFFSET_Y = (SCREEN_Y - HEIGHT) // 2

mappedKeys = {
    "left" : [pygame.K_LEFT, pygame.K_a],
    "right" : [pygame.K_RIGHT, pygame.K_d],
    "down" : [pygame.K_DOWN, pygame.K_s],
    "rotate" : [pygame.K_r],
}
allMappedKeys = [key for sublist in mappedKeys.values() for key in sublist]


# Functions
def drawGrid(screen):
    for row in range(ROWS):
        for col in range(COLS):
            x = GRID_OFFSET_X + col * BLOCK_SIZE
            y = GRID_OFFSET_Y + row * BLOCK_SIZE
            pygame.draw.rect(screen, (255, 255, 255), (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)


def grid_to_pixel(grid_x, grid_y):
    return GRID_OFFSET_X + grid_x * BLOCK_SIZE, GRID_OFFSET_Y + grid_y * BLOCK_SIZE


def collision(board, blocks):
    for x, y in blocks:
        if y >= ROWS-1 or board[y+1][x]:
            return True
    return False


def placePiece(board, piece):
    for x, y in piece.blocks:
        board[y][x] = piece.BLOCK_COLOR


def drawBoard(screen, board):
    for y in range(ROWS):
        for x in range(COLS):
            if board[y][x]:
                pixel_x, pixel_y = grid_to_pixel(x, y)
                pygame.draw.rect(screen, board[y][x], (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE))

# Pieces
class Square: 
    def __init__ (self, grid_x=(COLS // 2 - 1), grid_y=0):
        self.BLOCK_COLOR = random.choice([(0, 255, 255), (50, 205, 50), (191, 64, 191), (255, 165, 0), (255, 255, 204), (173, 216, 230), (255, 0, 0)])

        # Using grid coordinates for blocks
        self.blocks = [
            (grid_x, grid_y),
            (grid_x + 1, grid_y),
            (grid_x, grid_y + 1),
            (grid_x + 1, grid_y + 1)
        ]

    def move(self, dx, dy):
        positions = [(x + dx, y + dy) for x, y in self.blocks]
        
        # Check boundaries
        if any(x < 0 or x >= COLS or y >= ROWS for x, y in positions):
            return
        
        self.blocks = positions

    def draw(self, screen):
        for x, y in self.blocks:
            # Convert grid coordinates to pixel coordinates
            pixel_x = GRID_OFFSET_X + x * BLOCK_SIZE
            pixel_y = GRID_OFFSET_Y + y * BLOCK_SIZE
            pygame.draw.rect(screen, self.BLOCK_COLOR, (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE))



pieces = [Square]