/* Original analytical models: ideal unloaded RC and fixed-width PCM buffering. */
(function(root){'use strict';
function rc(resistance,capacitance,frequency){
 const x=2*Math.PI*frequency*resistance*capacitance,gain=1/Math.hypot(1,x);
 return {cutoff:1/(2*Math.PI*resistance*capacitance),gain,db:20*Math.log10(gain),phase:-Math.atan(x)*180/Math.PI,tau:resistance*capacitance};
}
function buffer(sampleRate,channels,storageBits,frames,seconds){
 const bytesPerFrame=channels*storageBits/8,bytesPerSecond=sampleRate*bytesPerFrame;
 return {bytesPerFrame,bytesPerSecond,blockBytes:frames*bytesPerFrame,blockMs:frames/sampleRate*1000,doubleBytes:2*frames*bytesPerFrame,totalBytes:seconds*bytesPerSecond};
}
const api={rc,buffer};if(typeof module!=='undefined')module.exports=api;else root.SNAnalog=api;
})(typeof window!=='undefined'?window:globalThis);
