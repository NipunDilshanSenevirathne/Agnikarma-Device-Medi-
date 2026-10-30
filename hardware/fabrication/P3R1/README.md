# P3R1 candidate fabrication data

Generated with native KiCad 10.0.8 after clean carrier ERC, DRC and schematic parity. **Independent CAM review and physical part/footprint checks remain open.** These files describe only the low-current carrier.

| Item | Definition |
|---|---|
| Board | 160 x 100 mm; 2 copper layers; nominal 1.6 mm FR4 |
| Proposed copper | 35 um finished nominal; confirm fabrication tolerance |
| Mask/silk | Both mask layers, top silk; ordinary through-hole assembly |
| F.Cu | `agni-controller-carrier-F_Cu.gtl` |
| B.Cu | `agni-controller-carrier-B_Cu.gbl` |
| Top silk | `agni-controller-carrier-f_silkscreen.gto` |
| F.Mask / B.Mask | `.gts` / `.gbs` |
| Closed board outline | `.gm1` |
| Plated drills | `-PTH.drl`: 160 x 1.0 mm holes, 2 x 1.3 mm holes |
| Non-plated drills | `-NPTH.drl`: 4 x 3.2 mm holes |
| Drill maps | Corresponding `-drl_map.svg` files |
| Job and drill records | `.gbrjob` and `drill-report.txt` |

Gerber coordinates and Excellon files were exported from the same board using absolute/default origin. Review their overlay in a CAM viewer, rather than manually changing one file's origin or mirroring a layer. Do not scale artwork for ordering. The top and bottom SVGs in docs are viewing aids.

Before order, the engineer/fabricator must review scale, closed outline, positive/negative mask polarity, copper layers, drill origin/plating, pad and hole sizes, annular rings, slot absence, silkscreen clearance and the actual header/terminal fit. Supplier stack/finish/tolerances must be agreed. No assembled board or continuity measurement exists yet.

The global source ZIP contains this directory. If the fabricator needs a separate ZIP, include the six Gerber layers, two drill files and job file together after approval; keep these instructions with the review record. A public GitHub repository is not an instruction to order or use the PCB clinically.
