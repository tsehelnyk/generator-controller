import time

DEBOUNCE_INTERVAL_MS = 30               # час стабільного стану кнопки


class DebouncedInput:
    def __init__(self, pin):
        self.pin = pin
        self.raw_value = pin.value()
        self.stable_value = self.raw_value
        self.changed_at = time.ticks_ms()

    def value(self):
        raw_value = self.pin.value()
        now = time.ticks_ms()

        if raw_value != self.raw_value:
            self.raw_value = raw_value
            self.changed_at = now
        elif (
            raw_value != self.stable_value
            and time.ticks_diff(now, self.changed_at) >= DEBOUNCE_INTERVAL_MS
        ):
            self.stable_value = raw_value

        return self.stable_value
