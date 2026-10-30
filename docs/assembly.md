# Assembly and commissioning

1. Review the schematic/net records and exact package pinouts with an electronics engineer. Resolve the test plan and limits before soldering. Record board/module serial numbers and revisions.
2. Build low-current logic wiring with no pack or heater connected. Use separate main/supervisor 3V3 rails and a controlled common return. Inspect polarity, insulation, continuity and accidental shorts.
3. Apply a current-limited bench source to the 5 V logic subsystem. Check VSYS and GPIO voltages. Upload both roles with disabled provisioning. Verify no PWM or relay output during startup, exceptions or missing communication.
4. Connect two sensor interfaces and resistance standards. Verify Pt1000 conversion, fault detection, role identity, OLED address, both UART directions and heartbeat inputs. See calibration record template.
5. Connect all buttons, dock and tip interlocks. Confirm COOL physically opens coil supply with either/both controllers absent or unpowered. Confirm only a locked tip closes the intended circuit.
6. Assemble the power stage in a guarded fixture. Inspect TC4420 duplicate pins, MOSFET pinout/tab, diode polarity and relay terminal mapping. Use suitable soldered terminals; do not depend on loose jumper contacts for heater power.
7. Use an appropriately rated 2.2 ohm dummy load mounted on its specified heat sink. Provide a guarded enclosure and independent emergency isolation. Verify power, PWM, relay operation and stop times using calibrated instruments. Do not attach tissue or a patient-contact tip at this stage.
8. Perform the physical fault tests in testing.md using controlled fixtures. Record actual stop times, sensor behaviour and temperature excursions. Investigate every unexpected reset or disagreement.
9. Only after evidence supports it, integrate a qualified custom cartridge and repeat all relevant thermal/mechanical/electrical tests in a nonclinical guarded fixture. Verify finished brass and reprocessing separately.
10. A battery build and compact enclosure require additional pack, charging, heat-soak and mechanical verification. No performance or clinical release follows automatically from a working bench demonstration.

Solder with power disconnected. Do not solder directly to loose lithium-ion cells. Module replacements require pinout, voltage and firmware review. No assembly test has been run on physical hardware for this release.
