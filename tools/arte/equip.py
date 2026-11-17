import math
from lib import C, sheet, RAMP
def tape(c,x,y,w,h=2):
    c.rect(x,y,x+w-1,y+h-1,'t'); 
    for k in range(w): c.px(x+k,y,'w' if k%3 else 't')
    c.px(x+w-1,y+h-1,'V')
# ---------------- RECIPIENTES ----------------
def lata():
    c=C(32,24)
    c.cyl(6,6,25,21,['U','u','V','t','w'])
    c.rect(6,10,25,16,'x'); c.rect(6,10,25,10,')'); c.rect(18,10,25,16,'v')   # rótulo
    c.rect(11,12,15,14,'P'); c.px(20,12,'X')
    c.rect(6,6,25,7,'t'); c.rect(7,4,24,5,'V'); c.rect(9,4,22,5,'B')        # borda e terra
    for x in (10,14,19): c.px(x,4,'D')
    c.px(8,17,'U'); c.px(9,18,'U'); c.px(23,8,'U')                         # amassados
    c.px(12,8,'x'); c.px(12,9,'x'); c.px(20,8,'x'); c.px(20,9,'x'); c.px(20,10,'x')   # tinta escorrida
    c.outline(); return c
def vaso_rachado():
    c=C(32,24)
    c.rect(4,4,27,7,'9'); c.rect(4,4,27,4,'&'); c.rect(6,5,25,6,'B')
    for y in range(8,21):
        k=(y-8)//4; x0=6+k; x1=25-k
        for x in range(x0,x1+1):
            t=(x-x0)/max(1,x1-x0); c.px(x,y,'&' if t<0.15 else '9' if t<0.6 else '8' if t<0.85 else '7')
    # rachadura
    for (x,y) in ((18,4),(18,5),(17,6),(17,7),(18,8),(19,9),(18,10),(17,11),(17,12),(18,13)): c.px(x,y,'6')
    c.px(21,4,'.'); c.px(22,4,'.'); c.px(22,5,'.')                          # lasca
    tape(c,13,10,9,2); c.line(14,8,20,14,'t'); c.line(15,8,21,14,'w')     # fita em X
    c.outline(); return c
def vaso_barro():
    c=C(32,24)
    c.rect(4,4,27,7,'9'); c.rect(4,4,27,4,'&'); c.rect(6,5,25,6,'B')
    for x in range(6,26,3): c.px(x,5,'D')
    for y in range(8,21):
        k=(y-8)//4; x0=6+k; x1=25-k
        for x in range(x0,x1+1):
            t=(x-x0)/max(1,x1-x0); c.px(x,y,'&' if t<0.15 else '9' if t<0.6 else '8' if t<0.85 else '7')
    c.rect(5,8,26,8,'7')
    c.outline(); return c
def floreira_caixote():
    c=C(64,28)
    # tábuas de pallet tortas, uma faltando um pedaço, pregos
    c.rect(2,4,61,7,'B'); 
    for x in range(3,61,4): c.px(x,5,'D')
    slats=[(8,13,'3'),(14,19,'4'),(20,25,'3')]
    for (y0,y1,col) in slats:
        c.rect(1,y0,62,y1,col); c.rect(1,y0,62,y0,'4' if col=='3' else '5'); c.rect(1,y1,62,y1,'2')
    c.rect(44,14,62,19,'2'); c.rect(46,15,61,18,'1')   # tábua quebrada (buraco)
    c.rect(1,2,4,25,'2'); c.rect(59,2,62,25,'2'); c.rect(1,2,1,25,'3')
    c.rect(1,2,62,3,'3'); c.rect(1,2,62,2,'4')
    for (x,y) in ((2,10),(2,16),(2,22),(60,10),(60,22),(30,10)): c.px(x,y,'u')
    c.line(30,9,33,8,'u')   # prego torto
    tape(c,40,8,7,2)
    c.outline(); return c
def bancada():
    c=C(96,40)
    for lx in (4,88): c.rect(lx,14,lx+3,37,'U'); c.rect(lx+1,14,lx+1,37,'t')
    c.rect(5,30,90,31,'U'); c.rect(5,30,90,30,'u')
    c.rect(0,0,95,15,'V'); c.rect(0,0,95,1,'w'); c.rect(2,2,93,6,'B')
    for x in range(3,93,4): c.px(x,4,'D')
    c.rect(0,7,95,15,'u'); c.rect(0,7,95,7,'t'); c.rect(0,15,95,15,'U')
    for i in range(5): c.rect(8+i*19,9,12+i*19,11,'w')
    c.outline(); return c
