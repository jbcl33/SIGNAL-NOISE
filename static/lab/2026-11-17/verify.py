"""Independent Python calculation. No packages required. Optional results.json argument."""
import math, json, sys
from pathlib import Path
cases = [(3000,8000,12),(3000,4000,12),(1000,48000,3),(1000,48000,8),(1000,48000,12)]
observed = json.loads(Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).with_name('results.json')).read_text())['cases']
for (f,fs,b),row in zip(cases,observed):
    step=2/(2**b-1); errors=[]
    for n in range(fs*2):
        x=.8*math.sin(2*math.pi*f*n/fs)
        q=math.floor((x+1)/step+.5)*step-1
        errors.append((q-x)**2)
    rms=math.sqrt(sum(errors)/len(errors))
    assert abs(rms-row['rms'])<1e-10,(rms,row['rms'])
    assert row['sampleCount']==fs*2
    print(f'{f} Hz / {fs} sps / {b} bit: RMS={rms:.10f}; matched JavaScript')
print('PASS independent quantization calculations')
