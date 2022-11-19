from settings import *
import pygame


class Renderer:
    def __init__(self):
        # initialize pygame
        pygame.init()
        self.width = COLUMNS * SCALE
        self.height = ROWS * SCALE
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Chip 8')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('Pixeltype.ttf', 200)

        # Set display in column major order 1D array
        self.display = [0] * (COLUMNS * ROWS)

    def draw_paused(self):
        message_text = self.font.render('PAUSED', False, 'RED')
        self.screen.blit(message_text, message_text.get_rect(center=(self.width/2, self.height/2)))

    def set_pixel(self, x, y):
        # Wrap around if out of bounds
        if x >= COLUMNS:
            x -= COLUMNS
        elif x < 0:
            x += COLUMNS
        if y >= ROWS:
            y -= ROWS
        elif y < 0:
            y += ROWS

        # XOR the display array to set pixels on and off
        self.display[x + (y * COLUMNS)] ^= 1
        return self.display[x + (y * COLUMNS)] != 1

    def clear(self):
        self.display = [0] * (COLUMNS * ROWS)

    def draw(self, paused):
        self.screen.fill('black')

        for i in range(len(self.display)):
            if self.display[i] == 1:
                # Get the x and y of the array from to be able to draw it at the right pos
                rect = pygame.Rect((i % COLUMNS) * SCALE, (i // COLUMNS) * SCALE, SCALE, SCALE)
                pygame.draw.rect(self.screen, 'White', rect)
            i += 1

        if paused:
            self.draw_paused()

        pygame.display.update()
        self.clock.tick(FPS)
