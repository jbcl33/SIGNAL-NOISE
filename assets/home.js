(()=>{'use strict';
const board=document.querySelector('.board'),canvas=document.querySelector('#pcb'),ctx=canvas.getContext('2d',{alpha:false}),button=document.querySelector('#motion'),reduce=matchMedia('(prefers-reduced-motion: reduce)');if(!ctx){button.hidden=true;return}
const layer=document.createElement('canvas'),ink=layer.getContext('2d',{alpha:false});let width=0,height=0,dpr=1,phase=0,last=0,frame=null,paused=reduce.matches,routes=[],layerMode='all';
function poly(c,points){c.beginPath();points.forEach((p,i)=>i?c.lineTo(p.x,p.y):c.moveTo(p.x,p.y))}
function via(x,y,r=2){ink.fillStyle='#020202';ink.strokeStyle='#aaa';ink.lineWidth=.8;ink.beginPath();ink.arc(x,y,r,0,6.283185307);ink.fill();ink.stroke();ink.fillStyle='#000';ink.beginPath();ink.arc(x,y,r*.44,0,6.283185307);ink.fill()}
function route(points,index=0,live=true,wide=false,kind=wide?'power':'signal'){if(layerMode!=='all'&&layerMode!==kind)return;ink.lineJoin='round';poly(ink,points);ink.strokeStyle='#050505';ink.lineWidth=wide?8:5;ink.stroke();if(kind==='back')ink.setLineDash([4,3]);poly(ink,points);ink.strokeStyle=kind==='back'?'rgba(255,255,255,.24)':wide?'#eee':'#ccc';ink.lineWidth=wide?2.3:.95;ink.stroke();ink.setLineDash([]);if(!live)return;const segments=[];let length=0;for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i],len=Math.hypot(b.x-a.x,b.y-a.y);if(len>.01){segments.push({a,b,len,start:length});length+=len}}routes.push({segments,length,speed:24+(index%5)*8,offset:index*.207,tail:12+(index%3)*7})}
function pour(clearances){
// A broad, chamfered ground pour. Component keepouts are subtracted, not outlined.
const plane=new Path2D();plane.rect(20,20,width-40,height-40);for(const q of clearances)plane.rect(q.x-12,q.y-16,q.w+24,q.h+34);
ink.save();ink.clip(plane,'evenodd');ink.fillStyle='rgba(255,255,255,.025)';ink.fillRect(0,0,width,height);ink.strokeStyle=layerMode==='gnd'?'rgba(255,255,255,.24)':'rgba(255,255,255,.075)';ink.lineWidth=.5;ink.beginPath();for(let x=-height;x<width;x+=10){ink.moveTo(x,0);ink.lineTo(x+height,height)}ink.stroke();
// Two quiet solid copper islands establish a diagonal, feather-like negative space.
ink.fillStyle=layerMode==='gnd'?'rgba(255,255,255,.13)':'rgba(255,255,255,.035)';poly(ink,[{x:28,y:height*.30},{x:width*.37,y:height*.16},{x:width*.37,y:height*.34},{x:width*.12,y:height*.57},{x:28,y:height*.57}]);ink.closePath();ink.fill();poly(ink,[{x:width-28,y:height*.30},{x:width*.63,y:height*.48},{x:width*.63,y:height*.64},{x:width-28,y:height*.46}]);ink.closePath();ink.fill();ink.restore();
}

