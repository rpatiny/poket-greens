import math, random
from pal import PAL, render
from PIL import Image
RAMP={
 'leaf':['k','l','L','m','n','o'],'skin':['b','c','C','d','e'],'wood':['0','1','2','3','4','5'],
 'brick':['6','7','8','9','&'],'stone':['T','U','u','V','t','w'],'denim':['p','q','r','s','S'],
 'gold':['%','G','O','Y','Z'],'crimson':['(','X','v','x',')'],'soil':['A','B','D','E'],
 'plum':['[','K','N',']'],'teal':['{','F','H','I','J'],'hair':['g','h','i','j'],
}
LX,LY=-0.55,-0.8   # luz de cima-esquerda
class C:
    def __init__(s,w,h): s.w,s.h=w,h; s.g=[['.']*w for _ in range(h)]
    def px(s,x,y,c):
        x,y=int(round(x)),int(round(y))
        if 0<=x<s.w and 0<=y<s.h and c: s.g[y][x]=c
    def get(s,x,y): return s.g[y][x] if 0<=x<s.w and 0<=y<s.h else '.'
    def rect(s,x0,y0,x1,y1,c):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1): s.px(x,y,c)
    def line(s,x0,y0,x1,y1,c):
        n=int(max(abs(x1-x0),abs(y1-y0),1))
        for i in range(n+1): s.px(x0+(x1-x0)*i/n,y0+(y1-y0)*i/n,c)
    def stamp(s,x0,y0,rows):
        for y,r in enumerate(rows):
            for x,c in enumerate(r):
                if c!='.': s.px(x0+x,y0+y,c)
    def shade(s,lit,ramp,lo=0):
        r=RAMP[ramp] if isinstance(ramp,str) else ramp
        r=r[lo:]
        # lit em [-1,1] -> índice
        t=(lit+1)/2; i=int(t*len(r)); return r[max(0,min(len(r)-1,i))]
    def sphere(s,cx,cy,rx,ry,ramp,lo=0,spec=True):
        for y in range(int(cy-ry-1),int(cy+ry+2)):
            for x in range(int(cx-rx-1),int(cx+rx+2)):
                nx,ny=(x-cx)/rx,(y-cy)/ry
                d=nx*nx+ny*ny
                if d<=1:
                    nz=math.sqrt(1-d); lit=-(LX*nx+LY*ny)*0.9+nz*0.25-0.15
                    s.px(x,y,s.shade(lit,ramp,lo))
    def blob(s,cx,cy,r,ramp,seed=0,bump=0.13,lobes=5,lo=0,owner=None,idx=0):
        for y in range(int(cy-r-2),int(cy+r+3)):
            for x in range(int(cx-r-2),int(cx+r+3)):
                dx,dy=x-cx,y-cy; d=math.hypot(dx,dy); a=math.atan2(dy,dx)
                re=r*(1+bump*math.sin(lobes*a+seed))
                if d<=re:
                    nx,ny=dx/re,dy/re; lit=-(LX*nx+LY*ny)
                    c=s.shade(lit*0.95,ramp,lo)
                    if owner is not None:
                        if d>re-1.1:
                            for a2,b2 in ((1,0),(-1,0),(0,1),(0,-1)):
                                o=owner.get((x+a2,y+b2))
                                if o is not None and o<idx: c=(RAMP[ramp] if isinstance(ramp,str) else ramp)[lo if lo else 1]
                        owner[(x,y)]=idx
                    s.px(x,y,c)
    def bush(s,blobs,ramp,lo=0,seed=0):
        owner={}
        for i,(cx,cy,r) in enumerate(blobs): s.blob(cx,cy,r,ramp,seed=seed+i*1.7,owner=owner,idx=i,lo=lo)
    def cyl(s,x0,y0,x1,y1,ramp,lo=0,top=None):
        w=x1-x0
        for x in range(x0,x1+1):
            t=(x-x0)/max(w,1); lit=0.9-1.9*t if t>0.25 else 0.2+t*2
            for y in range(y0,y1+1): s.px(x,y,s.shade(lit,ramp,lo))
        if top:
            for x in range(x0,x1+1): s.px(x,y0,top)
    def box(s,x0,y0,x1,y1,toph,ramp,lo=0):
        r=RAMP[ramp] if isinstance(ramp,str) else ramp
        s.rect(x0,y0,x1,y0+toph-1,r[-1] if len(r)>3 else r[-1])
        s.rect(x0,y0+toph,x1,y1,r[-3])
        for y in range(y0+toph,y1+1): s.px(x1,y,r[-4]); s.px(x0,y,r[-2])
        for x in range(x0,x1+1): s.px(x,y0+toph,r[-2]); s.px(x,y1,r[-4])
    def leaf(s,x0,y0,ang,L,W,ramp,lo=1,vein=True):
        ca,sa=math.cos(ang),math.sin(ang)
        r=RAMP[ramp] if isinstance(ramp,str) else ramp
        for i in range(int(L*4)+1):
            t=i/(L*4)
            half=W*math.sin(math.pi*t)**0.8
            for j in range(-int(half*4),int(half*4)+1):
                u=j/4
                x=x0+ca*t*L-sa*u; y=y0+sa*t*L+ca*u
                # lado de cima (contra a luz) mais claro
                side=-(sa*-1)*u
                nrm=(-sa*u, ca*u)
                lit=-(LX*(-sa)+LY*ca)*(1 if u>0 else -1)
                c=r[min(len(r)-1,lo+3)] if lit>0.2 else r[min(len(r)-1,lo+2)] if lit>-0.3 else r[lo+1]
                s.px(x,y,c)
        if vein:
            for i in range(int(L*0.8)):
                t=i/L; s.px(x0+ca*t*L,y0+sa*t*L,r[lo])
    def outline(s,c='a',corners=False):
        add=[]
        for y in range(s.h):
            for x in range(s.w):
                if s.g[y][x]=='.':
                    nb=((1,0),(-1,0),(0,1),(0,-1))+(((1,1),(1,-1),(-1,1),(-1,-1)) if corners else ())
                    if any(s.get(x+a,y+b) not in ('.',c) for a,b in nb): add.append((x,y))
        for x,y in add: s.g[y][x]=c
    def rows(s): return [''.join(r) for r in s.g]
    def paste(s,o,x0,y0):
        for y in range(o.h):
            for x in range(o.w):
                if o.g[y][x]!='.': s.px(x0+x,y0+y,o.g[y][x])
