# Firmware build, deployment and operation

## Environment
Host: Python 3.10+. Target: Raspberry Pi Pico RP2040 with MicroPython. API baseline: [MicroPython 1.26.0 RP2 documentation](https://docs.micropython.org/en/v1.26.0/rp2/quickref.html). Obtain the official RP2040 Pico UF2 from the MicroPython project; a UF2 runtime is not redistributed here. No target-board run was possible in this environment.

Run `python -m tools.deploy main` and `python -m tools.deploy supervisor`. Copy contents from each corresponding build folder to the board root using a MicroPython file tool such as `mpremote` or Thonny. The generated root `main.py` chooses the role. Do not interchange role configurations.

## Wiring/API contract
`hardware/pinmap.csv` is the GPIO/physical-pin authority. SPI0 is mode 1 at 500 kHz: SCK GP6, MOSI GP7, MISO GP4, CS GP5. Each controller has its own MAX31865 and sensor. Main I2C1 uses GP2 SDA/GP3 SCL. UART0 uses GP0 TX/GP1 RX crossed to the peer through branch resistors. No GPIO accepts a 5 V signal. Each role's GP20 pulse goes to the other role's GP19.

Select the Adafruit 326 STEMMA QT revision with automatic reset; older reset-dependent revisions need additional circuit/firmware changes. [Manufacturer wiring guide](https://learn.adafruit.com/monochrome-oled-breakouts/wiring-128x64-oleds).

MAX31865 configuration is continuous conversion, bias enabled, 4-wire and 50 Hz rejection. The two 4.3 kohm module references and conversion reference must agree. A 100 ohm/Pt100 module is not interchangeable. The minimal OLED driver defaults to 0x3C; check the actual I2C address and set `display_address` in provision.json to decimal 60 (0x3C) or 61 (0x3D). Missing display prevents main provisioning. Latched MAX31865 fault status is cleared for the next acquisition; controller re-arming still requires healthy measurements and a deliberate ARM edge.

## Provisioning
The JSON top level must be an object; numbers must be finite int/float values, not booleans or strings. Reads are bounded, role must match and the calibration identifier must be a nonempty measured-record name. These checks validate structure only.

Default `provision.json` has `bench_enabled=false` and `calibration_record=UNMEASURED`. Both inhibit all heat. Record an actual calibration identifier and measured correction values before enabling a guarded bench test. `sensor_offset_c` is bounded to +/-5 C and `battery_scale` to 0.8-1.2 as input checks, not a sufficient calibration model. A single offset cannot correct arbitrary thermal lag or nonlinear error; characterize and revise the model if necessary.

Do not claim that entering a calibration string proves calibration. The operator is responsible for retaining measured records. Maximum duty is initially restricted to 0.50; gains, thresholds, timeouts and limits in `config.py` are unvalidated bench settings. This can prevent reaching high setpoints under load. Do not increase limits just to pass a display demonstration.

## Operation
On startup both roles inhibit outputs. Release ARM/HEAT/COOL. Press a single preset for at least 200 ms, allow both controllers to agree, then press ARM while HEAT is released. Hold HEAT to request energy. Release HEAT to remove energy. Press COOL to latch off and cool. Setting changes and faults require a new release/press ARM sequence after conditions recover. Holding ARM at startup cannot arm the unit.

`HOLDING` only describes sensor error within the bench band; it is not a clinical READY claim. `COOLED_LOCKED` uses a 40 C bench display threshold, not a validated touch-safe threshold. Sensor disagreement, stale communication or invalid data withdraws output. COOL with an invalid sensor displays HOT_UNKNOWN.

## Failure boundaries
The RP2040 watchdog resets a stalled target after 2 s. The peer software checks heartbeat and packet age at a 350 ms bench limit. A stalled supervisor can retain relay drive until watchdog reset; release time and stored-energy consequences require measurement. The same software/runtime on both boards is a common-cause risk. CRC detects transmission errors, not malicious commands. No network connection is implemented.

Power the two Pico modules from 5 V VSYS, never 2S pack voltage. Keep USB disconnected during powered heater tests unless the combined supply/ground arrangement has been reviewed. A PC USB cable can create unexpected current paths and is not medical isolation.

## Deployment and recovery audit notes
Deployment preserves an existing local record by default. Use `--reset-provision` only when intentionally discarding it for disabled defaults. After a single-board reboot, sequence replay checks may require rebooting both boards together; automatic session resynchronization is not implemented. A supervisor relay output now requires both its own checks and the main armed permit. Firmware remains untested on an actual Pico.
