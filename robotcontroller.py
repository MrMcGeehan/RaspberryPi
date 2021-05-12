import pygame
import time
import RPi.GPIO

"""
Step 1. Install the latest version of pygame with the following terminal command:

pip3 install pygame --upgrade

Step2. Adjust the pin values so the robot acts as expected

Examples:
If motora goes backwards when it should go forwards, I would switch motorA_pin1 and motorA_pin2

If the robot turns left when it should turn right, I would swap motorB and motorB
"""
motorA_pin1 = 10
motorA_pin2 = 9
motorB_pin1 = 8
motorB_pin2 = 7

class Motor:
    def __init__(self, pin1: int, pin2: int):
        self.pin1 = pin1
        self.pin2 = pin2

        RPi.GPIO.setup(self.pin1, RPi.GPIO.OUT)
        RPi.GPIO.setup(self.pin2, RPi.GPIO.OUT)

        self.pwm1 = RPi.GPIO.PWM(self.pin1, 20)
        self.pwm2 = RPi.GPIO.PWM(self.pin2, 20)

        self.pwm1.start(0)
        self.pwm2.start(0)
    
    def set_forward_speed(self, speed: int):
        self.pwm2.ChangeDutyCycle(0)
        self.pwm1.ChangeDutyCycle(speed)
    
    def set_backwards_speed(self, speed: int):
        self.pwm1.ChangeDutyCycle(0)
        self.pwm2.ChangeDutyCycle(speed)

    def set_motor_val(self, val: int):
        
        # If value is positive, set forward speed, else backwards speed
        if val >= 0:
            self.set_forward_speed(val)
        elif val < 0:
            self.set_backwards_speed(abs(val))

class Robot:
    def __init__(self, a_pins: tuple, b_pins: tuple):
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setwarnings(False)

        self.motora = Motor(a_pins[0], a_pins[1])
        self.motorb = Motor(b_pins[0], b_pins[1])

    def update(self, speed: int, turning: int):

        # Set initial motor values to the speed
        aval = speed
        bval = speed

        # Adjust turning input based on speed to make the control feel more natural
        adjturning = turning * (abs(speed)/60)

        if abs(adjturning) < 25 and abs(turning) > 25:
            if turning > 0:
                adjturning = 25
            else:
                adjturning = -25
            

        # Adjust the motor values with the turning amount
        if adjturning > 0:
            aval += adjturning
            bval -= adjturning
        else:
            bval += abs(adjturning)
            aval -= abs(adjturning)
        
        # Check out of bounds
        if aval > 100:
            aval = 100
        
        if aval < -100:
            aval = -100
        
        if bval > 100:
            bval = 100
        
        if bval < -100:
            bval = -100
        

        self.motora.set_motor_val(aval)
        self.motorb.set_motor_val(bval)


    def __del__(self):
        RPi.GPIO.cleanup()

class JoystickHandler:
    def __init__(self, joystick_id: int, robot: Robot):
        pygame.init()
        pygame.joystick.init()

        self.joystick_id = joystick_id
        self.pygame_joystick = pygame.joystick.Joystick(self.joystick_id)

        self.pygame_joystick.init()

        self.robot = robot

    def update(self):
        pygame.event.get()

        # Get joystick position
        left_right_val = self.pygame_joystick.get_axis(0)
        forward_backward_val = self.pygame_joystick.get_axis(1)

        speed = 0
        turning = 0

        # If value is outside of deadzone, scale it by 100
        if abs(forward_backward_val) > 0.05:
            speed = forward_backward_val * 100
        
        if abs(left_right_val) > 0.05:
            turning = left_right_val * 50

        self.robot.update(speed, turning)


    def __del__(self):
        pygame.joystick.quit()
        pygame.quit()

if __name__ == "__main__":
    robot = Robot((motorA_pin1, motorA_pin2), (motorB_pin1, motorB_pin2))
    joystick = JoystickHandler(0, robot)

    # Call update 10x per second while program is open
    while True:
        joystick.update()
        time.sleep(0.1)
    