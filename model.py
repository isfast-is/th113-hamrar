# Þ113 Hamrar — Python replica of the cost estimate and rent model (used for scenarios/sensitivity + verification)
import math
BASE = dict(
    A_haed_gross=1368.5, stair_m2=48.0, N_haed=3, A_kj=328.5, A_teng=44.0, ext_stairs=22.0, A_paid=4334.0, N_mod=66, N_rymi=66,
    BVT_H=1.06,          # Hamranes EAC (BVT maí 2025 ~200) -> verðlag framkvæmda 2027
    VBC_rate=317.0,      # þ.kr/m² eininga án VSK, Akureyrar-tilboð VBC apr. 2026 (IS-10 24,7 m.kr / ~76 m², m. BANO), EUR 145
    VBC_ti=39.0,         # þ.kr/m² flutningur+uppsetning (Akureyri 233 m.kr / 5.963 m²)
    VBC_disc=0.0, VBC_eng=40.0, EURISK=145.0,
    IF_fee=0.06,
    kj_rate=None,        # computed bottom-up
    teng_rate=400.0, teng_lyfting=12.0, A2_inngrip=60.0, live_site=45.0,
    gatn=38.0,           # þ.kr/m² gatnagerðargjald (Hfj 2025: 36,3; Mosfellsbær 496/2017 - staðfesta)
    bbm_rate=616.0,      # brunabótamat þ.kr/m² (HMS vinnumat Hamranes)
    fmat_rate=309.0,     # fasteignamat húss þ.kr/m²
    lodmat=150.0,        # lóðarmat m.kr (áætlun; leigulóð)
    LTC=0.65, cl_rate=0.102, cl_fee=0.002, build_months=20, draw_factor=0.5,
    rent=5650.0, vat=0.24, infl=0.04, uplift_months=20, yld=0.057,
    fsk=0.0132, vatn=0.0017, ins=0.0012, m1=0.001, m2=0.002, m3=0.003, mgmt=0.01, other=1.0,
    bond_base=0.0286, bond_margin=0.0100, LTV=0.677, bond_cost=0.005, bond_years=25,
    tax=0.20, depr=0.03, sale_cost=0.005, sale_tax_share=0.5, disc_rate=0.09,
)
# Hamranes EAC per-m² rates án VSK (þ.kr/m² of 6.730 m²), source: Hamranes - Áætlun EAC 2025.xlsx Samantekt
HAM = dict(ch0=29.84, ch1=11.30, ch2_fp=68.7, ch3=24.79, ch4=49.52, ch5=38.04, ch7=40.82, ch8=15.74, hönnun_ark=26.6, umsysla=3.3)

