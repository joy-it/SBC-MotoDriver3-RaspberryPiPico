# Import of Librarys
from machine import I2C, Pin
import utime

_oe_pin = Pin(2, Pin.OUT)
_address = 0x15
i2c = I2C(0, sda = Pin(0), scl = Pin(1), freq = 100000)

numberSteps = 0
stepDelay = 0
stepNumber = 0
lastStepTime = 0
direction = 0

# Register addresses
LED_OFF_ALL = 0x00
LED_ON_ALL = 0x55
LED_PWM_ALL = 0xAA
LEDOUT0 = 0x0C
LEDOUT1 = 0x0D

def init(address, oe_pin):
    _oe_pin = oe_pin
    _oe_pin = Pin(oe_pin, Pin.OUT)
    _address = address

# Writes to a register
def write_reg(reg, val):
    msg = bytearray()
    msg.append(val)
    i2c.writeto_mem(_address, reg, msg)

# Reads from a register
def read_reg(reg):
    msg = bytearray()
    msg.append(reg & 0x1F)
    i2c.writeto(_address, msg)
    data = i2c.readfrom(_address, 1)
    return data

# Uses a I2C adress reset
def soft_reset():
    i2c.writeto(0x03, 0xA5)
    i2c.writeto(0x03, 0x5A)

# Sets up the whole chip and I2C connection
def begin():
    _oe_pin.low()
    utime.sleep(0.01)
    write_reg(0x00, 0x01)
    utime.sleep(0.0005)
    write_reg(0x01, 0x14)
    utime.sleep(0.01)

# Sets a channel or all channels to different state
def pinType(type, pin, all=False):
    dataType, regValue = None, None
    if(type > 2):
        type = 0
    if type == 0:
        if all:
            write_reg(LEDOUT0, LED_OFF_ALL)
            write_reg(LEDOUT1, LED_OFF_ALL)
        elif pin < 4:
            regValue = read_reg(LEDOUT0)
            bc0 = bitClear(regValue, (pin*2))
            bc1 = bitClear(regValue, (pin*2+1))
            write_reg(LEDOUT0, bc1)
        elif pin >= 4:
            pin -= 4
            regValue = read_reg(LEDOUT1)
            bc0 = bitClear(regValue, (pin*2))
            bc1 = bitClear(regValue, (pin*2+1))
            write_reg(LEDOUT1, bc1)
    elif type == 1:
        if all:
            write_reg(LEDOUT0, LED_ON_ALL)
            write_reg(LEDOUT1, LED_ON_ALL)
        elif pin < 4:
            regValue = read_reg(LEDOUT0)
            bc = bitClear(regValue, (pin*2))
            bs = bitSet(regValue, (pin*2+1))
            write_reg(LEDOUT0, bs)
        elif pin >= 4:
            pin -= 4
            regValue = read_reg(LEDOUT1)
            bc = bitClear(regValue, (pin*2))
            bs = bitSet(regValue, (pin*2+1))
            write_reg(LEDOUT1, bc)
    elif type == 2:
        if all:
            write_reg(LEDOUT0, LED_PWM_ALL)
            write_reg(LEDOUT1, LED_PWM_ALL)
        elif pin < 4:
            regValue = read_reg(LEDOUT0)
            bc = bitClear(regValue, (pin*2))
            bs = bitSet(regValue, (pin*2+1))
            write_reg(LEDOUT0, bs)
        elif pin >= 4:
            pin -= 4
            regValue = read_reg(LEDOUT1)
            bc = bitClear(regValue, (pin*2))
            bs = bitSet(regValue, (pin*2+1))
            write_reg(LEDOUT1, bs)

    # Writes a pwm value to a channel
def chanPwm(channel, value):
    channel += 2
    write_reg(channel, value)

# Uses the output enable pin to enable and disable all channels, doesn't effect the previous state.
def enabled(state):
    if state:
        _oe_pin.low()
    else:
        _oe_pin.high()

# Turn a channel on
def on(pin):
    pinType(1, pin)
    chanPwm(pin, 255)

# Turn a channel off
def off(pin):
    pinType(0, pin)
    chanPwm(pin, 0)

# Turn all channels on
def allOn(forward=False, backward=False):
    if (forward):
        pin = 0
        for i in range(4):
            pwm(pin, 255)
            pin = pin + 2
    elif (backward):
        pin = 1
        for i in range(4):
            pwm(pin, 255)
            pin = pin + 2
    else:
        pinType(1, 0, True)
        for i in range(8):
            chanPwm(i, 255)

# Turn all channels off
def allOff():
    pinType(0, 0, True)
    for i in range(8):
        chanPwm(i, 0)

