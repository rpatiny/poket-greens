import math, random
from lib import C, sheet, RAMP
W,H=32,40; BX,BY=16,39
def stem(c,x0,y0,x1,y1,col='L',col2='l'):
    c.line(x0,y0,x1,y1,col); c.line(x0+1,y0,x1+1,y1,col2)
def sparkle(c,x,y,col='Z'):
    c.px(x,y,col); c.px(x-1,y,'Y'); c.px(x+1,y,'Y'); c.px(x,y-1,'Y'); c.px(x,y+1,'Y')

def alface():
    c=C(W,H)
    # roseta de folhas onduladas claras
    c.bush([(9,32,6),(23,32,6),(16,27,7),(11,24,5),(21,24,5),(16,32,7)],['l','L','m','n','o','o'])
    for x,y in ((10,28),(14,24),(19,27),(22,31),(13,33)): c.px(x,y,'m'); c.px(x+1,y+1,'m')
    c.outline(); sparkle(c,26,17); c.px(6,20,'Z'); return c
def hortela():
    c=C(W,H)
    for (x1,y1) in ((9,14),(16,8),(23,13),(12,20),(21,19)):
        stem(c,BX,BY,x1,y1,'L','l')
    for (x,y,a) in ((9,14,-2.5),(9,14,-0.6),(16,8,-2.2),(16,8,-0.9),(23,13,-2.4),(23,13,-0.5),
                    (12,20,-2.7),(12,20,-0.3),(21,19,-2.8),(21,19,-0.4),(14,27,-2.6),(19,27,-0.5),(16,30,-1.6)):
        c.leaf(x,y,a,6,2.4,['k','l','L','m','n','n'],lo=1)
    c.outline(); return c
def manjericao():
    c=C(W,H)
    stem(c,BX,BY,BX,20)
    for (x,y,a,L) in ((16,14,-1.57,7),(16,18,-2.6,8),(16,18,-0.5,8),(15,25,-2.9,9),(17,25,-0.25,9),(15,31,-2.7,7),(17,31,-0.4,7),(16,22,-1.57,6)):
        c.leaf(x,y,a,L,3.3,['l','L','m','n','o','o'],lo=1)
    c.outline(); c.px(9,10,'Y'); c.px(10,9,'Z'); c.px(24,12,'Y'); return c
def tomate():
    c=C(W,H)
    c.bush([(10,24,6),(22,22,6),(16,15,7),(16,27,6)],['k','l','L','m','n','n'])
    for (x,y) in ((9,27),(20,26),(15,19),(23,17)):
        c.sphere(x,y,3,3,['(','X','v','x',')','Y'])
    c.outline()
    for (x,y) in ((8,26),(19,25),(14,18),(22,16)): c.px(x,y,'Z')
    # brilho atômico
    for (x,y) in ((5,15),(27,24),(25,10),(7,33)): c.px(x,y,'J'); 
    return c
def reaper():
    c=C(W,H)
    c.bush([(11,24,6),(21,23,6),(16,16,6)],['k','l','L','m','n','n'])
    for (x,y) in ((9,29),(17,29),(23,27),(13,20)):
        for k in range(7):
            w=2 if k<4 else 1
            for d in range(-w+1,w+1): c.px(x+d,y+k,'v' if d<=0 else 'X')
        c.px(x,y,'x'); c.px(x-1,y+1,')'); c.px(x+1,y+7,'X'); c.px(x+2,y+8,'X')
        c.px(x,y-1,'L')
    c.outline(); return c
def esporos():
    c=C(W,H)
    for (x,top,rx,ry,h,ram) in ((10,27,6,3,9,'teal'),(21,22,7,4,14,'plum'),(16,30,4,2,6,'teal')):
        c.rect(x-1,top,x+1,top+h,'t'); c.px(x+1,top+2,'V'); 
        c.sphere(x,top,rx,ry,RAMP[ram])
        for d in (-3,0,3): c.px(x+d,top-1 if d else top-2,'w')
    c.outline()
    for (x,y) in ((6,12),(26,9),(14,6),(28,16),(4,20)): c.px(x,y,'J')
    return c
