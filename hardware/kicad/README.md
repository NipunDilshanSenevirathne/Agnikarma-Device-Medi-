# Native KiCad projects, P3R1

Open `agni-controller-carrier.kicad_pro` for the routed passive carrier and matched schematic. Open `agni-module-system.kicad_pro` for the complete external module/terminal wiring schematic. The project-local AGNI libraries are included; preserve the directory structure and library-table files.

KiCad 10.0.8 ran ERC on both schematics and carrier DRC with schematic parity: all reported finding counts are zero. Exact reports, commands, limitations and input hashes are in [native-cad-checks.json](../../docs/records/native-cad-checks.json).

The carrier is 160 x 100 mm and carries only regulated logic supply and GPIO breakout wiring. External branch resistors and heater/sensor/power circuits are not silently integrated onto this PCB. Generic passive terminal symbols do not provide full component-direction ERC.

Use the [PCB guide](../../docs/pcb.md), [connector schedule](../carrier_connectors.csv), [carrier BOM](../carrier_BOM.csv) and [fabrication review instructions](../fabrication/P3R1/README.md). CAM files are engineering candidates pending independent review and physical fit/continuity tests, not a medical manufacturing release.
