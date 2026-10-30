"""MAX31865 4-wire Pt1000 driver. SPI mode 1; use matching 4.3k reference board."""
from firmware.core import temperature_from_resistance

class MAX31865:
    def __init__(self, spi, cs, rref=4300.0):
        self.spi, self.cs, self.rref = spi, cs, rref
        cs.value(1)
        self.write(0, 0xC3)  # Bias + continuous + 4-wire + clear faults + 50 Hz.
        self.write(0, 0xC1)

    def write(self, reg, value):
        self.cs.value(0)
        try: self.spi.write(bytes((reg | 0x80, value)))
        finally: self.cs.value(1)

    def read(self, reg, size):
        self.cs.value(0)
        try:
            self.spi.write(bytes((reg & 0x7F,)))
            data=self.spi.read(size)
            if not isinstance(data,(bytes,bytearray)) or len(data)!=size:
                raise ValueError("short or invalid SPI read")
            return data
        finally: self.cs.value(1)

    def temperature(self):
        raw = self.read(1, 2)
        code = (raw[0] << 8) | raw[1]
        if code & 1 or self.read(7, 1)[0]:
            # Clear the latched IC status for the next acquisition. Control remains
            # fault-latched until the operator re-arms after healthy measurements.
            self.write(0,0xC3)
            self.write(0,0xC1)
            raise ValueError("MAX31865 fault")
        return temperature_from_resistance((code >> 1)*self.rref/32768.0)