def rack():
    c=C(64,76)
    for lx in (0,60): c.rect(lx,0,lx+3,75,'u'); c.rect(lx+1,0,lx+1,75,'w')
    for ty in (32,70):
        ly=ty-28
        c.rect(3,ly,60,ly+2,'U'); c.rect(4,ly+1,59,ly+1,'Z')
        for y in range(ly+3,ty-4):
            for x in range(5,59):
                if (x+y)%2==0 and y<ly+8: c.px(x,y,']')
        c.rect(3,ty,60,ty+5,'t'); c.rect(4,ty+1,59,ty+3,'P'); c.rect(4,ty+4,59,ty+4,'V')
        for i in range(4): c.rect(9+i*14,ty+1,13+i*14,ty+2,'u')
    c.rect(56,40,58,68,'H'); c.rect(57,40,57,68,'I')  # cano de água
    c.outline(); return c
def torre():
    c=C(64,100)
    # câmara de vidro cilíndrica com 4 anéis de cultivo
    c.rect(4,90,59,99,'U'); c.rect(4,90,59,91,'u'); c.rect(6,94,57,95,'I')
    c.rect(4,0,59,9,'U'); c.rect(4,8,59,9,'u'); c.rect(8,4,55,5,'J')
    for y in range(10,90):
        for x in range(6,58):
            t=(x-6)/52
            c.px(x,y,'J' if t<0.08 else 'I' if t<0.18 else 'H' if t<0.7 else 'F' if t<0.9 else '{')
    for y in range(10,90,2):
        for x in range(10,54,7): 
            if (x+y)%4==0: c.px(x,y,'I')
    for ty in (26,46,66,86):
        c.rect(14,ty-2,49,ty,'t'); c.rect(14,ty-2,49,ty-2,'P')
    c.rect(31,10,32,89,'u')
    c.rect(7,12,8,86,'P')  # reflexo do vidro
    c.outline(); return c
# ---------------- EQUIPAMENTOS (32x32) ----------------
def regador():          # garrafa PET de cabeça pra baixo + fita + mangueirinha
    c=C(32,32)
    c.rect(11,2,20,20,'S'); c.rect(11,2,12,20,'P'); c.rect(18,2,20,20,'s')
    c.rect(13,21,18,24,'s'); c.rect(14,25,17,26,'x')       # gargalo + tampa
    c.rect(11,6,20,9,'J'); c.rect(11,6,12,9,'P')           # água
    tape(c,10,13,12,3)
    c.line(16,27,16,29,'H'); c.line(16,29,24,30,'H'); c.line(16,28,24,29,'I')
    c.rect(8,0,23,1,'2'); c.line(9,1,11,4,'2'); c.line(22,1,20,4,'2')  # suporte de arame
    c.outline(); c.px(25,31,'J'); return c
def tesoura():
    c=C(32,32)
    c.line(6,6,22,22,'t'); c.line(7,6,23,22,'w'); c.line(6,7,22,23,'V')
    c.line(22,6,8,22,'V'); c.line(23,6,9,22,'t')
    c.sphere(16,15,2,2,['U','u','V','t'])
    for (x,y) in ((6,24),(22,24)):
        c.sphere(x+2,y+2,4,3,['(','X','v','x'])
    tape(c,4,25,6,2); c.px(10,9,'%'); c.px(11,10,'%')   # ferrugem
    c.outline(); return c
def ventilador():
    c=C(32,32)
    c.rect(14,22,17,27,'u'); c.rect(9,27,22,30,'U'); c.rect(9,27,22,27,'V')
    for y in range(2,23):
        for x in range(5,27):
            d=math.hypot(x-15.5,y-12)
            if d<=10.5:
                if d>9.4: c.px(x,y,'V')
                elif (round(math.atan2(y-12,x-15.5)*6/math.pi))%2==0 and d>3: c.px(x,y,'t')
                else: c.px(x,y,'U' if d>3 else 'u')
    c.line(8,6,13,16,'V')                 # grade torta
    tape(c,20,4,6,2); tape(c,6,17,5,2)
    c.outline(); return c
def termometro():
    c=C(32,32)
    c.rect(9,3,22,28,'3'); c.rect(9,3,22,3,'4'); c.rect(22,3,22,28,'2')   # tábua
    c.rect(13,6,18,24,'P'); c.rect(15,8,16,22,'t'); c.rect(15,14,16,22,'x'); c.sphere(15.5,24,2.5,2.5,['X','v','x',')'])
    for y in range(8,22,3): c.px(13,y,'U')
    tape(c,11,5,10,2); tape(c,11,26,10,2)
    c.outline(); return c