def lines(p):
    p['A_haed'] = p.get('A_haed_override') or (p['A_haed_gross']-p['stair_m2'])
    A_mod = p['A_haed']*p['N_haed']; A_built = A_mod+p['A_kj']+p['A_teng']; fp = p['A_haed']
    H = p['BVT_H']; L=[]
    def add(ch,nr,name,qty,unit,rate,src,why):
        if unit=='heild': rate=rate*1000.0  # lump sums entered in m.kr -> þ.kr
        L.append(dict(ch=ch,nr=nr,name=name,qty=qty,unit=unit,rate=rate,src=src,why=why))
    # 0
    add(0,'0.1','Aðstaða, umsjón, byggingarstjórn, tryggingar, þrif (Hamranes-hlutfall)',A_built,'m²',HAM['ch0']*H,'Hamranes EAC kafli 0: 200,8 m.kr / 6.730 m² = 29,8 þ/m² án VSK','Sama verktilhögun og á Hamranesi (ÍF stýriverktaka, Hnit eftirlit). Verðbætt ×1,06 til 2027. Styttri aðstöðutími eininga vegur á móti lengri steypufasa kjallara.')
    add(0,'0.2','Álag vegna framkvæmda við starfandi hjúkrunarheimili (girðingar, hljóðvist, öryggi, áfangar)',1,'heild',p['live_site'],'Kröfulýsing Þ113 (rekstur Hamra setur skorður á vinnutíma/ónæði); mat ÍF','Ekki til staðar á Hamranesi. Lump sum 45 m.kr ≈ 1,2% af framkvæmdakostnaði.')
    # 1 jarðvinna
    add(1,'1.1','Laus jarðvegur, uppgröftur og fjarlæging',3000,'m³',3.5,'Akureyrar-áætlun 30.4.2026: 3.500 kr/m³','Byggingarreitur ~1.500 m² × ~2,0 m meðaldýpi á klöpp (GIR Verkís: klöpp 0,4–4,6 m).')
    add(1,'1.2','Losun á klöpp með fleygun (ekki sprengt við 2A), kjallari',2000,'m³',9.5,'Akureyri 5.750 kr/m³ opið svæði; +65% fyrir fleygun við starfandi hús','Kjallari 800 m² gröftur × ~2,5 m í klöpp. Sprengingar ekki heimilar við hlið hjúkrunarheimilis.')
    add(1,'1.3','Losun á klöpp undir sökklum og lögnum utan kjallara',350,'m³',9.5,'Sama eining og 1.2','~700 m² × 0,5 m.')
    add(1,'1.4','Hreinsun á klöpp',1500,'m²',1.75,'Akureyri 1.750 kr/m²','Allur byggingarreitur.')
    add(1,'1.5','Fylling innan sökkla og undir plötu',1000,'m³',3.75,'Akureyri 3.750 kr/m³','')
    add(1,'1.6','Frostfrí fylling utan með sökklum og á lóð',2500,'m³',3.5,'Akureyri 3.500 kr/m³','Lóð hallar; ný þjónustuaðkoma frá Skeiðholti.')
    add(1,'1.7','Drenmöl og drenlagnir með kjallara (grunnvatn getur staðið hátt)',1,'heild',7.0,'Akureyri 7.500 kr/m³ + 120 lm dren; GIR Verkís um grunnvatn','Lekavarnir kjallara í klöpp.')
    add(1,'1.8','Gröftur, söndun og fylling lagnaskurða; brunnar',1,'heild',4.5,'Akureyri: 8.000+3.000 kr/m, 150 þ/brunn','~300 m + 6 brunnar.')
    add(1,'1.9','Tímagjald og aukavinna í jarðvinnu',1,'heild',6.0,'Akureyri/Hamranes viðmið ~10% af jarðvinnu','Misgengi og bergeiningar (GIR) — endurmat klappar eftir hreinsun.')
    # 2 burðarvirki — kjallari bottom-up
    A_kj=p['A_kj']
    add(2,'2.1','Kjallari: botnplata — mót, einangrun, steypa C25/30 0,2 m, járn 150 kg/m³, vélslípun',A_kj,'m²',(14.5+6.0+0.2*55+0.2*150*0.6+3.5),'Akureyri einingaverð: plötumót 14.500, einangrun 6.000, steypa 55.000/m³, járn 600/kg, slípun 3.500','≈ 53,5 þ/m². Steypt beint á klöpp.')
    add(2,'2.2','Kjallari: útveggir 0,25 m, h 3,4 m — mót, steypa, járn 120 kg/m³',round(A_kj**0.5*4*1.05,0),'lm',(3.4*2*21+3.4*0.25*55+3.4*0.25*120*0.6),'Akureyri: veggmót 21.000/m², steypa 55.000/m³, járn 600/kg','≈ 115 lm ummál (750 m² ≈ 27×27 m + 5%). 204,7 þ/lm.')
    add(2,'2.3','Kjallari: innri burðarveggir og súlur',1,'heild',19.0,'Akureyri veggir C30/37 + súlur','~200 m² veggur + 20 súlur.')
    add(2,'2.4','Kjallari: loftplata (gólf 1. hæðar undir einingum) 0,25 m — mót, steypa, járn 150 kg/m³',A_kj,'m²',(14.5+0.25*55+0.25*150*0.6),'Akureyri einingaverð','≈ 50,8 þ/m². Einingar standa á plötunni; stálplattar í lið 2.5.')
    add(2,'2.5','Sökklar og undirstöður undir einingum utan kjallara (Hamranes-hlutfall á grunnflöt)',max(fp-A_kj,0),'m²',HAM['ch2_fp']*H,'Hamranes EAC kafli 2: 92,5 m.kr / 1.346 m² grunnflöt = 68,7 þ/m²','Sökklar á klöpp, stálplattar, stál svalir, stigar. Verðbætt ×1,06.')
    add(2,'2.6','Tengigangur, 2 hæðir — burðarvirki, klæðning og innanhúss, allt í einu lagi',p['A_teng'],'m²',p['teng_rate'],'Mat ÍF; Húsavíkur-tengigangur (172 m²/hæð) í áætlun 2025; ágúst-mat 250–330 m.kr f. tengigang + 2A','Steypt/stál, gler. 480 þ/m² án VSK fyrir fullbúið.')
    add(2,'2.7','Burðarvirki tengigangs hannað fyrir hækkun um eina hæð síðar',1,'heild',p['teng_lyfting'],'Samkomulag um byggingarrétt 10.7.2026, gr. um framtíðarheimild 2A','Þyngra þak og undirstöður.')
    add(2,'2.8','Inngrip í 2A: flóttastigi fjarlægður, neyðarútgangar aflagðir, brunahönnun/rýmingaráætlun, klæðningar samræmdar, THG-samráð',1,'heild',p['A2_inngrip'],'Kröfulýsing Þ113 og samkomulag um byggingarrétt — á kostnað bjóðanda','Lump sum; hönnunarhluti í B-1.')
    # 3,4,5
    add(3,'3.1','Lagnir og loftræsing utan eininga (Hamranes-hlutfall)',A_built,'m²',HAM['ch3']*H,'Hamranes EAC kafli 3: 166,8 m.kr / 6.730 m² = 24,8 þ/m²','Sama kerfishönnun (Lagnatækni/L&L). Einingar koma með lögnum.')
    add(3,'3.2','Viðbót: eldhús-, sjúkraþjálfunar- og tæknilagnir í kjallara',1,'heild',15.0,'Mat; Hamranes 1. hæð','Miðlæg rými í kjallara í stað 1. hæðar.')
    add(4,'4.1','Raflagnir, lýsing, öryggis- og hússtjórnarkerfi (Hamranes-hlutfall)',A_built,'m²',HAM['ch4']*H,'Hamranes EAC kafli 4: 333,2 m.kr / 6.730 m² = 49,5 þ/m²','Sömu kerfi og kröfulýsing (sama FSRE-sniðmát).')
    add(5,'5.1','Frágangur innanhúss utan eininga: kjallari, stigahús, tengingar (Hamranes-hlutfall)',A_built,'m²',HAM['ch5']*H,'Hamranes EAC kafli 5: 256,0 m.kr / 6.730 m² = 38,0 þ/m²','Hamranes-hlutfallið innihélt fullfrágengna 1. hæð (1.385 m² steypt) — hér kjallari 750 m².')
    # 6 VBC
    add(6,'6.1','VBC-einingar, 66 stk (22/hæð, Hamranes IS-6x), fullbúnar með BANO — Akureyrar-verð',A_mod,'m²',p['VBC_rate']*(1-p['VBC_disc']),'VBC tilboð f. Akureyri (apr. 2026): IS-10 24,70 m.kr, IS-13 21,86 m.kr án VSK, EUR 145 → 1.893 m.kr / 5.963 m² = 317 þ/m² m. BANO. Hamranes samningur: 2.097,5 m.kr / 6.730 m² = 312 þ/m² án BANO (+13,7 BANO)','Forsenda GT 4.9.2026: sömu verð og VBC gaf fyrir Akureyri. Hamranes-raun m. aukaverkum var 388 þ/m² — Akureyrar-grunnurinn er 8% lægri af því aukaverk (CO-6…CO-10) eru inni í verðinu.')
    add(6,'6.2','Flutningur (Gdynia–Hafnarfjörður) og uppsetning eininga',A_mod,'m²',p['VBC_ti'],'Akureyri: 78 × 2,175 m.kr flutningur + 0,811 m.kr uppsetning = 233 m.kr / 5.963 m² = 39 þ/m²','Hamranes: 89,7 uppsetning + 231 flutningur = 320,7 / 6.730 = 47,7 þ/m².')
    add(6,'6.3','VBC hönnunar- og verkfræðiþóknun (endurtekin hönnun)',1,'heild',p['VBC_eng'],'Hamranes B-5: 97 m.kr fyrir frumhönnun','Endurnýting IS-6x eininga; aðlögun að 3 hæðum og kjallara.')
    # 7,8
    add(7,'7.1','Frágangur utanhúss: þak, klæðning, gluggar, svalir (Hamranes-hlutfall)',A_mod+p['A_teng'],'m²',HAM['ch7']*H,'Hamranes EAC kafli 7: 274,7 m.kr / 6.730 m² = 40,8 þ/m²','Kjallari neðanjarðar að mestu — reiknað á hæðir + tengigang.')
    add(7,'7.2','Utanáliggjandi flóttastigar úr stáli, 2 stk × 3 hæðir, heitgalvaniseraðir með pöllum, útgangshurðum og skyggnum (B-rými)',1,'heild',p['ext_stairs'],'Mat ÍF; húsrýmisáætlun FSRE 4.5.4 „opinn flóttastigi“ (B-rými utan heildarflatarmáls); Húsavík: forsteyptur stigi 1,6 m.kr/hæð','Koma í stað lokaðra flóttastigahúsa Hamraness (240 m² brúttó A-rými). 2 × 3 hæðarbil × ~3,0 m.kr + 6 hurðir/skyggni ~4 m.kr. Forsenda GT 4.9.2026')
    add(8,'8.1','Lóðarfrágangur: endurgerð dvalarsvæðis norðan 2A, bílastæði, þjónustuaðkoma frá Skeiðholti, girðingar, gróður',1,'heild',120.0,'Hamranes kafli 8: 106 m.kr; kröfulýsing Þ113 og samkomulag um byggingarrétt (rafstrengir á kostnað Mosfellsbæjar)','Lítil lóð en endurgerð svæðis 2A og sér lóðaruppdráttur áskilinn.')
    return L, dict(A_mod=A_mod, A_built=A_built)

