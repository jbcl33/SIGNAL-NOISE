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
// Deterministic volumetric spiral cloud. No per-frame point allocation or sorting.
let seed=8123;function random(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return(seed+.5)/4294967296}function normal(){return Math.sqrt(-2*Math.log(random()))*Math.cos(6.283185307*random())}
const particles=[];for(let i=0;i<2000;i++){const core=i%6===0,r=core?Math.pow(random(),.8)*.25:.15+Math.pow(random(),.8)*.91,arm=i%3,angle=arm*2.094395102+r*5.2+normal()*(core?.8:.15+.1*r),spread=normal()*(.02+.04*r);particles.push({x:Math.cos(angle)*r+spread,y:Math.sin(angle)*r+spread,z:normal()*(.045+.09*r),r,glyph:i%words.length,noise:random()*6.283185307,brightness:.32+random()*.68})}
const stars=[];for(let i=0;i<65;i++)stars.push({x:random(),y:random(),alpha:.08+random()*.26});
function draw(){
ctx.globalAlpha=1;ctx.fillStyle='#050505';ctx.fillRect(0,0,width,height);
const turn=phase*.14,ct=Math.cos(turn),st=Math.sin(turn),tilt=.68+Math.sin(phase*.21)*.09,size=Math.min(width*.40,height*.43),font=Math.max(4.6,Math.min(7.4,width/108)),scale=font/28,centerX=width/2,centerY=height/2,count=width<600?1400:2000;
ctx.fillStyle='#fff';for(const star of stars){ctx.globalAlpha=star.alpha;ctx.fillRect(star.x*width,star.y*height,1,1)}
for(let i=0;i<count;i++){const p=particles[i],drift=.012*Math.sin(phase*.75+p.noise),px=p.x+drift,py=p.y+drift*.4,x=px*ct-py*st,y=(px*st+py*ct)*tilt+p.z*.7,z=p.z+Math.sin(phase*.19)*py*.12,k=4/(4+z),w=tileW*scale*k,h=tileH*scale*k;ctx.globalAlpha=Math.min(.9,(.08+.67*(1-p.r*.65))*p.brightness*(.9+.1*Math.sin(p.noise+phase*.4)));ctx.drawImage(atlas,p.glyph*tileW,0,tileW,tileH,centerX+x*size*k-w/2,centerY+y*size*k-h/2,w,h)}ctx.globalAlpha=1;
}
function resize(){const box=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,box.width<600?1.5:2);width=box.width;height=box.height;canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);draw()}
function loop(time){frame=null;if(paused||document.hidden)return;if(last)phase+=Math.min((time-last)/1000,.05)*.56;last=time;draw();frame=requestAnimationFrame(loop)}
function sync(){if(frame!==null)cancelAnimationFrame(frame);frame=null;button.textContent=paused?'播放动画':'暂停动画';button.setAttribute('aria-pressed',String(paused));last=0;if(!paused&&!document.hidden)frame=requestAnimationFrame(loop)}
button.addEventListener('click',()=>{paused=!paused;sync()});document.addEventListener('visibilitychange',sync);reduce.addEventListener('change',()=>{paused=reduce.matches;sync()});new ResizeObserver(resize).observe(canvas);resize();sync();
})();