def fertilizante():
    c=C(32,32)
    for y in range(6,30):
        w=9+min(2,(y-6)//3)
        for x in range(16-w,16+w):
            t=(x-(16-w))/(2*w); c.px(x,y,'5' if t<0.2 else '4' if t<0.7 else '3')
    c.rect(8,3,23,6,'4'); c.line(8,3,23,4,'5'); c.line(10,6,22,6,'3')     # dobra
    c.rect(10,13,22,21,'P'); c.rect(11,15,21,15,'X'); c.rect(11,18,18,18,'X')   # rótulo à mão
    tape(c,6,24,8,2)
    c.px(23,25,'2'); c.px(24,26,'2')     # rasgo
    c.outline(); return c
def lampada_uv():
    c=C(32,32)
    c.line(16,0,16,6,'a'); c.px(16,3,'t'); c.px(17,3,'t')      # fio emendado
    for y in range(7,16):
        w=4+(y-7)*1.2
        for x in range(int(16-w),int(16+w)+1): 
            c.px(x,y,'w' if (x+y)%3==0 else 't' if x<16 else 'V')   # refletor de papel alumínio
    c.rect(14,6,18,8,'U')
    c.sphere(16,19,4,4,[']','N','P','P'])
    for (x,y) in ((9,24),(16,27),(23,24),(6,20),(26,20)): c.px(x,y,']')
    c.outline(); return c
def medidor_ph():
    c=C(32,32)
    c.rect(12,3,19,24,'U'); c.rect(12,3,13,24,'u'); c.rect(19,3,19,24,'T')
    c.rect(13,6,18,12,'{'); c.rect(14,7,17,11,'I'); c.px(15,9,'{'); c.px(16,9,'{')
    c.rect(14,15,17,16,'x'); c.rect(14,19,17,20,'n')
    c.rect(15,25,16,30,'t'); c.px(15,30,'w')
    c.outline(); return c
def mini_estufa():
    c=C(32,32)
    c.rect(4,8,27,29,'S'); c.rect(4,8,8,29,'P'); c.rect(23,8,27,29,'s')
    c.line(4,8,16,1,'t'); c.line(27,8,16,1,'t')
    for y in range(2,8):
        for x in range(16-(y-1)*2,16+(y-1)*2): c.px(x,y,'S')
    c.line(16,8,16,28,'V'); c.px(16,15,'u'); c.px(16,22,'u')            # zíper
    c.bush([(12,24,3),(20,24,3)],['l','L','m','n'])
    c.rect(4,29,27,30,'U')
    c.outline(); return c
def drone():
    c=C(32,32)
    for (x,y) in ((5,8),(26,8),(5,20),(26,20)):
        c.rect(x-4,y,x+4,y,'V'); c.px(x,y-1,'U')
    c.line(5,9,26,20,'U'); c.line(26,9,5,20,'U')
    c.sphere(15.5,14,6,4,['T','U','u','V','t'])
    c.px(13,15,'x'); c.sphere(15.5,18,2,1.5,['{','F','H','I'])
    c.outline(); c.px(20,12,'P'); return c
def filtro_carbono():
    c=C(32,32)
    c.rect(15,0,16,4,'U')
    c.cyl(7,5,24,29,['T','U','u','V','t'])
    for y in range(8,28,3): c.rect(8,y,23,y,'U')
    c.rect(7,5,24,6,'t'); c.rect(7,28,24,29,'u')
    c.rect(11,14,20,18,'P'); c.rect(12,16,19,16,'a')
    c.outline(); return c
def led():
    c=C(32,32)
    c.line(4,0,6,4,'U'); c.line(27,0,25,4,'U')
    c.rect(2,4,29,14,'U'); c.rect(2,4,29,5,'u')
    for y in (7,10,13):
        for x in range(4,28,2): c.px(x,y,'x' if (x//2)%3==0 else 's' if (x//2)%3==1 else 'P')
    for y in range(15,30):
        for x in range(2+ (y-15)//3,30-(y-15)//3):
            if (x+y)%2==0 and y<22: c.px(x,y,')' if x<12 else ']' if x>20 else 'Z')
    c.outline(); return c
def hidroponico():
    c=C(32,32)
    c.box(3,12,28,29,4,['T','U','u','V','t','w'])
    c.rect(5,13,26,14,'H'); c.rect(5,13,12,13,'J')                      # água
    c.rect(20,18,25,24,'u'); c.rect(21,19,24,23,'H'); c.px(22,20,'J')    # bomba
    c.line(23,17,23,6,'P'); c.line(23,6,10,6,'P'); c.line(10,6,10,12,'P')   # tubo
    c.line(24,17,24,7,'t'); 
    for x in (8,14,19): c.sphere(x,10,2,2,['l','L','m','n'])
    c.outline(); return c
def co2():
    c=C(32,32)
    for x0 in (5,17):
        c.cyl(x0,8,x0+9,30,['T','U','u','V','t']) 
        c.rect(x0+3,4,x0+6,7,'u'); c.rect(x0+2,13,x0+7,16,'P'); c.rect(x0+3,14,x0+6,15,'F')
    c.sphere(15.5,4,3,3,['%','G','O','Y']); c.px(15,4,'a'); c.px(16,3,'a')   # manômetro
    c.outline(); return c
def cameras():
    c=C(32,32)
    c.rect(3,4,7,12,'U'); c.rect(4,5,5,11,'u')
    c.line(7,8,12,11,'u'); c.line(7,9,12,12,'U')
    c.rect(11,8,27,16,'t'); c.rect(11,8,27,9,'w'); c.rect(11,16,27,16,'V')
    c.rect(25,9,28,15,'U'); c.sphere(27,12,2,2,['[','K','N',']'])
    c.px(14,11,'x'); c.px(15,11,'('); 
    c.outline(); return c
def osmose():
    c=C(32,32)
    c.rect(2,3,29,7,'U'); c.rect(2,3,29,3,'u')
    for i,x0 in enumerate((4,13,22)):
        c.cyl(x0,8,x0+6,28,['F','H','I','J','P'] if i<2 else ['T','U','u','V','t'])
        c.rect(x0,8,x0+6,9,'P')
    c.line(8,29,26,29,'t')
    c.outline(); return c
def controlador_ia():
    c=C(32,32)
    c.box(4,14,27,30,3,['T','U','u','V','t','w'])
    c.rect(7,2,24,14,'U'); c.rect(8,3,23,13,'{')
    c.sphere(15.5,8,4,4,['F','H','I','J']); c.px(14,7,'{'); c.px(17,7,'{'); c.line(14,10,17,10,'{')   # rosto da IA
    for x in range(9,23,3): c.px(x,22,'J' if x%2 else 'x')
    c.rect(9,25,22,26,'F')
    c.outline(); return c
def bunker():
    c=C(32,32)
    c.sphere(15.5,17,13,12,['T','U','u','V','t'])
    c.sphere(15.5,17,9,8,['U','u','V','t'])
    for a in range(0,360,45):
        x=15.5+11*math.cos(math.radians(a)); y=17+10*math.sin(math.radians(a)); c.px(x,y,'T')
    c.rect(13,15,18,19,'O'); c.rect(14,16,17,18,'Y')
    for k in range(0,26,4):
        c.rect(3+k,29,4+k,30,'Y'); c.rect(5+k,29,6+k,30,'a')
    c.outline(); return c
def lab_genetica():
    c=C(32,32)
    c.box(3,22,28,30,3,['T','U','u','V','t','w'])
    c.rect(10,3,21,22,'S'); c.rect(10,3,11,22,'P')
    for y in range(4,21):
        a=math.sin(y/2.2)*4
        c.px(15.5+a,y,'J'); c.px(15.5-a,y,')')
        if y%3==0: c.line(15.5-a,y,15.5+a,y,'I')
    c.rect(9,1,22,3,'u'); c.rect(9,1,22,1,'t')
    c.px(6,26,'J'); c.px(8,26,'x'); c.px(24,26,'n')
    c.outline(); return c
CONT=[('lata_de_tinta',lata),('vaso_rachado',vaso_rachado),('vaso_de_barro',vaso_barro)]
EQ=[('regador_automatico',regador),('tesoura_de_poda',tesoura),('ventilador_silencioso',ventilador),('termometro_digital',termometro),
('fertilizante_el_secreto',fertilizante),('lampada_uv',lampada_uv),('medidor_de_ph',medidor_ph),('mini_estufa',mini_estufa),
('drone',drone),('filtro_de_carbono',filtro_carbono),('painel_led',led),('sistema_hidroponico',hidroponico),('gerador_co2',co2),
('cameras_4k',cameras),('osmose_reversa',osmose),('controlador_ia',controlador_ia),('kit_bunker',bunker),('lab_genetica',lab_genetica)]
BIG=[('floreira_caixote',floreira_caixote),('bancada',bancada),('rack_hidroponico',rack),('torre_vertical',torre)]
if __name__=='__main__':
    sheet([f() for _,f in EQ],9,32,32,'equipamentos.png',scale=5)
    sheet([f() for _,f in CONT],3,32,24,'vasos.png',scale=6)
    big=C(64+96+64+64+40,100)
    x=0
    for n,f in BIG:
        o=f(); big.paste(o,x,100-o.h); x+=o.w+10
    from pal import render
    render(big.rows(),'modulos.png',scale=3,bg=(58,52,72,255))
