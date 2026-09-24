#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Þ113 Hamrar — stjórnarsíða. Allar tölur reiknaðar úr model.py (sama líkan og Excel v1.7). python3 gen.py && python3 encrypt.py"""
import base64, copy, html as H, os
from model import BASE, cost, rent_model, rent_for_irr, lines, UNC
HERE = os.path.dirname(os.path.abspath(__file__))
def run(ov, rent=None):
    p = dict(BASE); p.update(ov)
    if rent: p['rent'] = rent
    C = cost(p); R = rent_model(p, C); return p, C, R
p, C, R = run({})
A = C['A']
def n0(x): return f"{x:,.0f}".replace(",", ".")
def n1(x): return f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
def pct(x, d=1): return f"{x*100:.{d}f}".replace(".", ",") + "%"
def b64file(fn):
    with open(os.path.join(HERE, "assets", fn), "rb") as f: return base64.b64encode(f.read()).decode()

SCEN = [
 ("Grunnur v1.7: opnir stigar, kjallari 328,5, tengigangur 44, einingaskrá VBC með BANO, −3% grind — byggt = greitt", {}),
 ("Lokuð flóttastigahús, kjallari 300, 110 m² tengigangur, engin grindarlækkun (v1.2)", dict(A_haed_override=1368.5, stair_m2=0.0, ext_stairs=0.0, A_teng=110.0, A_kj=300.0, VBC_light=0.0)),
 ("Besta tilfelli: VBC −5% til viðbótar, 18 mán", dict(VBC_disc=0.05, build_months=18)),
 ("Frekari þjöppun hæðar í 1.300 m² (snertir skipulag setustofa)", dict(A_haed_override=1300.0)),
 ("Varfærið: kj 500, teng 200 steypt, 24 mán, krafa 6,0%, verðb. 1,09, engin grindarlækkun", dict(A_kj=500.0, A_teng=200.0, teng_rate=480.0, gatn=42.0, build_months=24, yld=0.060, live_site=60.0, A2_inngrip=80.0, BVT_H=1.09, VBC_light=0.0)),
 ("Upphaflegt prógramm GT: kj 750, teng 320 steypt, lokuð stigahús, engin grindarlækkun", dict(A_kj=750.0, A_teng=320.0, teng_rate=480.0, stair_m2=0.0, ext_stairs=0.0, VBC_light=0.0)),
]
LEV = [
 ("Lokuð flóttastigahús í stað opinna (aftur í 1.368,5 m²/hæð)", dict(stair_m2=0.0, ext_stairs=0.0), "Neikvæð: 144 m² A-rými + einingar"),
 ("Frekari þjöppun hæðar í 1.300 m² (setustofur 111 → ~100 m²/eining)", dict(A_haed_override=1300.0), "Snertir skipulag Hamranes-hæðar; færi húsið undir 4.334"),
 ("Kjallari 328,5 → 450 m² (ef FSRE/Eir krefjast fleiri miðlægra rýma)", dict(A_kj=450.0), "Neikvæð"),
 ("Tengigangur 44 → 110 m² (nýbygging fjær gafli Hamra)", dict(A_teng=110.0), "Neikvæð: hver 10 m á 2 hæðum ≈ 60 m²"),
 ("Tengigangur 44 → 200 m² steypt tengibygging (ef krafist)", dict(A_teng=200.0, teng_rate=480.0), "Neikvæð"),
 ("Léttara burðarvirki EKKI staðfest af VBC (3% → 0)", dict(VBC_light=0.0), "Neikvæð: ef VBC gefur ekkert fyrir 3 hæðir / 0,15 g"),
 ("Léttara burðarvirki 3% → 5%", dict(VBC_light=0.05), "Efri mörk næmni"),
 ("Shell-verð miðeininga +15% (€1.375/m²)", dict(shell_eur=1196*1.15), "Neikvæð: eina afleidda talan í kafla 6 — fastverð VBC sker úr"),
 ("Shell-verð miðeininga −15% (€1.017/m²)", dict(shell_eur=1196*0.85), "Ef VBC verðleggur shell-einingar nær stálgrind + klæðningu"),
 ("EUR/ISK 145 → 138 (gengi 24.9.2026)", dict(EURISK=138.0), "Gengisáhætta fram að samningi — festa gengi eða verð í ISK"),
 ("EUR/ISK 145 → 160 (10% veiking krónu)", dict(EURISK=160.0), "Neikvæð"),
 ("Flutningur/uppsetning á Hamranes-raun (€20.009 í stað €20.594)", dict(ti_eur=20009.0), "Lítil"),
 ("VBC-afsláttur 5% til viðbótar", dict(VBC_disc=0.05), "VBC þarf verk og traustsyfirlýsingu eftir seinkunina"),
 ("VBC-afsláttur 10%", dict(VBC_disc=0.10), "Ólíklegra"),
 ("ÍF-þóknun 6% → 5%", dict(IF_fee=0.05), "Ákvörðun ÍF"),
 ("Gatnagerðargjald 38 → 25 þ/m²", dict(gatn=25.0), "Samþykkt 496/2017 — staðfesta"),
 ("Byggingartími 20 → 16 mán", dict(build_months=16), "VBC framleiðsla samhliða kjallara"),
 ("Ávöxtunarkrafa 5,7% → 5,4% (ríkið beint leigjandi)", dict(yld=0.054), "Ríkisábyrgð viðurkennd"),
 ("Álag skuldabréfs 100 → 89 pkt", dict(bond_margin=0.0089), "Ögurhvarfs-kjör"),
 ("LTV 67,7% → 72%", dict(LTV=0.72), "Lífeyrissjóðir"),
 ("SAMSETT: VBC −5%, 18 mán, krafa 5,4% (skipulag hæða óbreytt)", dict(VBC_disc=0.05, build_months=18, yld=0.054), "Allt samtímis"),
]
rents = [5400, 5500, 5600, 5650, 5700, 5800, 5900, 6000, 6100, 6200, 6400]
# ceiling
def irr_scale(s):
    Cq = copy.deepcopy(C)
    for k in ('framkv', 'des', 'fee', 'gj', 'total_exfin', 'fin', 'total'): Cq[k] = C[k] * s
    return rent_model(p, Cq)['irr_n']
lo, hi = 0.5, 1.5
for _ in range(60):
    m = (lo + hi) / 2
    if irr_scale(m) > 0.12: lo = m
    else: hi = m
ceiling = C['total'] * (lo + hi) / 2

