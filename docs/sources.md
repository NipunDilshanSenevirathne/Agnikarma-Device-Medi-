# Primary sources and interpretation limits

Research date: 30 October 2026. Targeted primary-source review, not a complete systematic review or licensed-standards audit. Module interfaces and part ratings must be verified against the actual purchased revision.

- [Raspberry Pi Pico datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf): supply, GPIO and physical header. Does not qualify this assembly.
- [MicroPython 1.26 RP2](https://docs.micropython.org/en/v1.26.0/rp2/quickref.html): target APIs. Host Python tests do not establish target runtime behaviour.
- [Adafruit 3648](https://www.adafruit.com/product/3648) and [reference-resistor FAQ](https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/f-a-q): Pt1000 module with 4.3 kohm reference.
- [MAX31865 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX31865.pdf): sensor-interface protocol and reference circuit.
- [TC4420/4429 datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/21419D.pdf): non-inverting driver, pinout and supply. Select TC4420, not TC4429.
- [IRLZ44N datasheet](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlz44n-datasheet-en.pdf): MOSFET ratings and gate requirements; thermal verification needed.
- [PN2222ABU datasheet](https://www.onsemi.com/pdf/datasheet/pn2222a-d.pdf): exact transistor package mapping; related names may differ.
- [Omron G5LE datasheet](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5le.pdf): coil/contact/package data, not medical safety certification.
- [Pololu 2858](https://www.pololu.com/product/2858): 5 V buck module.
- [Adafruit 326 OLED](https://www.adafruit.com/product/326): display module; actual interface/address configuration required.
- [KiCad PCB editor](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html): EDA workflow and output checks, not proof generated files pass them.
- [FDA QMSR](https://www.fda.gov/medical-devices/postmarket-requirements-devices/quality-management-system-regulation-qmsr): quality-system requirements, no product approval implied.
- [FDA reprocessing guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/reprocessing-medical-devices-health-care-settings-validation-methods-and-labeling): validated process required.
- [ISO 14971](https://www.iso.org/standard/72704.html), [IEC 60601-1](https://webstore.iec.ch/en/publication/2606), [ISO 10993-1](https://www.iso.org/standard/10993-1): relevant workstreams; full standards/recognized editions need professional assessment.

The current project uses the five-preset P3 architecture. The obsolete historical report is excluded from this folder to avoid mixing circuit and temperature revisions. No clinical evidence establishes safe use of this prototype or a five-temperature treatment protocol.


## 0.5.0 native CAD and calculation sources

- [Official KiCad Windows release and signature information](https://www.kicad.org/download/windows/): KiCad 10.0.8 installer signature verified as KICAD SERVICES CORPORATION, certificate serial 39DF6B588D969CA15D8D2756. The tool installer is not included in this project.
- [KiCad 10 CLI](https://docs.kicad.org/10.0/en/cli/cli.html): native ERC/DRC/parity, documentation, Gerber/drill/STEP/image exports.
- [OpenSCAD official downloads](https://openscad.org/downloads.html): 2021.01 Windows portable archive SHA-256 matched its official checksum before use.
- [Phoenix Contact 1715721](https://www.phoenixcontact.com/en-dk/products/pcb-terminal-block-mkds-15-2-508-1715721): 5.08 mm terminal pitch, 0.9 mm square pins and 1.3 mm recommended holes. Physical purchased part/footprint review remains necessary.
- [Kanthal Nikrothal 80](https://www.kanthal.com/products/datasheets/material-datasheets/wire/resistance-heating-wire-and-resistance-wire/nikrothal-80/): 20 C resistivity used only for the resistance-wire worksheet. No medical heater construction qualification is inferred.

Accessed 31 October 2026. Numerical design calculations and native tool reports are project-generated evidence within their stated scopes.
