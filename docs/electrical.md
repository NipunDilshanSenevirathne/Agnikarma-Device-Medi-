# Electrical assembly authority P4

The P3 module design supersedes the earlier conceptual small PCB and eFuse proposal. Do not combine unrelated revisions. The current netlist uses a normally-open relay for heater supply and a MOSFET for PWM return. Use `hardware/design.json`, `component_connections.csv` and `pinmap.csv` together.

## Power stage
Pack/bench positive -> F1 -> PACK_FUSED -> K1 COM. K1 NO -> heater positive. Heater negative -> Q1 drain. Q1 source -> power return. The DC current does not pass through a Pico or a sensor-module return wire. Q1's exposed tab is electrically connected to drain. Use a mechanically secure power harness and heat-rated insulating arrangement. Do not use a solderless breadboard for this current.

TC4420CPA PDIP-8: pins 1 and 8 to 5 V, pin 2 PWM input, pin 3 unconnected, pins 4 and 5 ground, pins 6 and 7 tied to DRIVE. DRIVE -> 10 ohm R1 -> Q1 gate. R2 gate-to-source=100k; R3 driver input-to-ground=100k. Place 100nF and 1uF bypasses next to driver supplies. Check manufacturer pinout before soldering; inverting TC4429 is not equivalent.

## Physical interruption
5 V -> COOL pole A NC -> dock pole A NC -> positively locked-tip pole A NO -> K1 coil A. K1 coil B -> PN2222ABU collector. Emitter -> GND; base from supervisor GP21 through 330 ohm, with 100k base-emitter pull-down. 1N4007 cathode at coil A, anode at coil B. Flyback suppression increases release time; measure it. NC relay contact is unused. A stuck/welded relay is a known unresolved failure requiring evaluation; this is not a certified safety relay.

COOL pole B NO shorts the shared COOL logic bus to GND. Dock and tip second poles independently report state to both controllers. Every shared button/input has a separate 1k branch to each Pico; the two Pico 3V3 regulator outputs are never joined. Select switches with ratings appropriate for the relay-coil current and actual environment. An open UI wire is not automatically diagnosed; hardware interruption and wiring faults need testing.

## ADC inputs
Each board has its own 100k/39k pack divider, 1k series resistor, 10nF shunt capacitor and clamp diodes. Nominal scale is 139/39. No pack voltage goes directly to an ADC. Verify worst-case clamp behaviour, source impedance, reference error, leakage and unpowered backfeeding. The dividers are not substitutes for battery-pack protection.

Each NTC input has 10k to its own 3V3 and an insulated 10k B3950 thermistor to GND. Sensor mechanical coupling and accuracy need tests. Each tip-identity input has 10k to its own 3V3 and a separate cartridge resistor to GND: 10k T01 or 16k T02. A removable resistor code does not prove tip authenticity, sterility or calibration.

## Battery, fuse and charger
The bench build begins on an instrumented current-limited supply. A portable build requires a qualified protected 2S pack, matching approved charger and supplier current/temperature limits. F1=5A is only an initial proposal; validate interrupt rating, time-current curve and wiring protection. No charging circuit is fabricated from this repo. Use the pack supplier's charge arrangement and prohibit treatment/heat during charging.

## Sensor and current limits
Two separate MAX31865 interfaces and Pt1000 elements are now included in the BOM and net records. Each element has two leads at end A and two at end B; force and sense leads terminate at the corresponding four interface terminals. Do not use colour alone to identify these leads. Leave each module 3Vo output unused and keep its supplied four-wire jumper configuration. [Manufacturer terminal/jumper guide](https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/pinouts). Sensor-to-working-face error, lag, retention and insulation remain unmeasured. No current-sense hardware is implemented in P3: power limiting uses nominal heater resistance and measured pack voltage, and cannot detect a partial heater short by itself. Fuse, pack protection and relay/temperature controls need a dedicated fault analysis. Do not claim closed-loop wattage measurement.
