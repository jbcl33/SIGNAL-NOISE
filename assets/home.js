(()=>{'use strict';
const menu=document.querySelector('#site-menu'),summary=menu.querySelector('summary');
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&menu.open){menu.open=false;summary.focus()}});
document.addEventListener('pointerdown',event=>{if(menu.open&&!menu.contains(event.target))menu.open=false});
menu.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{menu.open=false}));
const canvas=document.querySelector('#assembly'),ctx=canvas.getContext('2d',{alpha:false}),button=document.querySelector('#motion'),reduce=matchMedia('(prefers-reduced-motion: reduce)');
if(!ctx){button.hidden=true;return}
const words=['MOV','XOR','ADD','JMP','RET','CMP','NOP','SHL','SUB','AND','OR','LEA'];
// Rasterize glyphs once. Animation frames only project points and blit sprites.
const atlas=document.createElement('canvas'),tileW=96,tileH=56;atlas.width=tileW*words.length;atlas.height=tileH;
const ink=atlas.getContext('2d');ink.font='28px monospace';ink.textAlign='center';ink.textBaseline='middle';ink.fillStyle='#f5f5f5';words.forEach((word,i)=>ink.fillText(word,(i+.5)*tileW,tileH/2));
let paused=reduce.matches,phase=.65,frame=null,last=0,width=0,height=0;
const faces=[],n=15;
for(let face=0;face<6;face++){const points=[],sign=face%2?1:-1;for(let a=0;a<n;a++)for(let b=0;b<n;b++){const u=2*a/(n-1)-1,v=2*b/(n-1)-1;let x,y,z;if(face<2){x=sign;y=u;z=v}else if(face<4){x=u;y=sign;z=v}else{x=u;y=v;z=sign}points.push({x,y,z,glyph:(a*7+b*3+face)%words.length})}faces.push({points,x:face<2?sign:0,y:face>=2&&face<4?sign:0,z:face>=4?sign:0,depth:0})}
function draw(){
ctx.globalAlpha=1;ctx.fillStyle='#050505';ctx.fillRect(0,0,width,height);
const ax=.38+Math.sin(phase*.51)*.22,ay=phase*.32,cx=Math.cos(ax),sx=Math.sin(ax),cy=Math.cos(ay),sy=Math.sin(ay),size=Math.min(width*.255,height*.34),font=Math.max(4.7,Math.min(7.5,width/105)),scale=font/28,centerX=width/2,centerY=height/2;
// Six planar faces can be depth-sorted without allocating/sorting 1,350 objects.
for(const face of faces)face.depth=face.y*sx+(-face.x*sy+face.z*cy)*cx;
faces.sort((a,b)=>b.depth-a.depth);
for(const face of faces)for(const p of face.points){const swell=1+.025*Math.sin(p.y*4+phase*1.6),px=p.x*swell,py=p.y*swell,pz=p.z*swell,x=px*cy+pz*sy,z=-px*sy+pz*cy,y=py*cx-z*sx,depth=py*sx+z*cx,k=4/(4+depth),w=tileW*scale*k,h=tileH*scale*k;ctx.globalAlpha=Math.max(.06,Math.min(.95,.5-depth*.28));ctx.drawImage(atlas,p.glyph*tileW,0,tileW,tileH,centerX+x*size*k-w/2,centerY+y*size*k-h/2,w,h)}ctx.globalAlpha=1;
}
function resize(){const box=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,box.width<600?1.5:2);width=box.width;height=box.height;canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);draw()}
function loop(time){frame=null;if(paused||document.hidden)return;if(last)phase+=Math.min((time-last)/1000,.05)*.56;last=time;draw();frame=requestAnimationFrame(loop)}
function sync(){if(frame!==null)cancelAnimationFrame(frame);frame=null;button.textContent=paused?'播放动画':'暂停动画';button.setAttribute('aria-pressed',String(paused));last=0;if(!paused&&!document.hidden)frame=requestAnimationFrame(loop)}
button.addEventListener('click',()=>{paused=!paused;sync()});document.addEventListener('visibilitychange',sync);reduce.addEventListener('change',()=>{paused=reduce.matches;sync()});new ResizeObserver(resize).observe(canvas);resize();sync();
})();
