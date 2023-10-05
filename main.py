from src import *

def menu():
    screen.fill((0, 0, 0)) # Clear screen with black
    
    font = pygame.font.SysFont(None, 100)
    label = font.render("TETRIS", True, (255, 255, 255))
    screen.blit(label, (int(SCREEN_X / 2 - label.get_width() / 2), int(SCREEN_Y / 4 - label.get_height() / 2)))

    instructions_font = pygame.font.SysFont(None, 32)
    instructions = [
        "Press S to Start",
        "Press Q to Quit"
    ]
    for index, line in enumerate(instructions):
        label = instructions_font.render(line, True, (255, 255, 255))
        screen.blit(label, (int(SCREEN_X / 2 - label.get_width() / 2), int(SCREEN_Y / 2 + index * 40)))
    
   # Display the high score
    high_score_font = pygame.font.SysFont(None, 32)
    high_score_label = high_score_font.render(f"HIGH SCORE: {highScore}", True, (255, 255, 255))
    screen.blit(high_score_label, (int(SCREEN_X / 2 - high_score_label.get_width() / 2), int(SCREEN_Y / 4 + label.get_height())+ 30))

    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    gameLoop()
                    return
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()

# Game Loop
def gameLoop():
    global soundOn # State variable

    pieceQueue =  [pieces[random.randint(0, len(pieces)-1)] for _ in range(10)] # Queue of pieces, one more is added everytime a piece is placed
    piece = pieceQueue.pop()()  # Start with the first piece
    nextPiece = pieceQueue.pop()()  # Initialize the next pierce
    board = [[None for _ in range(COLS)] for _ in range(ROWS)] # Initialize the board
    scoreDict = {
        "totalClearedRows" : 0, # Total rows cleared
        "clearedRows" : 0, # Rows cleared in the current level
        "score" : 0 # Current score
    }
    LEVEL = scoreDict["clearedRows"] // 10 # Level is the number of rows cleared divided by 10
    LOWER_INTERVAL =  800.16 - (83.35 * LEVEL)  # Like the NES--Drop every 800milisecond  and add subtract 83 miliseconds every 10 rows
    lastLower = pygame.time.get_ticks() # Variable to track time since the last drop to move the block down every 1 sec
    lastHardDrop = 0 # Variable to track time since the last hard drop to prevent double drops
    while True:
        screen.fill((110, 110, 110)) # Grey Background
        clk.tick(60)

        # Screen Drawing
        drawGrid() # Draw the grid
        drawBoard(board) # Draw the pieces onto the grid from the board
        drawNextPiece(piece=nextPiece) # Show the next piece on the left corner
        drawScore(scoreDict) # Show the score on the right corner

        # Draw the sound toggle button
        if soundOn:
            soundButton("Music: ON")
        else:
            soundButton("Muic: OFF")

        # Lower Piece every second
        currentTime = pygame.time.get_ticks()
        if currentTime - lastLower > LOWER_INTERVAL:
            piece.move(0, 1)  # Move down by one grid unit
            lastLower = currentTime

        # If collision, but not block out
        if collision(piece.blocks, board) == 1:
            placePiece(piece, board) # Place the piece on the board
            pieceQueue.append(pieces[random.randint(0,len(pieces)-1)]) # Add another piece to the queue

            clearedLines = removeCompletedRows(board) # Remove completed rows and track how many
            if clearedLines:
                scoreDict["clearedRows"] = clearedLines
                scoreDict["score"] += updateScore(scoreDict) # Update the score

            piece = nextPiece # Get the next already seleced piece
            nextPiece = pieceQueue.pop()() # Get the next preview piece from queue

        # If block out
        elif collision(piece.blocks, board) == 2:
            startTime = pygame.time.get_ticks() # Get the time of collision
            piece = None # Remove the current piece
           
            if soundOn:
                pygame.mixer.music.pause() # Pause music
                loseSound.play()
            pygame.time.wait(3000) # Wait 3 seconds
            if soundOn:
                pygame.mixer.music.unpause() # Resume music
            
            if scoreDict["score"] > highScore: # If the score is higher than the high score, update the high score
                with open("high_score.txt", "w") as file:
                    file.write(str(scoreDict["score"]))

            menu() # Go back to menu
            return

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
                    lastLower = pygame.time.get_ticks() # Reset the last drop time so it doesnt double lower on top of the user input

                if event.key in mappedKeys['drop']: # Space/Enter - Drop Piece
                    dropTrigger = pygame.time.get_ticks() # Get the time of the drop
                    if dropTrigger - lastHardDrop > 500: # If the last drop was more than 500 miliseconds ago 
                        while collision(piece.blocks, board) == 0: # Move down until a collision
                            piece.move(0, 1)
                    lastHardDrop = dropTrigger  # variable to track the last hard drop time

                if event.key in mappedKeys['rotate']: # R - Rotate
                    piece.rotate()

                if event.key in mappedKeys['menu']: # Esc/M - Return to menu
                    piece = None # Remove the current piece
                    menu()
                    return
            
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

if __name__ == "__main__":
    menu()