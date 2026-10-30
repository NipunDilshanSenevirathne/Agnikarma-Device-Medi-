# Electrical definition P3R1
The current implementation uses two Pico modules, two Adafruit 3648 sensor interfaces, a driver/MOSFET power stage and an independently controlled relay. `design.json`, `BOM.csv`, `component_connections.csv` and `pinmap.csv` define the bench wiring together. A pin/terminal name on a bought module is its silk-screen name; it is not a numeric internal IC pin.

The schematic drawings are generated from these records. Bought-module internals belong to their manufacturers; this repo does not redesign every IC or battery pack. The supplied low-current carrier is routed, with a matched schematic, local libraries and clean native ERC/DRC/parity records. Candidate Gerber/drill outputs are in `fabrication/P3R1`; independent CAM/footprint review and physical tests remain necessary. First assembly is a reviewed module/harness bench fixture. Keep heater current outside the carrier and solderless breadboards.

Use [carrier_BOM.csv](carrier_BOM.csv), [carrier_connectors.csv](carrier_connectors.csv) and [the PCB assembly guide](../docs/pcb.md) together. The carrier provides Pico breakout connections; external branch resistors, RTD boards, relay, gate driver, MOSFET and interlock circuits remain required.

The custom sterilizable cartridge, battery pack selection, precise high-current connector and patient-contact material process require supplier qualification. The test load replaces the cartridge during commissioning. F1=5A is a starting selection requiring fuse/wire coordination and testing, not a final safety approval.