def sheet(cells,cols,cw,ch,name,scale=4,bg=(58,52,72,255),labels=None):
    rows_n=(len(cells)+cols-1)//cols
    big=C(cols*cw,rows_n*ch)
    for i,c in enumerate(cells): big.paste(c,(i%cols)*cw,(i//cols)*ch)
    im=render(big.rows(),name,scale=scale,bg=bg)
    # 1x transparente
    t=Image.new('RGBA',(big.w,big.h),(0,0,0,0))
    for y,r in enumerate(big.rows()):
        for x,ch_ in enumerate(r):
            if ch_!='.':
                hx=PAL[ch_]; t.putpixel((x,y),tuple(int(hx[i:i+2],16) for i in (1,3,5))+(255,))
    t.save(name.replace('.png','_1x.png'))
    return big
class CS(C):
    """Canvas que encolhe tudo o que é desenhado em torno da base da planta (16,39)."""
    def __init__(s,w,h,f=0.62,ax=16,ay=39):
        super().__init__(w,h); s.f,s.ax,s.ay=f,ax,ay
    def px(s,x,y,c):
        if getattr(s,'_raw',False): return C.px(s,x,y,c)
        C.px(s,s.ax+(x-s.ax)*s.f,s.ay+(y-s.ay)*s.f,c)
    def outline(s,c='a',corners=False):
        s._raw=True
        # remove contornos encolhidos (podem ficar dentro) e refaz
        for y in range(s.h):
            for x in range(s.w):
                if s.g[y][x]==c: s.g[y][x]='.'
        # preenche buracos isolados de 1px
        for y in range(1,s.h-1):
            for x in range(1,s.w-1):
                if s.g[y][x]=='.':
                    n=[s.g[y][x+1],s.g[y][x-1],s.g[y+1][x],s.g[y-1][x]]
                    f=[v for v in n if v!='.']
                    if len(f)>=3: s.g[y][x]=f[0]
        C.outline(s,c,corners); s._raw=False