def lavanda():
    c=C(W,H)
    for (x1,y1) in ((8,10),(13,6),(19,7),(24,11),(11,15),(21,14)):
        c.line(BX,BY,x1,y1+6,'L')
        for k in range(7):
            c.px(x1,y1+k,'N' if k%2 else ']'); c.px(x1+1,y1+k,'K' if k%2 else 'N')
        c.px(x1,y1-1,']')
    c.leaf(16,34,-2.9,8,2,'leaf'); c.leaf(16,34,-0.2,8,2,'leaf')
    c.outline()
    # espiral hipnótica
    for (x,y) in ((27,4),(28,5),(27,6),(26,5)): c.px(x,y,']')
    return c
def cacto():
    c=C(W,H)
    c.cyl(12,10,19,39,['k','l','L','m','n'])
    for x in (14,17): 
        for y in range(11,39,2): c.px(x,y,'l')
    c.cyl(6,18,9,27,['k','l','L','m','n']); c.rect(9,25,12,27,'L')
    c.cyl(22,14,25,22,['k','l','L','m','n']); c.rect(19,20,22,22,'m')
    for (x,y) in ((12,14),(19,20),(13,30),(18,33),(7,20),(24,16)): c.px(x,y,'w')
    c.stamp(14,7,[".PPP.","PP)PP",".PPP."]) 
    c.outline(); return c
def lotus():
    c=C(W,H)
    c.sphere(9,34,7,3,['{','F','H','I'] ); c.sphere(24,35,6,3,['{','F','H','I'])
    stem(c,16,36,16,18,'H','F')
    petals=[(16,8,2.2,8),(10,11,2.2,7),(22,11,2.2,7),(7,16,2,6),(25,16,2,6)]
    for (x,y,rx,ry) in petals: c.sphere(x,y+4,rx+1.5,ry,['p','q','r','s','S'])
    c.sphere(16,17,4,2,['G','O','Y','Z'])
    c.outline(); return c
def ayahuasca():
    c=C(W,H)
    c.rect(15,6,16,39,'2'); c.rect(17,6,17,39,'1'); c.px(15,6,'3')
    for k in range(0,34):
        y=38-k; x=16+round(6*math.sin(k/3.2))
        c.px(x,y,'m'); c.px(x+1,y,'L')
        if k%5==2: c.leaf(x,y,-2.6 if math.sin(k/3.2)<0 else -0.5,6,2.4,'leaf',lo=1)
    c.outline(); return c
def orquidea():
    c=C(W,H)
    for (x,y,k) in ((10,34,0),(14,35,1),(19,34,2),(23,33,3)):
        c.line(16,32,x,y+4,'t')
    stem(c,16,32,18,14,'L','l')
    def flower(x,y):
        c.stamp(x-5,y-3,[
        "..PP.....PP..",
        ".PwwP...PwwP.",
        "..PwwP.PwwP..",
        "....PPPPP....",
        ".....P)P.....",
        "....PtPtP....",
        "...Pt...tP...",
        "..Pt.....tP..",
        ".t.........t."])
    flower(18,11); flower(10,20)
    c.outline('u'); return c
def trufa():
    c=C(W,H)
    for (x,y,r) in ((10,34,4),(19,33,5),(15,28,4),(24,36,3)):
        c.blob(x,y,r,['[','K','U','u'],seed=x,bump=0.25,lobes=7)
    for (x,y) in ((9,32),(18,31),(14,27),(20,34)): c.px(x,y,'N')
    c.outline()
    for (x,y) in ((6,22),(25,24),(17,18),(29,30)): c.px(x,y,']'); 
    c.px(17,17,'J'); return c
def mandragora():
    c=C(W,H)
    for a in (-2.4,-2.0,-1.57,-1.15,-0.75):
        c.leaf(16,26,a,13,3,'leaf',lo=1)
    # raiz com rosto saindo da terra
    c.sphere(16,33,6,5,['B','D','E','d','e'])
    c.px(14,32,'a'); c.px(18,32,'a'); c.px(15,35,'a'); c.px(16,35,'a'); c.px(17,35,'a')
    c.px(13,33,'*'); c.px(19,33,'*')
    c.outline(); return c
