import math
import time

from bluer_sbc.hardware.hardware import Hardware
from bluer_sbc.logger import logger


class Abstract_Hat(Hardware):
    def __init__(self):
        super().__init__()

        self.switch_pin = -1

        self.green_switch_pin = -1
        self.red_switch_pin = -1
        self.trigger_pin = -1

        self.looper_pin = -1  # red led
        self.incoming_pin = -1  # yellow led
        self.data_pin = -1  # green led
        self.outgoing_pin = -1  # blue led

        self.green_led_pin = -1
        self.red_led_pin = -1

        self.pin_history = {}

    def activated(self, pin):
        """
        is pin activated?
        :param pin: pin number
        :return: True / False
        """
        if pin in self.input_pins:
            return self.input(pin) == False

        return False

    def input(self, pin):
        """
        read pin input.
        :param pin: pin number
        :return: True / False
        """
        return True

    @property
    def input_pins(self):
        return [
            pin
            for pin in [
                self.switch_pin,
                self.green_switch_pin,
                self.red_switch_pin,
                self.trigger_pin,
            ]
            if pin != -1
        ]

    def output(self, pin, output):
        """
        set pin to output
        :param pin: pin number
        :param output: True / False
        :return: self
        """
        return self

    @property
    def output_pins(self):
        return [
            pin
            for pin in [
                self.looper_pin,
                self.incoming_pin,
                self.data_pin,
                self.outgoing_pin,
                self.green_led_pin,
                self.red_led_pin,
            ]
            if pin != -1
        ]

    def pulse(self, pin=None, frequency=None):
        """
        pulse pin.
        :param pin: pin number / "data" / "incoming" / "loop" / "outputs"
        :param frequency: frequency
        :return: self
        """
        super().pulse(pin, frequency)

        if pin == "data":
            pin = self.data_pin

        if pin == "incoming":
            pin = self.incoming_pin

        if pin == "loop":
            pin = self.looper_pin

        if pin == "outputs":
            for index, pin in enumerate(self.output_pins):
                self.pulse(pin, index)

            return self

        if pin is None:
            for pin in self.output_pins:
                self.pulse(pin, frequency)

            return self

        self.pin_history[pin] = (
            not bool(self.pin_history.get(pin, False))
            if frequency is None
            else (lambda x: x - math.floor(x))(time.time() * (10 + frequency)) >= 0.5
        )

        return self.output(pin, self.pin_history[pin])

    def release(self):
        """
        release self
        :return: self
        """
        return self

    def setup(self, pin, what, pull_up_down=None):
        """
        Set up pin.
        :param pin: pin number
        :param what: "input" / "output"
        :return: self
        """
        return self
