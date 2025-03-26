from time import sleep
from europi import *      
from europi_script import EuroPiScript

'''
SixBit

author: dorian fraser-moore ( [firstname]@fraser-moore.com - github.com/dorianfm )

Analog to Digital Sample and Hold.

SixBit samples the analog input when the digital input transitions from low to high (IE on a gate or trigger), translates the output
into a 6 bit value (0-63) and sets each output high or low corresponing to the values of each bit.

It can be used to generate interesting gate patterns from LFOs, amongst other things. 

The binary value is big endian, with the most significant bit being output on CV out 1

Digital In: trigger sample input
Analog In: Incoming CV
Knob 1: Set a minimum offset to determine output value from incoming CV
Knob 2: Set a maximum offset to determine output value from incoming CV
Button 1: manual sample of input
Button 2: resets minimum / maximum input percent values

CV Out [1-6] gates corresponding to the bit value calculated from analgoue in.

The display echos settings, input values and output value

Top Row: Minimum input percent < current input percent < Maximum input percent
Middle Row: Minimum sample offset < current sample percent < Maximum sample offset 
Bottom Row: current sample value = current binary output

The current sample offset is a scaled 64 bit representation of the current percent value between Minimum sample offset and Maximum sample offset.

--
This code is completely free to use and modify, no rights reserved, given or implied. Credit is appreciated, where practical. If you make any music using this I would love to hear it!

https://dorian.fraser-moore.com
https://onymous.in
https://theusefularts.org

'''

ORDERING_MSB=0
ORDERING_LSB=1

class SixBit(EuroPiScript):

    def __init__(self):
        super().__init__()
        self.sampled = False
        self.state = self.load_state_json()
        self.current_percent = 0
        self.reset_max_min()
        self.current_value = int(self.current_percent*63)
        self.current_binary = '{:0>{w}}'.format('0', w=6)
                
        if 'ordering' not in self.state.keys():
            self.state = {
                'ordering': ORDERING_MSB
            }
            self.save_state_json(self.state)


        @din.handler
        def gate_on():
            if self.sampled == False:
                self.sampled = True
                sample()

        @din.handler_falling
        def gate_off():
            all_off()
            self.sampled = False


        @b1.handler
        def b1_handler():
            sample()
            
        @b2.handler
        def b2_handler():
            self.reset_max_min()
    
       
        def sample():
            self.current_percent = ain.percent()
            pc_range = abs(self.max_percent - self.min_percent)
            if self.min_percent < self.max_percent:
                relative_value = abs(clamp(self.current_percent, self.min_percent, self.max_percent) - self.min_percent)
            else:
                relative_value = abs(clamp(self.current_percent, self.max_percent, self.min_percent) - self.min_percent)
            if pc_range == 0:
                self.current_percent = 0
            else:
                self.current_percent = round(relative_value/pc_range,2)
            self.current_value = int(self.current_percent*63)
            binary = '{:b}'.format(self.current_value)
            self.current_binary = '{:0>{w}}'.format(binary, w=6)
            set_binary(self.current_binary)
            
            
        def all_off():
            for idx in range(6):
                cvs[idx].off()    


        def set_binary(binary):
            bits = enumerate(binary)
            
            if self.state['ordering'] == ORDERING_MSB:
                bits = reversed(list(bits))
            
            idx = 0
            for i, c in bits:
                if c == "1":
                    cvs[idx].on()
                else:
                    cvs[idx].off()
                idx += 1
            

        def change_ordering():
            if self.state['ordering'] == ORDERING_MSB:
                self.state['ordering'] = ORDERING_LSB
            else:
                self.state['ordering'] = ORDERING_MSB
            set_binary(self.current_binary)


        def clamp(n, minn, maxn):
            return max(min(maxn, n), minn)
        

    @classmethod
    def display_name(cls):
        return "SixBit"


    def save_state(self):
        """Save the current state variables as JSON."""
        if self.last_saved() < 5000:
            return

        self.save_state_json(self.state)

    def reset_max_min(self):
        self.min_input_percent = 100;
        self.max_input_percent = 0;

    def main(self):
        # Remove builtin_driver=True if you don't want the MicroPython serial REPL available.
                    
        while True:
            self.min_percent = round(k1.percent(), 2)
            self.max_percent = round(k2.percent(), 2) 
            input_percent = round(ain.percent(), 2)
            if input_percent < self.min_input_percent:
                self.min_input_percent = input_percent
            if input_percent > self.max_input_percent:
                self.max_input_percent = input_percent;	
            input_value = int(input_percent*64)
            
            oled.fill(0)
            oled.text(f"{self.min_input_percent*100:03.0f} < {input_percent*100:03.0f} < {self.max_input_percent*100:03.0f}",0,0)
            oled.text(f"{self.min_percent*100:03.0f} < {self.current_percent*100:03.0f} < {self.max_percent*100:03.0f}",0,10);
            oled.text(f"{self.current_value} = {self.current_binary}",0,20);
            oled.show()
            time.sleep_ms(50)


if __name__ == "__main__":
    SixBit().main()


