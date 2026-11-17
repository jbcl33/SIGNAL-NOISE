'use strict';
(()=>{
 const $=id=>document.getElementById(id),r=$('rc-r'),c=$('rc-c'),f=$('rc-f');
 function rc(){const R=+r.value,C=+c.value*1e-9,F=+f.value,v=SNAnalog.rc(R,C,F);$('rc-frequency').textContent=F+' Hz';$('rc-cutoff').textContent=v.cutoff.toFixed(1)+' Hz';$('rc-gain').textContent=v.db.toFixed(2)+' dB';$('rc-phase').textContent=v.phase.toFixed(1)+'°';$('rc-summary').textContent=`在 ${F} Hz，输出幅度是输入的 ${(v.gain*100).toFixed(1)}%；时间常数 ${(v.tau*1e6).toFixed(1)} μs。`;
 const canvas=$('rc-plot'),ctx=canvas.getContext('2d'),w=canvas.clientWidth,h=canvas.clientHeight,dpr=Math.min(devicePixelRatio||1,2),left=46,right=w-20,top=20,bottom=h-32;canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);ctx.fillStyle='#ddd';ctx.font='11px monospace';ctx.strokeStyle='#444';ctx.lineWidth=1;
 const X=hz=>left+(Math.log10(hz)-1)/4*(right-left),Y=db=>top-db/60*(bottom-top);
 for(let db=0;db>=-60;db-=20){ctx.beginPath();ctx.moveTo(left,Y(db));ctx.lineTo(right,Y(db));ctx.stroke();ctx.fillText(db+' dB',2,Y(db)+5)}for(const hz of [10,100,1000,10000,100000]){ctx.beginPath();ctx.moveTo(X(hz),top);ctx.lineTo(X(hz),bottom);ctx.stroke();ctx.fillText(hz>=1000?hz/1000+'k':hz,X(hz)-10,h-14)}
 ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.beginPath();for(let n=0;n<=600;n++){const hz=10**(1+4*n/600),y=Y(Math.max(-60,SNAnalog.rc(R,C,hz).db));n?ctx.lineTo(X(hz),y):ctx.moveTo(X(hz),y)}ctx.stroke();ctx.fillStyle='#c6ff00';ctx.beginPath();ctx.arc(X(F),Y(Math.max(-60,v.db)),5,0,Math.PI*2);ctx.fill();}
 for(const x of [r,c,f])x.addEventListener('input',rc);
 $('rc-preset').addEventListener('click',()=>{r.value='10000';c.value='10';f.value='1600';rc()});
 const rate=$('buffer-rate'),channels=$('buffer-channels'),depth=$('buffer-bits'),frames=$('buffer-frames');
 function memory(){const v=SNAnalog.buffer(+rate.value,+channels.value,+depth.value,+frames.value,60);$('buffer-rate-value').textContent=(v.bytesPerSecond/1000).toFixed(1)+' kB/s';$('buffer-time').textContent=v.blockMs.toFixed(3)+' ms';$('buffer-ram').textContent=v.doubleBytes+' B';$('buffer-minute').textContent=(v.totalBytes/1e6).toFixed(2)+' MB';$('buffer-summary').textContent=`每块 ${v.blockBytes} 字节；双缓冲轮换时，另一块约在 ${v.blockMs.toFixed(3)} ms 后填满。此值只估算连续流的处理窗口，未计调度、传输与存储抖动。`;}
 for(const x of [rate,channels,depth,frames])x.addEventListener('input',memory);new ResizeObserver(rc).observe($('rc-plot'));rc();memory();
})();
