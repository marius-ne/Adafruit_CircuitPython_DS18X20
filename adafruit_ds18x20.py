import time
from adafruit_onewire.device import OneWireDevice

_CONVERT = b"\x44"
_RD_SCRATCH = b"\xBE"
_WR_SCRATCH = b"\x4E"
RESOLUTION = (9, 10, 11, 12)

class DS18X20:
    def __init__(self, bus, address):
        if address.family_code == 0x10 or address.family_code == 0x28:
            self._address = address
            self._device = OneWireDevice(bus, address)
            self._buf = bytearray(9)
        else:
            raise ValueError("Incorrect family code in device address.")

    @property
    def temperature(self):
        """The temperature in degrees Celsius."""
        self._convert_temp()
        return self._read_temp()

    def _convert_temp(self):
        with self._device as dev:
            dev.write(_CONVERT)
            start_time = time.monotonic()
            if timeout > 0:
                dev.readinto(self._buf, end=1)
                # 0 = conversion in progress, 1 = conversion done
                while self._buf[0] == 0x00:
                    dev.readinto(self._buf, end=1)

    def _read_temp(self):
        buf = self._read_scratch()
        if self._address.family_code == 0x10:
            if buf[1]:
                t = buf[0] >> 1 | 0x80
                t = -((~t + 1) & 0xFF)
            else:
                t = buf[0] >> 1
            return t - 0.25 + (buf[7] - buf[6]) / buf[7]
        t = buf[1] << 8 | buf[0]
        if t & 0x8000:  # sign bit set
            t = -((t ^ 0xFFFF) + 1)
        return t / 16

    def _read_scratch(self):
        with self._device as dev:
            dev.write(_RD_SCRATCH)
            dev.readinto(self._buf)
        return self._buf