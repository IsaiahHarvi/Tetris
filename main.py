from src import *

# Game Loop
pieceQueue = [random.choice(pieces), random.choice(pieces), random.choice(pieces)] # Queue of pieces, one is added each placed piece
piece = pieceQueue.pop()()  # Start with the first piece
nextPiece = pieceQueue.pop()()  # Initialize the next piece

while True:
    screen.fill((110, 110, 110)) # Grey Background
    clk.tick(60)

    # Screen Drawing
    drawGrid() # Draw the grid
    drawBoard() # Draw the pieces onto the grid from the board
    drawNextPiece(piece=nextPiece) # Show the next piece on the left corner
    drawScore(score) # Show the score on the right corner

    # Draw the sound toggle button
    if soundOn:
        soundButton("Music: ON")
    else:
        soundButton("Muic: OFF")

    # Lower Piece every second
    currentTime = pygame.time.get_ticks()
    if currentTime - lastDrop > DROP_INTERVAL:
        piece.move(0, 1)  # Move down by one grid unit
        lastDrop = currentTime

    # If collision, but not block out
    if collision(piece.blocks) == 1:
        placePiece(piece) # Place the piece on the board
        pieceQueue.append(random.choice(pieces)) # Add another piece to the queue
        rowsRemoved = removeCompletedRows(board)  # Check and remove completed rows
        score += (rowsRemoved * 200) if rowsRemoved == 4 else (rowsRemoved * 100) # If tetris double the score
        piece = nextPiece # Get the next already seleced piece
        nextPiece = pieceQueue.pop()() # Get the next piece from queue

    # If block out
    elif collision(piece.blocks) == 2:
        pygame.draw.rect(screen, (255, 0, 0), (GRID_OFFSET_X, GRID_OFFSET_Y, WIDTH, HEIGHT)) # Draw a red rectangle over the grid

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
                lastDrop = pygame.time.get_ticks() # Reset the last drop time so it doesnt double lower on top of the user input

            if event.key in mappedKeys['drop']: # Space/Enter - Drop Piece
                while collision(piece.blocks) == 0: # Move down until a collision
                    piece.move(0, 1)

            if event.key in mappedKeys['rotate']: # R - Rotate
                piece.rotate()
        
        # Click Mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if 20 <= x <= 20 + 100 and 700 <= y <= 700 + 50: # If clicking in bounds of sound button
                soundOn = not soundOn  # Toggle Music
                if soundOn:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()

    # Draw Piece
    piece.draw(screen)

    # Update Screen
    pygame.display.update()