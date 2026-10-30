// Nominal brass CONTACT-END shape studies, mm. No heater, sensor or lock release.
// tip_id=0 shows family; 1..5 exports one solid. T03..T05 firmware unsupported.
$fn=96;tip_id=0;
module rounded_plate(l=6,w=2,h=2,r=.2){hull(){for(x=[-l/2+r,l/2-r])for(y=[-w/2+r,w/2-r])translate([x,y,0])cylinder(r=r,h=h);}}
module tip(n){union(){
 cylinder(d=5,h=14.05);
 if(n==1||n==2){
  d=n==1?2:4;
  translate([0,0,14])cylinder(d1=5,d2=d,h=5.05);
  translate([0,0,19])cylinder(d=d,h=2.05);
  translate([0,0,21])sphere(d=d);
 }
 if(n==3){translate([0,0,14])cylinder(d=5,h=5.05);translate([0,0,19])cylinder(d=6,h=2);}
 if(n==4){hull(){translate([0,0,14])cylinder(d=5,h=.1);translate([0,0,19])rounded_plate(6,2,.1);}
  translate([0,0,19])rounded_plate(6,2,2);}
 if(n==5){translate([0,0,14])cylinder(d1=5,d2=3,h=2.05);translate([0,0,16])rotate([0,30,0])union(){cylinder(d=3,h=7.05);translate([0,0,7])sphere(d=3);}}
}}
color([.72,.53,.18])if(tip_id==0){for(n=[1:5])translate([(n-1)*18,0,0])tip(n);}else tip(tip_id);
