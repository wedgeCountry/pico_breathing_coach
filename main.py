# This example shows you how you can use Pico Explorer's onboard buzzer as a speaker to play different notes and string them together into a bleepy tune.
# It uses code written by Avram Piltch - check out his Tom's Hardware article! https://www.tomshardware.com/uk/how-to/buzzer-music-raspberry-pi-pico
# You'll need to connect a jumper wire between GPO and AUDIO on the Explorer Base to hear noise.

import time

from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER
from pimoroni import Button, Analog, Buzzer

from machine import Pin, PWM, Timer
import math

display = PicoGraphics(display=DISPLAY_PICO_EXPLORER)

BLACK = display.create_pen(0, 0, 0) # black back light
BASE_COLOR = display.create_pen(255, 100, 30)  # Use warm nightlight color

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

# Create a buzzer on pin 0
# Don't forget to wire GP0 to AUDIO!
BUZZER = Buzzer(0)

# this handy list converts notes into frequencies, which you can use with the explorer.set_tone function
tones = { "B0": 31, "C1": 33, "CS1": 35, "D1": 37, "DS1": 39, "E1": 41, "F1": 44, "FS1": 46, "G1": 49,  "GS1": 52, "A1": 55, "AS1": 58, "B1": 62, "C2": 65, "CS2": 69, "D2": 73, "DS2": 78, "E2": 82, "F2": 87, "FS2": 93, "G2": 98, "GS2": 104, "A2": 110, "AS2": 117, "B2": 123, "C3": 131, "CS3": 139, "D3": 147, "DS3": 156, "E3": 165, "F3": 175, "FS3": 185, "G3": 196, "GS3": 208, "A3": 220, "AS3": 233, "B3": 247, "C4": 262, "CS4": 277, "D4": 294, "DS4": 311, "E4": 330, "F4": 349, "FS4": 370, "G4": 392, "GS4": 415, "A4": 440, "AS4": 466, "B4": 494, "C5": 523, "CS5": 554, "D5": 587, "DS5": 622, "E5": 659, "F5": 698, "FS5": 740, "G5": 784, "GS5": 831, "A5": 880, "AS5": 932, "B5": 988, "C6": 1047, "CS6": 1109, "D6": 1175, "DS6": 1245, "E6": 1319, "F6": 1397, "FS6": 1480, "G6": 1568, "GS6": 1661, "A6": 1760, "AS6": 1865, "B6": 1976, "C7": 2093, "CS7": 2217, "D7": 2349, "DS7": 2489, "E7": 2637, "F7": 2794, "FS7": 2960, "G7": 3136, "GS7": 3322, "A7": 3520, "AS7": 3729, "B7": 3951, "C8": 4186, "CS8": 4435, "D8": 4699, "DS8": 4978}

sound_pitch = "D8"
signal_tone = tones[sound_pitch]

def clear_display():                        # this function clears Pico Explorer's screen to black
    display.set_pen(BLACK)
    display.clear()
    display.update()

def playtone(frequency):            # this function tells your program how to make noise
    BUZZER.set_tone(frequency)

def bequiet():                      # this function tells your program how not to make noise
    BUZZER.set_tone(-1)

def any_button_pressed():
    return button_a.is_pressed or button_b.is_pressed or button_x.is_pressed or button_y.is_pressed        

playing_flag = False

WIDTH, HEIGHT = display.get_bounds()
CX = WIDTH // 2
CY = HEIGHT // 2

# Ripple parameters
MAX_RADIUS = min(WIDTH, HEIGHT) // 2
RIPPLE_SPACING = 12      # distance between waves
SPEED = 2                # pixels per frame
FADE_STEPS = 1           # number of visible ripples

def draw_frame(radius):
    display.set_pen(BLACK)
    display.clear()
    
    display.set_pen(BASE_COLOR)
    display.circle(CX, CY, radius)
    display.update()


class Mode:
    IN = "IN"
    HOLD = "HOLD"
    OUT = "OUT"
    STAY = "STAY"

class BreathingSettings:

    def __init__(self):
        self.total_duration = 10
        self.half_seconds_in = 8
        self.half_seconds_hold = 0
        self.half_seconds_out = 12
        self.half_seconds_stay = 4

    def get_seconds(self, mode:Mode):
        if mode == Mode.IN:
            return self.half_seconds_in / 2.0
        if mode == Mode.HOLD:
            return self.half_seconds_hold / 2.0
        if mode == Mode.OUT:
            return self.half_seconds_out / 2.0
        if mode == Mode.STAY:
            return self.half_seconds_stay / 2.0

    def get_signal_tone(self, mode:Mode):
        # Ein – Halten – Aus – Halten
        # D8 → B7 → A7 → G7
        # D-Dur-Pentatonik abwärts
        if mode == Mode.IN:
            return tones["D8"]
        if mode == Mode.HOLD:
            return tones["B7"]
        if mode == Mode.OUT:
            return tones["A7"]
        if mode == Mode.STAY:
            return tones["G6"]

