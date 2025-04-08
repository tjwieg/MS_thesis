# MicroPython
# TJ Wiegman // Purdue University ABE

from machine import Pin, Timer
import machine, time

# Hardware Definitions
motorPin = machine.PWM(Pin(2), freq=333) # D2 has own LED, visualizes PWM
cameraPin = Pin(25, Pin.OUT, value=0) # Value: 0=on, 1=off

def motor_on(x):    
    # Turn on motor and camera
    motorPin.duty(562)
    cameraPin.value(0)

    # Turn off after 10 minutes
    schedule_timer.init(
        period = 1000*60*10,
        mode = Timer.ONE_SHOT,
        callback = motor_off
    )

def motor_off(x):
    # Turn off motor and camera
    motorPin.duty(512)
    cameraPin.value(1)

    # Turn back on after 5 minutes
    schedule_timer.init(
        period = 1000*60*5,
        mode = Timer.ONE_SHOT,
        callback = motor_on
    )

schedule_timer = Timer(0)
schedule_timer.init(
    period = 1000*20, # turn on after 20s
    mode = Timer.ONE_SHOT,
    callback = motor_on
)