# Fade in for single led channel
def fadeIn(pin, timer, brightness):
    pinType(2, pin)
    interval = timer / brightness
    for i in range(0, brightness+1, +1):
        chanPwm(pin, i)
        utime.sleep(interval)
    if brightness == 255:
        pinType(1, pin)

# Fade out for single led channel
def fadeOut(pin, timer, brightness):
    regValue = read_reg(pin + 2)
    ib = int.from_bytes(regValue, "big")
    pinType(2, pin)
    interval = timer / (ib - brightness)
    for i in range(ib, brightness-1, -1):
        chanPwm(pin, i)
        utime.sleep(interval)
    if brightness == 0:
        pinType(0, pin)

# Pwm function for each individual channel
def pwm(pin, value):
    pinType(2, pin)
    chanPwm(pin, value)

# Check if a led is Off, On or PWM modus
def ledStatus(pin):
    regValue = 0
    first, second = False, False
    if pin < 4:
        regValue = read_reg(LEDOUT0)
        ib = int.from_bytes(regValue, "big")
        first = bool((ib >> (pin*2)) & 0x01)
        second = bool((ib >> (pin*2+1)) & 0x01)
    else:
        pin -= 4
        regValue = read_reg(LEDOUT1)
        ib = int.from_bytes(regValue, "big")
        first = bool((ib >> (pin*2)) & 0x01)
        second = bool((ib >> (pin*2+1)) & 0x01)
    if not first and not second:
        return 0
    elif first and not second:
        return 1
    elif not first and second:
        return 2

# Check the PWM value of a channel
def pwmStatus(pin):
    ib = int.from_bytes((read_reg(pin + 2)), "big")
    return ib

# Set the speed and the max amount of steps for the stepper motor
def StepperSpeed(speed, steps):
    global numberSteps
    global stepDelay
    numberSteps = steps
    stepDelay = (60 * 1000 * 1000 / steps / speed)

# Decide the direction in which the stepper motor is supposed to turn
def Stepper(stepAmount, pin1, pin2, pin3, pin4):
    global numberSteps
    global lastStepTime
    global stepNumber
    global direction
    stepsRemaining = abs(stepAmount)
    if stepAmount > 0: direction = 1
    if stepAmount < 0: direction = 0
    
    while stepsRemaining > 0:
        now = utime.ticks_us()
        if (now - lastStepTime) >= stepDelay:
            lastStepTime = now
            if direction == 1:
                stepNumber += 1
                if stepNumber == numberSteps:
                    stepNumber = 0
            else:
                if stepNumber == 0:
                    stepNumber = numberSteps
                stepNumber -= 1
            stepsRemaining -= 1
            stepMotor(stepNumber % 4, pin1, pin2, pin3, pin4)
            
# Makes the Stepper motor move according to the direction
def stepMotor(thisStep, pin1, pin2, pin3, pin4):
    if direction == 1:
        if thisStep == 0:
            pwm(pin1, 250)
            pwm(pin2, 0)
            pwm(pin3, 250)
            pwm(pin4, 0)
        if thisStep == 1:
            pwm(pin1, 0)
            pwm(pin2, 250)
            pwm(pin3, 250)
            pwm(pin4, 0)
        if thisStep == 2:
            pwm(pin1, 0)
            pwm(pin2, 250)
            pwm(pin3, 0)
            pwm(pin4, 250)
        if thisStep == 3:
            pwm(pin1, 250)
            pwm(pin2, 0)
            pwm(pin3, 0)
            pwm(pin4, 250)
    elif direction == 0:
        if thisStep == 0:
            pwm(pin4, 250)
            pwm(pin3, 0)
            pwm(pin2, 250)
            pwm(pin1, 0)
        if thisStep == 1:
            pwm(pin4, 0)
            pwm(pin3, 250)
            pwm(pin2, 250)
            pwm(pin1, 0)
        if thisStep == 2:
            pwm(pin4, 0)
            pwm(pin3, 250)
            pwm(pin2, 0)
            pwm(pin1, 250)
        if thisStep == 3:
            pwm(pin4, 250)
            pwm(pin3, 0)
            pwm(pin2, 0)
            pwm(pin1, 250)
    
def bitSet(int_type, offset):
    # Returns an integer with the bit at 'offset' set to 1.
    mask = 1 << offset
    binary = int.from_bytes(int_type, "big")
    return (binary | mask)

def bitClear(int_type, offset):
    # Returns an integer with the bit at 'offset' cleared.
    mask = ~(1 << offset)
    binary = int.from_bytes(int_type, "big")
    return (binary & mask)