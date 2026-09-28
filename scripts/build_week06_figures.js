#!/usr/bin/env node
// Original teaching diagrams; coordinates and schedule values remain editable here.
const fs = require('fs');
const path = require('path');
const out = path.join(__dirname, '..', 'images', 'week06');
fs.mkdirSync(out, { recursive: true });
const G = '#0F5A4B', INK = '#203331', GRAY = '#627571', TEAL = '#E9F3EF', GOLD = '#B97812';
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const text = (x,y,s,size=22,color=INK,weight=400,anchor='start') => `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" font-weight="${weight}" text-anchor="${anchor}">${esc(s)}</text>`;
const rect = (x,y,w,h,fill='#fff',stroke=G,rx=8) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
const line = (x1,y1,x2,y2,color=GRAY,width=3,dash='') => `<path d="M${x1},${y1} L${x2},${y2}" fill="none" stroke="${color}" stroke-width="${width}" ${dash ? `stroke-dasharray="${dash}"` : ''}/>`;
const arrow = (points,color=GRAY,width=3) => `<path d="${points}" fill="none" stroke="${color}" stroke-width="${width}" marker-end="url(#${color===G?'green':'gray'})"/>`;
function save(name,title,desc,w,h,body) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" role="img" aria-labelledby="title desc" style="width:100%;height:${h}px;font-family:Arial,sans-serif">
<title id="title">${esc(title)}</title><desc id="desc">${esc(desc)}</desc>
<defs><marker id="green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="${G}"/></marker><marker id="gray" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="${GRAY}"/></marker></defs>
<rect width="${w}" height="${h}" fill="#fff"/>${body}</svg>\n`;
  fs.writeFileSync(path.join(out,name+'.svg'),svg);
}

let b='';
const steps=[['WBS','Defined deliverables','and work packages'],['Activities','Observable work','and duration estimates'],['Network','Predecessors and','permitted overlap'],['Schedule','Calculated timing','and calendar dates']];
steps.forEach((s,i)=>{const x=25+i*265;b+=text(x,47,`0${i+1}`,18,GRAY,700)+rect(x,70,220,138,TEAL)+text(x+18,108,s[0],25,G,700)+text(x+18,149,s[1],18)+text(x+18,177,s[2],18);if(i<3)b+=arrow(`M${x+225},137 H${x+256}`,G);});
b+=text(25,261,'Keep the WBS code, activity owner and definition of done connected across the four steps.',20,GRAY);
save('planning-flow','How work becomes a schedule','A WBS defines work packages, activities add durations, a network adds logic, and the schedule calculates timing.',1090,300,b);

const pos={A:[25,187],B:[235,40],C:[235,265],D:[445,40],E:[445,187],F:[445,340],G:[655,155],H:[865,235],I:[1075,235]};
const duration={A:2,B:5,C:6,D:4,E:8,F:5,G:3,H:4,I:2};
const names={A:'Event brief',B:'Venue',C:'Program draft',D:'Registration',E:'Speakers',F:'Exhibitors',G:'Publish program',H:'Materials',I:'Rehearsal'};
const critical=new Set(['A','C','E','G','H','I']);
b=arrow('M175,237 H205 V90 H235')+arrow('M175,237 H205 V315 H235',G,5)+arrow('M385,90 H445')+arrow('M385,315 H412 V237 H445',G,5)+arrow('M385,315 H412 V390 H445')+arrow('M595,90 H623 V180 H655')+arrow('M595,237 H623 V225 H655',G,5)+arrow('M595,390 H835 V310 H865')+arrow('M805,205 H835 V260 H865',G,5)+arrow('M1015,285 H1075',G,5);
Object.entries(pos).forEach(([id,[x,y]])=>{const c=critical.has(id);b+=rect(x,y,150,100,c?TEAL:'#F5F7F7',c?G:GRAY)+text(x+13,y+29,id,25,c?G:GRAY,700)+text(x+137,y+29,`${duration[id]} d`,21,INK,400,'end')+text(x+75,y+68,names[id],17,INK,400,'middle');});
b+=line(25,485,80,485,G,5)+text(92,492,'Critical path: A–C–E–G–H–I = 25 workdays',21,G,700)+line(650,485,705,485,GRAY,3)+text(718,492,'Other precedence links',20,GRAY);
save('conference-network','Conference activity-on-node network','All ten links: A to B and C; B to D; C to E and F; D and E to G; F and G to H; H to I. Critical activities are A C E G H I.',1250,525,b);

b=text(38,45,'Field positions',24,G,700)+text(588,45,'Worked example: activity D',24,G,700);
for(const [x,example] of [[38,false],[588,true]]) {
 b+=rect(x,72,470,244,TEAL);
 b+=line(x,140,x+470,140,G,2)+line(x,248,x+470,248,G,2)+line(x+155,72,x+155,140,G,2)+line(x+315,72,x+315,140,G,2)+line(x+155,248,x+155,316,G,2)+line(x+315,248,x+315,316,G,2);
 [[77,115,example?'7':'ES'],[235,115,example?'4 days':'Duration'],[392,115,example?'11':'EF'],[77,291,example?'12':'LS'],[235,291,example?'5 days':'Total slack'],[392,291,example?'16':'LF']].forEach(([dx,y,s])=>b+=text(x+dx,y,s,23,INK,600,'middle'));
 b+=text(x+235,188,example?'D · Configure registration':'Activity ID and description',23,G,700,'middle')+text(x+235,225,example?'Free slack = 16 − 11 = 5 days':'Free slack shown separately',20,GRAY,400,'middle');
}
b+=text(38,368,'Early window: day 7 to 11',22)+text(588,368,'Late window: day 12 to 16',22)+text(38,407,'Moving D five days later uses its total slack; its four-day duration stays the same.',21,GRAY);
save('activity-node','Reading an activity node','Node legend with ES duration EF above, LS total slack LF below; D has ES 7 EF 11 LS 12 LF 16 total slack 5 and free slack 5.',1100,450,b);

b=text(25,38,'Forward pass: wait for every predecessor',23,G,700)+text(595,38,'Backward pass: protect every successor',23,G,700);
b+=rect(25,75,185,80,TEAL)+text(117,108,'D finishes 11',21,INK,600,'middle')+text(117,139,'EF = 11',19,GRAY,400,'middle')+rect(25,235,185,80,TEAL)+text(117,268,'E finishes 16',21,INK,600,'middle')+text(117,299,'EF = 16',19,GRAY,400,'middle');
b+=arrow('M210,115 H265 V175 H320')+arrow('M210,275 H265 V225 H320',G,5)+rect(320,157,205,86,TEAL)+text(422,190,'G starts 16',23,G,700,'middle')+text(422,224,'max(11, 16)',21,INK,400,'middle');
b+=rect(595,157,200,86,TEAL)+text(695,190,'C finishes by 8',21,G,700,'middle')+text(695,224,'min(8, 14)',21,INK,400,'middle')+rect(920,75,190,80,TEAL)+text(1015,108,'E starts by 8',21,INK,600,'middle')+text(1015,139,'LS = 8',19,GRAY,400,'middle')+rect(920,235,190,80,TEAL)+text(1015,268,'F starts by 14',21,INK,600,'middle')+text(1015,299,'LS = 14',19,GRAY,400,'middle');
b+=arrow('M920,115 H860 V175 H795',G,5)+arrow('M920,275 H860 V225 H795');
b+=text(25,373,'Choosing 11 would begin G before E is complete.',20,GRAY)+text(595,373,'Choosing 14 would make C too late for E.',20,GRAY);
save('pass-logic','Why the forward pass uses max and the backward pass uses min','The forward pass at G selects predecessor EF 16, not 11. The backward pass at C selects successor LS 8, not 14. Arrows show calculation direction.',1140,415,b);

const schedule=[['A',0,2,0],['B',2,7,5],['C',2,8,0],['D',7,11,5],['E',8,16,0],['F',8,13,6],['G',16,19,0],['H',19,23,0],['I',23,25,0]];
const x0=220, scale=33;
b=text(25,36,'Early-start schedule and available total slack',25,G,700);
for(let day=0;day<=25;day++){const x=x0+day*scale;b+=line(x,84,x,505,'#E0E7E4',1);if(day%5===0)b+=text(x,72,day,20,GRAY,400,'middle');}
schedule.forEach(([id,es,ef,ts],i)=>{const y=96+i*44;b+=text(25,y+23,`${id}  ${names[id]}`,18,INK,600);b+=rect(x0+es*scale,y,(ef-es)*scale,30,critical.has(id)?G:'#83ADA0','none',3);if(ts)b+=`<rect x="${x0+ef*scale}" y="${y}" width="${ts*scale}" height="30" fill="#FFF4DE" stroke="${GOLD}" stroke-width="2" stroke-dasharray="6 4"/>`;});
b+=rect(25,530,32,20,G,'none',2)+text(70,547,'Critical work',18)+rect(250,530,32,20,'#83ADA0','none',2)+text(295,547,'Other work',18)+rect(470,530,32,20,'#FFF4DE',GOLD,2)+text(515,547,'Total slack (shared along a path)',18)+text(1038,547,'Workdays',18,GRAY,400,'end');
b+=text(25,593,'B and D share five days of path slack. Their dashed allowances cannot be added together.',20,G,700);
save('schedule-slack','Time-scaled schedule with total slack','Gantt chart from day 0 through day 25. B and D each show five days of total slack, shared along their branch; F has six days.',1090,625,b);

b=text(25,35,'Each relationship constrains a specific start or finish',24,G,700);
const cases=[{name:'FS + 2',y:78,p:[0,6],s:[8,12],label:'Successor starts ≥ predecessor finish + 2',a:[6,8]}, {name:'SS + 2',y:218,p:[0,6],s:[2,10],label:'Successor starts ≥ predecessor start + 2',a:[0,2]}, {name:'FF + 2',y:358,p:[0,6],s:[4,8],label:'Successor finishes ≥ predecessor finish + 2',a:[6,8]}];
cases.forEach(c=>{const start=230,k=48,y=c.y;b+=text(25,y+29,c.name,25,G,700)+text(25,y+99,c.label,19,GRAY);b+=rect(start+c.p[0]*k,y,(c.p[1]-c.p[0])*k,27,G,'none',2)+rect(start+c.s[0]*k,y+47,(c.s[1]-c.s[0])*k,27,'#83ADA0','none',2);b+=text(875,y+21,'Predecessor',18)+text(875,y+68,'Successor',18);b+=arrow(`M${start+c.a[0]*k},${y+29} V${y+36} H${start+c.a[1]*k} V${y+46}`,GRAY,2);});
b+=text(25,508,'A lag is a minimum separation. Other dependencies can push the successor later.',21,G,700);
save('lag-relationships','Finish-to-start, start-to-start and finish-to-finish lags','Three timelines show the activity endpoints constrained by a positive two-day lag. The successor may start or finish later if another constraint controls.',1090,550,b);

b=text(25,40,'Three segments; one crew for each type of work',25,G,700);
const labels=['Dig','Lay pipe','Refill'];
for(let row=0;row<3;row++)for(let col=0;col<3;col++){
 const x=200+col*310,y=83+row*108;
 if(col<2)b+=arrow(`M${x+220},${y+32} H${x+300}`,GRAY,3);
 if(row<2)b+=arrow(`M${x+110},${y+64} V${y+99}`,G,3);
 b+=rect(x,y,220,64,row===0?TEAL:'#F5F7F7')+text(x+110,y+39,`${labels[row]} ${col+1}`,23,G,700,'middle');
}
b+=text(25,122,'Trench crew',20,INK,600)+text(25,230,'Pipe crew',20,INK,600)+text(25,338,'Refill crew',20,INK,600)+text(25,447,'Horizontal links preserve crew order. Vertical links preserve the handoff within each segment.',21,GRAY);
save('laddering','Laddering for three pipeline segments','Each crew moves from segment 1 to 2 to 3. Within each segment digging precedes laying pipe and laying pipe precedes refill. Different crews can overlap across segments.',1090,480,b);
console.log(`Wrote seven Week 6 diagrams to ${out}`);
