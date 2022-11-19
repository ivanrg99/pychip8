import pygame


class Keyboard:
    """
    Hex Keyboard in Chip 8:
    1	2	3	C
    4	5	6	D
    7	8	9	E
    A	0	B	F
    We map each hex value to more usable keys using pygame K map.
    """
    def __init__(self):
        self.keys = {
            0x1: pygame.K_1,
            0x2: pygame.K_2,
            0x3: pygame.K_3,
            0xC: pygame.K_4,
            0x4: pygame.K_q,
            0x5: pygame.K_w,
            0x6: pygame.K_e,
            0xD: pygame.K_r,
            0x7: pygame.K_a,
            0x8: pygame.K_s,
            0x9: pygame.K_d,
            0xE: pygame.K_f,
            0xA: pygame.K_z,
            0x0: pygame.K_x,
            0xB: pygame.K_c,
            0xF: pygame.K_v
        }