UNC = {0:0.05,1:0.20,2:0.12,3:0.08,4:0.08,5:0.08,6:0.03,7:0.08,8:0.15}

def cost(p):
    L, A = lines(p)
    ch = {}
    for l in L: ch[l['ch']] = ch.get(l['ch'],0)+l['qty']*l['rate']/1000.0  # m.kr
    unc = {k: ch[k]*UNC[k] for k in ch}
    framkv = sum(ch.values())+sum(unc.values())
    A_built=A['A_built']
    design = dict(ark=80.0, ll=22.0, burd=18.0, raf=22.0, vott=8.0, ums=20.0)
    des = sum(design.values())
    fee = framkv*p['IF_fee']
    bbm = p['bbm_rate']*A_built/1000.0
    gjold = dict(gatn=p['gatn']*A_built/1000.0, skip=0.003*bbm, bygg=4.0, veitur=25.0)
    gj = sum(gjold.values())
    total_exfin = framkv+des+fee+gj
    fin = total_exfin*p['LTC']*p['cl_rate']*(p['build_months']/12)*p['draw_factor'] + total_exfin*p['LTC']*p['cl_fee']
    total = total_exfin+fin
    return dict(lines=L,ch=ch,unc=unc,framkv=framkv,design=design,des=des,fee=fee,gjold=gjold,gj=gj,total_exfin=total_exfin,fin=fin,total=total,A=A,bbm=bbm)