# ---------- SVG chart: IRR vs rent for 3 scenarios ----------
def chart():
    W, Hh, L, T, Rr, B = 760, 330, 60, 20, 20, 50
    xs = list(range(5400, 6401, 50))
    series = [("Grunnur", {}, "#1D5FA8"), ("Besta tilfelli (VBC −5% til viðbótar, 18 mán)", dict(VBC_disc=0.05, build_months=18), "#2a9d5c"), ("Lokuð stigahús + 110 m² tengigangur, engin grindarlækkun (v1.2)", dict(A_haed_override=1368.5, stair_m2=0.0, ext_stairs=0.0, A_teng=110.0, A_kj=300.0, VBC_light=0.0), "#c0504d")]
    ymin, ymax = 0.08, 0.16
    def X(v): return L + (v - 5400) / 1000 * (W - L - Rr)
    def Y(v): return T + (ymax - v) / (ymax - ymin) * (Hh - T - B)
    out = [f'<svg viewBox="0 0 {W} {Hh}" width="100%" style="max-width:{W}px;font-family:inherit">']
    for yv in [0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]:
        out.append(f'<line x1="{L}" y1="{Y(yv):.1f}" x2="{W-Rr}" y2="{Y(yv):.1f}" stroke="{"#c0504d" if abs(yv-0.12)<1e-9 else "#e3e9f0"}" stroke-width="{2 if abs(yv-0.12)<1e-9 else 1}" stroke-dasharray="{"6,4" if abs(yv-0.12)<1e-9 else "0"}"/>')
        out.append(f'<text x="{L-6}" y="{Y(yv)+4:.1f}" text-anchor="end" font-size="11" fill="#5A6B7A">{int(round(yv*100))}%</text>')
    for xv in range(5400, 6401, 200):
        out.append(f'<text x="{X(xv):.1f}" y="{Hh-B+16}" text-anchor="middle" font-size="11" fill="#5A6B7A">{n0(xv)}</text>')
    out.append(f'<text x="{(L+W-Rr)/2:.0f}" y="{Hh-8}" text-anchor="middle" font-size="12" fill="#1c2b3a">Tilboðsverð kr/m²/mán m.vsk (greidd 4.334 m²)</text>')
    out.append(f'<text x="{X(5405):.1f}" y="{Y(0.12)-5:.1f}" font-size="11" fill="#c0504d">Markmið Stafa 12%</text>')
    out.append(f'<line x1="{X(5650):.1f}" y1="{T}" x2="{X(5650):.1f}" y2="{Hh-B}" stroke="#C9A227" stroke-width="1.5" stroke-dasharray="4,3"/><text x="{X(5650)+4:.1f}" y="{T+12}" font-size="11" fill="#8a6a06">5.650</text>')
    for i, (nm, ov, col) in enumerate(series):
        pts = []
        for xv in xs:
            _, _, r_ = run(ov, xv); pts.append(f"{X(xv):.1f},{Y(min(max(r_['irr_n'], ymin), ymax)):.1f}")
        out.append(f'<polyline fill="none" stroke="{col}" stroke-width="2.5" points="{" ".join(pts)}"/>')
        out.append(f'<rect x="{L+10+i*250}" y="{T+2}" width="12" height="12" fill="{col}"/><text x="{L+26+i*250}" y="{T+12}" font-size="11" fill="#1c2b3a">{H.escape(nm)}</text>')
    out.append('</svg>')
    return "".join(out)

# ---------- tables ----------
def tbl(header, rows, cls="", numcols=()):
    h = "".join(f'<th class="{"n" if i in numcols else ""}">{H.escape(str(x))}</th>' for i, x in enumerate(header))
    b = ""
    for r_ in rows:
        b += "<tr>" + "".join(f'<td class="{"n" if i in numcols else ""}">{x if isinstance(x, str) and x.startswith("<") else H.escape(str(x))}</td>' for i, x in enumerate(r_)) + "</tr>"
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'

scen_rows = []
for nm, ov in SCEN:
    q, Cq, Rq = run(ov)
    scen_rows.append([nm, n0(Cq['A']['A_built']), n0(Cq['A']['A_built'] - q['A_paid']), n0(Cq['total']), n0(Cq['total'] * 1000 / q['A_paid']), pct(Rq['irr_n']), pct(Rq['irr_r']), n0(Rq['npv']), f"{Rq['moic_sale']:.2f}".replace(".", ","), n0(rent_for_irr(q, 0.12, Cq)), n0(rent_for_irr(q, 0.10, Cq))])
grid_rows = []
for nm, ov in SCEN[:4]:
    row_ = [nm]
    for rt in rents:
        _, _, r_ = run(ov, rt); row_.append(pct(r_['irr_n']))
    grid_rows.append(row_)
lev_rows = [["Grunnur", n0(C['total']), "0", pct(R['irr_n']), n0(rent_for_irr(p, 0.12, C)), "—"]]
for nm, ov, cond in LEV:
    q, Cq, Rq = run(ov)
    lev_rows.append([nm, n0(Cq['total']), ("+" if Cq['total'] - C['total'] > 0 else "") + n0(Cq['total'] - C['total']), pct(Rq['irr_n']), n0(rent_for_irr(q, 0.12, Cq)), cond])
L_, _ = lines(dict(p))
CHN = {0: "0 Aðstaða og umsjón", 1: "1 Jarðvinna", 2: "2 Burðarvirki, kjallari, tengigangur, 2A", 3: "3 Lagnir og loftræsing", 4: "4 Raflagnir og kerfi", 5: "5 Frágangur innanhúss utan eininga", 6: "6 Einingar VBC", 7: "7 Frágangur utanhúss (þ.m.t. opnir stigar)", 8: "8 Lóð"}
cost_rows = []
for ch in range(9):
    cost_rows.append([CHN[ch], n1(C['ch'][ch]), n0(C['ch'][ch] * 1000 / A['A_built']), "; ".join(l['name'].split(" (")[0][:60] for l in L_ if l['ch'] == ch)[:180]])
cost_rows += [["Óvissa (class 4, 3–20% eftir kafla)", n1(sum(C['unc'].values())), n0(sum(C['unc'].values()) * 1000 / A['A_built']), "Hamranes EAC 3,5% raun, Akureyri 11,5% áætlun"],
              ["<b>Framkvæmdakostnaður alls</b>", f"<b>{n1(C['framkv'])}</b>", n0(C['framkv'] * 1000 / A['A_built']), ""],
              ["Hönnun og annar kostnaður", n1(C['des']), n0(C['des'] * 1000 / A['A_built']), "Arkís 80 (endurnýting), L&L 22, burðarþol 18, rafmagn 22, vottun 8, umsýsla 20"],
              [f"Stýriverktökuálag ÍF {pct(p['IF_fee'],0)}", n1(C['fee']), n0(C['fee'] * 1000 / A['A_built']), "Hamranes 10%, Akureyri 8,5%"],
              ["Lóð og gjöld", n1(C['gj']), n0(C['gj'] * 1000 / A['A_built']), "Gatnagerðargjald 38 þ/m² (ÓSTAÐFEST), skipulagsgjald, leyfi, veitur; engin lóðarleiga"],
              ["<b>Alls fyrir utan fjármagn</b>", f"<b>{n1(C['total_exfin'])}</b>", n0(C['total_exfin'] * 1000 / A['A_built']), ""],
              ["Fjármagnskostnaður á byggingartíma", n1(C['fin']), n0(C['fin'] * 1000 / A['A_built']), f"65% lánsfé, 10,2% + 0,2%, {p['build_months']} mán"],
              ["<b>HEILDARFJÁRFESTING án VSK</b>", f"<b>{n1(C['total'])}</b>", f"<b>{n0(C['total'] * 1000 / A['A_built'])}</b>", f"= {n0(C['total']/66*1000)} þ.kr á rými"]]
