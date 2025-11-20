from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
from unittest.mock import Mock
from mock import GPIO
from mock.SDL_DS3231 import SDL_DS3231
from src.parking_garage import ParkingGarage
from src.parking_garage import ParkingGarageError

class TestParkingGarage(TestCase):

    @patch.object(GPIO, "input")
    def test_something(self, mock_object: Mock):
        mock_object.return_value = True
        garage = ParkingGarage()
        outcome = garage.check_occupancy(garage.INFRARED_PIN2)
        self.assertTrue(outcome)

    @patch.object(SDL_DS3231, "read_datetime")
    def test_calculate_parking_fee_monday(self, mock_datetime: Mock):
        entry_time = datetime(2025, 11, 18, 12, 30)
        exit_time = datetime(2025, 11, 18, 15, 24)
        mock_datetime.return_value = exit_time

        garage = ParkingGarage()
        fee = garage.calculate_parking_fee(entry_time)
        self.assertEqual(fee, 7.50)

    @patch.object(SDL_DS3231, "read_datetime")
    def test_calculate_parking_fee_saturday(self, mock_datetime: Mock):
        entry_time = datetime(2025, 11, 16, 10, 15)
        exit_time = datetime(2025, 11, 16, 18, 12)
        mock_datetime.return_value = exit_time

        garage = ParkingGarage()
        fee = garage.calculate_parking_fee(entry_time)
        self.assertEqual(fee, 25.00)

    @patch.object(GPIO, "PWM")
    def test_open_garage_door(self, mock_pwm: Mock):
        garage = ParkingGarage()
        garage.open_garage_door()
        self.assertTrue(garage.door_open)

    @patch.object(GPIO, "PWM")
    def test_close_garage_door(self, mock_pwm: Mock):
        garage = ParkingGarage()
        garage.close_garage_door()
        self.assertFalse(garage.door_open)

    @patch.object(GPIO, "output")
    def test_turn_on_red_light(self, mock_output: Mock):
        garage = ParkingGarage()
        garage.turn_on_red_light()
        self.assertTrue(garage.red_light_on)

    @patch.object(GPIO, "output")
    def test_turn_off_red_light(self, mock_output: Mock):
        garage = ParkingGarage()
        garage.turn_off_red_light()
        self.assertFalse(garage.red_light_on)

    @patch.object(GPIO, "input")
    @patch.object(GPIO, "output")
    def test_manage_red_light_on_when_full(self, mock_output: Mock, mock_input: Mock):
        mock_input.return_value = True
        garage = ParkingGarage()
        garage.manage_red_light()
        self.assertTrue(garage.red_light_on)

    @patch.object(GPIO, "input")
    @patch.object(GPIO, "output")
    def test_manage_red_light_off_when_not_full(self, mock_output: Mock, mock_input: Mock):
        mock_input.return_value = False
        garage = ParkingGarage()
        garage.manage_red_light()
        self.assertFalse(garage.red_light_on)
