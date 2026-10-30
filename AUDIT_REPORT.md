# Current project audit - version 0.5.0

This report consolidates the source corrections and native-CAD results for the current five-preset project. [BUILD_COMPLETENESS](BUILD_COMPLETENESS.md) gives the current release-gate status.

31 October 2026. Scope: source review, automated host checks, cross-file electrical records, package/build tooling, visual-document provenance and manufacturing-readiness assessment.

## Findings corrected

| ID | Finding | Correction / evidence |
|---|---|---|
| A01 | Supervisor relay permit did not explicitly require the main armed permit | Added peer permit condition; regression test withdraws relay on main permit loss |
| A02 | Malformed provisioning could pass weak checks or fail with wrong JSON types | Added type/range/schema validation, bounded reads, nonempty calibration identifier and safe defaults |
| A03 | Boolean values were accepted as numeric measurements | finite() now accepts actual int/float types only; regression tests |
| A04 | Short SPI reads could produce indexing errors | Driver reports controlled fault and releases chip select; regression tests |
| A05 | Main output was not cut at the earliest local dock/tip/selection check | Early software shutdown before peripheral work; hardware interlocks remain necessary |
| A06 | BOM lacked the two RTD sensor elements and their four terminal connections | Added both sensor elements, interface terminals, full net schedule and cross-file tests |
| A07 | Controller JSON recorded only supply pins while GPIO lived elsewhere | Expanded each controller component to physical-header/GPIO nets and checked against pin map |
| A08 | OLED revision/reset requirement was ambiguous | Restricted assembly to the documented auto-reset STEMMA QT revision; older variants need redesign |
| A09 | Re-deployment silently replaced local commissioning records | Preserve existing record by default; explicit reset option; tool regression test |
| A10 | Repackaging an extracted source could duplicate SOURCE_MANIFEST.json | Excluded prior manifest and check archive uniqueness; test actual package script |
| A11 | Packaging did not exclude common local provisioning/secrets | Exclude provision.json, .env/secrets names and private-key extensions; fixture test |
| A12 | Previous risk register referenced obsolete Vxx verification IDs | Added current traceability and release-gate records instead of treating old identifiers as completed tests |
| A13 | Direct execution of the expanded repository checker lacked the repository import root | Added an explicit script import root and verified the documented entrypoint |

## Checks actually performed

See [host-checks.txt](docs/records/host-checks.txt) and [verification.json](docs/records/verification.json) for the final executed commands and outcomes. Host tests include the actual application with mocked machine/SPI/UART/ADC/display interfaces. The source checker covers syntax, local links, pin ownership, circuit invariants, BOM/net schedules, SVG XML and basic EDA structure. Packaging is extracted and checked against every recorded SHA-256 digest.

The drawing/EDA generators are rerun from the updated records. The AI images are checked as illustrations only and cannot verify physical wires. Standardized component names do not establish that every rendered package is exact.

## Open findings / limitations

- **Manufacturing release incomplete:** the low-current carrier is routed and passes native ERC/DRC/parity. Independent circuit/CAM review, purchased-footprint fit and fabricated-board tests remain open. The complete compact integrated PCB is not delivered.
- **Medical release blocked:** no hardware, clinical, sterilization, biological, safety/EMC or production tests occurred.
- **Cartridge incomplete:** exact winding, materials, insulation, joining, tolerances and qualified sensor installation require supplier work.
- **Battery incomplete:** no qualified pack/charger model or final interlocked charge assembly selected.
- **Common-cause risk:** both controllers share software/runtime and some physical switches/ground. Two boards do not establish independence sufficient for a medical safety claim.
- **Stalled supervisor:** output may persist until watchdog reset; real detection/relay release and stored-energy consequences must be measured.
- **Peer restart:** sequence replay protection may require rebooting both controllers together after a single-board restart. Session-resynchronization protocol is not implemented.
- **Power estimation:** no actual current measurement; a resistance-based duty bound cannot diagnose every heater fault.
- **Input/reference limits:** ADC leakage, reference error, unpowered backfeed and switch/wire failures still need hardware analysis.
- **Mechanical:** carrier-aligned mounts and native closed meshes are included. Physical fit, mounting strength, hot-part locking and seals are unvalidated. Slim handheld packaging is not implemented.
- **Licensing:** owner must decide reuse/manufacturing terms; public hosting alone grants no license.

The audit improves the prototype source package. It does not mark the unfinished device as perfect, production-ready or safe for patient use.


## Native CAD evidence

Both generic passive-symbol ERC checks, carrier DRC and schematic parity report zero findings. Routed source, local libraries, candidate Gerbers/drills, PDF/STEP and native images are supplied. Eight enclosure/tip meshes pass native compilation and closed-edge checks. Source hashes bind these records to the delivered files. See [PCB details](docs/pcb.md) and [mechanical details](docs/mechanical.md). External circuit verification, independent CAM/physical-footprint review, full cartridge/battery/handheld integration and all physical/medical evidence remain open.
