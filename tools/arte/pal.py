PAL = {
 'a':'#1a1420',
 # hair
 'g':'#24161f','h':'#432532','i':'#6b3a3a','j':'#94573f',
 # skin
 'b':'#5c2b36','c':'#8f4a45','C':'#c27a5c','d':'#e8a87c','e':'#f7d4b0',
 # leaf
 'k':'#14292b','l':'#1d4537','L':'#2c6a40','m':'#4a8f40','n':'#7cb342','o':'#bcd95e',
 # denim
 'p':'#1b1f45','q':'#283c74','r':'#3a5ea3','s':'#6590cc','S':'#a6cbeb',
 # stone
 'T':'#272436','U':'#403d54','u':'#646379','V':'#8f90a2','t':'#bfbfc8','w':'#ebe9e1','W':'#fffbef',
 # crimson
 'v':'#a62e4a','x':'#d95463','X':'#6e1b3d',
 '$':'#1b1b2a','!':'#f4f1ea','M':'#8f3a3a','*':'#f08c8c',
 'y':'#1d1824',
 # wood
 '0':'#3b1f2b','1':'#5e2f2e','2':'#8a4a33','3':'#b5703f','4':'#d99a5b','5':'#f0c487',
 # brick
 '6':'#401a2c','7':'#6e2834','8':'#a3423a','9':'#cc6748','&':'#e99568',
 # gold
 'G':'#94592a','O':'#d1952e','Y':'#f0c94f','Z':'#fff0a6',
 # soil
 'A':'#2b1a24','B':'#47292b','D':'#6b4234','E':'#8f6040',
 # teal/plum
 'F':'#1b4a55','H':'#2a7470','I':'#48a38a','J':'#8fd4a8','K':'#352450','N':'#56397a',
}
from PIL import Image
def render(rows, name, scale=8, bg=(120,140,110,255)):
    w=max(len(r) for r in rows)
    bad=[(i,len(r)) for i,r in enumerate(rows) if len(r)!=w]
    if bad: print('WIDTH MISMATCH', bad, 'expected', w)
    im=Image.new('RGBA',(w,len(rows)),bg)
    for y,r in enumerate(rows):
        for x,ch in enumerate(r):
            if ch!='.':
                hx=PAL[ch]; im.putpixel((x,y),tuple(int(hx[i:i+2],16) for i in (1,3,5))+(255,))
    im.resize((w*scale,len(rows)*scale),Image.NEAREST).save(name)
    return im
PAL.update({'%':'#5a2f1f','(':'#3d0f2e',')':'#f2918a','[':'#1f1630',']':'#8160a8','{':'#132b38','P':'#fffbef'})
