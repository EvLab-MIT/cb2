#! /usr/bin/env python
# Time-stamp: <2021-03-04 12:15:50 christophe@pallier.org>
# Time-stamp: <2023-06-01 asathe@mit.edu>
""" Display a fixation cross.

   See:
   - `Pygame drawing basics <https://www.cs.ucsb.edu/~pconrad/cs5nm/topics/pygame/drawing/>`__
   - `Pygame's online documentation <https://www.pygame.org/docs/>`

"""

import pygame
import logging

logger = logging.getLogger(__file__)


def init_screen() -> pygame.Surface:
    #  create the window
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return screen


def draw_fixation_cross(x, y, screen, length=20, width=5, color=pygame.Color("black")):
    pygame.draw.line(screen, color, (x, y - length), (x, y + length), width)
    pygame.draw.line(screen, color, (x - length, y), (x + length, y), width)


def show_fixation(t: int):
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
            logger.debug(event)

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


def draw_text(text, screen):
    screen.fill(pygame.Color("white"))
    font = pygame.font.Font(pygame.font.get_default_font(), 45)
    text = font.render(text, True, pygame.Color("black"))

    W, H = screen.get_size()

    text_rect = text.get_rect(center=(W / 2, H / 2))
    screen.blit(text, text_rect)
    pygame.display.flip()


def accept_key(
    keycode: str,
    keyname: str,
    caption: str = "Practice buttonpress",
    instruction: str = "Please press {keyname}",
    success: str = "Success!",
    failure: str = "Wrong key! Please press: {keyname}",
) -> bool:
    """Get a user to press a certain key before proceeding.
        Shows a white screen with black text in a blocking
        fashion. Shows feedback in case an incorrect keypress is
        registered. Can be exited using ESC.

    Args:
        keycode (str): keycode of the key to accept
        keyname (str): human-readable name of the key (e.g. Left arrow key)
        caption (str, optional): window caption. Defaults to "Practice buttonpress".
        instruction (str, optional): instruction to show on the screen while waiting.
            Defaults to "Please press {keyname}". Is rendered using `.format(keycode=keycode, keyname=keyname)`
            before displaying.
        success (str, optional): Message upon successful keypress. Defaults to "Success!".
        failure (str, optional): Message upong incorrect keypress. Defaults to "Wrong key! Please press: {keyname}".
            Is rendered using `.format(keycode=keycode, keyname=keyname)`
            before displaying.

    Returns:
        bool: was the correct key eventually pressed?
    """
    pygame.init()

    screen = init_screen()
    W, H = screen.get_size()
    pygame.display.set_caption(caption)

    draw_text(instruction.format(keycode=keycode, keyname=keyname), screen)

    correct_button_pressed = False
    while not correct_button_pressed:
        pygame.time.wait(10)  # milliseconds

        for event in pygame.event.get():
            logger

            if event.type == pygame.KEYDOWN and event.key == keycode:
                correct_button_pressed = True
                draw_text(success.format(keycode=keycode, keyname=keyname), screen)
                pygame.quit()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                correct_button_pressed = True
                pygame.quit()
                return False

            elif event.type == pygame.KEYDOWN:
                draw_text(failure.format(keycode=keycode, keyname=keyname), screen)

    return True


def wait_for_trigger():
    """
    wrapper around `accept_key` to wait for the scanner to
    send a `+` key trigger signaling start of the functional run
    """
    accept_key(
        keycode=pygame.K_PLUS,
        keyname="+",
        caption="waiting for trigger",
        instruction="waiting for scanner...",
        success="starting experiment!",
        failure="waiting for scanner...",
    )


def practice_arrow_keys():
    accept_key(pygame.K_UP, "[Forwards]") and accept_key(
        pygame.K_DOWN, "[Backwards]"
    ) and accept_key(pygame.K_LEFT, "[<< Turn Left]") and accept_key(
        pygame.K_RIGHT, "[Turn Right >>]"
    )


if __name__ == "__main__":
    show_fixation(5)
