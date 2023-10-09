import pygame 
import random
import os, sys, subprocess

# Check to see if pygame is installed
try:
    import pygame
except ImportError:
    print("pygame is not installed. Installing it now...")
    print("If issues persist, please install it using 'pip install pygame' or 'pip3 install pygame")

    subprocess.call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

# CONSTANTS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'Assets')

# Screen
SCREEN_X = 800 # Screen Boundaries
SCREEN_Y = 800 # Screen Boundaries
WIDTH, HEIGHT = 300, 600  # This gives each block a size of 30x30
ROWS, COLS = 20, 10 # Grid Size
BLOCK_SIZE = WIDTH // COLS # Size of each block in pixels

# Next Box (Holds the preivew piece)
NEXT_BOX_X = 50 
NEXT_BOX_Y = 150  
NEXT_BOX_WIDTH = BLOCK_SIZE * 4
NEXT_BOX_HEIGHT = BLOCK_SIZE * 4

# Score Box and High Score Box
SCORE_BOX_X = SCREEN_X - NEXT_BOX_X - NEXT_BOX_WIDTH
SCORE_BOX_Y = NEXT_BOX_Y
SCORE_BOX_WIDTH = NEXT_BOX_WIDTH
SCORE_BOX_HEIGHT = NEXT_BOX_HEIGHT
HIGH_SCORE_BOX_X = SCORE_BOX_X
HIGH_SCORE_BOX_Y = SCORE_BOX_Y - SCORE_BOX_HEIGHT // 2
HIGH_SCORE_BOX_WIDTH = SCORE_BOX_WIDTH
HIGH_SCORE_BOX_HEIGHT = SCORE_BOX_HEIGHT // 2 # Half the height of the score box

# Start the game grid at the center of the screen
GRID_OFFSET_X = (SCREEN_X - WIDTH) // 2
GRID_OFFSET_Y = (600 - HEIGHT) // 2 + 100

# Dict of keybinds
mappedKeys = {
    "left" : [pygame.K_LEFT, pygame.K_a], # Left and A
    "right" : [pygame.K_RIGHT, pygame.K_d], # Right and D
    "down" : [pygame.K_DOWN, pygame.K_s], # Down and S
    "rotate" : [pygame.K_r], # R
    "drop" : [pygame.K_SPACE, pygame.K_RETURN], # Space and Enter
    "menu" : [pygame.K_ESCAPE, pygame.K_m] # Esc and M
}
allMappedKeys = [key for sublist in mappedKeys.values() for key in sublist] # All mapped keys in a list

# Initialize pygame
pygame.init()
pygame.mixer.init()
clk = pygame.time.Clock()

# Load Assets
try:
    pygame.display.set_icon(pygame.image.load(ASSETS_DIR + "/Icon.PNG")) # Load icon
    pygame.mixer.music.load(ASSETS_DIR + "/soundtrack.mp3") # Load soundtrack
    loseSound = pygame.mixer.Sound(ASSETS_DIR + "/lose.wav") # Load lose sound
    clearSound = pygame.mixer.Sound(ASSETS_DIR + "/clear.wav") # Load clear sound
    dropSound = pygame.mixer.Sound(ASSETS_DIR + "/drop.wav") # Load drop sound
    rotateSound = pygame.mixer.Sound(ASSETS_DIR + "/rotate.wav") # Load rotate sound
    highScore = int((open(ASSETS_DIR + "/highScore.txt", "r").readline())) # Load high score
    overlay = pygame.image.load(ASSETS_DIR + "/overlay.png") # Load NES Overlay
    assets = True
    drawOverlay = True # Set this to false if you do not want the NES overlay
except Exception as e: # If assets are not found, run without them
    assets = False # Assets are not found
    drawOverlay = False
    highScore = 0 # High score is 0 (since it is not saved)

# Create the screen
screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y)) # 600, 800
pygame.display.set_caption("Tetris")

