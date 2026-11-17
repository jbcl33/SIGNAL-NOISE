"""Verify RC analytical results by time-domain differential equation integration.
Python standard library only; numerical simulation, not a hardware measurement.
"""
import math, json
from pathlib import Path
p=Path(__file__).with_name('extension-results.json')
data=json.loads(p.read_text())
for c in data['rcCases']:
    f=c['frequency']; tau=c['resistance']*c['capacitance']
    # 4000 steps per period, and at least 1000 steps per time constant.
    dt=min(1/(f*4000),tau/1000)
    settle=math.ceil(15*tau/dt); measure=round(20/f/dt)
    v=0.0;sin_sum=cos_sum=0.0
    for n in range(settle+measure):
        t=n*dt; vin=math.sin(2*math.pi*f*t)
        if n>=settle:
            sin_sum+=v*math.sin(2*math.pi*f*t)
            cos_sum+=v*math.cos(2*math.pi*f*t)
        v+=dt/tau*(vin-v)
    gain=math.hypot(sin_sum,cos_sum)*2/measure
    phase=math.degrees(math.atan2(cos_sum,sin_sum))
    assert abs(gain/c['gain']-1)<.002,(gain,c)
    assert abs(phase-c['phase'])<.15,(phase,c)
    print(f"RC {f} Hz / C={c['capacitance']*1e9:g} nF: numerical gain={gain:.6f}, phase={phase:.3f} deg; analytical matched within tolerance")
for c in data['bufferCases']:
    assert c['totalBytes']==c['rate']*c['channels']*c['bits']//8*60
    assert c['blockBytes']==c['frames']*c['channels']*c['bits']//8
    assert c['doubleBytes']==2*c['blockBytes']
assert data['bufferCases'][0]['blockMs']==data['bufferCases'][1]['blockMs']
print('PASS RC time-domain cross-check and PCM storage accounting')