rym_floor = [["4.1.1","Einkarými 66 × 28","1.848","1.848","0","Herb. 22,7 + Vs. 5,3 (201–222)"],["4.1.2","Setustofur, borðstofa, eldhús 6 × 113","678","662","−16","Eldhús 18,7 + stofur 100,1 + 101,9 = 220,7/hæð"],["4.1.3","Línlager í skápum 6 × 4","24","20","−4","Línskápar 3,3 í gangi"],["4.1.4","Aðstaða starfsmanna 6 × 6","36","0","−36","Sama rými og 4.1.3; búningsaðstaða í kjallara bætir upp"],["4.1.5","Snyrting starfsmanna 6 × 3","18","16","−2","Vs. 2,7"],["4.1.6","Skol, þvottur, ræsting 6 × 15","90","103","+13","Skol/þv. 17,1; rúmar 4.2.7"],["4.2.1","Lyfjageymsla 1 × 8","8","17","+9","Lyf 5,5 á hverri hæð"],["4.2.2","Hjúkrunarvakt 1 × 12","12","45","+33","Vakt 15,1 á hverri hæð"],["4.2.3","Geymsla jóladót 3 × 14","42","44","+2","1,9 + 6,0 + 6,6 á hæð"],["4.2.4","Gestasalerni 3 × 4","12","12","0","Vs. 4,0"],["4.2.5","Farandskrifstofa 2 × 12","24","41","+17","13,7 á hverri hæð"],["4.2.6","Viðtalsherbergi 3 × 8","24","24","0","Viðtöl 8,1"],["4.2.7","Geymsla óhreins líns 1 × 4","4","0","−4","Í skolrýmum"],["<b>—</b>","<b>Dagskrárrými á hæðum, nettó</b>","<b>2.820</b>","<b>2.831</b>","<b>+11</b>","Hamranes 2. hæð 943,8 nettó"],["<b>—</b>","<b>Brúttó hæðir (×1,4 / 3 × 1.320,5)</b>","<b>3.948</b>","<b>3.962</b>","<b>+14</b>","Álag Hamranes-hæðar 1,40 = stuðull FSRE"]]
rym_kj = [["4.3.1","Aðalinngangur","15","Aðalinngangur/sjúkraflutningar 43,7 (100)"],["4.3.2","Starfsmanna-/sjúkraflutningainngangur","10","sama rými"],["4.3.3","Vörumóttaka","15","15,7 + sorppressa 12,5 (105)"],["4.3.4","Móttaka/skrifstofa","10","Forstöðumaður/skrifstofa 23,7 (102)"],["4.3.7","Iðjuþjálfun","40","nýtt — íbúar Hamra sækja hingað (Q&A 5.C)"],["4.3.8","Fjölnotarými/sjúkraþjálfun","60","Þjálfunaraðstaða 84,5 (109)"],["4.3.9","Búningsaðstaða og munaskápar","16","Búningsaðstaða + klefar 31 (107)"],["4.3.10","Hleðslurými matarvagna","3","Matarvagnar 29,0 (106) — matur frá Hömrum um tengigang"],["4.3.11","Miðlæg ræstimiðstöð","15","14,3 (111)"],["4.3.12","Sorpflokkun innanhúss","25","ekkert innanhúss á Hamranesi (skýli 33,1 úti)"],["4.3.13","Miðlæg geymsla","10","3 geymslur 32,9"],["4.3.14","Geymsla húsvörslu","10","7,2 (103-1)"],["4.3.15","Hjólageymsla og rafskutlur","15","Mhl.02 34,1"],["<b>—</b>","<b>Samtals nettó</b>","<b>244</b>","Brúttó FSRE ×1,4 = 341,6; kjallari 328,5 = álag 1,35"]]

# einingaskrá rows from model
_kE = p['EURISK']/1000.0*(1-p['VBC_disc'])*(1-p['VBC_light'])
_sh = p['shell_eur']*(1-p['VBC_disc'])*(1-p['VBC_light'])
ein_rows = [
 ["IS-10 / IS-11 / IS-13","10","74,7","2 íbúðarrými (herb. 22,7 + bað 5,3) sitt hvorum megin gangs; stöður 02–06, 17–21","Fullbúin m. BANO","Tilboð VBC 20.4.2026 −7%", n0(p['IS10_eur']*(1-p['VBC_disc'])*(1-p['VBC_light'])), n1(p['N_haed']*p['N_IS10']*p['IS10_eur']*_kE/1000)],
 ["IS-12","2","74,7","1 íbúðarrými + skol/þvottur/ræsting + gesta-WC; stöður 07, 16","Fullbúin m. BANO","Tilboð VBC 20.4.2026 −7%", n0(p['IS12_eur']*(1-p['VBC_disc'])*(1-p['VBC_light'])), n1(p['N_haed']*p['N_IS12']*p['IS12_eur']*_kE/1000)],
 ["IS-30 – IS-37 (8 stk)","8","376,7 alls","Setustofur 1–2, borðstofur 1–2, uppvask, lyftur 2, forrými, vakt/skrifstofa, lyf, aðstandendur, tækni; stöður 08–15","Shell (orange)","Hamranes-samningur, shell-liðir × 0,93 = €1.196/m²", n0(_sh*p['A_central']/8)+" meðaltal", n1(p['N_haed']*p['A_central']*_sh*p['EURISK']/1e6)],
 ["Endaeiningar (í stað IS-70)","2",f"{A['A_end']/2:.1f}".replace('.',','),"Lagnaskakt, geymsla, útgangur á opinn flóttastiga — stiginn (24 m²) fer út; stöður 01, 22","Shell (orange)","Sama shell-verð", n0(_sh*A['A_end']/2), n1(p['N_haed']*A['A_end']*_sh*p['EURISK']/1e6)],
 ["Flutningur og uppsetning","22","—","Chojnice–Gdynia–Hafnarfjörður, krani, festingar, einangrun, þétting","Á einingu","Akureyrar-forsendur 15.000 + 5.594", n0(p['ti_eur']), n1(p['N_haed']*p['N_mod_floor']*p['ti_eur']*p['EURISK']/1e6)],
 ["Hönnun VBC","","","Endurtekin hönnun, aðlögun að 3 hæðum og kjallara","","Hamranes 97 → 40","", n1(p['VBC_eng'])],
 ["<b>Kafli 6 alls</b>","<b>22 / 66</b>","<b>1.308,5/hæð</b>","","","","<b>€"+n0((p['N_haed']*p['N_IS10']*p['IS10_eur']+p['N_haed']*p['N_IS12']*p['IS12_eur']+p['N_haed']*(p['A_central']+A['A_end'])*p['shell_eur'])*(1-p['VBC_disc'])*(1-p['VBC_light'])/1e6*100)/100 if False else "<b>€"+f"{(p['N_haed']*p['N_IS10']*p['IS10_eur']+p['N_haed']*p['N_IS12']*p['IS12_eur']+p['N_haed']*(p['A_central']+A['A_end'])*p['shell_eur'])*(1-p['VBC_disc'])*(1-p['VBC_light'])/1e6:.2f}".replace('.',',')+" M einingar</b>", "<b>"+n1(C['ch'][6])+"</b>"],
]
_Amod3 = p['N_haed']*((p['N_IS10']+p['N_IS12'])*74.7+p['A_central']+A['A_end'])
ein_mod = (p['N_haed']*p['N_IS10']*p['IS10_eur']+p['N_haed']*p['N_IS12']*p['IS12_eur']+p['N_haed']*(p['A_central']+A['A_end'])*p['shell_eur'])*(1-p['VBC_disc'])*(1-p['VBC_light'])*p['EURISK']/1e6
ein_hus = (_Amod3*7926525/3880*0.93*(1-p['VBC_light'])+66*6332)*p['EURISK']/1e6
ein_ham = (14450000+2106671)/6863*_Amod3*p['EURISK']/1e6
DL = f'''<div class="dl">
<a download="Þ113 Hamrar - Kostnaðaráætlun og leigumódel Stafir - v1.7 24.09.2026 (einingaskrá VBC, allt formúlur).xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64file("model.xlsx")}">⬇ Excel-líkan v1.7 (allt formúlur)</a>
<a download="Þ113 Hamrar - Rökstuðningsskjal v1.9 24.09.2026 (einingaskrá VBC, Q&A, rúmmyndun).docx" href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64file("memo.docx")}">⬇ Rökstuðningsskjal v1.9 (Word)</a>
<a download="Þ113 Hamrar - Rökstuðningsskjal v1.9 24.09.2026 (einingaskrá VBC, Q&A, rúmmyndun).pdf" href="data:application/pdf;base64,{b64file("memo.pdf")}">⬇ Rökstuðningsskjal v1.9 (PDF)</a>
<a download="Þ113 Hamrar - Viðbótargögn FSRE (teikningar Hamra) - rúmmyndun byggingarreits 2B - 24.09.2026.pdf" href="data:application/pdf;base64,{b64file("teikn.pdf")}">⬇ Minnisblað: teikningar Hamra og rúmmyndun 2B (PDF)</a>
</div>'''

