# Verification plan and evidence levels

## Implemented host checks
Run the README commands. Unit tests exercise the actual portable firmware core and driver interface with instrumented mocks, not a separate explanatory toy model. The simulation uses this same Controller but assumes a single 3 J/K thermal node, conductance 0.025 W/K, 25 C ambient and no tissue. It cannot establish patient effects or actual performance.

## Native engineering checks performed

KiCad 10.0.8 checked both passive-terminal schematics and the carrier PCB, including schematic parity. All finding counts and unconnected counts were zero. OpenSCAD 2021.01 compiled eight part meshes; bounds, closed-edge incidence and mounting arithmetic passed. Individual reports and source/output hashes are in docs/records. Host CI verifies that the stored evidence matches delivered files; it does not rerun native tools. Independent circuit/CAM review and physical tests remain necessary.

## Physical tests not yet executed
| Test | Measurements / required evidence |
|---|---|
| Logic startup | Outputs low across reset, brownout, failed peripheral initialization and flash/deploy |
| Communication | CRC errors, replay, disconnected UART/heartbeat, hung main/supervisor, watchdog restart |
| COOL/interlocks | Physical coil interruption, contact bounce, stuck/open wires, dock/lock sequencing |
| Sensor faults | Open, short, detachment, plausible stuck values, lead/mating contact changes |
| Thermal regulation | Independent working-face reference at every preset/tip, load transitions and worst battery |
| Relay/MOSFET | Welded contact, shorted MOSFET, release time, flyback effects, switching transients |
| Pack/charge | Supplier qualification, protection, wiring/fuse coordination, charging interlock, heat soak |
| Mechanical | Retention, twisting, drop, transport, guard, enclosure fit and local surface temperatures |
| Reprocessing | Validated cleaning, sterilization and material/measurement durability |
| Clinical | Authorized indication-specific study, safety endpoints and benefit/risk evaluation |

Write approved protocols and quantitative criteria before running physical tests. Use qualified people, calibrated equipment, a guarded nonclinical load and independent isolation. No universal safe contact time or clinical temperature margin is asserted. Host check success cannot close these rows.