def irr(cfs, lo=-0.9, hi=1.0):
    f=lambda r: sum(cf/(1+r)**t for t,cf in enumerate(cfs))
    a,b=lo,hi
    if f(a)*f(b)>0: return float('nan')
    for _ in range(200):
        m=(a+b)/2
        if f(a)*f(m)<=0: b=m
        else: a=m
    return (a+b)/2

def rent_model(p, C=None):
    C = C or cost(p)
    A=C['A']; total=C['total']
    uplift=(1+p['infl'])**(p['uplift_months']/12)
    rent1 = p['rent']/(1+p['vat'])*p['A_paid']*12/1e6*uplift
    fmat = p['fmat_rate']*A['A_built']/1000.0*uplift + p['lodmat']
    bbm = C['bbm']*uplift
    stofn = total - C['fin']  # skattaleg fyrning á stofnverð án fjármagns
    loan = total*p['LTC']; equity = total-loan
    idx=[(1+p['infl'])**t for t in range(0,27)]
    # year 1 NOI
    def opex(t):
        m = p['m1'] if t<=5 else (p['m2'] if t<=15 else p['m3'])
        return (fmat*(p['fsk']+p['vatn']) + bbm*(p['ins']+m) + p['other'])*idx[t-1] + rent1*idx[t-1]*p['mgmt']
    noi=[None]+[rent1*idx[t-1]-opex(t) for t in range(1,27)]
    value = noi[1]/p['yld']
    bond = value*p['LTV']; r=p['bond_base']+p['bond_margin']; n=p['bond_years']
    ann = bond*r/(1-(1+r)**-n)
    bal=bond; pool=0.0; cfs=[-equity]; rel = bond*(1-p['bond_cost'])-loan
    for t in range(1,26):
        int_real=bal*r; princ=ann-int_real; bal_prev=bal; bal=bal-princ
        ds_nom = ann*idx[t]  # greitt í lok árs t, verðbætt
        int_nom = int_real*idx[t] + bal_prev*(idx[t]-idx[t-1])
        taxable = noi[t] - int_nom - p['depr']*stofn
        if taxable<0: pool+=-taxable; tx=0.0
        else:
            use=min(pool,taxable); pool-=use; tx=(taxable-use)*p['tax']
        cf = noi[t]-ds_nom-tx
        if t==1: cf+=rel
        if t==25:
            tv = noi[26]/p['yld']; sale = tv*(1-p['sale_cost']); gain_tax = max(0,(tv-stofn))*p['tax']*p['sale_tax_share']
            cf += sale - gain_tax - bal*idx[25]
        cfs.append(cf)
    irr_n = irr(cfs); irr_r=(1+irr_n)/(1+p['infl'])-1
    npv = sum(cf/(1+p['disc_rate'])**t for t,cf in enumerate(cfs))
    dscr = min(noi[t]/(ann*idx[t]) for t in range(1,26))
    moic_sale = (value*(1-p['sale_cost']) - loan - max(0,(value-stofn))*p['tax']*p['sale_tax_share'])/equity
    return dict(rent1=rent1,noi1=noi[1],value=value,bond=bond,loan=loan,equity=equity,release=rel,irr_n=irr_n,irr_r=irr_r,npv=npv,dscr=dscr,moic_sale=moic_sale,cfs=cfs,ann=ann,total=total,fmat=fmat,bbm=bbm,stofn=stofn)

