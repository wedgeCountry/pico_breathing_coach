# This example shows you how you can use Pico Explorer's onboard buzzer as a speaker to play different notes and string them together into a bleepy tune.
# It uses code written by Avram Piltch - check out his Tom's Hardware article! https://www.tomshardware.com/uk/how-to/buzzer-music-raspberry-pi-pico
# You'll need to connect a jumper wire between GPO and AUDIO on the Explorer Base to hear noise.

import time

from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER
from pimoroni import Button, Analog, Buzzer

from machine import Pin, PWM, Timer
import math

import json
import os
from lib import BreathingSettings, Mode, get_signal_tone

PRODUCTION_MODE = False # LCD
if PRODUCTION_MODE:
    from lcd import display, clear_display, write_menu, visualize
    from lcd import button_up, button_down, button_left, button_right
    from lcd import BUZZER, playtone, bequiet    
else: # pico explorer
    from pico_explorer import display, clear_display, write_menu, visualize
    from pico_explorer import button_up, button_down, button_left, button_right
    from pico_explorer import BUZZER, playtone, bequiet

def any_button_pressed():
    return button_up() or button_down() or button_left() or button_right()


playing_flag = False

def main(settings: BreathingSettings):
    global playing_flag
    
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
            
            if not playing_flag:
                    break
                
            mode_start_time = time.ticks_ms()
            playtone(get_signal_tone(mode))
            while True:

                elapsed = time.ticks_diff(time.ticks_ms(), mode_start_time)

                if elapsed > sound_duration_ms:
                    bequiet()

                progress = min(1.0 * elapsed / current_cycle_length_ms, 1.0)

                visualize(progress, mode)

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

    # final tone at end
    final_start_time = time.ticks_ms()
    playtone(get_signal_tone(Mode.STAY))
    while True:
        elapsed = time.ticks_diff(time.ticks_ms(), final_start_time)
        if elapsed > 500:
            break
    bequiet()

clear_display()

settings = BreathingSettings()
settings.load()

current_selected_line = 10

# notify change for display reload
change_flag = False

clear_display()
write_menu(settings, current_selected_line)

while True:
    #print("running")
    if button_down():
        current_selected_line = 1 if current_selected_line == 10 else current_selected_line + 1
        change_flag = True
        time.sleep(0.1)
    
    elif button_up():
        current_selected_line = 10 if current_selected_line == 1 else current_selected_line - 1
        change_flag = True
        time.sleep(0.1)
        
    elif button_right():
        
        # run program
        if current_selected_line == 10:

            # save settings
            settings.save()
            
            # clear display to start
            clear_display()
            
            # wait until released
            while any_button_pressed():
                time.sleep(0.1)
            
            playing_flag = True
            
            main(settings)
            
            # at the end of the main program, clear display
            time.sleep(0.05)
            clear_display()
            
        else:
                
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
                
            # presets
            elif current_selected_line == 6: # 4-7-8
                settings.half_seconds_in = 4 * 2
                settings.half_seconds_hold = 7 * 2
                settings.half_seconds_out = 8 * 2
                settings.half_seconds_stay = 0 
            elif current_selected_line == 7: # box
                settings.half_seconds_in = 4 * 2
                settings.half_seconds_hold = 4 * 2
                settings.half_seconds_out = 4 * 2
                settings.half_seconds_stay = 4 * 2
            elif current_selected_line == 8: # gold
                settings.half_seconds_in = 5.5 * 2
                settings.half_seconds_hold = 0
                settings.half_seconds_out = 5.5 * 2
                settings.half_seconds_stay = 0
            elif current_selected_line == 9: # nat
                settings.half_seconds_in = 4 * 2
                settings.half_seconds_hold = 2 * 2
                settings.half_seconds_out = 6 * 2
                settings.half_seconds_stay = 3*2
                
        change_flag = True
        time.sleep(0.05)
        
    elif button_left():
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
        
    if change_flag:
        
        write_menu(settings, current_selected_line)
        time.sleep(0.1)
        change_flag = False
    #display.update()
    