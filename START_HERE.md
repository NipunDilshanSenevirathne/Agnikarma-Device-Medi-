# Agni Karma - start here

This is the current five-preset project folder. Read START_HERE, README and BUILD_GUIDE in that order. Superseded reports, old PCB pictures and duplicate release archives are excluded. Native CAD files, engineering diagrams, firmware, parts lists and verification records are retained.
1. [README](README.md): illustrated repository overview and commands.
2. [BUILD_GUIDE](BUILD_GUIDE.md): integrated prototype assembly and test sequence.
3. [AUDIT_REPORT](AUDIT_REPORT.md): actual findings, corrections and limitations.
4. [PCB and fabrication guide](docs/pcb.md): native CAD, routed carrier, Gerbers/drills and pin order.
5. [Engineering handover](docs/engineering-handover.md): concrete deliverables and required supplier/physical work.
6. [BUILD_COMPLETENESS](BUILD_COMPLETENESS.md): outstanding work for a finished medical device.

Run `python tools/verify.py` from this folder. It uses the Python standard library and saves the executed results. The hardware is not built or tested; engineering and clinical release gates remain open. Product appearance images are AI illustrations; carrier images are native KiCad renders. Electrical records govern wiring.
