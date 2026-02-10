# This example shows you how you can use Pico Explorer's onboard buzzer as a speaker to play different notes and string them together into a bleepy tune.
# It uses code written by Avram Piltch - check out his Tom's Hardware article! https://www.tomshardware.com/uk/how-to/buzzer-music-raspberry-pi-pico
# You'll need to connect a jumper wire between GPO and AUDIO on the Explorer Base to hear noise.

import time
from lib import BreathingSettings, Mode, get_signal_tone

from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER
from pimoroni import Button, Analog, Buzzer

from machine import Pin, PWM, Timer
import math

import json
import os

display = PicoGraphics(display=DISPLAY_PICO_EXPLORER)

BLACK = display.create_pen(0, 0, 0) # black back light
BASE_COLOR = display.create_pen(255, 100, 30)  # Use warm nightlight color

BUTTON_UP = Button(12)
BUTTON_DOWN = Button(13)
BUTTON_PLUS = Button(14)
BUTTON_MINUS = Button(15)

def button_up():
    return BUTTON_UP.is_pressed
def button_down():
    return BUTTON_DOWN.is_pressed
def button_left():
    return BUTTON_MINUS.is_pressed
def button_right():
    return BUTTON_PLUS.is_pressed

BUZZER = Buzzer(0)

def clear_display():                        # this function clears Pico Explorer's screen to black
    display.set_pen(BLACK)
    display.clear()
    display.update()

def playtone(frequency):            # this function tells your program how to make noise
    BUZZER.set_tone(frequency)

def bequiet():                      # this function tells your program how not to make noise
    BUZZER.set_tone(-1)

playing_flag = False

WIDTH, HEIGHT = display.get_bounds()
CX = WIDTH // 2
CY = HEIGHT // 2
MAX_RADIUS = min(WIDTH, HEIGHT) // 2

def draw_circle(radius):
    display.set_pen(BLACK)
    display.clear()
    
    display.set_pen(BASE_COLOR)
    display.circle(CX, CY, radius)
    display.update()

def visualize(progress, mode):

    min_radius = 5
    if mode == Mode.IN:
        radius = max(min_radius, int(progress * MAX_RADIUS))
    elif mode == Mode.HOLD:
        radius = MAX_RADIUS
    elif mode == Mode.OUT:
        radius = max(min_radius, int((1.0 - progress) * MAX_RADIUS))
    elif mode == Mode.STAY:
        radius = min_radius
    else:
        raise Exception("Unknown mode")

    draw_circle(radius)


def draw_text(text, x, y, scale=4, underline=False, clearing=False):
    text_width = display.measure_text(text, scale=scale)
    text_height = int(8 * scale)  # bitmap8 is ~8px tall

    # if clearing:
    display.set_pen(BLACK)
    display.rectangle(x, y, text_width + display.measure_text(" ", scale=scale), y + text_height)  # height of underline

    display.set_pen(BASE_COLOR)

    display.text(text, x, y, text_width, scale=scale)

    if underline:
        # underline position (y + font height)
        display.line(x, y + text_height, x + text_width, y + text_height)

def write_menu(settings, current_selected_line):
    display.set_pen(BASE_COLOR)
    scale_title = 3.5
    scale_text = 2
    scale_numbers = 3

    draw_text("Pico Atemcoach ", 0, 0, scale=scale_title)
    draw_text("------------------- ", 0, 20, scale=scale_title)
    draw_text("Laufzeit [min]:", 0, 50, scale=scale_text)
    draw_text("%s" % settings.total_duration, 160, 45, scale=scale_numbers, underline=current_selected_line == 1)
    
    draw_text("Dauer [sec]:", 0, 80, scale=scale_text)
    y_duration = 105
    draw_text(" in", 5, y_duration, scale=scale_text)
    draw_text("%s" % (0.5 * settings.half_seconds_in), 5, y_duration, scale=scale_numbers, underline=current_selected_line == 2)
    draw_text("hold", 65, y_duration, scale=scale_text)
    draw_text("%s" % (0.5 * settings.half_seconds_hold), 65, y_duration, scale=scale_numbers, underline=current_selected_line == 3)
    draw_text(" out", 125, y_duration, scale=scale_text)
    draw_text("%s" % (0.5 * settings.half_seconds_out), 125, y_duration, scale=scale_numbers, underline=current_selected_line == 4)
    draw_text("keep", 185, y_duration, scale=scale_text)
    draw_text("%s" % (0.5 * settings.half_seconds_stay), 185, y_duration, scale=scale_numbers, underline=current_selected_line == 5)
    
    draw_text("Presets:", 0, 140, scale=scale_text)
    y_presets = 165
    draw_text("4-7-8", 0, y_presets, scale=scale_text, underline=current_selected_line == 6)
    draw_text("box", 70, y_presets, scale=scale_text, underline=current_selected_line == 7)
    draw_text("gold", 120, y_presets, scale=scale_text, underline=current_selected_line == 8)
    draw_text("nat", 190, y_presets, scale=scale_text, underline=current_selected_line == 9)

    draw_text("START BREATHING", 10, 200, scale=scale_text, underline=current_selected_line == 10)
    display.update()
