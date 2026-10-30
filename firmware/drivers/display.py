"""Minimal SSD1306 I2C framebuffer display, written for this project."""
class Display:
    def __init__(self, i2c, address=0x3C):
        import framebuf
        self.i2c,self.address = i2c,address
        self.data=bytearray(1024)
        self.fb=framebuf.FrameBuffer(self.data,128,64,framebuf.MONO_VLSB)
        for cmd in (0xAE,0x20,0x00,0x40,0xA1,0xC8,0xA8,63,0xD3,0,0xDA,0x12,
                    0xD5,0x80,0xD9,0xF1,0xDB,0x30,0x81,0x7F,0xA4,0xA6,0x8D,0x14,0xAF):
            self.command(cmd)
    def command(self,v): self.i2c.writeto(self.address,bytes((0,v)))
    def show(self,lines):
        self.fb.fill(0)
        for n,line in enumerate(lines[:8]): self.fb.text(str(line)[:16],0,n*8,1)
        for cmd in (0x21,0,127,0x22,0,7): self.command(cmd)
        self.i2c.writeto(self.address,b"\x40"+self.data)
