"""Deterministic bench thermal simulation; not measured tissue/device performance."""
import csv
from pathlib import Path
from firmware.core import Controller,Inputs,Sample
def simulate(target):
    c=Controller();c.select(target);t=25.0;rows=[]
    for k in range(2400):
        now=k*100
        cool=k>=1800
        i=Inputs(now,Sample(t,now),t,0,0,target,True,7.2,25,
                 heat=k>=3 and not cool,cool=cool,arm=k==1,provisioning_ok=True)
        duty=c.step(i)
        # Hypothetical lumped cartridge C=3 J/K, UA=0.025 W/K; no tissue.
        t+=(duty*7.2**2/2.2-.025*(t-25))*.1/3
        rows.append((now/1000,target,round(t,4),round(duty,5),c.state))
    return rows
def main():
    out=Path("build/simulation");out.mkdir(parents=True,exist_ok=True)
    for t in (50,100,150,200,250):
        with (out/(str(t)+"C.csv")).open("w",newline="") as f:
            w=csv.writer(f);w.writerow(["seconds","setpoint_C","model_C","duty","state"]);w.writerows(simulate(t))
    print("Five hypothetical simulations written to",out)
if __name__=="__main__":main()
