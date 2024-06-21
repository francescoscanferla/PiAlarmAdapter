import threading
import time


class MockSensor:
    def __init__(self, btn, interval=10):
        self.sensor = btn
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._toggle_state)
        self._state = False

    def _toggle_state(self):
        while not self._stop_event.is_set():
            self._state = not self._state
            if self._state:
                self.sensor.pin.drive_low()
                print(f"Sensor on pin {self.sensor.pin} set to LOW (pressed).")
            else:
                self.sensor.pin.drive_high()
                print(f"Sensor on pin {self.sensor.pin} set to HIGH (released).")
            time.sleep(self.interval)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()
