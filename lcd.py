from machine import Pin,SPI,PWM
import framebuf
import time

import pico_lcd_096
from lib import Mode
#color is BGR
RED = 0x00F8
GREEN = 0xE007
BLUE = 0x1F00
WHITE = 0xFFFF
BLACK = 0x0000


LINE_HEIGHT = 10 + 4
TOP_OFFSET = 20

def draw_text(text, x, line, scale=4, selected=False):
    y = line*LINE_HEIGHT
    if selected:
        lcd.text(">", x - 8, y, WHITE)
    lcd.text(text, x, y, RED)
    return line + 1
    
    
KEY_UP = Pin(2,Pin.IN,Pin.PULL_UP)
KEY_DOWN = Pin(18,Pin.IN,Pin.PULL_UP)
KEY_LEFT= Pin(16,Pin.IN,Pin.PULL_UP)
KEY_RIGHT= Pin(20,Pin.IN,Pin.PULL_UP)
KEY_CTRL=Pin(3,Pin.IN,Pin.PULL_UP)
KEY_A=Pin(15,Pin.IN,Pin.PULL_UP)
KEY_B=Pin(17,Pin.IN,Pin.PULL_UP)

lcd = pico_lcd_096.LCD_0inch96()

def button_up():
    return KEY_UP.value() == 0 or KEY_LEFT.value() == 0
def button_down():
    return KEY_DOWN.value() == 0 or KEY_RIGHT.value() == 0
def button_left():
    return KEY_B.value() == 0
def button_right():
    return KEY_A.value() == 0
    

BASE_COLOR = RED
display = lcd
def clear_display():
    lcd.fill(BLACK)

from pimoroni import Buzzer
BUZZER = Buzzer

def playtone(freq):
    pass

def bequiet():
    pass


def write_menu(settings, current_selection):
    
    lcd.fill(BLACK)
    x_offset = 10
    x_offset_2 = 45
    x_offset_3 = x_offset_2 + x_offset + 30
    x_offset_4 = x_offset_3 + 45
    line = draw_text("Pico Atemcoach ", x_offset, 0)
    line = draw_text("Laufzeit:", x_offset, line, selected=current_selection == 1)
    line = draw_text("%s" % settings.total_duration, 90, line - 1)
    
    line = draw_text("in", x_offset, line, selected=current_selection == 2)
    line = draw_text("%s" % (0.5 * settings.half_seconds_in), x_offset_2, line-1)
    line = draw_text("hold", x_offset_3, line-1, selected=current_selection == 3)
    line = draw_text("%s" % (0.5 * settings.half_seconds_hold), x_offset_4, line-1)
    
    line = draw_text("out", x_offset, line, selected=current_selection == 4)
    line = draw_text("%s" % (0.5 * settings.half_seconds_out), x_offset_2, line-1)
    line = draw_text("keep", x_offset_3, line-1, selected=current_selection == 5)
    line = draw_text("%s" % (0.5 * settings.half_seconds_stay), x_offset_4, line-1)
   
    line = draw_text("4-7-8", x_offset, line, selected=current_selection == 6)
    line = draw_text("box", x_offset_2 + 10, line-1, selected=current_selection == 7)
    line = draw_text("gold", x_offset_3 + 5, line-1, selected=current_selection == 8)
    line = draw_text("nat", x_offset_4, line-1, selected=current_selection == 9)

    line = draw_text("START BREATHING", x_offset, line, selected=current_selection == 10)
    lcd.display()
    
    
    
def visualize(progress, mode):

    if mode == Mode.IN:
        radius = max(1, int(progress * lcd.width))
        lcd.fill_rect(0, 0, radius, lcd.height, RED)
    elif mode == Mode.HOLD:
        lcd.fill_rect(0, 0, lcd.width, lcd.height, RED)
    elif mode == Mode.OUT:
        radius = max(1, int((1-progress) * lcd.width))
        lcd.fill_rect(radius, 0, radius, lcd.height, BLACK)
    elif mode == Mode.STAY:
        lcd.fill_rect(0, 0, lcd.width, lcd.height, BLACK)
    else:
        raise Exception("Unknown mode")

    lcd.display()

