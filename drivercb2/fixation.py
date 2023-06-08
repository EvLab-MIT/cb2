#! /usr/bin/env python
# Time-stamp: <2021-03-04 12:15:50 christophe@pallier.org>
# Time-stamp: <2023-06-01 asathe@mit.edu>
""" Display a fixation cross.

   See:
   - `Pygame drawing basics <https://www.cs.ucsb.edu/~pconrad/cs5nm/topics/pygame/drawing/>`__
   - `Pygame's online documentation <https://www.pygame.org/docs/>`

"""

import pygame

# def quit():
#    return


def init_screen() -> pygame.Surface:
    #  create the window
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return screen


def draw_fixation_cross(x, y, screen, length=20, width=5, color=pygame.Color("black")):
    pygame.draw.line(screen, color, (x, y - length), (x, y + length), width)
    pygame.draw.line(screen, color, (x - length, y), (x + length, y), width)


def show_fixation(t: int = 3):
    # shows fixation cross for t **seconds** and then quits

    pygame.init()

    screen = init_screen()
    W, H = screen.get_size()

    # W, H = 500, 500  # Size of the graphic window
    center_x = W // 2
    center_y = H // 2
    # screen = pygame.display.set_mode((W, H), pygame.DOUBLEBUF)

    pygame.display.set_caption("Fixation cross")
    screen.fill(pygame.Color("white"))

    draw_fixation_cross(center_x, center_y, screen)

    pygame.display.flip()
    time_start = pygame.time.get_ticks()

    # Wait until the window is closed
    quit_button_pressed = False
    while not quit_button_pressed:
        pygame.time.wait(10)

        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                quit_button_pressed = True
                pygame.quit()
                return

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                quit_button_pressed = True
                pygame.quit()
                return

        if pygame.time.get_ticks() - time_start >= t * 1000:
            quit_button_pressed = True
            pygame.quit()
            return


if __name__ == "__main__":
    show_fixation()
