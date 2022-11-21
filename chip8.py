from renderer import Renderer
from keyboard import Keyboard
from speaker import Speaker

import pygame
import random
import sys


class Chip8:
    def __init__(self):
        self.memory = [0] * 4096
        self.registers = [0] * 16
        self.index = 0
        self.pc = 0x200
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.paused = False
        self.speed = 10
        try:
            self.load_rom(sys.argv[1])
        except:
            print("Usage: chip8.py path_of_rom")
            exit()

        self.renderer = Renderer()
        self.keyboard = Keyboard()
        self.speaker = Speaker()

    def load_rom(self, rom_path):
        f = open(rom_path, "rb")
        rom = f.read()
        for i in range(len(rom)):
            self.memory[0x200 + i] = rom[i]

    def update_timers(self):
        # Each cycle, decrease each timer by 1
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def load_default_sprites(self):
        """
        Programs may also refer to a group of sprites representing the hexadecimal digits 0 through F. These sprites
        are 5 bytes long, or 8x5 pixels. The data should be stored in the interpreter area of Chip-8 memory (0x000 to
        0x1FF). Below is a listing of each character's bytes, in binary and hexadecimal:
        """
        sprites = [0xF0, 0x90, 0x90, 0x90, 0xF0, 0x20, 0x60, 0x20, 0x20, 0x70, 0xF0, 0x10, 0xF0, 0x80, 0xF0, 0xF0, 0x10,
                   0xF0, 0x10, 0xF0, 0x90, 0x90, 0xF0, 0x10, 0x10, 0xF0, 0x80, 0xF0, 0x10, 0xF0, 0xF0, 0x80, 0xF0, 0x90,
                   0xF0,
                   0xF0, 0x10, 0x20, 0x40, 0x40,
                   0xF0, 0x90, 0xF0, 0x90, 0xF0,
                   0xF0, 0x90, 0xF0, 0x10, 0xF0,
                   0xF0, 0x90, 0xF0, 0x90, 0x90,
                   0xE0, 0x90, 0xE0, 0x90, 0xE0,
                   0xF0, 0x80, 0x80, 0x80, 0xF0,
                   0xE0, 0x90, 0x90, 0x90, 0xE0,
                   0xF0, 0x80, 0xF0, 0x80, 0xF0,
                   0xF0, 0x80, 0xF0, 0x80, 0x80
                   ]
        for i in range(len(sprites)):
            self.memory[i] = sprites[i]

    def decode_instruction(self, instruction):
        # Each instruction is 2 bytes long so add 2 to increment PC
        self.pc += 2
        # Get first 4 bits (1B)
        b1 = (instruction & 0xF000) >> 12
        # Get next 4 bits ...
        b2 = (instruction & 0x0F00) >> 8  # 4 bits per place * 2 places to shift
        b3 = (instruction & 0x00F0) >> 4
        b4 = (instruction & 0x000F)

        # Find correct instruction
        if instruction == 0x00E0:
            self.renderer.clear()
        elif instruction == 0x00EE:
            self.pc = self.stack.pop()
        elif b1 == 0x1:
            self.pc = (instruction & 0x0FFF)
        elif b1 == 0x2:
            self.stack.append(self.pc)
            self.pc = (instruction & 0x0FFF)
        elif b1 == 0x3:
            if self.registers[b2] == (instruction & 0x00FF):
                self.pc += 2
        elif b1 == 0x4:
            if self.registers[b2] != (instruction & 0x00FF):
                self.pc += 2
        elif b1 == 0x5:
            if self.registers[b2] == self.registers[b3]:
                self.pc += 2
        elif b1 == 0x6:
            self.registers[b2] = (instruction & 0x00FF)
        elif b1 == 0x7:
            self.registers[b2] += (instruction & 0x00FF)
            if self.registers[b2] > 255:
                # We need to overflow the number ourselves since Python uses a 32 bit number for the regs
                self.registers[b2] -= 256
        elif b1 == 0x8:
            if b4 == 0x0:
                self.registers[b2] = self.registers[b3]
            elif b4 == 0x1:
                self.registers[b2] |= self.registers[b3]
            elif b4 == 0x2:
                self.registers[b2] &= self.registers[b3]
            elif b4 == 0x3:
                self.registers[b2] ^= self.registers[b3]
            elif b4 == 0x4:
                self.registers[b2] += self.registers[b3]
                # Check if result is greater than 8 bits
                if self.registers[b2] > 255:
                    self.registers[b2] &= 0x00FF
                    self.registers[0xF] = 1
                else:
                    self.registers[0xF] = 0
            elif b4 == 0x5:
                self.registers[b2] -= self.registers[b3]
                if self.registers[b2] < 0:
                    self.registers[0xF] = 0
                else:
                    self.registers[0xF] = 1
            elif b4 == 0x6:
                if self.registers[b2] & 0b1 == 1:
                    self.registers[0xF] = 1
                else:
                    self.registers[0xF] = 0
                self.registers[b2] //= 2
            elif b4 == 0x7:
                if self.registers[b3] > self.registers[b2]:
                    self.registers[0xF] = 1
                else:
                    self.registers[0xF] = 0
                self.registers[b2] = self.registers[b3] - self.registers[b2]
            elif b4 == 0xE:
                # Get how many bits in the number
                num_bits = self.registers[b2].bit_length()
                msb = self.registers[b2] & 2 ** (num_bits - 1)
                if msb == 1:
                    self.registers[0xF] = 1
                else:
                    self.registers[0xF] = 0
                self.registers[b2] *= 2
        elif b1 == 0x9:
            if self.registers[b2] != self.registers[b3]:
                self.pc += 2
        elif b1 == 0xA:
            self.index = (instruction & 0x0FFF)
        elif b1 == 0xB:
            self.pc = (instruction & 0x0FFF) + self.registers[0]
        elif b1 == 0xC:
            self.registers[b2] = random.randrange(0, 256) & (instruction & 0x00FF)
        elif b1 == 0xD:
            # Iterate over the sprite, row by row and column by column
            # Each sprite is 8 pixels wide
            # Read n bytes, 1 byte is 8 bits, which is how many rows / how tall the sprite is
            self.registers[0xF] = 0
            for row in range(b4):
                sprite = self.memory[self.index + row]
                for col in range(8):
                    # 0x80 = 0b1000 0000
                    # We shift that 1 with each column to get the pixel
                    pixel = sprite & (0x80 >> col)
                    if pixel > 0:
                        # Set pixel and check if there was a collision
                        if self.renderer.set_pixel(self.registers[b2] + col, self.registers[b3] + row):
                            self.registers[0xF] = 1
        elif b1 == 0xE:
            if (instruction & 0x00FF) == 0x9E:
                keys = pygame.key.get_pressed()
                if keys[self.keyboard.keys[self.registers[b2]]]:
                    self.pc += 2
            elif (instruction & 0x00FF) == 0xA1:
                keys = pygame.key.get_pressed()
                if not keys[self.keyboard.keys[self.registers[b2]]]:
                    self.pc += 2
        elif b1 == 0xF:
            if (instruction & 0x00FF) == 0x07:
                self.registers[b2] = self.delay_timer
            elif (instruction & 0x00FF) == 0x0A:
                #  All execution stops until a key is pressed, then the value of that key is stored in Vx.
                waiting_key_press = True
                while waiting_key_press:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        if event.type == pygame.KEYDOWN:
                            for k in self.keyboard.keys:
                                if self.keyboard.keys[k] == event.key:
                                    self.registers[b2] = k
                                    waiting_key_press = False
                                    break

            elif (instruction & 0x00FF) == 0x15:
                self.delay_timer = self.registers[b2]
            elif (instruction & 0x00FF) == 0x18:
                self.sound_timer = self.registers[b2]
            elif (instruction & 0x00FF) == 0x1E:
                self.index += self.registers[b2]
            elif (instruction & 0x00FF) == 0x29:
                # Character sprites are located at 0x50, 5 bytes each
                # So we get the digit from Vx and multiply it by 5
                # Ex: Get sprite for the number 3? We multiply 3 times 5 to offset the memory location of the sprite
                self.index = 0x50 + (self.registers[b2] * 5)
            elif (instruction & 0x00FF) == 0x33:
                num = self.registers[b2]
                self.memory[self.index + 2] = num % 10
                num //= 10
                self.memory[self.index + 1] = num % 10
                num //= 10
                self.memory[self.index] = num % 10
            elif (instruction & 0x00FF) == 0x55:
                for i in range(b2 + 1):
                    self.memory[self.index + i] = self.registers[i]
            elif (instruction & 0x00FF) == 0x65:
                for i in range(b2 + 1):
                    self.registers[i] = self.memory[self.index + i]
        else:
            print(f"ERROR: BAD OPCODE {hex(instruction)}")
            pass

    def cycle(self):
        for i in range(self.speed):
            if not self.paused:
                opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
                self.decode_instruction(opcode)
        if not self.paused:
            self.update_timers()

        self.renderer.draw(self.paused)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    # PAUSE CHIP 8
                    if event.key == pygame.K_SPACE:
                        if self.paused:
                            self.paused = False
                        else:
                            self.paused = True
                    elif event.key == pygame.K_RETURN:
                        return "RESET"

            self.cycle()


if __name__ == '__main__':
    while True:
        chip8 = Chip8()
        chip8.load_default_sprites()
        if chip8.run() != "RESET":
            exit()
