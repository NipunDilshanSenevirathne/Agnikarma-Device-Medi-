# Build completeness and release gates

31 October 2026. Version 0.5.0. **This is still not a finished medical product.** Native CAD work is now implemented and checked, rather than left as unrouted starters.

| Subsystem | Included and verified here | Still required for full product release |
|---|---|---|
| Main/supervisor software | Real source/drivers, provisioning, host tests and simulation | Actual RP2040/HIL execution, timing, requirements and fault validation |
| Electrical assembly | Parts values, module names, physical terminals/nets, native connected PDF/schematic | Independent component/circuit review, purchased revisions, electrical/fault/thermal/insulation measurements |
| Carrier PCB | Routed 2-layer carrier, matched schematic/local libraries; native ERC/DRC/parity all zero; candidate Gerbers/drills/STEP/images | Independent CAM/footprint review, fabrication, assembly/continuity test; compact integrated power/logic PCB remains future work |
| Power subsystem | Defined relay/MOSFET driver circuit, guarded-load plan, current/power worksheets | Fuse/wire/connector coordination, current/thermal/fault testing and additional protections as required |
| Battery and charger | 2S architecture and constraints | Qualified exact protected pack/matched charger, charging lockout and system tests |
| Brass ends | Corrected nominal geometry and five native closed shape meshes | Released tolerances/material/finish/process and biological evaluation; T03-T05 firmware support |
| Heater cartridge | Supplier specification and resistance-wire calculation worksheet | Actual construction/winding/ceramic/joints/dual-sensor integration/lock/seals, supplier and finished-device testing |
| Enclosure | Carrier-aligned base/lid/clamp source and native closed meshes; coordinate checks | Exact switches/display adapter, component guards/strain relief, physical fit/material/strength/thermal tests; complete handheld enclosure |
| Cooling | Physical coil interruption and inhibited passive-cooling logic | Measured cooldown/sensor lag, safe handling and power-loss validation; qualified active cooling if required |
| Medical readiness | Risk/test/reprocessing/clinical planning and traceability | Electrical/EMC, biological, reprocessing, usability, clinical/regulatory, quality and production evidence |

The native records are [CAD checks](docs/records/native-cad-checks.json) and [mesh checks](docs/records/mechanical-checks.json). The [handover](docs/engineering-handover.md) specifies what a contractor can build and what needs engineering/supplier/laboratory work. A clean DRC and a source ZIP cannot substitute for that work.
