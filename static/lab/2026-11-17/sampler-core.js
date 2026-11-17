/* SIGNAL / NOISE original educational sampler. */
(function(root){'use strict';
function alias(f,fs){return Math.abs(((f+fs/2)%fs+fs)%fs-fs/2)}
function generate(f,fs,bits,seconds=2){
 const out=new Float64Array(Math.round(fs*seconds)), step=2/(2**bits-1);let e=0;
 for(let n=0;n<out.length;n++){const x=.8*Math.sin(2*Math.PI*f*n/fs);const q=Math.round((x+1)/step)*step-1;out[n]=q;e+=(q-x)**2}
 return {samples:out,step,rms:Math.sqrt(e/out.length),alias:alias(f,fs)};
}
function wav(samples,fs){const a=new ArrayBuffer(44+samples.length*2),v=new DataView(a);
 const str=(p,s)=>{for(let i=0;i<s.length;i++)v.setUint8(p+i,s.charCodeAt(i))};
 str(0,'RIFF');v.setUint32(4,36+samples.length*2,true);str(8,'WAVE');str(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,fs,true);v.setUint32(28,fs*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);str(36,'data');v.setUint32(40,samples.length*2,true);
 samples.forEach((x,n)=>v.setInt16(44+2*n,Math.round(Math.max(-1,Math.min(1,x))*32767),true));return a;
}
const api={alias,generate,wav};if(typeof module!=='undefined')module.exports=api;else root.SNSampler=api;
})(typeof window!=='undefined'?window:globalThis);