def main(settings: BreathingSettings):
    global playing_flag
    
    radius_offset = 0
    direction = 1  # 1 = outward, -1 = inward
    
    bequiet()
    
    start_time = time.ticks_ms()
    total_duration_ms = int(settings.total_duration * 60 * 1000)
    sound_duration_ms = 10

    while True:
        
        # make interruptable
        if any_button_pressed():
            playing_flag = False
        if not playing_flag:
            break

        for mode in [Mode.IN, Mode.HOLD, Mode.OUT, Mode.STAY]:
            
            print(mode, settings.get_seconds(mode))
            current_cycle_length_ms = settings.get_seconds(mode) * 1000
            
            if current_cycle_length_ms == 0:
                continue
            
            mode_start_time = time.ticks_ms()
            playtone(settings.get_signal_tone(mode))
            while True:

                elapsed = time.ticks_diff(time.ticks_ms(), mode_start_time)

                if elapsed > sound_duration_ms:
                    bequiet()

                progress = min(1.0 * elapsed / current_cycle_length_ms, 1.0)

                radius = 0
                if mode == Mode.IN:
                    radius = int(progress * MAX_RADIUS)
                elif mode == Mode.HOLD:
                    radius = MAX_RADIUS
                elif mode == Mode.OUT:
                    radius = int((1.0 - progress) * MAX_RADIUS)
                elif mode == Mode.STAY:
                    radius = 0
                else:
                    raise Exception("Unknown mode")
                
                #print(radius, elapsed, progress, MAX_RADIUS, progress * MAX_RADIUS)
                draw_frame(radius)

                # make interruptable
                if any_button_pressed():
                    playing_flag = False
                if not playing_flag:
                    break
                if progress >= 1.0:
                    break
            bequiet()

        elapsed_total = time.ticks_diff(time.ticks_ms(), start_time)
        if elapsed_total > total_duration_ms:
            break
    bequiet()
    

clear_display()
# no button press was detected
display.set_pen(BASE_COLOR)
display.text("Plug a jumper wire from GP0 to AUDIO to hear noise!", 20, 110, 200)

settings = BreathingSettings()

duration_in_minutes = 10
half_seconds_per_round = 11

current_selected_line = 1

def draw_text(text, x, y, scale = 4, underline=False, clearing=False):
    
    text_width = display.measure_text(text, scale=scale)
    text_height = int(8 * scale)  # bitmap8 is ~8px tall
    
    #if clearing:
    display.set_pen(BLACK)
    display.rectangle(x, y + text_height, text_width, y)   # height of underline
    
    display.set_pen(BASE_COLOR)
        
    display.text(text, x, y, text_width, scale=scale)

    if underline:
        # underline position (y + font height)
        display.line(x, y + text_height, x + text_width, y + text_height)

def write_menu():    
    display.set_pen(BASE_COLOR)
    scale_title = 3.5
    scale_text = 2
    scale_settings = 3

    draw_text("Pico Atemcoach ", 0, 0, scale=scale_title)
    draw_text("------------------- ", 0, 20, scale=scale_title)
    draw_text("Dauer [min]:", 0, 60, scale=scale_text)
    draw_text("%s" % settings.total_duration, 140, 50, scale=4, underline=current_selected_line == 1)
    
    draw_text("Dauer Atemphasen:", 0, 100, scale=scale_text)
    draw_text(" in", 5, 130, scale=scale_text)
    draw_text("%s" % (0.5 * settings.half_seconds_in), 5, 150, scale=scale_settings, underline=current_selected_line == 2)
    draw_text("hold", 65, 130, scale=scale_text)
    draw_text("%s" % (0.5 * settings.half_seconds_hold), 65, 150, scale=scale_settings, underline=current_selected_line == 3)
    draw_text(" out", 125, 130, scale=scale_text)
    draw_text("%s" % (0.5 * settings.half_seconds_out), 125, 150, scale=scale_settings, underline=current_selected_line == 4)
    draw_text("keep", 185, 130, scale=scale_text)
    draw_text("%s" % (0.5 * settings.half_seconds_stay), 185, 150, scale=scale_settings, underline=current_selected_line == 5)
    display.update()

# notify change for display reload
change_flag = False

clear_display()
write_menu()

while True:

    if button_a.is_pressed:
        current_selected_line = 1 if current_selected_line == 5 else current_selected_line + 1
        change_flag = True
        time.sleep(0.1)
        
    elif button_x.is_pressed:
        clear_display()
        # wait until released
        while any_button_pressed():
            time.sleep(0.1)
        
        playing_flag = True
        
        main(settings)
    
        time.sleep(0.1)
        write_menu()
        
    elif button_b.is_pressed:
        #clear_display()
        if current_selected_line == 1:
            settings.total_duration = max(1, settings.total_duration - 1)
        elif current_selected_line == 2:
            settings.half_seconds_in = max(1, settings.half_seconds_in - 1)
        elif current_selected_line == 3:
            settings.half_seconds_hold = max(0, settings.half_seconds_hold - 1)
        elif current_selected_line == 4:
            settings.half_seconds_out = max(1, settings.half_seconds_out - 1)
        elif current_selected_line == 5:
            settings.half_seconds_stay = max(0, settings.half_seconds_stay - 1)
        change_flag = True
        time.sleep(0.05)
        
    elif button_y.is_pressed:
        #clear_display()
        if current_selected_line == 1:
            settings.total_duration += 1
        elif current_selected_line == 2:
            settings.half_seconds_in += 1
        elif current_selected_line == 3:
            settings.half_seconds_hold += 1
        elif current_selected_line == 4:
            settings.half_seconds_out += 1
        elif current_selected_line == 5:
            settings.half_seconds_stay += 1
        change_flag = True
        time.sleep(0.05)
      
    if change_flag:
        
        write_menu()
        time.sleep(0.1)
        change_flag = False
    #display.update()
    