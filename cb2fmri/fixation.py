#! /usr/bin/env python
# Time-stamp: <2021-03-04 12:15:50 christophe@pallier.org>
# Time-stamp: <2023-06-01 asathe@mit.edu>
""" Display a fixation cross.

   See:
   - `Pygame drawing basics <https://www.cs.ucsb.edu/~pconrad/cs5nm/topics/pygame/drawing/>`__
   - `Pygame's online documentation <https://www.pygame.org/docs/>`

"""

import time
import pygame
import logging

from py_client.game_endpoint import Action

logger = logging.getLogger(__file__)

FONT_SIZE = 75


def init_screen() -> pygame.Surface:
    #  create the window
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return screen


def draw_fixation_cross(x, y, screen, length=20, width=5, color=pygame.Color("black")):
    pygame.draw.line(screen, color, (x, y - length), (x, y + length), width)
    pygame.draw.line(screen, color, (x - length, y), (x + length, y), width)


def show_fixation(t):
    # shows fixation cross for t **seconds** and then quits

    pygame.init()

    screen = init_screen()
    W, H = screen.get_size()

    center_x = W // 2
    center_y = H // 2

    pygame.display.set_caption("Fixation cross")
    screen.fill(pygame.Color("white"))

    draw_fixation_cross(center_x, center_y, screen)

    pygame.display.flip()
    pygame.time.wait(t * 1000)
    pygame.quit()


def show_result(success: bool, t):
    # shows result (check for success, X for failure) for t **seconds** and then quits

    pygame.init()

    screen = init_screen()

    if success:
        draw_text('Success!', screen, textcolor='blue')
    else:
        draw_text('Timed out.', screen, textcolor='red')

    pygame.display.set_caption("Result")
    pygame.time.wait(t * 1000)
    pygame.quit()


def show_run_complete():
    # shows run complete screen until keypress

    instruction = 'Run complete. Press any button to exit.'

    accept_key(
        keycode=None,
        keyname='',
        caption=instruction,
        instruction=instruction,
        success="",
        failure="",
    )
    pygame.quit()


def draw_text(text, screen, textcolor="black", bgcolor="white", fontsize=FONT_SIZE):
    screen.fill(pygame.Color(bgcolor))
    font = pygame.font.Font(pygame.font.get_default_font(), fontsize)
    text = font.render(text, True, pygame.Color(textcolor))

    W, H = screen.get_size()

    text_rect = text.get_rect(center=(W / 2, H / 2))
    screen.blit(text, text_rect)
    pygame.display.flip()


def accept_key(
    keycode,
    keyname,
    caption="Practice buttonpress",
    instruction="Please press {keyname}",
    success="Success!",
    failure="Wrong key! Please press: {keyname}",
    game=None
):
    pygame.init()

    screen = init_screen()
    pygame.display.set_caption(caption)

    draw_text(instruction.format(keycode=keycode, keyname=keyname), screen)

    correct_button_pressed = False
    last_step = time.time()
    if game is not None:
        game.step(Action.NoopAction())
        last_step = time.time()

    while not correct_button_pressed:
        pygame.time.wait(10)  # milliseconds
        if game is not None:
            delay = time.time() - last_step
            if delay > 5:
                game.step(Action.NoopAction())
                last_step = time.time()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and (keycode is None or event.key == keycode):
                correct_button_pressed = True
                if success:
                    draw_text(success.format(keycode=keycode, keyname=keyname), screen)
                    pygame.time.wait(1000)
                pygame.quit()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                correct_button_pressed = True
                pygame.quit()
                return False

            elif event.type == pygame.KEYDOWN:
                if failure:
                    draw_text(failure.format(keycode=keycode, keyname=keyname), screen)

    return True


def wait_for_trigger(game=None, in_scanner=True):
    """
    wrapper around `accept_key` to wait for the scanner to
    send a `+` key trigger signaling start of the functional run
    """

    if in_scanner:
        instruction = "Waiting for scanner..."
        key = pygame.K_EQUALS
    else:
        instruction = 'Press any key to continue...'
        key = None

    accept_key(
        keycode=key,
        keyname="=",
        caption=instruction,
        instruction=instruction,
        success="Starting experiment",
        failure=instruction,
        game=game
    )


def practice_arrow_keys():
    return (
        accept_key(pygame, None, 'Press any button to test controls.')
        and accept_key(pygame.K_UP, "[Forwards]")
        and accept_key(pygame.K_DOWN, "[Backwards]")
        and accept_key(pygame.K_LEFT, "[<< Turn Left]")
        and accept_key(pygame.K_RIGHT, "[Turn Right >>]")
    )


if __name__ == "__main__":
    show_fixation(5)
