# Import all required libraries
import machine
import SBC_MotoDriver3_Lib
from utime import sleep, sleep_ms
import sys

# Main Loop
if __name__ == '__main__':
    try:
        # Initialization of the board with I2C address 0x15 and oe_pin 17
        SBC_MotoDriver3_Lib.init(0x15, 16)
        # Pull the oe_pin low to activate the board
        SBC_MotoDriver3_Lib.enabled(True)
        # Starts the I2C communication
        SBC_MotoDriver3_Lib.begin()
        # Switch off all outputs
        SBC_MotoDriver3_Lib.allOff()
        # Define the RPM and the maximum number of steps for the stepper motor
        SBC_MotoDriver3_Lib.StepperSpeed(60, 2048)
        while True:
            print("Normal usage")
            # Switch on all even outputs
            SBC_MotoDriver3_Lib.allOn(True, False)
            sleep(1)
            SBC_MotoDriver3_Lib.allOff()
            sleep(1)
            # Switch on all odd outputs
            SBC_MotoDriver3_Lib.allOn(False, True)
            sleep(1)
            SBC_MotoDriver3_Lib.allOff()
            sleep(2)
            # Switch on a specific output
            SBC_MotoDriver3_Lib.on(0)
            sleep(2)
            # Switch off a specific output
            SBC_MotoDriver3_Lib.off(0)
            sleep(.5)
            # A specific output is faded in to a specific value over a specific 
            SBC_MotoDriver3_Lib.fadeIn(0, 20, 250)
            SBC_MotoDriver3_Lib.fadeOut(0, 20, 0)
            sleep(1)
            # Sets the Pwm value of a specific output
            SBC_MotoDriver3_Lib.pwm(0, 199)
            sleep(1)
            # Read the status of the specified output
            print(SBC_MotoDriver3_Lib.ledStatus(0))
            print(SBC_MotoDriver3_Lib.pwmStatus(0))
            sleep(2)
            SBC_MotoDriver3_Lib.allOff()
            sleep(1)
            print("Stepper")
            # Let the stepper motor move the desired number of steps on the desired pins at the previously set speed.
            SBC_MotoDriver3_Lib.Stepper(2000, 4, 5, 6, 7)
            sleep(1)

    except KeyboardInterrupt:
        SBC_MotoDriver3_Lib.allOff()
        sys.exit()