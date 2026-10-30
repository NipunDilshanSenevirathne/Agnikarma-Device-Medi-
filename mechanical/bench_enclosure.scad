// P3R1 LOW-CURRENT CONTROLLER housing, mm. Prototype fit-check, no clinical release.
// Only the 160 x 100 carrier is mounted here. Power stage, RTD modules, pack,
// hot load and cartridge remain on the guarded external bench fixture.
$fn=64;
part="assembly"; // base, lid, clamp, assembly
outer=[180,120,65]; wall=3; lid_t=3; floor_t=3;
pcb_origin=[10,10]; pcb_size=[160,100,1.6]; pcb_z=9;
pcb_holes=[[15,15],[165,15],[15,105],[165,105]];
lid_holes=[[7,7],[173,7],[7,113],[173,113]];
presets=[[85,30],[110,30],[135,30],[97.5,55],[122.5,55]];
controls=[[50,90],[90,90],[135,90]]; // ARM, HEAT, COOL
module post(p,h,od=8,id=2.5){translate([p[0],p[1],floor_t-.01])difference(){cylinder(d=od,h=h+.01);translate([0,0,-.1])cylinder(d=id,h=h+.3);}}
module base(){difference(){
 union(){difference(){cube(outer);translate([wall,wall,floor_t])cube([outer[0]-2*wall,outer[1]-2*wall,outer[2]]);}
  for(p=pcb_holes)post(p,pcb_z-floor_t);
  for(p=lid_holes)post(p,outer[2]-floor_t,9,2.5);
 }
 translate([78,-1,43])cube([24,wall+2,outer[2]-43+1]);
 for(x=[72,108])translate([x,wall+1,53])rotate([90,0,0])cylinder(d=2.5,h=wall+2);
}}
module lid(){difference(){
 cube([outer[0],outer[1],lid_t]);
 for(p=lid_holes)translate([p[0],p[1],-1])cylinder(d=3.4,h=lid_t+2);
 translate([22,25,-1])cube([30,18,lid_t+2]);
 for(p=presets)translate([p[0],p[1],-1])cylinder(d=8.2,h=lid_t+2);
 for(p=controls)translate([p[0],p[1],-1])cylinder(d=12.2,h=lid_t+2);
}
// Adjustable OLED adapter rails; no guessed OEM mounting-hole spacing.
for(x=[16,58])translate([x,18,-7])difference(){cube([6,34,7]);translate([3,5,-1])cylinder(d=2.5,h=9);translate([3,29,-1])cylinder(d=2.5,h=9);}
}
module clamp(){difference(){cube([44,8,26]);
 translate([10,-1,0])cube([24,10,12]);
 for(x=[4,40])translate([x,-1,10])rotate([-90,0,0])cylinder(d=3.4,h=10);
}}
module board(){color([.04,.35,.19])translate([pcb_origin[0],pcb_origin[1],pcb_z])cube(pcb_size);
for(x=[45,115])color([.02,.3,.15])translate([x-1.5,28.5,pcb_z+10])cube([20.78,51,1]);}
if(part=="base")base();
else if(part=="lid")translate([0,0,7])lid();
else if(part=="clamp")clamp();
else {color([.15,.2,.23,.5])base();board();translate([0,0,outer[2]+20])color([.8,.82,.83])lid();translate([68,-8,43])color([.15,.2,.23])clamp();}
