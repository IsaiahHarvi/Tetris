

import pygame 
import random
import time

# CONSTANTS
# Screen
SCREEN_X = 800 # Screen Boundaries
SCREEN_Y = 800 # Screen Boundaries
WIDTH, HEIGHT = 300, 600  # This gives each block a size of 30x30
ROWS, COLS = 20, 10 # Grid Size
BLOCK_SIZE = WIDTH // COLS # Size of each block in pixels

# Next Box
NEXT_BOX_X = 50
NEXT_BOX_Y = 150  
NEXT_BOX_WIDTH = BLOCK_SIZE * 4
NEXT_BOX_HEIGHT = BLOCK_SIZE * 4

# Score Box
SCORE_BOX_X = SCREEN_X - NEXT_BOX_X - NEXT_BOX_WIDTH
SCORE_BOX_Y = NEXT_BOX_Y
SCORE_BOX_WIDTH = NEXT_BOX_WIDTH
SCORE_BOX_HEIGHT = NEXT_BOX_HEIGHT

# Start the game grid at the center of the screen
GRID_OFFSET_X = (SCREEN_X - WIDTH) // 2
GRID_OFFSET_Y = (600 - HEIGHT) // 2 + 100

# Dict of keybinds
mappedKeys = {
    "left" : [pygame.K_LEFT, pygame.K_a],
    "right" : [pygame.K_RIGHT, pygame.K_d],
    "down" : [pygame.K_DOWN, pygame.K_s],
    "rotate" : [pygame.K_r],
    "drop" : [pygame.K_SPACE, pygame.K_RETURN]
}
allMappedKeys = [key for sublist in mappedKeys.values() for key in sublist] # All mapped keys in a list

# Initialize pygame
pygame.init()
pygame.mixer.init()
clk = pygame.time.Clock()
lastDrop = pygame.time.get_ticks() # Variable to track time since the last drop to move the block down every 1 sec

# Create the screen
screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y)) # 600, 800
pygame.display.set_caption("Tetris")
pygame.display.set_icon(pygame.image.load("Assets/icon.jpg"))

# Background Music
pygame.mixer.music.load("Assets/soundtrack.mp3")
pygame.mixer.music.play(-1) # Loop
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.pause()
soundOn = False

# Board
board = [[None for _ in range(COLS)] for _ in range(ROWS)] # 2D list of None values

# Score
score = 0 # Starts at zero adds 100 every row; 4 rows = 400, 4 rows at once = 800

DROP_INTERVAL =  1000 + (250 * score/1000)  # Drop every second and add .25 seconds every 10 blocks

