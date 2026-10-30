"""Reproducible electrical design calculations. No thermal or medical validation."""
from pathlib import Path
import csv,json,math,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from firmware import config

def main():
    out=ROOT/'hardware/calculations';out.mkdir(exist_ok=True)
    records=[]
    for v in (6.2,7.4,8.4,8.5):
        for factor in (.9,1,1.1):
            r=config.HEATER_OHMS*factor
            duty=min(config.MAX_DUTY,config.MAX_POWER_W*config.HEATER_OHMS/(v*v))
            records.append({'Voltage_V':v,'Resistance_ohm':round(r,6),'On_current_A':round(v/r,4),
             'Full_on_power_W':round(v*v/r,4),'Command_duty_limit':round(duty,6),
             'Actual_average_W_at_command_limit':round(duty*v*v/r,4)})
    with (out/'power-envelope.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    wire=[]
    # Kanthal Nikrothal 80 data: rho20 = 1.09 ohm mm2/m. Arithmetic only.
    for diameter in (.15,.20,.25,.30,.35,.40):
        area=math.pi*diameter*diameter/4
        length_m=config.HEATER_OHMS*area/1.09
        surface_cm2=math.pi*diameter*length_m*1000/100
        wire.append({'Diameter_mm':diameter,'Area_mm2':round(area,6),'Nominal_cold_length_mm':round(length_m*1000,3),
          'Wire_surface_cm2':round(surface_cm2,5),'Full_on_surface_load_W_per_cm2_at_8p4V':round(8.4**2/config.HEATER_OHMS/surface_cm2,3)})
    with (out/'nichrome-arithmetic-NOT-a-winding-release.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(wire[0]));w.writeheader();w.writerows(wire)
    record={'nominal_heater_ohm':config.HEATER_OHMS,'pwm_hz':config.PWM_HZ,'max_duty':config.MAX_DUTY,
     'power_command_bound_W':config.MAX_POWER_W,'gate_peak_ideal_A':5/10,
     'relay_base_resistor_ohm':330,'base_current_mA_at_Vbe_0p8':(3.3-.8)/330*1000,
     'adc_ideal_at_pack8p5V':8.5*39/139,'adc_at8p5V_with1pct_worst_divider':8.5*(39*1.01)/(100*.99+39*1.01),
     'limits':['Gate current ignores driver and gate internal resistance; not measured.',
       'Power bound uses nominal resistance; a lower actual heater resistance increases real current/power.',
       'Wire length excludes cold leads, joining and resistance tolerances; surface-load arithmetic does not establish permissible wire temperature.',
       'No mandrel, winding pitch, cement, insulation, sensor or cartridge process is released by this calculation.',
       'No charger, battery qualification, runtime promise or clinical exposure limit is established.']}
    (out/'design-margins.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Calculated power envelope, ADC/base-drive assumptions and resistance-wire arithmetic.')
if __name__=='__main__':main()