def bonsai():
    c=C(W,H)
    # tronco retorcido
    pts=[(16,39),(15,35),(13,31),(14,27),(17,24),(19,20),(17,16)]
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        c.line(x0-1,y0,x1-1,y1,'3'); c.line(x0,y0,x1,y1,'2'); c.line(x0+1,y0,x1+1,y1,'1')
    c.line(14,27,8,23,'2'); c.line(19,20,25,18,'2')
    c.bush([(7,20,4),(11,19,4)],['l','L','m','n','o'])
    c.bush([(23,16,4),(27,17,3)],['l','L','m','n','o'])
    c.bush([(13,11,5),(19,10,5),(16,8,4)],['l','L','m','n','o'])
    c.outline(); return c
def rafflesia():
    c=C(W,H)
    for (x,y) in ((8,28),(24,28),(10,36),(22,36),(16,24)):
        c.sphere(x,y,6,4,['(','X','v','x'])
        for (dx,dy) in ((-2,-1),(1,1),(2,-2)): c.px(x+dx,y+dy,')')
    c.sphere(16,31,5,3,['[','(','X','v'])
    c.rect(13,30,19,31,'('); 
    c.outline(); return c
def aurora():
    c=C(W,H)
    stem(c,16,39,16,26,'H','F')
    cols=[['{','F','H','I','J'],['[','K','N',']'],['{','F','H','I','J'],['[','K','N',']'],['{','F','H','I','J']]
    for i,a in enumerate((-2.5,-2.1,-1.57,-1.05,-0.6)):
        c.leaf(16,27,a,14,3.2,cols[i],lo=0)
    c.outline()
    for (x,y) in ((5,10),(27,8),(16,3),(9,4),(23,3)): c.px(x,y,'J')
    return c
def eden():
    c=C(W,H)
    stem(c,16,39,16,22,'2','1')
    c.bush([(10,17,6),(22,16,6),(16,11,7),(16,19,6)],['l','L','m','n','o'])
    c.sphere(19,20,3.5,3.5,['%','G','O','Y','Z'])
    c.px(19,16,'2'); c.px(20,16,'m')
    c.outline(); c.px(18,19,'P'); 
    for (x,y) in ((25,24),(6,9),(27,12)): c.px(x,y,'Z')
    return c
def yggdrasil():
    c=C(W,H)
    c.rect(14,24,18,39,'3'); c.rect(17,24,18,39,'2'); c.rect(14,24,14,39,'4')
    for (x,y) in ((12,38),(20,38),(10,39),(22,39)): c.px(x,y,'2')
    c.line(13,37,9,39,'2'); c.line(19,37,23,39,'2')
    c.bush([(7,18,6),(25,18,6),(11,11,7),(21,11,7),(16,6,6),(16,17,7)],['L','m','n','o','Z'])
    c.outline()
    for (x,y) in ((15,30),(16,33),(15,27)): c.px(x,y,'J')
    for (x,y) in ((4,6),(28,4),(30,22),(2,24)): c.px(x,y,'Z')
    return c
def broto():
    c=C(W,H)
    c.stamp(12,31,["..a.....",".ana.aa.","anoaanoa",".annmaa.","..aama..","...aLa..","...aLa..","...aLa.."])
    return c
def muda():
    c=C(W,H)
    stem(c,16,39,16,26)
    for (a,L) in ((-2.6,7),(-0.5,7),(-1.9,6),(-1.2,6)): c.leaf(16,30,a,L,2.6,'leaf',lo=1)
    c.outline(); return c
PL=[('broto',broto),('muda',muda),('alface_mistica',alface),('hortela_selvagem',hortela),('manjericao_do_olimpo',manjericao),
('tomate_atomico',tomate),('carolina_reaper',reaper),('esporos_especiais',esporos),('lavanda_hipnotica',lavanda),
('cacto_san_pedro',cacto),('lotus_azul',lotus),('cipo_ayahuasca',ayahuasca),('orquidea_fantasma',orquidea),
('trufa_negra',trufa),('mandragora',mandragora),('bonsai_milenar',bonsai),('rafflesia',rafflesia),('aurora_boreal',aurora),
('fruto_do_eden',eden),('broto_de_yggdrasil',yggdrasil)]
if __name__=='__main__':
    cells=[f() for _,f in PL]
    sheet(cells,10,W,H,'plantas.png',scale=5)
