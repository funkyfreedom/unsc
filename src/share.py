"""Draw the social share image (dist/assets/share-v2.png). Needs the Inter .otf fonts."""
from PIL import Image, ImageDraw, ImageFont
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *
W,H=1200,630
S=2
im=Image.new('RGB',(W*S,H*S),'white'); d=ImageDraw.Draw(im)
F=INTER_OTF.rstrip('/')+'/'
f=lambda n,s: ImageFont.truetype(F+n,s*S)
blue=(44,120,212); bink=(29,95,174); grey=(196,195,182); ink=(29,29,27); muted=(100,99,93); light=(217,216,210)
# ink header
d.rectangle((0,0,W*S,88*S),fill=ink)
x0,y0=60,22
d.rounded_rectangle((x0*S,y0*S,(x0+44)*S,(y0+44)*S),radius=8*S,fill=blue)
u=44/28
for x,y in ((6,15),(12.2,10),(18.4,6)): d.rectangle(((x0+x*u)*S,(y0+y*u)*S,(x0+(x+3.6)*u)*S,(y0+22*u)*S),fill='white')
d.text((118*S,29*S),'Security Council Record',font=f('Inter-ExtraBold.otf',30),fill='white')
d.text((W*S-60*S,34*S),'securitycouncilrecord.org',font=f('Inter-Medium.otf',22),fill=light,anchor='ra')
# headline
d.text((60*S,122*S),'80 years of the UN Security Council',font=f('Inter-ExtraBold.otf',58),fill=ink)
d.text((60*S,198*S),'Patterns in themes, voting and language since 1946',font=f('Inter-Regular.otf',28),fill=muted)
# chart
Y=json.load(open(os.path.join(DIST,'assets','years.json')))
ys=[int(k) for k in Y if int(k)<=2025]; mx=max(Y[str(y)] for y in ys)
left,right,base,top=60,W-60,560,262
bw=(right-left)/len(ys)
for v in (25,50,75):
    yy=base-(v/mx)*(base-top); d.line((left*S,yy*S,right*S,yy*S),fill=(233,232,227),width=S)
for i,y in enumerate(ys):
    h=Y[str(y)]/mx*(base-top); c=blue if y in (1993,2025) else grey
    d.rectangle(((left+i*bw+1.2)*S,(base-h)*S,(left+(i+1)*bw-1.2)*S,base*S),fill=c)
def lab(y,txt,anchor):
    i=ys.index(y); x=left+i*bw+bw/2; h=Y[str(y)]/mx*(base-top)
    d.text(((x+(10 if anchor=='la' else -10))*S,(base-h+2)*S),txt,font=f('Inter-Bold.otf',22),fill=bink,anchor=anchor)
i=ys.index(1993); x=left+i*bw
d.text(((x-10)*S,(top+2)*S),'93 resolutions in 1993',font=f('Inter-Bold.otf',22),fill=bink,anchor='ra')
rec=max(Y[str(y)] for y in ys[-6:]); yy=base-rec/mx*(base-top)
d.text((right*S,(yy-34)*S),'44 in 2025',font=f('Inter-Bold.otf',22),fill=bink,anchor='ra')
d.line((left*S,base*S,right*S,base*S),fill=(185,184,174),width=2*S)
for y in (1950,1970,1990,2010):
    i=ys.index(y); d.text(((left+i*bw+bw/2)*S,(base+12)*S),str(y),font=f('Inter-Medium.otf',18),fill=muted,anchor='ma')
d.text((60*S,600*S),'Resolutions adopted per year, 1946 to 2025',font=f('Inter-Medium.otf',18),fill=muted)
im.resize((W,H),Image.LANCZOS).save(os.path.join(DIST,'assets','share-v2.png'),optimize=True)
