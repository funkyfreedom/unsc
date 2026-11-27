from PIL import Image, ImageDraw, ImageFont
import json
W,H=1200,630
im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
F='/usr/share/fonts/opentype/inter/'
bold=ImageFont.truetype(F+'Inter-Bold.otf',62); semi=ImageFont.truetype(F+'Inter-SemiBold.otf',34); reg=ImageFont.truetype(F+'Inter-Regular.otf',28)
blue=(44,120,212); grey=(196,195,182); text=(29,29,27); muted=(107,106,100)
d.rounded_rectangle((80,80,140,140),10,fill=blue)
for x,y in ((93,112),(106,101),(119,92)): d.rectangle((x,y,x+8,128),fill='white')
d.text((160,88),'Security Council Record',font=semi,fill=text)
d.text((80,200),'Every UN Security Council',font=bold,fill=text)
d.text((80,272),'resolution, vote and veto',font=bold,fill=text)
d.text((80,344),'since 1946',font=bold,fill=text)
Y=json.load(open('dist/assets/years.json'))
ys=[int(k) for k in Y if int(k)<=2025]; mx=max(Y[str(y)] for y in ys)
x0,base,bw=80,580,(1040)/len(ys)
for i,y in enumerate(ys):
    h=Y[str(y)]/mx*95; col=blue if y in (1993,2025) else grey
    d.rectangle((x0+i*bw+1,base-h,x0+(i+1)*bw-2,base),fill=col)
d.text((80,420),'An independent record, counted from the documents',font=reg,fill=muted)
im.save('dist/assets/share.png',optimize=True)
