from src import *


# Initialize pygame
pygame.init()
pygame.mixer.init()

# Create the screen
screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y)) # 600, 800
pygame.display.set_caption("Tetris")
pygame.display.set_icon(pygame.image.load("Assets/icon.jpg"))

# Background Music
pygame.mixer.music.load("Assets/soundtrack.mp3")
pygame.mixer.music.play(-1) # Loop
pygame.mixer.music.set_volume(0.10) # Start at 10%

# Board
board = [[None for _ in range(COLS)] for _ in range(ROWS)]

# Game Loop
clk = pygame.time.Clock()
lastDrop = pygame.time.get_ticks()
piece = random.choice(pieces)()

while True:
    clk.tick(60)
    screen.fill((12,12,12))


    # Screen Drawing
    drawGrid(screen)
    drawBoard(screen, board)

    currentTime = pygame.time.get_ticks()
    if currentTime - lastDrop > DROP_INTERVAL:
        piece.move(0, 1)  # Move down by one grid unit
        lastDrop = currentTime

    if collision(board, piece.blocks):
        placePiece(board, piece)
        piece = random.choice(pieces)()
        print(f"New piece spawned at coordinates: {piece.blocks}")

    # Event Handler
    for event in pygame.event.get():
        # Close Game
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Press Key
        if event.type == pygame.KEYDOWN:
            if event.key in mappedKeys['left']: # Left Arrow/A - Move left
                piece.move(-1, 0)  # Move left by one grid unit

            if event.key in mappedKeys['right']: # Right Arrow/D - Move right
                piece.move(1, 0)  # Move right by one grid unit
                
            if event.key in mappedKeys['down']: # Down Arrow/S - Move down
                piece.move(0, 1)  # Move down by one grid unit

            if event.key in mappedKeys['rotate']: # R - Rotate
                print("Rotate")
                
    piece.draw(screen)

    # Update Screen
    pygame.display.update()