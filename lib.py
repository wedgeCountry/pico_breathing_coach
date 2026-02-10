import os
import json 
# this handy list converts notes into frequencies, which you can use with the explorer.set_tone function
tones = { "B0": 31, "C1": 33, "CS1": 35, "D1": 37, "DS1": 39, "E1": 41, "F1": 44, "FS1": 46, "G1": 49,  "GS1": 52, "A1": 55, "AS1": 58, "B1": 62, "C2": 65, "CS2": 69, "D2": 73, "DS2": 78, "E2": 82, "F2": 87, "FS2": 93, "G2": 98, "GS2": 104, "A2": 110, "AS2": 117, "B2": 123, "C3": 131, "CS3": 139, "D3": 147, "DS3": 156, "E3": 165, "F3": 175, "FS3": 185, "G3": 196, "GS3": 208, "A3": 220, "AS3": 233, "B3": 247, "C4": 262, "CS4": 277, "D4": 294, "DS4": 311, "E4": 330, "F4": 349, "FS4": 370, "G4": 392, "GS4": 415, "A4": 440, "AS4": 466, "B4": 494, "C5": 523, "CS5": 554, "D5": 587, "DS5": 622, "E5": 659, "F5": 698, "FS5": 740, "G5": 784, "GS5": 831, "A5": 880, "AS5": 932, "B5": 988, "C6": 1047, "CS6": 1109, "D6": 1175, "DS6": 1245, "E6": 1319, "F6": 1397, "FS6": 1480, "G6": 1568, "GS6": 1661, "A6": 1760, "AS6": 1865, "B6": 1976, "C7": 2093, "CS7": 2217, "D7": 2349, "DS7": 2489, "E7": 2637, "F7": 2794, "FS7": 2960, "G7": 3136, "GS7": 3322, "A7": 3520, "AS7": 3729, "B7": 3951, "C8": 4186, "CS8": 4435, "D8": 4699, "DS8": 4978}

class Mode:
    IN = "IN"
    HOLD = "HOLD"
    OUT = "OUT"
    STAY = "STAY"


def get_signal_tone(mode:Mode):
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


class BreathingSettings:

    FILE = "settings.json"
    
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

    def reset(self):
        self.__init__()
        if self.FILE in os.listdir():
            os.remove(self.FILE)
    
    def save(self):
        with open(self.FILE, "w") as f:
            json.dump(self.__dict__, f)
        print("saved json settings")
    
    def load(self):
        try:
            with open(self.FILE) as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("Settings file is not a dict")

            for key, value in data.items():
                setattr(self, key, value)

            return True

        except Exception as e:
            import sys
            print("Settings load failed")
            sys.print_exception(e)
            return False

        