M2R = f"{A['A_built']/66:.1f}".replace('.', ',')
RENT_ROOM = n0(p['rent']*p['A_paid']/66/1000)
kpi = f'''<div class="kpis">
<div class="kpi"><div class="v">{n0(C['total'])} <span>m.kr</span></div><div class="l">Heildarfjárfesting án VSK, með fjármagni</div></div>
<div class="kpi"><div class="v">{n0(C['total']*1000/p['A_paid'])} <span>þ.kr/m²</span></div><div class="l">Á greiddan = byggðan m² (Hamranes 815)</div></div>
<div class="kpi"><div class="v">{n0(A['A_built'])} <span>m²</span></div><div class="l">Byggt = greitt 4.334, ekkert umfram = {M2R} m²/rými</div></div>
<div class="kpi"><div class="v">{RENT_ROOM} <span>þ.kr/rými/mán</span></div><div class="l">Samanburðargrunnur FSRE: tilboð × 4.334 / 66 (Hamranes 5.950 × 65 = 387)</div></div>
<div class="kpi"><div class="v">{pct(R['irr_n'])}</div><div class="l">IRR eiginfjár nafn við 5.650 ({pct(R['irr_r'])} raun)</div></div>
<div class="kpi"><div class="v">{n0(rent_for_irr(p,0.12,C))} <span>kr/m²</span></div><div class="l">Leiga fyrir 12% (besta tilfelli {n0(rent_for_irr(*run(dict(VBC_disc=0.05,build_months=18))[:1], 0.12, run(dict(VBC_disc=0.05,build_months=18))[1]))})</div></div>
<div class="kpi"><div class="v">{n0(R['equity'])} <span>m.kr</span></div><div class="l">Eigið fé Stafa (35%), losun +{n0(R['release'])} við endurfjármögnun</div></div>
</div>'''