def rent_for_irr(p,target=0.12,C=None):
    lo,hi=4000.0,12000.0
    for _ in range(60):
        m=(lo+hi)/2; q=dict(p); q['rent']=m
        if rent_model(q,C)['irr_n']<target: lo=m
        else: hi=m
    return (lo+hi)/2

if __name__=='__main__':
    p=dict(BASE); C=cost(p)
    print("Kaflar (m.kr án VSK):",{k:round(v,1) for k,v in C['ch'].items()})
    print("Óvissa:",round(sum(C['unc'].values()),1),"Framkv:",round(C['framkv'],1),"Hönnun:",C['des'],"Fee:",round(C['fee'],1),"Gjöld:",round(C['gj'],1))
    print("Alls f.u. fjármagn:",round(C['total_exfin'],1),"Fjármagn:",round(C['fin'],1),"ALLS:",round(C['total'],1),"A_built",C['A']['A_built'],"per paid m²",round(C['total']/p['A_paid']*1000),"per built m²",round(C['total']/C['A']['A_built']*1000))
    R=rent_model(p,C)
    print({k:(round(v,3) if isinstance(v,float) else v) for k,v in R.items() if k!='cfs'})
    print("Rent for 12% nafn IRR:",round(rent_for_irr(p,0.12,C)),"; for 10%:",round(rent_for_irr(p,0.10,C)),"; NPV0@9% rent:",)
    for r in (5400,5650,5900,6200,6500):
        q=dict(p); q['rent']=r; m=rent_model(q,C); print(r, "IRR",round(m['irr_n']*100,1),"raun",round(m['irr_r']*100,1),"NPV",round(m['npv']),"DSCR",round(m['dscr'],2),"MOIC sala",round(m['moic_sale'],2))
