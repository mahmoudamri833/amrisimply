#!/usr/bin/env python3
"""Pont entre produits.json (editable a la main) et index.html.

  python3 outils/produits.py extraire    cree produits.json depuis index.html
  python3 outils/produits.py construire  reecrit les cartes de index.html depuis produits.json
  python3 outils/produits.py controler   verifie liens affilies et mentions

Securite : "construire" avec un produits.json inchange doit redonner un
index.html strictement identique, sinon le script s'arrete sans rien ecrire.
"""
import json, re, sys, pathlib

HTML = pathlib.Path("index.html")
JSON_ = pathlib.Path("produits.json")
TAG = "tag=amrisimply49-21"
MENTION = "As an Amazon Associate I earn from qualifying purchases"

RE_BLOC = re.compile(r'(<div class="cards">)(.*?)(</div>\s*</section>)', re.S)
RE_CARTE = re.compile(r'<article class="card[^"]*">.*?</article>', re.S)
RE_POINTS = re.compile(r'<li><span class="lg-fr">(.*?)</span><span class="lg-nl">(.*?)</span></li>', re.S)
RE_UL = re.compile(r'(<ul>)(.*?)(\s*</ul>)', re.S)

CHAMPS = [
    ("badge_fr",    r'(<span class="badge"><span class="lg-fr">)(.*?)(</span>)'),
    ("badge_nl",    r'(<span class="badge"><span class="lg-fr">.*?</span><span class="lg-nl">)(.*?)(</span>)'),
    ("marque",      r'(<div class="brandname">)(.*?)(</div>)'),
    ("titre",       r'(<h3>)(.*?)(</h3>)'),
    ("etoiles",     r'(<span class="stars">)(.*?)(</span>)'),
    ("note_avis",   r'(<span class="stars">.*?</span> <span>)(.*?)(\s?<span class="lg-fr">)'),
    ("argument_fr", r'(<p class="why"><span class="lg-fr">)(.*?)(</span>)'),
    ("argument_nl", r'(<p class="why"><span class="lg-fr">.*?</span><span class="lg-nl">)(.*?)(</span>)'),
    ("prix_niveau", r'(<span class="tierdots"><b>)(.*?)(</b>)'),
    ("prix_reste",  r'(<span class="tierdots"><b>.*?</b><i>)(.*?)(</i>)'),
    ("palier_fr",   r'(<span class="tierlabel"><span class="lg-fr">)(.*?)(</span>)'),
    ("palier_nl",   r'(<span class="tierlabel"><span class="lg-fr">.*?</span><span class="lg-nl">)(.*?)(</span>)'),
    ("lien",        r'(<a class="btn wide" href=")(.*?)(")'),
]


def bloc_cartes(html):
    m = RE_BLOC.search(html)
    if not m:
        sys.exit('ERREUR : bloc <div class="cards"> introuvable dans index.html')
    return m


def lire_carte(carte):
    p = {}
    for nom, motif in CHAMPS:
        m = re.search(motif, carte, re.S)
        p[nom] = m.group(2) if m else None
    points = RE_POINTS.findall(carte)
    p["points_fr"] = [a for a, b in points]
    p["points_nl"] = [b for a, b in points]
    return p


def ecrire_carte(carte, p):
    for nom, motif in CHAMPS:
        valeur = p.get(nom)
        if valeur is None:
            continue
        carte, n = re.subn(motif, lambda m: m.group(1) + str(valeur) + m.group(3), carte, count=1, flags=re.S)
        if n == 0:
            print("ATTENTION : le champ '%s' n'existe pas dans cette carte, valeur ignoree" % nom)
    m = RE_UL.search(carte)
    if m:
        lis = "".join(
            '\n          <li><span class="lg-fr">%s</span><span class="lg-nl">%s</span></li>' % (fr, nl)
            for fr, nl in zip(p["points_fr"], p["points_nl"])
        )
        carte = carte[:m.start(2)] + lis + carte[m.end(2):]
    return carte


def reconstruire(html, produits):
    m = bloc_cartes(html)
    corps = m.group(2)
    cartes = RE_CARTE.findall(corps)
    if not cartes:
        sys.exit("ERREUR : aucune carte produit trouvee dans index.html")
    sorties = [ecrire_carte(cartes[i] if i < len(cartes) else cartes[-1], p) for i, p in enumerate(produits)]
    debut = corps[:corps.find(cartes[0])]
    fin = corps[corps.rfind(cartes[-1]) + len(cartes[-1]):]
    return html[:m.start(2)] + debut + debut.join(sorties) + fin + html[m.end(2):]


def extraire():
    html = HTML.read_text(encoding="utf-8")
    produits = [lire_carte(c) for c in RE_CARTE.findall(bloc_cartes(html).group(2))]
    for i, p in enumerate(produits, 1):
        absents = [k for k, v in p.items() if v is None]
        if absents:
            print("Carte %d : champs absents de la mise en page (laisses a null) : %s" % (i, ", ".join(absents)))
    if reconstruire(html, produits) != html:
        sys.exit("ERREUR : l'aller-retour n'est pas fidele, produits.json n'a pas ete cree")
    JSON_.write_text(json.dumps(produits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("%d produits extraits vers produits.json (aller-retour verifie a l'identique)" % len(produits))


def construire():
    html = HTML.read_text(encoding="utf-8")
    produits = json.loads(JSON_.read_text(encoding="utf-8"))
    if not produits:
        sys.exit("ERREUR : produits.json est vide")
    nouveau = reconstruire(html, produits)
    if nouveau == html:
        print("Aucun changement : index.html est deja a jour.")
        return
    HTML.write_text(nouveau, encoding="utf-8")
    print("index.html mis a jour (%d produits)." % len(produits))


def controler():
    html = HTML.read_text(encoding="utf-8")
    liens = re.findall(r'href="(https://www\.amazon\.com\.be/[^"]+)"', html)
    cartes = RE_CARTE.findall(bloc_cartes(html).group(2))
    pbs = []
    if not liens:
        pbs.append("aucun lien Amazon dans la page")
    for l in liens:
        if TAG not in l:
            pbs.append("lien sans tag affilie : %s" % l)
    if JSON_.exists():
        n = len(json.loads(JSON_.read_text(encoding="utf-8")))
        if n != len(cartes):
            pbs.append("%d cartes dans index.html mais %d produits dans produits.json" % (len(cartes), n))
    if MENTION not in html:
        pbs.append("mention Amazon Associates absente")
    if pbs:
        sys.exit("CONTROLE ECHOUE :\n- " + "\n- ".join(pbs))
    print("Controle OK : %d cartes, %d liens Amazon tous tagues, mention presente." % (len(cartes), len(liens)))


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "extraire":
        extraire()
    elif action == "construire":
        construire(); controler()
    elif action == "controler":
        controler()
    else:
        sys.exit("usage: produits.py extraire|construire|controler")
