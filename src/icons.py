"""Draw the favicons, app icons and logo into dist/."""
from PIL import Image, ImageDraw
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *
BLUE=(44,120,212)
def logo(size, pad=0.0, bg_white=False):
    S=size*4
    im=Image.new('RGBA',(S,S),(255,255,255,255) if bg_white else (0,0,0,0)); d=ImageDraw.Draw(im)
    p=int(S*pad); w=S-2*p
    d.rounded_rectangle((p,p,p+w,p+w),radius=int(w*5/28),fill=BLUE)
    u=w/28
    for x,y in ((6,15),(12.2,10),(18.4,6)):
        d.rectangle((p+x*u,p+y*u,p+(x+3.6)*u,p+22*u),fill='white')
    return im.resize((size,size),Image.LANCZOS)
D=DIST+'/'
logo(48).save(D+'favicon-48.png'); logo(96).save(D+'favicon-96.png')
logo(192).save(D+'icon-192.png'); logo(512).save(D+'icon-512.png')
logo(180,pad=0.08,bg_white=True).convert('RGB').save(D+'apple-touch-icon.png')
logo(512,pad=0.1,bg_white=True).convert('RGB').save(D+'assets/logo.png')
logo(48).save(D+'favicon.ico',sizes=[(16,16),(32,32),(48,48)])
json.dump({"name":"Security Council Record","short_name":"SC Record","icons":[{"src":"/icon-192.png","sizes":"192x192","type":"image/png"},{"src":"/icon-512.png","sizes":"512x512","type":"image/png"}],"start_url":"/","display":"standalone","background_color":"#ffffff","theme_color":"#1d1d1b"},open(D+'site.webmanifest','w'))
print('icons ok')