# Background Music
if assets:
    pygame.mixer.music.play(-1) # Loop
    pygame.mixer.music.set_volume(0.05)
    loseSound.set_volume(.5)
    clearSound.set_volume(.20)
    #dropSound.set_volume(.5)
    #rotateSound.set_volume(.5)
    pygame.mixer.music.pause() 
soundOn = False # Start with music off

# DRAW FUNCTIONS
def drawGrid(screen=screen):
    # Draw the black background
    border_rect = pygame.Rect(GRID_OFFSET_X-5, GRID_OFFSET_Y-4, WIDTH+9, HEIGHT+10) 
    pygame.draw.rect(screen, (0, 0, 0), border_rect)

    # Draw the white lines inside the grid | NOTE: This loop can be uncommented to show the grid lines
    #for row in range(ROWS):
    #    for col in range(COLS):
    #        pygame.draw.rect(screen, (150, 150, 150), ((GRID_OFFSET_X + col * BLOCK_SIZE), (GRID_OFFSET_Y + row * BLOCK_SIZE), BLOCK_SIZE, BLOCK_SIZE), 1)  # Slightly lighter color for inner grid
    
    # Draw the thick border around the game grid
    pygame.draw.rect(screen, (255,255,255), (GRID_OFFSET_X - 4, GRID_OFFSET_Y - 4, WIDTH + 2 * 4, HEIGHT + 2 * 4), 5)
    
    # Draw score/highscore and next box
    pygame.draw.rect(screen, (255, 255, 255), (SCORE_BOX_X, SCORE_BOX_Y, SCORE_BOX_WIDTH, SCORE_BOX_HEIGHT), 4) # Score portion
    pygame.draw.rect(screen, (255, 255, 255), (HIGH_SCORE_BOX_X, HIGH_SCORE_BOX_Y, HIGH_SCORE_BOX_WIDTH, HIGH_SCORE_BOX_HEIGHT), 4) # High score portion
    pygame.draw.rect(screen, (255, 255, 255), (NEXT_BOX_X, NEXT_BOX_Y, NEXT_BOX_WIDTH, NEXT_BOX_HEIGHT), 4) # Next box

    # Draw the labels
    scoreLabel = pygame.font.SysFont(None, 36).render("SCORE", True, (255, 255, 255)) # Score label
    screen.blit(scoreLabel, (SCORE_BOX_X + (SCORE_BOX_WIDTH - scoreLabel.get_width()) // 2, SCORE_BOX_Y + SCORE_BOX_HEIGHT + 10)) # Center the label
    nextLabel = pygame.font.SysFont(None, 36).render("NEXT", True, (255, 255, 255)) # Next label
    screen.blit(nextLabel, (NEXT_BOX_X + (NEXT_BOX_WIDTH - nextLabel.get_width()) // 2, NEXT_BOX_Y + NEXT_BOX_HEIGHT + 10)) # Center the label

    if assets and overlay:
        screen.blit(overlay, (-1.5, -6.5)) # Overlay

    
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
    
    for block in piece.blocks: # Draw each block in the piece
        blockPixel_x = NEXT_BOX_X + (block[0] - min_x) * BLOCK_SIZE + offsetX
        blockPixel_y = NEXT_BOX_Y + (block[1] - min_y) * BLOCK_SIZE + offsetY

        pygame.draw.rect(screen, darkerShade(piece.BLOCK_COLOR), (NEXT_BOX_X + (block[0] - min_x)*BLOCK_SIZE + offsetX, NEXT_BOX_Y + (block[1] - min_y)*BLOCK_SIZE + offsetY, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(screen, piece.BLOCK_COLOR, (blockPixel_x + 3, blockPixel_y + 3, BLOCK_SIZE - 6, BLOCK_SIZE - 6))

# Draw Sound button
def soundButton(text, screen=screen):
    if assets:
        pygame.draw.rect(screen, (255,255,255), (20, 700, 100, 50)) # Draw the button
        label = pygame.font.SysFont(None, 24).render(text, True, (0,0,0))
        screen.blit(label, (20 + 100 // 2 - label.get_width() // 2, 700 + 50 // 2 - label.get_height() // 2))

# Show the score inside the box generated by the grid
def drawScore(scoreDict, screen=screen):
    # Show the current score
    scoreNumber = pygame.font.SysFont(None, 32).render(str(scoreDict["score"]), True, (255, 255, 255))
    screen.blit(scoreNumber, (SCORE_BOX_X + (SCORE_BOX_WIDTH - scoreNumber.get_width()) // 2, SCORE_BOX_Y + (SCORE_BOX_HEIGHT - scoreNumber.get_height()) // 2))

    # Show the high score
    highScoreNumber = pygame.font.SysFont(None, 24).render(str(highScore), True, (255, 255, 255))
    screen.blit(highScoreNumber, (HIGH_SCORE_BOX_X + (HIGH_SCORE_BOX_WIDTH - highScoreNumber.get_width()) // 2, HIGH_SCORE_BOX_Y + (HIGH_SCORE_BOX_HEIGHT - highScoreNumber.get_height()) // 2))

# Draw the pieces to the screen pulling from the board
def drawBoard(board, screen=screen):
    for y in range(ROWS):
        for x in range(COLS):
            if board[y][x]:
                pixel_x, pixel_y = grid_to_pixel(x, y)
                pygame.draw.rect(screen, darkerShade(board[y][x]), (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE)) # Draw the darker outline
                pygame.draw.rect(screen, board[y][x], (pixel_x + 3, pixel_y + 3, BLOCK_SIZE - 6, BLOCK_SIZE - 6))
            

# HELPER FUNCTIONS 
# Compute the pixel coordinates of a block given its grid coordinates
def grid_to_pixel(grid_x, grid_y):
    return GRID_OFFSET_X + grid_x * BLOCK_SIZE, GRID_OFFSET_Y + grid_y * BLOCK_SIZE

# Darken RGB values of a color
def darkerShade(color, shade_percentage=0.7):
    return tuple(int(value * shade_percentage) for value in color)

# Using the NES Tetris scoring system
def updateScore(scoreDict):
    scoreDict["totalClearedRows"] += scoreDict["clearedRows"]
    LEVEL = scoreDict["totalClearedRows"] // 10 # Next level every 10 cleared lines

    if scoreDict["clearedRows"] == 1:
        return 40 * (LEVEL+1)
    elif scoreDict["clearedRows"] == 2:
        return 100 * (LEVEL+1)
    elif scoreDict["clearedRows"] == 3:
        return 300 * (LEVEL+1)
    elif scoreDict["clearedRows"] == 4:
        clearSound.play() # Tetris sound
        return 1200 * (LEVEL+1)

# Check if the piece has collided with the board or the ground
def collision(blocks, board, screen=screen):
    for x, y in blocks:  
        if y >= ROWS-1 or board[y+1][x]:
            if y <= -1 or board[y][x]:
                dropSound.play()
                return 2
            dropSound.play()
            return 1
    return 0

# Place the piece on the board
def placePiece(piece, board):
    for x, y in piece.blocks:
        board[y][x] = piece.BLOCK_COLOR # Store the color of the block on the board--giving us the index of a placed piece and the color in which it should appear

# Remove rows with a full set of blocks
def removeCompletedRows(board):
    removedRows = 0 # Count how many deleted rows
    for y in range(ROWS):
        if all(board[y][x] for x in range(COLS)):  # If the entire row is filled
            del board[y]  # Remove the row
            board.insert(0, [None for _ in range(COLS)])  # Add an empty row at the top because we cleared a bottom line
            removedRows += 1

    return removedRows  # Return the number of rows removed for scoring

# Rotate block around center, clockwise 90 deg
def rotateBlock(block, center):
    rel_x, rel_y = block[0] - center[0], block[1] - center[1] # Get the relative coordinates of the block
    new_rel_x, new_rel_y = -rel_y, rel_x # Rotate the block
    return center[0] + new_rel_x, center[1] + new_rel_y # Return the new coordinates


# PIECE CLASSES
class Piece:
    def __init__(self, grid_x, grid_y, color):
        self.BLOCK_COLOR = color
        self.blocks = []
    
    # Movement
    def move(self, dx, dy):
        positions = [(x + dx, y + dy) for x, y in self.blocks]
        
        # Check all boundaries
        if any(x < 0 or x >= COLS or y >= ROWS for x, y in positions):
            return
        self.blocks = positions

    # Rotate the piece around its center block
    def rotate(self):
        center = self.blocks[2] # Center block 
        rotatedBlocks = [rotateBlock(block, center) for block in self.blocks] # Rotate each block around the center
        
        # Check boundaries and collisions before accepting the new positions
        if any(x < 0 or x >= COLS or y < 0 or y >= ROWS for x, y in rotatedBlocks):
            return
        rotateSound.play()
        self.blocks = rotatedBlocks

    # Draw the piece to the screen
    def draw(self, screen=screen):
        self.darkerShade = darkerShade(self.BLOCK_COLOR)
        for x, y in self.blocks:
            # Convert grid coordinates to pixel coordinates
            pixel_x = GRID_OFFSET_X + x * BLOCK_SIZE
            pixel_y = GRID_OFFSET_Y + y * BLOCK_SIZE
            pygame.draw.rect(screen, self.darkerShade, (pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, self.BLOCK_COLOR, (pixel_x + 3, pixel_y + 3, BLOCK_SIZE - 6, BLOCK_SIZE - 6))

# Children of Piece class
class Square(Piece):
    def __init__ (self, grid_x=(COLS // 2 - 1), grid_y=0):
        super().__init__(grid_x, grid_y, (255, 255, 0)) # Inherit from the Piece class

        # Using grid coordinates for blocks
        self.blocks = [ 
            (grid_x, grid_y),
            (grid_x + 1, grid_y),
            (grid_x, grid_y + 1),
            (grid_x + 1, grid_y + 1)
        ]

    def rotate(self): # Overwrite the rotate function
        pass # What is the point of rotating a 2x2 object?

# L-Shaped Piece (two variations)
class L(Piece):
    def __init__ (self, grid_x=(COLS // 2 - 1), grid_y=0):
        variation = random.randint(0, 1)
        super().__init__(grid_x, grid_y, [(0, 0, 255), (255, 165, 0)][variation]) # Inherit from the Piece class

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
        ])][variation] # Choose right or left

# T-Shaped Piece
class T(Piece):
    def __init__ (self, grid_x=(COLS // 2 - 1), grid_y=0):
        super().__init__(grid_x, grid_y, (204, 0, 204))

        # Using grid coordinates for blocks
        self.blocks = ([ 
            (grid_x, grid_y),
            (grid_x-1, grid_y),
            (grid_x, grid_y+1),
            (grid_x + 1, grid_y),
        ])

# Straight Piece
class I(Piece):
    def __init__ (self, grid_x=(COLS // 2 - 1), grid_y=0):
        super().__init__(grid_x, grid_y, (0, 255, 255)) # Inherit from the Piece class

        # Using grid coordinates for blocks
        self.blocks = ([ 
            (grid_x, grid_y),
            (grid_x+1, grid_y),
            (grid_x+2, grid_y),
            (grid_x+3, grid_y)
        ])

# S-Shaped Piece (two variations)
class S(Piece):
    def __init__ (self, grid_x=(COLS // 2 - 1), grid_y=0):
        variation = random.randint(0,1)
        super().__init__(grid_x, grid_y, [(50, 205, 50), (255, 0 ,0)][variation]) # Inherit from the Piece class

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
        ][variation] # Choose right or left

# List of all pieces
pieces = [Square, L, T, I, S]