function rect(name,selector){const element=selector?document.querySelector(selector):document.querySelector('[data-node="'+name+'"]'),a=element.getBoundingClientRect(),b=canvas.getBoundingClientRect();return{x:a.x-b.x,y:a.y-b.y,w:a.width,h:a.height,cx:a.x-b.x+a.width/2,cy:a.y-b.y+a.height/2}}
function cap(x,y,vertical=false,label=''){ink.save();ink.translate(x,y);if(vertical)ink.rotate(1.570796327);ink.fillStyle='#939393';ink.fillRect(-7,-3,4,6);ink.fillRect(3,-3,4,6);ink.fillStyle='#050505';ink.fillRect(-3,-3,6,6);ink.strokeStyle='#666666';ink.lineWidth=.6;ink.strokeRect(-3,-3,6,6);ink.restore();if(label){ink.fillStyle='#727272';ink.font='6px monospace';ink.fillText(label,x+10,y+2)}}
function rebuild(){const box=canvas.getBoundingClientRect();width=box.width;height=box.height;dpr=Math.min(devicePixelRatio||1,width<600?1.5:2);canvas.width=layer.width=Math.round(width*dpr);canvas.height=layer.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ink.setTransform(dpr,0,0,dpr,0,0);ink.fillStyle='#050505';ink.fillRect(0,0,width,height);routes=[];
const m=rect('mcu'),display=rect('display'),xtal=rect('archive'),sw=rect('motion'),pitch=m.w/13;
const packages=[...document.querySelectorAll('.ldo-package')].map(el=>rect(null,'.ldo[data-node="'+el.closest('.ldo').dataset.node+'"] .ldo-package'));
const clearances=[m,display,xtal,sw,...[...document.querySelectorAll('.ldo')].map(el=>rect(null,'.ldo[data-node="'+el.dataset.node+'"]')),{x:35,y:14,w:width-70,h:45},{x:width*.12,y:height*.82,w:width*.76,h:height*.16}];
if(layerMode==='all'||layerMode==='gnd')pour(clearances);
// Bottom-layer return/debug traces sit underneath the front signal channels.
for(let i=0;i<4;i++){const hx=width*.91,hy=height*.23,ex=m.x+m.w+12,ey=m.y+pitch*(i+2);route([{x:hx+(i%2?5:-5),y:hy-14+Math.floor(i/2)*14},{x:width-35-i*5,y:hy-14+Math.floor(i/2)*14},{x:width-35-i*5,y:m.y-42-i*6},{x:ex+29+i*5,y:m.y-42-i*6},{x:ex+15,y:ey-14},{x:ex,y:ey}],30+i,true,false,'back')}
// Ground stitching fence: real annular rings around dark drilled holes.
for(let x=45;x<width-40;x+=32){via(x,64,1.7);via(x,height-66,1.7)}for(let y=86;y<height-75;y+=32){via(16,y,1.7);via(width-16,y,1.7)}
// Local fan-out vias at unused MCU corner pins.
for(const side of [-1,1])for(let i=0;i<3;i++){const y=m.y+8+i*pitch*1.2,x=side<0?m.x-27:m.x+m.w+27;route([{x:side<0?m.x-12:m.x+m.w+12,y},{x:x-side*4,y},{x,y:y-4}],0,false);via(x,y-4,1.6)}
// QFP48 footprint: short, evenly spaced pads, not arbitrary perimeter fan-outs.
ink.fillStyle='#afafaf';for(let i=0;i<12;i++){const offset=(i-5.5)*pitch;ink.fillRect(m.x-12,m.cy+offset-1.1,8,2.2);ink.fillRect(m.x+m.w+4,m.cy+offset-1.1,8,2.2);ink.fillRect(m.cx+offset-1.1,m.y-12,2.2,8);ink.fillRect(m.cx+offset-1.1,m.y+m.h+4,2.2,8)}
// Display SPI bus: consistent trace spacing and short 45-degree transitions.
for(let i=0;i<4;i++){const sx=m.cx+(i-1.5)*pitch,tx=display.cx+(i-1.5)*10,dy=display.y+display.h+10,knee=dy+35+i*6;route([{x:sx,y:m.y-12},{x:sx,y:knee+Math.abs(sx-tx)},{x:tx,y:knee},{x:tx,y:dy}],i);ink.fillStyle='#9d9d9d';ink.fillRect(tx-1.5,dy-6,3,6)}
// Crystal sits beside the clock pins, with a compact parallel pair.
for(let i=0;i<2;i++){const y=xtal.cy+(i?5:-5),endY=m.cy+(i?pitch*1.5:-pitch*1.5);route([{x:xtal.x+xtal.w+11,y},{x:m.x-26,y},{x:m.x-18,y:endY},{x:m.x-12,y:endY}],6+i)}
// Clock control is a real board switch in the UI, routed on the opposite side.
for(let i=0;i<2;i++){const y=m.cy+(i?pitch*2.5:0),tx=sw.x-11;route([{x:m.x+m.w+12,y},{x:tx-14,y},{x:tx,y:sw.cy+(i?5:-5)},{x:sw.x-6,y:sw.cy+(i?5:-5)}],9+i)}
// Three LDO islands with input, output and local ground / decoupling footprints.

const busY=packages[0].y+packages[0].h+73;
route([{x:25,y:height*.11},{x:25,y:busY-14},{x:39,y:busY},{x:width-37,y:busY}],12,true,true);
for(let i=0;i<packages.length;i++){const p=packages[i],target=m.cx+(i-1)*pitch*3.5,knee=m.y+m.h+46+Math.abs(i-1)*14,start={x:p.cx,y:p.y-8};let points;if(i===1)points=[start,{x:target,y:m.y+m.h+12}];else{const delta=i===0?-1:1;points=[start,{x:p.cx,y:knee+14},{x:target+delta*14,y:knee+14},{x:target,y:knee},{x:target,y:m.y+m.h+12}]}route(points,15+i,true,true);
const input=p.cx+(width<600?11:15),ground=p.cx-(width<600?13:17);route([{x:input,y:p.y+p.h+10},{x:input,y:busY}],18+i,true,true);route([{x:ground,y:p.y+p.h+10},{x:ground,y:p.y+p.h+19},{x:ground-11,y:p.y+p.h+19}],0,false);via(ground-11,p.y+p.h+19);cap(p.cx-22,p.y-44,true,'');cap(p.cx+23,p.y-44,true,'');route([{x:p.cx,y:p.y-8},{x:p.cx,y:p.y-22},{x:p.cx-15,y:p.y-22}],0,false);via(p.cx+29,p.y-52,1.8);}
// Thermal via arrays inside each LDO heat-spreader copper island.
for(const p of packages){if(layerMode==='all'||layerMode==='power'){ink.fillStyle='rgba(255,255,255,.15)';ink.fillRect(p.cx-14,p.y-53,28,30);ink.strokeStyle='#aaa';ink.lineWidth=.7;ink.strokeRect(p.cx-14,p.y-53,28,30)}for(let row=0;row<3;row++)for(let col=0;col<3;col++)via(p.cx+(col-1)*7,p.y-38+(row-1)*7,1.65)}
// Local bypass capacitors and a crystal load pair, kept close to their devices.
cap(m.x-22,m.y+12,true,'C1');cap(m.x+m.w+23,m.y+m.h-12,true,'C2');cap(m.x+18,m.y-26,false,'');cap(m.x+m.w-18,m.y+m.h+26,false,'');cap(xtal.cx-13,xtal.cy+xtal.h/2+37,false,'');cap(xtal.cx+13,xtal.cy+xtal.h/2+37,false,'');
// Power entry from the top connector follows the outer rail, clear of display.
route([{x:width/2,y:25},{x:width/2,y:height*.10-12},{x:width/2-12,y:height*.10},{x:37,y:height*.10},{x:25,y:height*.11}],24,true,true);
// Test header / power indicator details use aligned, compact footprints.
const hx=width*.91,hy=height*.23;ink.strokeStyle='#525252';ink.strokeRect(hx-10,hy-22,20,44);for(let col=0;col<2;col++)for(let row=0;row<3;row++)via(hx-5+col*10,hy-14+row*14,2);ink.fillStyle='#727272';ink.font='6px monospace';ink.fillText('J2 / SWD',hx-15,hy+33);via(width*.13,height*.23,2.5);ink.fillStyle='#a1a1a1';ink.fillRect(width*.13-2,height*.23-20,4,8);ink.fillStyle='#5e5e5e';ink.fillText('PWR',width*.13-7,height*.23+15);
draw()}
function at(t,d){for(const s of t.segments)if(d<=s.start+s.len){const u=Math.max(0,(d-s.start)/s.len);return{x:s.a.x+(s.b.x-s.a.x)*u,y:s.a.y+(s.b.y-s.a.y)*u}}return t.segments.at(-1).b}
function pulse(t,start,end){const a=at(t,start),b=at(t,end);ctx.beginPath();ctx.moveTo(a.x,a.y);for(const s of t.segments)if(s.start+s.len>start&&s.start+s.len<end)ctx.lineTo(s.b.x,s.b.y);ctx.lineTo(b.x,b.y);ctx.stroke()}
function draw(){ctx.globalAlpha=1;ctx.drawImage(layer,0,0,layer.width,layer.height,0,0,width,height);ctx.lineJoin='round';ctx.lineCap='round';for(const t of routes){const head=(phase*t.speed+t.offset*t.length)%(t.length+t.tail),start=Math.max(0,head-t.tail),end=Math.min(head,t.length);if(end<=start)continue;ctx.strokeStyle='#6dff7f';ctx.globalAlpha=.09;ctx.lineWidth=5;pulse(t,start,end);ctx.globalAlpha=.78;ctx.lineWidth=1.3;pulse(t,start,end);const p=at(t,end);ctx.globalAlpha=.9;ctx.fillStyle='#c1ffcb';ctx.beginPath();ctx.arc(p.x,p.y,1.15,0,6.283185307);ctx.fill()}ctx.globalAlpha=1}
function loop(time){frame=null;if(paused||document.hidden)return;if(last)phase+=Math.min((time-last)/1000,.05);last=time;draw();frame=requestAnimationFrame(loop)}
function sync(){if(frame!==null)cancelAnimationFrame(frame);frame=null;last=0;button.setAttribute('aria-pressed',String(paused));button.setAttribute('aria-label',paused?'播放动画':'暂停动画');button.querySelector('.motion-state').textContent=paused?'HOLD / 播放':'RUN / 暂停';if(!paused&&!document.hidden)frame=requestAnimationFrame(loop)}
document.querySelectorAll('[data-layer]').forEach(control=>control.addEventListener('click',()=>{layerMode=control.dataset.layer;document.querySelectorAll('[data-layer]').forEach(el=>el.setAttribute('aria-pressed',String(el===control)));rebuild()}));
button.addEventListener('click',()=>{paused=!paused;sync()});document.addEventListener('visibilitychange',sync);reduce.addEventListener('change',()=>{paused=reduce.matches;sync()});new ResizeObserver(rebuild).observe(board);rebuild();sync();
})();
