from time import sleep
from europi import *      
from europi_script import EuroPiScript
import usb.device
from usb.device.midi import MIDIInterface

'''
MIDI
author: dorian fraser-moore ( dorian.fraser-moore.com / onymous.in / theusefularts.org / github.com/dorianfm )

MIDI to CV converter.

CV Out [1-6] gates corresponding to the bit value calcualted from analgoue in

Ideas / to do:

Allow reversing the endian of the outputs
Allow for scaling or limiting the range that output value is calcualted from.
'''

_CIN_PITCH_BEND = const(0xE)

DEFAULT_STATE = {
    'preset': 5,
    'presets': {
        0: {
            1: {
                "channel": 1,
                "type": 'gate'
            },
            2: {
                "channel": 1,
                "type": 'note',
            },
            3: {
                "channel": 1,
                "type": 'velocity',
            },
            4: {
                "channel": 1,
                "type": 'bend'
            },
            5: {
                "channel": 1,
                "type": 'cc',
                "controller": 0,
            },
            6: {
                "channel": 1,
                "type": 'cc',
                "controller": 1,
            }
        },
        1: {
            1: {
                "channel": 1,
                "type": 'gate'
            },
            2: {
                "channel": 1,
                "type": 'note',
            },
            3: {
                "channel": 1,
                "type": 'velocity',
            },
            4: {
                "channel": 2,
                "type": 'gate'
            },
            5: {
                "channel": 2,
                "type": 'note',
            },
            6: {
                "channel": 2,
                "type": 'velocity',
            }
        },
        2: {
          1: {
                "channel": 1,
                "type": 'gate'
            },
            2: {
                "channel": 2,
                "type": 'gate',
            },
            3: {
                "channel": 3,
                "type": 'gate',
            },
            4: {
                "channel": 1,
                "type": 'note'
            },
            5: {
                "channel": 2,
                "type": 'note',
            },
            6: {
                "channel": 3,
                "type": 'note',
            }   
        },
        3: {
          1: {
                "channel": 1,
                "type": 'gate',
                "note": 80,
            },
            2: {
                "channel": 1,
                "type": 'gate',
                "note": 81,
            },
            3: {
                "channel": 1,
                "type": 'gate',
                "note": 82,
            },
            4: {
                "channel": 1,
                "type": 'gate',
                "note": 83,
            },
            5: {
                "channel": 1,
                "type": 'gate',
                "note": 84,
            },
            6: {
                "channel": 1,
                "type": 'gate',
                "note": 85,
            },  
        },
        4: {
          1: {
                "channel": 1,
                "type": 'cc',
                "controller": 0,
            },
            2: {
                "channel": 1,
                "type": 'cc',
                "controller": 1,
            },
            3: {
                "channel": 1,
                "type": 'cc',
                "controller": 2,
            },
            4: {
                "channel": 1,
                "type": 'cc',
                "controller": 3,
            },
            5: {
                "channel": 1,
                "type": 'cc',
                "controller": 4,
            },
            6: {
                "channel": 1,
                "type": 'cc',
                "controller": 5,
            },  
        },
        5: {
            1: {
                "channel": 1,
                "type": 'bend',
            },
            2: {
                "channel": 2,
                "type": 'bend',
            },
            3: {
                "channel": 3,
                "type": 'bend',
            },
            4: {
                "channel": 4,
                "type": 'bend',
            },
            5: {
                "channel": 5,
                "type": 'bend',
            },
            6: {
                "channel": 6,
                "type": 'bend',
            },  
        },
    }
}

class MIDIListener(MIDIInterface):
    # Very simple example event handler functions, showing how to receive note
    # and control change messages sent from the host to the device.
    #
    # If you need to send MIDI data to the host, then it's fine to instantiate
    # MIDIInterface class directly.

    def on_open(self):
        super().on_open()
        

    def on_midi_event(self, cin, midi0, midi1, midi2):
        ch = midi0 & 0x0F
        oled.fill_rect(0, 0, 128, 12, 0)
        oled.text(f"! c{ch} {midi0} {midi1} {midi2}", 0, 0)         
        if cin == _CIN_PITCH_BEND:
            self.on_pitch_bend(ch, midi1, midi2);
        else:
            super().on_midi_event(cin, midi0, midi1, midi2);
    

    def on_note_on(self, channel, pitch, vel):
        oled.fill_rect(0, 12, 128, 24, 0)
        if (pitch > 120):
            pitch = 120
        if channel == 0:
            oled.text(f"On c{channel} p{pitch} v{vel}", 0, 12)
            cv1.on()
            cv2.voltage(10 * (pitch / 120))
            cv3.voltage(10 * (vel / 127))
        elif channel == 1:
            oled.text(f"On c{channel} p{pitch} v{vel}", 0, 12)
            cv4.on()
            cv5.voltage(10 * (pitch / 120))
            cv6.voltage(10 * (vel / 127))

    def on_note_off(self, channel, pitch, vel):
        oled.fill_rect(0, 12, 128, 24, 0)
        if channel == 0:
            oled.text(f"Off c{channel} p{pitch} v{vel}", 0, 12)
            cv1.off()
        elif channel == 1:
            oled.text(f"Off c{channel} p{pitch} v{vel}", 0, 12)
            cv4.off()

    def on_control_change(self, channel, controller, value):
        oled.centre_text(f"CC c{channel} x{controller} v{value}")
        
    def on_pitch_bend(ch, midi1, midi2):
        oled.centre_text(f"PB c{channel} 1:{midi1} 2:{midi2}")

class Display():
    def setup(self):
        oled.fill(0);
        oled.hline(0,16,128,16);
        oled.vline(42,0,42,16);
        oled.vline(84,0,84,16);
        oled.show()
        
    def output1(self, value):
        oled.fill_rect(0,0,41,15)
        oled.text(f"{value}",0, 0)
    

class MIDI(EuroPiScript):
    d = Display()
    m = MIDIListener()
    enabled = False
    
    def __init__(self):
        super().__init__()
        state = self.load_state_json()

        self.enabled = state.get("enabled", True)

        @b1.handler
        def b1_handler():
            self.toggle_enablement()

    @classmethod
    def display_name(cls):
        return "MIDI"

    def toggle_enablement(self):
        self.enabled = not self.enabled
        self.save_state()

    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:
            return

        # state = 
        self.save_state_json(self.state)
        

    def main(self):
        oled.centre_text('INIT')
        # Remove builtin_driver=True if you don't want the MicroPython serial REPL available.
        usb.device.get().init(self.m, manufacturer_str="Onymous", product_str="EuroPiMIDI")
        
        while True:
            oled.fill_rect(0, 24, 128, 12, 0)
            pc = k1.percent()
            if self.enabled:
               oled.text(f"enabled {pc}", 0, 24)
            else:
               oled.text(f"disabled {pc}", 0, 24)
            oled.show()
            time.sleep_ms(100)

if __name__ == "__main__":
    MIDI().main()