# DRAW FUNCTIONS
def drawGrid(screen=screen):
    for row in range(ROWS):
        for col in range(COLS):
            x = GRID_OFFSET_X + col * BLOCK_SIZE
            y = GRID_OFFSET_Y + row * BLOCK_SIZE
            pygame.draw.rect(screen, (150, 150, 150), (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)  # Slightly lighter color for inner grid
    
    # Draw the thick border around the game grid
    pygame.draw.rect(screen, (255,255,255), (GRID_OFFSET_X - 4, GRID_OFFSET_Y - 4, WIDTH + 2 * 4, HEIGHT + 2 * 4), 4)
    
    # Draw the outer NEXT box
    pygame.draw.rect(screen, (255, 255, 255), (NEXT_BOX_X, NEXT_BOX_Y, NEXT_BOX_WIDTH, NEXT_BOX_HEIGHT), 4)

    # Draw the "NEXT" label
    font = pygame.font.SysFont(None, 36)
    label = font.render("NEXT", True, (255, 255, 255))
    screen.blit(label, (NEXT_BOX_X + (NEXT_BOX_WIDTH - label.get_width()) // 2, NEXT_BOX_Y + NEXT_BOX_HEIGHT + 10))

    # Draw the outer SCORE box
    pygame.draw.rect(screen, (255, 255, 255), (SCORE_BOX_X, SCORE_BOX_Y, SCORE_BOX_WIDTH, SCORE_BOX_HEIGHT), 4)
    
    # Draw the "SCORE" label
    font = pygame.font.SysFont(None, 36)  
    label = font.render("SCORE", True, (255, 255, 255))
    screen.blit(label, (SCORE_BOX_X + (SCORE_BOX_WIDTH - label.get_width()) // 2, SCORE_BOX_Y + SCORE_BOX_HEIGHT + 10))
    
    
# Draw next piece inside of the box created by the grid
def drawNextPiece(piece, screen=screen):
    # Calculate the width of the piece in blocks
    min_x, min_y = min((block[0], block[1]) for block in piece.blocks)
    max_x, max_y = max((block[0], block[1]) for block in piece.blocks)
    pieceWidth = (max_x - min_x + 1) * BLOCK_SIZE
    pieceHeight = (max_y - min_y + 1) * BLOCK_SIZE

    # Draw the next piece inside the next box
    offsetX = (NEXT_BOX_WIDTH - pieceWidth) // 2
    offsetY = (NEXT_BOX_HEIGHT - pieceHeight) // 2
    
    for block in piece.blocks:
        pygame.draw.rect(screen, piece.BLOCK_COLOR, (NEXT_BOX_X + (block[0] - min_x)*BLOCK_SIZE + offsetX, NEXT_BOX_Y + (block[1] - min_y)*BLOCK_SIZE + offsetY, BLOCK_SIZE, BLOCK_SIZE))

# Draw Sound button
def soundButton(text, screen=screen):
    pygame.draw.rect(screen, (255,255,255), (20, 700, 100, 50))
    font = pygame.font.SysFont(None, 24)  # Adjust font size if needed
    label = font.render(text, True, (0,0,0))
    screen.blit(label, (20 + 100 // 2 - label.get_width() // 2, 700 + 50 // 2 - label.get_height() // 2))

# Show the score inside the box generated by the grid
def drawScore(score=score, screen=screen):
    font = pygame.font.SysFont(None, 32)
    score_label = font.render(str(score), True, (255, 255, 255))
    screen.blit(score_label, (SCORE_BOX_X + (SCORE_BOX_WIDTH - score_label.get_width()) // 2, SCORE_BOX_Y + (SCORE_BOX_HEIGHT - score_label.get_height()) // 2))

# Draw the board to the screen
def drawBoard(screen=screen, board=board):
    for y in range(ROWS):
        for x in range(COLS):
            if board[y][x]:
                pixel_x, pixel_y = grid_to_pixel(x, y)
                pygame.draw.rect(screen, board[y][x], (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE))

# HELPER FUNCTIONS 
# Compute the pixel coordinates of a block given its grid coordinates
def grid_to_pixel(grid_x, grid_y):
    return GRID_OFFSET_X + grid_x * BLOCK_SIZE, GRID_OFFSET_Y + grid_y * BLOCK_SIZE

# Check if the piece has collided with the board or the ground
def collision(blocks, board=board, screen=screen):
    for x, y in blocks:
        if y >= ROWS-1 or board[y+1][x]:
            if y <= -1 or board[y][x]:
                return 2
            return 1
    return 0

# Place the piece on the board
def placePiece(piece, board=board):
    for x, y in piece.blocks:
        board[y][x] = piece.BLOCK_COLOR

# Remove rows with a full set of blocks
def removeCompletedRows(board=board):
    rowsToRemove = []  # A list to keep track of which rows to remove
    for y in range(ROWS):
        if all(board[y][x] for x in range(COLS)):  # If the entire row is filled
            rowsToRemove.append(y)

    for y in rowsToRemove:
        del board[y]  # Remove the row
        board.insert(0, [None for _ in range(COLS)])  # Add an empty row at the top

    return len(rowsToRemove)  # Return the number of rows removed for score

# Rotate block around center, clockwise 90 deg
def rotateBlock(block, center):
    rel_x, rel_y = block[0] - center[0], block[1] - center[1]
    new_rel_x, new_rel_y = -rel_y, rel_x
    return center[0] + new_rel_x, center[1] + new_rel_y

# PIECE CLASSES
class Square:
    def __init__ (self, grid_x=(COLS // 2 - 1), grid_y=0):
        self.BLOCK_COLOR = (255, 255, 0)
        self.ID = "SQ"

        # Using grid coordinates for blocks
        self.blocks = [
            (grid_x, grid_y),
            (grid_x + 1, grid_y),
            (grid_x, grid_y + 1),
            (grid_x + 1, grid_y + 1)
        ]

    # Movement
    def move(self, dx, dy):
        positions = [(x + dx, y + dy) for x, y in self.blocks]
        
        # Check boundaries
        if any(x < 0 or x >= COLS or y >= ROWS for x, y in positions):
            return
        self.blocks = positions

    # Rotate the piece around its center block
    def rotate(self):
        pass # What is the point of rotating a 2x2 object?

    # Draw the piece to the screen
    def draw(self, screen=screen):
        for x, y in self.blocks:
            # Convert grid coordinates to pixel coordinates
            pixel_x = GRID_OFFSET_X + x * BLOCK_SIZE
            pixel_y = GRID_OFFSET_Y + y * BLOCK_SIZE
            pygame.draw.rect(screen, self.BLOCK_COLOR, (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE))

# L-Shaped Piece (two variations)
class L:
    def __init__ (self, grid_x=(COLS // 2 - 1), grid_y=0):
        variation = random.randint(0, 1)
        self.BLOCK_COLOR = [(0, 0, 255), (255, 165, 0)][variation]
        self.ID = "L"

        # Using two different types of grid coordinates for blocks
        self.blocks = [
            ([ # Right
            (grid_x, grid_y+1),
            (grid_x, grid_y),
            (grid_x + 1, grid_y+1),
            (grid_x + 2, grid_y+1),
        ]), ([ # Left
            (grid_x, grid_y+1),
            (grid_x, grid_y),
            (grid_x - 1, grid_y+1),
            (grid_x - 2, grid_y+1),
        ])][variation]

    # Movement
    def move(self, dx, dy):
        positions = [(x + dx, y + dy) for x, y in self.blocks]
        
        # Check boundaries
        if any(x < 0 or x >= COLS or y >= ROWS for x, y in positions):
            return
        self.blocks = positions

    # Rotate the piece around its center block
    def rotate(self):
        center = self.blocks[2]  # Assuming the center block is always the second one.
        new_blocks = [rotateBlock(block, center) for block in self.blocks]
        
        # Check boundaries and collisions before accepting the new positions
        if any(x < 0 or x >= COLS or y < 0 or y >= ROWS for x, y in new_blocks):
            return
        self.blocks = new_blocks

    # Draw the piece to the screen
    def draw(self, screen):
        for x, y in self.blocks:
            # Convert grid coordinates to pixel coordinates
            pixel_x = GRID_OFFSET_X + x * BLOCK_SIZE
            pixel_y = GRID_OFFSET_Y + y * BLOCK_SIZE
            pygame.draw.rect(screen, self.BLOCK_COLOR, (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE))

# T-Shaped Piece
class T:
    def __init__ (self, grid_x=(COLS // 2 - 1), grid_y=0):
        self.BLOCK_COLOR = (204, 0, 204)
        self.ID = "T"

        # Using grid coordinates for blocks
        self.blocks = ([ 
            (grid_x, grid_y),
            (grid_x-1, grid_y),
            (grid_x + 1, grid_y),
            (grid_x, grid_y+1)
        ])

    # Movement
    def move(self, dx, dy):
        positions = [(x + dx, y + dy) for x, y in self.blocks]
        
        # Check boundaries
        if any(x < 0 or x >= COLS or y >= ROWS for x, y in positions):
            return
        self.blocks = positions

    # Rotate the piece around its center block
    def rotate(self):
        center = self.blocks[3]
        new_blocks = [rotateBlock(block, center) for block in self.blocks]
        
        # Check boundaries and collisions before accepting the new positions
        if any(x < 0 or x >= COLS or y < 0 or y >= ROWS for x, y in new_blocks):
            return
        self.blocks = new_blocks

    # Draw the piece to the screen
    def draw(self, screen):
        for x, y in self.blocks:
            # Convert grid coordinates to pixel coordinates
            pixel_x = GRID_OFFSET_X + x * BLOCK_SIZE
            pixel_y = GRID_OFFSET_Y + y * BLOCK_SIZE
            pygame.draw.rect(screen, self.BLOCK_COLOR, (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE))

# Straight Piece
class I:
    def __init__ (self, grid_x=(COLS // 2 - 1), grid_y=0):
        self.BLOCK_COLOR = (0, 255, 255)
        self.ID = "I"

        # Using grid coordinates for blocks
        self.blocks = ([ 
            (grid_x, grid_y),
            (grid_x+1, grid_y),
            (grid_x+2, grid_y),
            (grid_x+3, grid_y)
        ])

    # Movement
    def move(self, dx, dy):
        positions = [(x + dx, y + dy) for x, y in self.blocks]
                
        # Check boundaries
        if any(x < 0 or x >= COLS or y >= ROWS for x, y in positions):
            return
        self.blocks = positions

    # Rotate the piece around its center block
    def rotate(self):
        center = self.blocks[2]
        new_blocks = [rotateBlock(block, center) for block in self.blocks]
        
        # Check boundaries and collisions before accepting the new positions
        if any(x < 0 or x >= COLS or y < 0 or y >= ROWS for x, y in new_blocks):
            return
        self.blocks = new_blocks

    # Draw the piece to the screen
    def draw(self, screen):
        for x, y in self.blocks:
            # Convert grid coordinates to pixel coordinates
            pixel_x = GRID_OFFSET_X + x * BLOCK_SIZE
            pixel_y = GRID_OFFSET_Y + y * BLOCK_SIZE
            pygame.draw.rect(screen, self.BLOCK_COLOR, (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE))

# S-Shaped Piece (two variations)
class S:
    def __init__ (self, grid_x=(COLS // 2 - 1), grid_y=0):
        variation = random.randint(0,1)
        self.BLOCK_COLOR = [(50, 205, 50), (255, 0 ,0)][variation]
        self.ID = "S"

        # Using grid coordinates for blocks
        self.blocks = [
            ([(grid_x, grid_y+1), # Right
            (grid_x+1, grid_y+1),
            (grid_x+1, grid_y),
            (grid_x+2, grid_y)]),
            ([(grid_x, grid_y), # Left
            (grid_x+1, grid_y),
            (grid_x+1, grid_y+1),
            (grid_x+2, grid_y+1)
             ]) 
        ][variation]

    # Movement
    def move(self, dx, dy):
        positions = [(x + dx, y + dy) for x, y in self.blocks]
        
        # Check boundaries
        if any(x < 0 or x >= COLS or y >= ROWS for x, y in positions):
            return
        self.blocks = positions

    # Rotate the piece around its center block
    def rotate(self):
        center = self.blocks[2]
        new_blocks = [rotateBlock(block, center) for block in self.blocks]
        
        # Check boundaries and collisions before accepting the new positions
        if any(x < 0 or x >= COLS or y < 0 or y >= ROWS for x, y in new_blocks):
            return
        self.blocks = new_blocks

    # Draw the piece to the screen
    def draw(self, screen):
        for x, y in self.blocks:
            # Convert grid coordinates to pixel coordinates
            pixel_x = GRID_OFFSET_X + x * BLOCK_SIZE
            pixel_y = GRID_OFFSET_Y + y * BLOCK_SIZE
            pygame.draw.rect(screen, self.BLOCK_COLOR, (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE))

# List of all pieces
pieces = [Square, L, T, I, S]