HDR_GRID = ['Sviðsmynd / leiga m.vsk'] + [n0(r) for r in rents]
GRID = tbl(HDR_GRID, grid_rows, numcols=tuple(range(1, len(rents) + 1)))
page = f'''<!doctype html><html lang="is"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>Þ113 Hamrar — tilboð Stafa</title>
<style>
:root{{--navy:#12263A;--blue:#1D5FA8;--gold:#C9A227;--ink:#1c2b3a;--line:#d7e0ea}}
*{{box-sizing:border-box}} body{{margin:0;font-family:-apple-system,'Segoe UI',Arial,sans-serif;color:var(--ink);background:#f4f7fa}}
header{{background:var(--navy);color:#fff;padding:26px 20px 18px}} header h1{{margin:0;font-size:24px}} header .sub{{color:var(--gold);font-size:13.5px;margin-top:4px}}
nav{{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--line);padding:8px 14px;z-index:9;display:flex;flex-wrap:wrap;gap:6px}}
nav a{{text-decoration:none;color:var(--blue);font-size:13px;padding:5px 10px;border-radius:14px;background:#eef4fb}} nav a:hover{{background:#dbe9f9}}
main{{max-width:980px;margin:0 auto;padding:18px 14px 60px}}
.co{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:18px 0;box-shadow:0 1px 3px rgba(18,38,58,.06)}}
h2{{color:var(--blue);font-size:19px;margin:0 0 10px;border-bottom:2px solid var(--blue);padding-bottom:8px}} h3{{color:var(--blue);font-size:15.5px;margin:22px 0 8px}}
p,li{{font-size:14px;line-height:1.55}} .hl{{font-size:14px;background:#f2f7fd;border-left:3px solid var(--blue);padding:10px 12px;border-radius:0 8px 8px 0;margin:10px 0;line-height:1.55}}
.warn{{font-size:13px;background:#fdf8e8;border-left:3px solid var(--gold);padding:9px 12px;border-radius:0 8px 8px 0;margin:10px 0;line-height:1.5}}
table{{width:100%;border-collapse:collapse;font-size:12.5px;margin:8px 0}} th{{text-align:left;color:#5A6B7A;font-weight:600;border-bottom:1px solid var(--line);font-size:11.5px;padding:6px 7px;vertical-align:bottom}}
td{{padding:5px 7px;border-bottom:1px solid #eef2f6;vertical-align:top}} td.n,th.n{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:14px 0}} .kpi{{background:#f2f7fd;border-radius:10px;padding:12px 14px}} .kpi .v{{font-size:24px;font-weight:700;color:var(--navy)}} .kpi .v span{{font-size:13px;font-weight:500;color:#5A6B7A}} .kpi .l{{font-size:12px;color:#44566b;margin-top:3px;line-height:1.4}}
.dl{{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0}} .dl a{{background:var(--blue);color:#fff;text-decoration:none;padding:9px 14px;border-radius:9px;font-size:13px;font-weight:600}} .dl a:hover{{background:#174c86}}
.scroll{{overflow-x:auto}} footer{{text-align:center;color:#8898a8;font-size:11.5px;padding:20px}} footer a{{color:#8898a8}}
@media print{{nav,.dl{{display:none}}.co{{break-inside:avoid;border:none;box-shadow:none}}}}
</style></head><body>
<header><h1>Þ113 Hamrar, Mosfellsbær — tilboð Stafa</h1><div class="sub">Kostnaðaráætlun og leiguverðsmódel · Hamranes endurtekið í þéttu prógrammi · útgáfa 1.7/1.9, 24. september 2026 · TRÚNAÐARMÁL</div></header>
<nav><a href="#nidurstada">Niðurstaða</a><a href="#husid">Húsið og rýmistafla</a><a href="#einingar">Einingaskrá VBC</a><a href="#kostnadur">Kostnaðaráætlun</a><a href="#leiga">Leigumódel</a><a href="#svidsmyndir">Sviðsmyndir</a><a href="#bil">Bilgreining</a><a href="#haefi">Hæfi Stafa</a><a href="#naest">Næstu skref</a><a href="#skjol">Skjöl</a></nav>
<main>
<div class="co" id="nidurstada"><h2>1. Niðurstaða</h2>
{kpi}
<p class="hl"><b>Kenningin um byggingarkostnað heldur:</b>  húsið kostar {n0(C['total']*1000/A['A_built'])} þ.kr á byggðan fermetra, á pari við Hamranes (815 með fjármagni), þrátt fyrir klöpp, tengigang og inngrip í 2A. <b>Stærðin réð úrslitum og hún er leyst:</b> Hamranes-hæðirnar 2–5 óbreyttar nema lokuðu flóttastigahúsin (48 m²/hæð) fara út og opnir utanáliggjandi stálstigar koma í staðinn sem B-rými, tengigangurinn er 44 m² eins og FSRE reiknar sjálft, og kjallarinn 328,5 m² ber miðlægu rýmin. Byggt = greitt = 4.334 m². Kafli 6 er nú einingaskrá Hamranes-hæðar verðlögð eining fyrir eining: 36 íbúðaeiningar á Akureyrar-tilboðsverðum VBC 20.4.2026 með BANO (krafa í kröfulýsingu 3.7.2), 24 miðeiningar og 6 endaeiningar sem shell á verði leiddu af Hamranes-samningnum, stigahúseiningarnar út, og 3% léttara burðarvirki fyrir 3 hæðir og 0,15 g í Mosfellsbæ (VBC að staðfesta). <b>Við 5.650 kr/m² m.vsk skilar verkefnið Stöfum {pct(R['irr_n'])} nafnávöxtun eiginfjár ({pct(R['irr_r'])} raun); 12% nást við {n0(rent_for_irr(p,0.12,C))} í grunni.</b> Upphaflega prógrammið (750 m² kjallari, 320 m² steypt tengibygging, lokuð stigahús, 842 m² umfram) hefði gefið {pct(run(dict(A_kj=750.0, A_teng=320.0, teng_rate=480.0, stair_m2=0.0, ext_stairs=0.0, VBC_light=0.0))[2]['irr_n'])} og krafist {n0(rent_for_irr(*run(dict(A_kj=750.0, A_teng=320.0, teng_rate=480.0, stair_m2=0.0, ext_stairs=0.0, VBC_light=0.0))[:1],0.12,run(dict(A_kj=750.0, A_teng=320.0, teng_rate=480.0, stair_m2=0.0, ext_stairs=0.0, VBC_light=0.0))[1]))}.</p>
<p><b>Ráðlegging:</b> tilboðsrammi 5.650–5.850 í þéttu prógrammi stendur. Einingaskráin lækkaði kafla 6 um 122 m.kr en staðfest gatnagerðargjald Mosfellsbæjar (Q&A 8, 48,3 þ/m²) tók 54 af því til baka: 5.650 gefur {pct(R['irr_n'])} í grunni og 12% liggja við {n0(rent_for_irr(p,0.12,C))} ({pct(run(dict(shell_eur=1196*1.15),5650)[2]['irr_n'])} við 5.650 ef shell-verð miðeininga reynist 15% hærra, {pct(run(dict(VBC_disc=0.05,build_months=18),5650)[2]['irr_n'])} með frekari VBC-afslætti). 5.650 er verjandi gólf, 5.750 gefur {pct(run({},5750)[2]['irr_n'])} og 5.850 {pct(run({},5850)[2]['irr_n'])} — á samanburðargrunni FSRE 371–384 þ.kr á rými á mánuði — allt innan vinningsbils Húsavíkur og Akureyrar (5.645–6.350). Þrennt þarf að negla fyrir 9.11.: opnu stigarnir gagnvart brunahönnun og FSRE, VBC-fastverð í einingaskrána, og afstaða FSRE/Eir til miðlægra rýma í kjallara.</p>
{DL}
</div>
<div class="co" id="husid"><h2>2. Húsið og rýmistafla</h2>
<p>Útboðsgögnin ráða stærðinni: FSRE greiðir 4.334 m² brúttó og „fermetrar umfram þörf leigjanda skulu innifaldir í leigutilboðinu“. Húsrýmisáætlun FSRE (17.08.26) = heimiliseiningar 3.772 + stoðrými 176 + miðlæg rými 342 + tengigangur 44; ekkert eldhús, þvottahús eða kjallari í prógrammi FSRE. Samkomulag um byggingarrétt: „4.334 m² auk tengigangs“, heimild 4.500 m² á þremur hæðum auk kjallara fyrir tækni- og stoðrými. Q&A svar 3: 3 hæðir × 2 einingar — nákvæmlega Hamranes-hæðin. Svar 5.D: 44 m² = tengigangur á tveimur hæðum. Húsnæðisþörfin er lágmark sem verður að uppfylla — aldrei undir, sem minnst yfir.</p>
<p class="warn"><b>Nýtt í Q&A 24.9.2026 (spurningar 7–13, svör 11.–14.9.):</b> (7) hæfi má byggja á fleiri en einu móðurfélagi með óskiptri ábyrgð og Viðauka I fyrir hvert — en ársreikningur 2026 og YTD-tölur gilda ekki, aðeins fullgerður endurskoðaður ársreikningur 2025 (Stafir – hótel 2025 stendur; arðgreiðslan 2026 snertir ekki hæfið). (8) <b>Fullt gatnagerðargjald Mosfellsbæjar</b> skv. samþykkt 496/2017, flokkur þjónustuhúsnæðis = 15% af vísitöluhúsi = 48.294 kr/m² frá 1.7.2026, af öllu brúttóflatarmáli á aðaluppdráttum — kjallari með aðkomu frá Skeiðholti er ekki undanþeginn; auk þess öll byggingarleyfis-, þjónustu-, tengi- og skráningargjöld á bjóðanda; engin innviða-/byggingarréttargjöld og engin lóðarleiga. Forsendan 38 þ/m² hækkuð í 49,7 (+54 m.kr). (9) Tengigangur og allir fermetrar umfram 4.334 innifaldir í verði — staðfestir grunninn. (10) Gera skal ráð fyrir breytingum á rýmisskipan og grunnskipulagi í fullvinnslu hönnunar með FSRE og rekstraraðila á kostnað bjóðanda; aðeins breytingar eftir undirritun leigusamnings fara í gr. 1.5 — áhætta fyrir „byggt = greitt“, sjá fyrirvara. (11) Hönnunarráðgjafa (Arkís, verkfræðistofur) skal tilgreina með kennitölu í tilboði (kafli 1.2.9); má bæta við síðar. (12) Ekkert forhæfismat á reynsluverkum. (13) FSRE birti „Viðbótargögn – teikningar“ af Hömrum: 23 aðaluppdrættir núverandi húss, mæliblað og lóðar-/hæðarblað COWI 2024 og grunngögn Mosfellsbæjar 8.9.2026 með gildandi byggingarreit 2B — greind 24.9., sjá hér að neðan; Mosfellsbær ber kostnað af færslu raflagna á lóð.</p>
<h3>Byggingarreitur 2B og Hamranes-hæðin (viðbótargögn FSRE, 24.9.2026)</h3>
<p>Byggingarreitur 2B í grunngögnum Mosfellsbæjar 8.9.2026 er <b>3.055 m²</b> norðan við norðurálmu Hamra, meðfram Skeiðholti, og nær alveg að norðurenda álmunnar (0 m bil). Rúmmyndun á DWG-gögnunum (0,5 m raster, öll horn): lengsta 16,4 m breið stöng er 84 m, 22 m breið 70,5 m; <b>Hamranes-hæðin (73 × 16,4 m + miðsvæði 18,2 × 5,4) rúmast í heilu lagi 24–38° frá norðri, samsíða Skeiðholti, með litlu svigrúmi</b>. Tengigangurinn getur því verið stuttur (44 m² stendur). Tvennt þarf að gæta að: hæðarsetning — lóð K = 52,23 (K = 47,83), Skeiðholt G = 49,65–50,05, svo kjallaragólf á 47,83 er ~2 m undir götu og „jarðhæð frá Skeiðholti“ kallar á hærri plötu eða rampa; og 4 m lagnakvöð milli nýbyggingar og norðurálmu sem tengigangurinn þverar. Engar burðarþols-, lagna- eða brunateikningar fylgja (FSRE: ekki þörf). Ekkert í gögnunum breytir kostnaðaráætluninni.</p>
<p style="text-align:center"><img src="data:image/png;base64,{b64file('reitur.png')}" alt="Byggingarreitur 2B með Hamranes-hæð" style="max-width:520px;width:100%;border:1px solid var(--line);border-radius:8px"></p>
{tbl(["Stærð","m²","Rök"],[["3 × Hamranes-hæð með opnum stigum (66 VBC-einingar)","3.961,5","Hæð 2.–5. Hamraness 1.368,5 − lokuð flóttastigahús 48 = 1.320,5. Skipulag eininga, setustofa og ganga óbreytt"],["Kjallari = jarðhæð frá Skeiðholti, miðlæg rými FSRE","328,5","Stillt svo byggt = greitt; FSRE reiknar 342, hæðirnar taka 13,5"],["Tengigangur 2 hæðir, léttur (stál/gler)","44,0","Talan í húsrýmisáætlun FSRE (40 nettó × 1,1). Bláa svæðið á THG-grunnmyndum í kröfulýsingu er merking FSRE um tengistað við vesturgafl norðurálmu — bjóðandi hannar"],["<b>Byggt = greitt</b>","<b>4.334,0</b>","Umfram 0 (var 842 í upphaflegu prógrammi)"]],numcols=(1,))}
<h3>Hæðirnar: 4.1 heimiliseiningar og 4.2 stoðrými (nettó m²) — Hamranes 2. hæð × 3</h3>
<div class="scroll">{tbl(["Nr.","Rými FSRE","FSRE","Þ113","Frávik","Hamranes-rými (rýmisskrá 24.8.2026)"],rym_floor,numcols=(2,3,4))}</div>
<h3>Kjallarinn: 4.3 miðlæg rými (nettó m² FSRE)</h3>
<div class="scroll">{tbl(["Nr.","Rými","m²","Sama rými á Hamranesi 1. hæð"],rym_kj,numcols=(2,))}</div>
{tbl(["A-rými alls","FSRE brúttó","Þ113 byggt","Frávik","m²/rými FSRE","m²/rými Þ113"],[["Hæðir (4.1 + 4.2)","3.948,0","3.961,5","+13,5","59,8","60,0"],["Kjallari (4.3)","341,6","328,5","−13,1","5,2","5,0"],["Tengigangur (4.4)","44,0","44,0","0","0,7","0,7"],["<b>Samtals = greidd stærð</b>","<b>4.333,6</b>","<b>4.334,0</b>","<b>+0,4</b>","<b>65,7</b>","<b>65,7</b>"],["Viðmið FSRE 65 × 66 / Hamranes raun","4.290","—","—","65,0","69,7"]],numcols=(1,2,3,4,5))}
<h3>Á hvert hjúkrunarrými — samanburðargrunnur FSRE</h3>
<p>FSRE miðar leiguverð við 65 m² brúttó á rými og ber tilboð saman á þeim grunni: tilboð × 4.334 m² / 66 rými = leiga á rými á mánuði. Húsið okkar er {M2R} m²/rými, nákvæmlega greidda talan, á móti 69,7 á Hamranesi.</p>
{tbl(["Tilboð kr/m² m.vsk","Leiga á rými þ.kr/mán","Samanburður"],[["5.650",n0(5650*p['A_paid']/66/1000),"gólf"],["5.750",n0(5750*p['A_paid']/66/1000),"12% í grunni"],["5.850",n0(5850*p['A_paid']/66/1000),"efri mörk ramma"],["Hamranes 5.950 × 65","387","tilboð HH til FSRE 1.7.2026, á 65 m²-grunni"],["Húsavík: Reitir/Rauðsvík 5.645","377","lægsta verð, opnun jan. 2026"],["Húsavík: Pekron 6.350","425","efstur á einkunn"],["Húsavík: Reitir/ÍF 6.775","453","okkar tilboð"]],numcols=(1,))}
<p class="warn">Ekki byggt, þótt það væri á 1. hæð Hamraness: fundarrými 2 × 13,7, forstöðumaður 11,7, fótsnyrting 20,5, hársnyrting 21,8, fjölnotasalur 88,5, miðlægur línlager 29,0, matarvagnar 29,0 — 228 m² nettó sem Þ113-prógrammið biður ekki um (stjórnun Eirs og hársnyrting í 2A, Q&A 5.C). Kjallarinn ber 4.3-listann með álagi 1,35; tæknirými og lyfta/stigi þurfa að rúmast í álaginu. Opnir flóttastigar þurfa staðfestingu brunahönnuðar.</p>
</div>
<div class="co" id="einingar"><h2>3. Einingaskrá VBC — Hamranes-hæðin verðlögð eining fyrir eining</h2>
<p>Hamranes-hæð 2.–5. er 22 einingar af 13 tegundum (einingaskrá VBC jan. 2025; stálgrindarreikningar 2026 gefa stöður 01–22 á hæð). Tólf íbúðaeiningar 4,56 × 16,38 m (74,7 m²) mynda álmurnar: tíu tveggja rýma (IS-10, IS-11 og IS-13 eru sama einingin spegluð, herbergi–gangur–herbergi) og tvær IS-12 með einu rými og skol/þvotti heimiliseiningarinnar. Átta miðeiningar IS-30–IS-37 (376,7 m²) mynda miðsvæðið: setustofur, borðstofur, uppvask, lyftur, forrými, vakt, stoðrými. Tvær stigahúseiningar IS-70 (41,5 m²) eru á endunum með stiga, lagnaskakti og geymslu. Litamerkt scope-plan VBC (2.4.2025) og elemental-sundurliðun samningsins segja hvað VBC afhendir: íbúðarrými og bað fullbúin (green), allt annað sem shell (stálgrind, útveggir, gluggar, gólf, fastir innveggir, 1. fix lagna) — stigar, lyftur, innihurðir, loft, gólfefni og 2./3. fix eru á staðnum. Sama verkaskipting og á Hamranesi, svo Hamranes-hlutföllin í köflum 3–5 bera frágang miðrýmanna án tvítalningar.</p>
<div class="scroll">{tbl(["Eining","Á hæð","m²/ein.","Innihald","Scope VBC","Verðgrunnur","EUR/ein. í Þ113 (m. −3%)","3 hæðir m.kr"],ein_rows,numcols=(1,2,6,7))}</div>
<p class="hl"><b>Hvaðan verðin koma.</b> VBC verðleggur húsið í heild með elemental-sundurliðun, ekki eftir einingategund; Akureyrar-tilboðið er hins vegar á einingu: IS-10 €183.191 og IS-12 €162.093 með BANO, lækkað 7% í €170.367 / €150.745 með léttari stálgrind fyrir steypta kjarna — notuð beint á 36 íbúðaeiningar. Shell-verðið er leitt af Hamranes-samningnum (CO1 Rev5, 3.12.2025): liðir sem gilda jafnt um shell-rými — stálgrind €608/m², klæðning 398, gluggar/útihurðir 36, verksmiðjuvinna 244 — gera €1.286/m² af 6.863 m², × 0,93 = €1.196/m² (173 þ.kr). Stigahúsin falla út: af 41,5 m² fara 24 (stiginn) í opinn stálstiga (liður 7.2) og 17,5 m² standa eftir sem endaeining. Flutningur og uppsetning: Akureyrar-forsendur Sveins €15.000 + €5.594 á einingu (Hamranes-raun CO2 + CO3: €20.009).</p>
{tbl(["Krossprófun","m.kr","Lesið"],[["Einingaskráin (einingar án flutnings/hönnunar)",n0(ein_mod),"Grunnur v1.7: 79% tilboðsverð, 21% afleitt shell-verð"],["Húsavíkur-ROM VBC jan. 2026 ofan frá: €2.043/m² × 0,93 + BANO €6.332/rými, á 3.926 m²",n0(ein_hus),"Sama uppsetning (rými fullbúin, miðrými shell, kjarnar steyptir) — 5% hærra: shell-verðið er varfærið en ekki sannað"],["Aðferð v1.6: allt flatarmál á íbúðaeiningaverði 317 þ/m² × 0,97",n0(317*A['A_mod']*0.97/1000),"Ofmat: miðrými verðlögð eins og fullbúin herbergi"],["Hamranes-raun m. öllum aukaverkum (€16,56 M / 6.863 m²) á sama flatarmál",n0(ein_ham),"Efri mörk (jarðhæð, kjarnar, CO-1…CO-10)"]],numcols=(1,))}
<p class="warn">Óvissa kafla 6 hækkuð úr 3% í 5% (3% á tilboðsliði, 15% á afleidda shell-liði). Shell-verð ±15% = ±37 m.kr og 12% halda í báðum tilvikum. Fastverðsbeiðni til VBC á að vera á þessari einingaskrá: 30 IS-10/11/13, 6 IS-12, 24 IS-30–37 shell, 6 endaeiningar shell, flutningur og uppsetning á einingu.</p>
</div>
<div class="co" id="kostnadur"><h2>4. Kostnaðaráætlun (Class 4, verðlag 2027–28, án VSK)</h2>
<p>ÍF-sniðmátið (kaflar 0–8). Heimildir: Hamranes EAC 3.9.2026 (raun, á m²), einingaskrá VBC (kafli 3: Akureyrar-tilboð 20.4.2026 + Hamranes-samningur; Hamranes-raun m. aukaverkum 388 þ/m²), steypu-/jarðvinnueiningaverð Akureyrar, Þ113-sérliðir (klöpp fleyguð, kjallari botn-upp, tengigangur, 2A-inngrip, gjöld Mosfellsbæjar). Hver liður hefur heimild og rök í Excel.</p>
<div class="scroll">{tbl(["Kafli","m.kr","þ.kr/m²","Helstu liðir"],cost_rows,numcols=(1,2))}</div>
{tbl(["þ.kr á byggðan m² án VSK","Hamranes EAC (6.730 m²)","Akureyri/Heimar (9.100 m²)","Þ113 grunnur (4.334 m²)"],[["Einingar VBC","388","234",n0(C['ch'][6]*1000/A['A_built'])],["Kerfi og frágangur (3–5, 7)","153","178",n0((C['ch'][3]+C['ch'][4]+C['ch'][5]+C['ch'][7])*1000/A['A_built'])],["Burðarvirki + jarðvinna (1–2)","25","77",n0((C['ch'][1]+C['ch'][2])*1000/A['A_built'])],["Aðstaða/umsjón + lóð (0, 8)","46","40",n0((C['ch'][0]+C['ch'][8])*1000/A['A_built'])],["Hönnun, þóknun, annað","127","85",n0((C['des']+C['fee'])*1000/A['A_built'])],["Lóð og gjöld","44","27",n0(C['gj']*1000/A['A_built'])],["<b>Alls f.u. fjármagn</b>","<b>803</b>","<b>702</b>",f"<b>{n0(C['total_exfin']*1000/A['A_built'])}</b>"]],numcols=(1,2,3))}
</div>
<div class="co" id="leiga"><h2>5. Leiguverðs- og ávöxtunarmódel</h2>
<p>Spegill Hamranes-líkans v2.2: 25 ára VNV-tryggð leiga (verðbætt +6,7% frá tilboðsdegi til afhendingar), rekstrarkostnaður eiganda (fasteignaskattur 1,32% + vatn/fráveita 0,17% af fasteignamati, tryggingar 0,12% og viðhald 0,1/0,2/0,3% af brunabótamati, umsýsla 1%), verðmat á NOI árs 1 við 5,7%, framkvæmdalán 65% á 10,2%, endurfjármögnun með verðtryggðu jafngreiðslubréfi RIKS37 2,86% + 100 pkt, LTV 67,7%, skattur 20% með 3% fyrningu, lokavirði ár 25. Verðbólga 4%.</p>
{chart()}
<div class="scroll">{GRID}</div>
{tbl(["Lykiltala við 5.650","Gildi"],[["Nettóleiga ár 1 / NOI ár 1",f"{n0(R['rent1'])} / {n0(R['noi1'])} m.kr"],["Verðmæti við afhendingu @5,7%",f"{n0(R['value'])} m.kr (verðmæti/kostnaður {R['value']/C['total']:.2f})".replace(".",",")],["Framkvæmdalán / eigið fé",f"{n0(R['loan'])} / {n0(R['equity'])} m.kr"],["Skuldabréf 67,7% LTV / losun við endurfjármögnun",f"{n0(R['bond'])} / +{n0(R['release'])} m.kr"],["IRR nafn / raun · NPV@9% · DSCR · MOIC sala strax",f"{pct(R['irr_n'])} / {pct(R['irr_r'])} · +{n0(R['npv'])} · {R['dscr']:.2f} · {R['moic_sale']:.2f}".replace(".",",")]])}
</div>
<div class="co" id="svidsmyndir"><h2>6. Sviðsmyndir</h2>
<div class="scroll">{tbl(["Sviðsmynd","Byggt m²","Umfram","Fjárfesting","þ/greiddan m²","IRR nafn @5.650","IRR raun","NPV@9%","MOIC sala","Leiga f. 12%","Leiga f. 10%"],scen_rows,numcols=tuple(range(1,11)))}</div>
</div>
<div class="co" id="bil"><h2>7. Bilgreining — hvað þarf að vera satt fyrir 5.650 og 12%</h2>
<p>Kostnaðarþakið fyrir 12% við 5.650 er <b>{n0(ceiling)} m.kr</b>; áætlunin er {n0(abs(C['total']-ceiling))} m.kr ({pct(abs(C['total']-ceiling)/C['total'])}) {"undir" if C['total']<ceiling else "yfir"} þakinu — í v1.6 var hún 82 m.kr yfir og í upphaflega prógramminu 667 m.kr (16%) yfir. {"Bilið er lokað en þunnt" if C['total']<ceiling else "Bilið er nánast lokað"}. Hver lyftistöng ein sér, miðað við grunn:</p>
<div class="scroll">{tbl(["Lyftistöng","Fjárfesting","Δ m.kr","IRR @5.650","Leiga f. 12%","Hvað þarf að vera satt"],lev_rows,numcols=(1,2,3,4))}</div>
</div>
<div class="co" id="haefi"><h2>8. Hæfi Stafa (undirritaðir ársreikningar 2025)</h2>
{tbl(["Skilyrði Þ113","Krafa","Stafir – hótel ehf. 2025","Staða"],[["Eigið fé","≥ 2.000 m.kr","3.209,5","✓"],["Leigutekjur","≥ 300 m.kr","587,4 (+ Stafir – verslun 54,5 má leggja við, Q&A 6)","✓"],["Eiginfjárhlutfall","≥ 25%","27,0% (eignir 11.898,5)","✓"],["Eignasafn í rekstri","3 × >1.000 m²","Laugavegur 33–35 (2.961), Grensásvegur 16A (2.955), Hverfisgata 78 (1.424), Skeifan 11 (1.036)","✓"],["Reynsluverk","2 × ≥1.000 m.kr + yfirstjórnandi","ÍF með samstarfsyfirlýsingu: Hamranes, Hyatt Centric, G16A","✓"]])}
<p class="warn">Stafir – hótel ehf. er hæfur bjóðandi án nýs SPV. Athugið: fyrirhuguð 810 m.kr arðgreiðsla 2026 lækkar eigið fé í ~2.400 og hlutfallið í ~21% í ársreikningi 2026; 660 m.kr sjálfskuldarábyrgð fyrir tengd félög. Q&A 6 (4.9.2026): engin frávik frá fjárhagskröfum, leigutekjur má leggja saman úr fleiri félögum með óskiptri ábyrgð og Viðauka I fyrir hvert.</p>
</div>
<div class="co" id="naest"><h2>9. Næstu skref fyrir 9. nóvember</h2>
<ul>
<li><b>Arkís og brunahönnuður:</b> Hamranes-hæðin rúmast á reit 2B (rúmmyndun 24.9., 24–38°, þröngt) — Arkís staðfestir með svölum, opnum stigum og fjarlægðum, setur kjallaraplötu gagnvart Skeiðholti (K 47,83 ~2 m undir götu) og leysir tengiganginn yfir 4 m lagnakvöðina; og standast opnir utanáliggjandi flóttastigar brunahönnun þriggja hæða hjúkrunarheimilis (rýming rúmliggjandi, veðurvörn, hálka)?</li>
<li><b>VBC:</b> fastverðstilboð í einingaskrána (kafli 3): 30 IS-10/11/13 og 6 IS-12 með BANO á Akureyrar-verðum 20.4.2026 (€170.367 / €150.745, endursend af Mark Kane 23.9.), 24 miðeiningar IS-30–37 og 6 stuttar endaeiningar sem shell (afleitt €1.196/m² — eina talan sem VBC þarf að staðfesta), flutningur og uppsetning á einingu, með tafabótaábyrgð; og staðfesting á lækkun fyrir léttara burðarvirki (3 hæðir, 0,15 g) — reiknuð 3% í grunni. Verð án BANO eiga ekki við: BANO-jafngildi er krafa (3.7.2).</li>
<li><b>Fyrirspurnir til FSRE fyrir 31.10.:</b> teljast miðlæg rými í kjallara (jarðhæð frá Skeiðholti) til 4.334 m²? Hvaða miðlæg rými má samnýta með Hömrum um tengiganginn? Teljast opnir utanáliggjandi flóttastigar B-rými (4.5.4) í þessu verki? Gatnagerðargjald Mosfellsbæjar og fasteignaskattsflokkur.</li>
<li><b>Stjórn Stafa:</b> ávöxtunarviðmið (12% nafn) og eigið fé {n0(R['equity'])} m.kr samhliða arðgreiðslu 2026; óskipt ábyrgð ef byggt er á getu annarra.</li>
<li><b>Koma viðbótargögnum FSRE</b> (teikningar Hamra, grunngögn 8.9.2026, minnisblað 24.9.) til Arkís fyrir tengigang og 2A-inngrip; skrá Arkís og verkfræðistofur með kennitölu í tilboðið (Q&A 11).</li>
<li><b>Það sem má ekki gerast:</b> að prógrammið stækki í hönnunarfasa — Q&A 10 gefur FSRE og rekstraraðila rétt til breytinga á rýmisskipan í fullvinnslu á okkar kostnað. Hver 100 m² umfram 4.334 kosta 30–45 m.kr og 0,2–0,5 pp í ávöxtun.</li>
</ul>
</div>
<div class="co" id="skjol"><h2>10. Skjöl og heimildir</h2>
{DL}
<p style="font-size:12.5px;color:#44566b">Frumgögn: útboðslýsing 25-0300, kröfulýsing, húsrýmisáætlun FSRE 17.08.26, samkomulag um byggingarrétt 10.7.2026, GIR Verkís, Q&A 4.9.2026 (mappa Claude Projects/Hamrar Þ113). Kostnaðargrunnar: Hamranes EAC 3.9.2026, VBC Akureyrar-tilboð 20.4.2026 og Hamranes-samningur VBC (elemental breakdown CO1 Rev5 3.12.2025, einingaskrá jan. 2025, scope-plan 2.4.2025, CO2/CO3/CO5), Húsavíkur-ROM VBC des. 2025/jan. 2026, Þursaholt/Heimar-áætlun 30.4.2026, Húsavík 2025. Rekstrar- og fjármögnunarforsendur: Hamranes-líkan v2.2. Rýmisskrá Hamraness 24.8.2026. Hæfi: undirritaðir ársreikningar Stafa 2025 og ársrit ÍFj 2025. Fyrirvarar: Class 4 (±15–25%); gatnagerðargjald staðfest 48,3 þ/m² (Q&A 8) en verðbætt í 49,7, fasteignaskattsflokkur óstaðfestur, breytingar á rýmisskipan að ósk FSRE/rekstraraðila í fullvinnslu (Q&A 10), hæðarsetning kjallara og 4 m lagnakvöð (viðbótargögn 24.9), brunahönnun opinna stiga, 3% lækkun VBC fyrir léttara burðarvirki, shell-verð miðeininga (afleitt, ±15% = ±37 m.kr), EUR/ISK 145 (138 í dag), verðbætur 1,06, kjör Stafa (100 pkt).</p>
<p style="font-size:12px;color:#8898a8">Síðan er reiknuð beint úr Python-spegli Excel-líkansins (model.py); Excel v1.7 er frumheimildin með lifandi formúlum. Unnið fyrir Gunnar Thoroddsen, 4. september 2026, uppfært 24. september 2026.</p>
</div>
</main>
<footer>Þ113 Hamrar · Stafir / Íslenskar fasteignir · trúnaðarmál · <a href="#" onclick="try{{localStorage.removeItem('th113_pass')}}catch(e){{}};location.reload();return false;">Læsa þessu tæki</a></footer>
</body></html>'''
with open(os.path.join(HERE, "app.html"), "w", encoding="utf-8") as f: f.write(page)
print("app.html", len(page)//1024, "KB; base total", round(C['total']), "IRR", round(R['irr_n']*100,1), "ceiling", round(ceiling))
