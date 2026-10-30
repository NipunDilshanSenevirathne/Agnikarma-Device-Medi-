# Engineering handover and next physical build

Version 0.5.0 is a real source/CAD prototype package. It is **not a complete patient-use product manufacturing package**. A competent engineer can inspect the circuits, make the carrier after independent review, assemble the specified guarded module system and deploy the source. They cannot obtain a qualified battery/heater/cartridge or medical approval merely by building the included PCB.

## What is concrete now

The repository includes the actual control and supervisor applications, drivers and provisioning; full component/terminal/net data; conventional component identifiers and values; connected native schematics; routed matched carrier; local libraries; native ERC/DRC/parity records; six Gerber layers and two drill sets; top/bottom board images; carrier BOM and pin schedule; mechanical source and eight compiled meshes; board STEP; electrical worksheets; and build, calibration, fault-test and research records. Five presets remain 50/100/150/200/250 C. COOL removes heater input and requests inhibited passive cooling; it does not instantly cool brass.

## Contractor sequence

1. Read README, BUILD_GUIDE, BUILD_COMPLETENESS and this document. Review native files and exact purchased module revisions against the electrical data. Record the independent reviewer and discrepancies.
2. Review carrier Gerbers/drills in CAM and perform a 1:1 physical footprint fit check before ordering. Assemble and continuity-test the passive board before installing powered modules.
3. Construct a guarded low-voltage bench fixture with the full external circuit, matching instruments, independent cutoff and rated load/heatsink. The carrier alone cannot drive a heater safely. Start with the pack and heater disconnected.
4. Execute target firmware and hardware-in-the-loop tests. Record raw measured values, instruments, calibration, configuration and exact source/runtime hashes. Run startup/brownout, one-board reset, communications loss, sensor faults, COOL/interlocks, welded/shorted switch analysis and watchdog timing tests.
5. Commission the custom cartridge work below. Qualify the pack/charger and connector separately. Rework the electronics/mechanics around measured thermal, power, current, insulation and fault-energy requirements.
6. Confirm first market, intended clinical use and trained user group with the owner and regulatory professional. Complete the necessary quality, usability, biological, reprocessing, electrical/EMC, preclinical/clinical and manufacturing work for that specific device before clinical release.

## Cartridge supplier request

Use [cartridge-specification.md](cartridge-specification.md), the nominal shape CAD and [calculation worksheets](design-calculations.md). Request a controlled assembly drawing, exact BOM and processes for a **low-voltage insulated heater**, two independent four-wire Pt1000 channels, retained brass contact end and positive mechanical lock. The nominal circuit assumption is 2.2 ohm; no tolerance or voltage/current rating is accepted merely because it is proposed in this repo.

Require certificates/limits for the selected brass alloy and every exposed/joining/insulating material; actual resistance and insulation measurements at cold and hot conditions; face-to-sensor mapping and response at every preset; separate element retention and lead routes; oxidation/corrosion/reprocessing evidence; expansion and cycling; hot-part retention and safe insertion/removal sequence; lock/identity contacts and traceability. Ask for their proposed winding/ceramic/cold-lead/joint/seal design and inspection methods. No quote or supplier approval has been obtained here.

The five contact-end STLs have no cartridge internals. A part made only from those STLs is not a complete heated tip. T03-T05 require new ID records, calibration, thermal characterization and release before firmware support.

## Battery/charger and compact product

Select a protected 2S pack with controlled cell provenance, temperature sensing and suitable documented discharge/fault performance, plus its matched charger. Determine exact protection, physical charging lockout, connector polarity/keying, cable/fuse coordination, short-circuit response, crush/drop/transport and heat-soak performance. Pack certification does not certify the whole device. No final pack/charger model is selected in this release.

The present 180 x 120 x 65 mm housing is for the carrier and controls. Sensor boards, power stage, hot fixture and pack are external. To achieve the requested portable soldering-iron-style form, develop an integrated PCB and insulated handpiece around the measured cartridge, cells, controls, guards, lock and service/reprocessing boundaries. The AI handheld image is an appearance target; the current carrier cannot be inserted into it.

## Release records

Keep evidence tied to actual revisions. [requirements_traceability.csv](requirements_traceability.csv), [risk-register.csv](risk-register.csv), [testing.md](testing.md) and the blank physical-test forms are starting records. Do not mark a planned test as passed. Native CAD and host tests close only their recorded scopes. Temperature accuracy, stop energy, safe handling, sterilization, patient outcomes and regulatory approval require physical/professional evidence.
