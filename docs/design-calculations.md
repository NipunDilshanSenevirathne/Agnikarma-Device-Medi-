# Reproducible electrical calculations

Run `python tools/engineering_calculations.py`. Outputs in [hardware/calculations](../hardware/calculations/power-envelope.csv) are derived from the actual firmware configuration. These calculations test assumptions, not measured hardware.

For the nominal 2.2 ohm heater, full-on current is V/R and full-on power is V squared/R. At 8.4 V, these are **3.82 A and 32.07 W**. A 50% command cap gives about 16.04 W average for the nominal load. The switch, wiring, contacts and fuse still experience full on-current during PWM. At -10% heater resistance, current and power rise by about 11.1%; the firmware uses nominal resistance and cannot measure or eliminate this error. Lower-resistance faults need physical protection/analysis.

The 100k/39k pack divider ideally produces about 2.385 V at an 8.5 V pack; 1% resistor worst-case mismatch gives about 2.419 V. Actual Pico ADC reference, divider tolerance, filtering, leakage and unpowered backfeed require measurement. ADC clamps must not be treated as a complete protection system.

A 330 ohm relay-transistor base resistor gives an approximate 7.58 mA base current if GPIO is 3.3 V and Vbe is 0.8 V. Verify GPIO drive, saturation, coil current and thermal limits on real parts. The gate driver's 5 V/10 ohm ideal initial current is 0.5 A before internal resistances and gate dynamics; it is not a steady current or measured switching result.

## Coil name and resistance-wire arithmetic

The proposed heater material family is **NiCr 80/20 resistance wire**, for example Kanthal **Nikrothal 80**. Its manufacturer gives 20 C resistivity 1.09 ohm mm2/m. The [wire worksheet](../hardware/calculations/nichrome-arithmetic-NOT-a-winding-release.csv) calculates length using L=R*pi*d squared/(4*rho), plus full-on wire-surface loading for several diameters. This answers the resistance calculation explicitly while exposing how concentrated the heat could be. The manufacturer's [Nikrothal 80 data](https://www.kanthal.com/products/datasheets/material-datasheets/wire/resistance-heating-wire-and-resistance-wire/nikrothal-80/) describe the alloy; they do not qualify a medical cartridge.

These are **not approved winding dimensions**. Turn count/pitch, ceramic mandrel, wire temperature, hotspots, lead joints, potting, expansion, insulation, dual-sensor attachment and leakage into brass are unsolved until a supplier construction is reviewed and tested. Alloy maximum-use temperature is not a rating for an assembled heater, its insulation, its brass surface or tissue exposure. Do not convert the worksheet into a clinical assembly recipe.

The initial H_TEST is a guarded chassis resistor on its specified heat sink. It has no treatment contact end. The [cartridge procurement specification](cartridge-specification.md) lists the evidence required to replace it. Battery capacity, runtime, heat-up/cooldown times and achievable 250 C under load are not established by electrical arithmetic.
