import time
from datetime import datetime

DEPLOYMENT = False  # This variable is to understand whether you are deploying on the actual hardware

try:
    import RPi.GPIO as GPIO
    import SDL_DS3231

    DEPLOYMENT = True
except:
    import mock.GPIO as GPIO
    import mock.SDL_DS3231 as SDL_DS3231


class ParkingGarage:
    # Pin number declarations
    INFRARED_PIN1 = 11
    INFRARED_PIN2 = 12
    INFRARED_PIN3 = 13
    SERVO_PIN = 16
    LED_PIN = 18

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.INFRARED_PIN1, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN2, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN3, GPIO.IN)
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        self.rtc = SDL_DS3231.SDL_DS3231(1, 0x68)
        self.servo = GPIO.PWM(self.SERVO_PIN, 50)
        self.servo.start(
            2)  # Starts generating PWM on the pin with a duty cycle equal to 2% (corresponding to 0 degree)
        if DEPLOYMENT:  # Sleep only if you are deploying on the actual hardware
            time.sleep(1)  # Waits 1 second so that the servo motor has time to make the turn
        self.servo.ChangeDutyCycle(0)  # Sets duty cycle equal to 0% (corresponding to a low signal)
        self.door_open = False
        self.red_light_on = False

    def check_occupancy(self, pin: int) -> bool:
        valid_pins = [self.INFRARED_PIN1, self.INFRARED_PIN2, self.INFRARED_PIN3]

        if pin not in valid_pins:
            raise ParkingGarageError(f"Pin {pin} is not a valid sensor pin")

        value = GPIO.input(pin)
        return bool(value)

    def get_number_occupied_spots(self) -> int:
        pins = [self.INFRARED_PIN1, self.INFRARED_PIN2, self.INFRARED_PIN3]

        count = 0
        for pin in pins:
            if self.check_occupancy(pin):
                count += 1

        return count

    def calculate_parking_fee(self, entry_time: datetime) -> float:
        current_time = self.rtc.read_datetime()

        # Calculate hours spent
        time_diff = current_time - entry_time
        hours = time_diff.total_seconds() / 3600

        # Round up to nearest hour
        import math
        hours = math.ceil(hours)

        # Base price: 2.50€ per hour
        price = hours * 2.50

        # Add 25% fee on weekends (Saturday and Sunday)
        if current_time.weekday() >= 5:
            price *= 1.25

        return price

    def open_garage_door(self) -> None:
        # Open door: 180 degrees
        duty_cycle = (180 / 18) + 2
        self.change_servo_angle(duty_cycle)
        self.door_open = True

    def close_garage_door(self) -> None:
        # Close door: 0 degrees
        duty_cycle = (0 / 18) + 2
        self.change_servo_angle(duty_cycle)
        self.door_open = False

    def turn_on_red_light(self) -> None:
        GPIO.output(self.LED_PIN, True)
        self.red_light_on = True

    def turn_off_red_light(self) -> None:
        GPIO.output(self.LED_PIN, False)
        self.red_light_on = False

    def manage_red_light(self) -> None:
        occupied_spots = self.get_number_occupied_spots()

        if occupied_spots >= 3:
            self.turn_on_red_light()
        else:
            self.turn_off_red_light()

    def change_servo_angle(self, duty_cycle):
        """
        Changes the servo motor's angle by passing it the corresponding PWM duty cycle
        :param duty_cycle: the PWM duty cycle (it's a percentage value)
        """
        self.servo.ChangeDutyCycle(duty_cycle)
        if DEPLOYMENT:  # Sleep only if you are deploying on the actual hardware
            time.sleep(1)
        self.servo.ChangeDutyCycle(0)


class ParkingGarageError(Exception):
    pass
