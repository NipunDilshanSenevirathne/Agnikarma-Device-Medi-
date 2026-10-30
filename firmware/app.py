"""MicroPython RP2040 hardware adapter. No output enabled without bench provisioning."""
def run(role):
    from machine import Pin, SPI, I2C, PWM, ADC, UART, WDT
    import time, math, json
    from firmware import config as C
    from firmware.core import Controller,Supervisor,Sample,Inputs,Link,encode_frame,finite
    from firmware.drivers.max31865 import MAX31865
    from firmware.drivers.display import Display
    from firmware.provision import validate
    if role not in ("main", "supervisor"):
        raise ValueError("unknown controller role")
    out=Pin(C.PIN["output"],Pin.OUT,value=0)
    pulse=Pin(C.PIN["local_pulse"],Pin.OUT,value=0)
    pwm=None
    if role=="main":
        pwm=PWM(out);pwm.freq(C.PWM_HZ);pwm.duty_u16(0)
    def off():
        if pwm: pwm.duty_u16(0)
        else: out.value(0)
    off()
    ctrl=Controller() if role=="main" else Supervisor()
    spi=SPI(0,baudrate=500000,polarity=0,phase=1,sck=Pin(6),mosi=Pin(7),miso=Pin(4))
    uart=UART(0,baudrate=115200,tx=Pin(0),rx=Pin(1),timeout=0)
    link=Link("S" if role=="main" else "M")
    buttons=[Pin(x,Pin.IN,Pin.PULL_UP) for x in C.BUTTON_PINS]
    inputs={n:Pin(C.PIN[n],Pin.IN,Pin.PULL_UP) for n in ("cool","heat","arm","dock","tip")}
    peer=Pin(C.PIN["peer_pulse"],Pin.IN,Pin.PULL_DOWN)
    pack=ADC(26);ntc=ADC(27);tip=ADC(28)
    cfg={}
    try:
        with open("provision.json") as f:
            data=f.read(2049)
        if len(data)<=2048:cfg=json.loads(data)
    except (OSError,ValueError): pass
    provision,cfg=validate(cfg,role)
    offset=cfg["sensor_offset_c"];scale=cfg["battery_scale"]
    ref=cfg["reference_resistor_ohm"]
    sensor=MAX31865(spi,Pin(5,Pin.OUT,value=1),ref)
    display=None
    if role=="main":
        address=cfg["display_address"]
        try: display=Display(I2C(1,sda=Pin(2),scl=Pin(3),freq=400000),address)
        except OSError: provision=False  # A missing display prevents normal arming.
    wdt=WDT(timeout=2000)
    last_raw=time.ticks_ms(); now=0;seq=0;last_peer=peer.value();peer_stamp=-1000000
    choice_last=None;choice_since=0;last_display=-1000000
    try:
        while True:
            start=time.ticks_ms();delta=time.ticks_diff(start,last_raw);last_raw=start
            if delta<0: raise RuntimeError("clock discontinuity")
            now+=delta
            # Immediate output removal precedes all bus transactions.
            cool=not inputs["cool"].value();heat=not inputs["heat"].value()
            docked=not inputs["dock"].value();tip_present=not inputs["tip"].value()
            if cool or not heat or docked or not tip_present: off()
            val=peer.value()
            if val!=last_peer:last_peer=val;peer_stamp=now
            data=uart.read(96)
            if data:link.feed(data,now)
            pressed=[n for n,b in enumerate(buttons) if not b.value()]
            choice=pressed[0] if len(pressed)==1 else None
            if choice!=choice_last:choice_last=choice;choice_since=now
            if choice is not None and now-choice_since>=50:
                if C.PRESETS[choice]!=ctrl.target:off()
                ctrl.select(C.PRESETS[choice])
            if len(pressed)>1:off();ctrl.select(-1)
            valid=True
            try: temp=sensor.temperature()+offset
            except (OSError,ValueError,TypeError):temp=0.0;valid=False
            # ADC voltages are limited by external divider/protection; never connect pack directly.
            v=pack.read_u16()/65535*3.3*(139.0/39.0)*scale
            ratio=ntc.read_u16()/65535.0
            if .001<ratio<.999:
                r=10000*ratio/(1-ratio)
                tc=1/(1/298.15+math.log(r/10000)/3950)-273.15
            else:tc=999.0
            tip_ratio=tip.read_u16()/65535.0
            tid=next((n for n,r in C.TIP_CODES if abs(tip_ratio-r)<C.TIP_TOLERANCE),None)
            i=Inputs(now,Sample(temp,now,valid),link.temp,link.age(now),now-peer_stamp,
                     link.target,link.allow,v,tc,tid,heat,cool,not inputs["arm"].value(),
                     docked,tip_present,not valid,provision)
            if role=="main":
                duty=ctrl.step(i)
                pwm.duty_u16(int(duty*65535))
                permit=ctrl.armed and not ctrl.fault
            else:
                permit=ctrl.step(i);out.value(int(permit))
            uart.write(encode_frame("M" if role=="main" else "S",seq,ctrl.target,temp if valid else 0.0,permit))
            seq=(seq+1)&65535
            # Pulse only after complete acquisition/control/packet operation.
            pulse.value(1-pulse.value())
            if display and now-last_display>=250:
                display.show(["AGNI BENCH",ctrl.state,"SET %d C"%ctrl.target,
                              "TIP %.1f C"%temp if valid else "TEMP UNKNOWN",
                              "PACK %.2f V"%v,ctrl.fault or "HOLD HEAT"])
                last_display=now
            wdt.feed()
            elapsed=time.ticks_diff(time.ticks_ms(),start)
            time.sleep_ms(max(1,C.SAMPLE_MS-elapsed))
    finally:
        off();pulse.value(0)
