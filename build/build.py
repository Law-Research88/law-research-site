#!/usr/bin/env python3
"""Genereert de statische HTML-pagina's van law-research.nl (gedeelde header/footer)."""
import json, html, sys
from pathlib import Path

OUT = Path(sys.argv[1])
SITE = "https://law-research.nl"
EMAIL = "blokland@law-research.nl"
FORM = "https://formspree.io/f/JOUW_FORM_ID"
TODAY = "2026-10-13"
ORG_ID = SITE + "/#organisatie"

# ---------- iconen ----------
def svg(body, vb="0 0 24 24", extra=""):
    return (f'<svg viewBox="{vb}" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"{extra}>{body}</svg>')

ICON = {
    # Vrouwe Justitia: weegschaal
    "scale": svg('<path d="M12 3v18"/><path d="M8 21h8"/><path d="M5 7h14"/><path d="M12 4.5l-7 2.5"/><path d="M12 4.5l7 2.5"/>'
                 '<path d="M5 7l-3 7a3 3 0 0 0 6 0z"/><path d="M19 7l-3 7a3 3 0 0 0 6 0z"/>'),
    # Wetgeving: wetboek met paragraafteken
    "wet": svg('<path d="M5 4.5A1.5 1.5 0 0 1 6.5 3H19v15H6.5A1.5 1.5 0 0 0 5 19.5z"/><path d="M5 19.5A1.5 1.5 0 0 0 6.5 21H19v-3"/>'
               '<path d="M13.6 7.3a1.8 1.8 0 1 0-1.8 2.1 1.8 1.8 0 1 1-1.4 2.9"/><path d="M10.3 8.3a1.8 1.8 0 1 0 1.8 2"/>'),
    "bestuur": svg('<path d="M3 10l9-6 9 6"/><path d="M4 10h16"/><path d="M6 10v8M10 10v8M14 10v8M18 10v8"/><path d="M3 21h18"/><path d="M4 18h16"/>'),
    "arbeid": svg('<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7"/><path d="M3 12.5h18"/><path d="M11 12.5v2h2v-2"/>'),
    "contract": svg('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M8.5 13h7M8.5 9.5h3"/><path d="M8.5 17.5c1-1.5 2-1.5 2.5 0s1.5 1.5 2.5 0"/>'),
    "research": svg('<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5"/><path d="M8 10.5h5M10.5 8v5"/>'),
    "lock": svg('<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>'),
    "mail": svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/>'),
    "clock": svg('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    "chat": svg('<path d="M20 15a2 2 0 0 1-2 2H8l-4 4V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z"/><path d="M8 9h8M8 12.5h5"/>'),
    "shield": svg('<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>'),
    "calc": svg('<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2.5v3M16 2.5v3"/><path d="M8 13h.01M12 13h.01M16 13h.01M8 17h.01M12 17h.01"/>'),
    "menu": svg('<path d="M4 7h16M4 12h16M4 17h16"/>'),
}

AREAS = [
    ("bestuursrecht", "Bestuursrecht", "bestuur", "Bezwaar en beroep tegen besluiten van gemeente, UWV, Belastingdienst en andere overheden."),
    ("arbeidsrecht", "Arbeidsrecht", "arbeid", "Ontslag, vaststellingsovereenkomst, ziekte, loon en arbeidscontracten."),
    ("contractenrecht", "Contractenrecht", "contract", "Contracten en algemene voorwaarden opstellen, toetsen en geschillen oplossen."),
]
AREA_NAME = {a[0]: a[1] for a in AREAS}

# ---------- nieuws ----------
# type: "jurisprudentie" (weegschaal) of "wetgeving" (wetboek). Datum = datum van uitspraak / inwerkingtreding.
NEWS = [
    dict(id="deliveroo-bezorgers-werknemers", type="jurisprudentie", gebied="arbeidsrecht", date="2023-03-24",
         datelabel="Uitspraak Hoge Raad, 24 maart 2023",
         title="Bezorgers van Deliveroo zijn gewoon werknemers",
         text="De Hoge Raad besliste dat de maaltijdbezorgers van Deliveroo een arbeidsovereenkomst hadden, ook al stond in hun contract dat ze zelfstandig waren. Wat telt is hoe het werk in de praktijk gaat, niet het etiket op het contract.",
         foryou=["Werkt u als zzp'er, maar werkt u eigenlijk net als een werknemer? Dan heeft u misschien recht op loon bij ziekte, vakantiegeld en ontslagbescherming.",
                 "Werkgever? Kijk kritisch naar uw zzp-afspraken. Een verkeerde inschatting kan achteraf veel geld kosten."],
         source="ECLI:NL:HR:2023:443", url="https://uitspraken.rechtspraak.nl/details?id=ECLI:NL:HR:2023:443"),
    dict(id="wet-transparante-arbeidsvoorwaarden", type="wetgeving", gebied="arbeidsrecht", date="2022-08-01",
         datelabel="In werking sinds 1 augustus 2022",
         title="Bijbaan mag, verplichte cursus is gratis",
         text="Door de Wet transparante en voorspelbare arbeidsvoorwaarden mag een werkgever een bijbaan alleen verbieden als daar een goede reden voor is. Verplichte opleidingen zijn gratis voor de werknemer en tellen als werktijd.",
         foryou=["Verbiedt uw contract elke nevenfunctie zonder uitleg? Dan is dat beding mogelijk niet geldig.",
                 "Moet u studiekosten terugbetalen voor een cursus die verplicht was voor uw functie? Dat hoeft meestal niet."],
         source="Art. 7:653a en 7:611a BW", url="https://wetten.overheid.nl/BWBR0005290/"),
    dict(id="slapend-dienstverband-xella", type="jurisprudentie", gebied="arbeidsrecht", date="2019-11-08",
         datelabel="Uitspraak Hoge Raad, 8 november 2019",
         title="Twee jaar ziek? Uw werkgever mag u niet 'slapend' houden",
         text="Een werkgever die een langdurig zieke werknemer na twee jaar niet ontslaat om de transitievergoeding te ontlopen, moet in principe meewerken aan een beëindiging mét vergoeding. De werkgever kan die vergoeding sinds 2020 terugkrijgen van het UWV.",
         foryou=["Bent u twee jaar of langer ziek en nog steeds in dienst zonder loon? Vraag uw werkgever schriftelijk om beëindiging met transitievergoeding.",
                 "Werkgever? Vraag de compensatie bij het UWV aan, zodat de vergoeding u per saldo weinig kost."],
         source="ECLI:NL:HR:2019:1734 (Xella)", url="https://uitspraken.rechtspraak.nl/details?id=ECLI:NL:HR:2019:1734"),
    dict(id="minimumuurloon", type="wetgeving", gebied="arbeidsrecht", date="2024-01-01",
         datelabel="In werking sinds 1 januari 2024",
         title="Eén minimumloon per uur voor iedereen",
         text="Sinds 1 januari 2024 geldt één wettelijk minimumloon per uur. Het maakt niet meer uit of uw werkgever een werkweek van 36, 38 of 40 uur hanteert. Het bedrag wordt elk half jaar (1 januari en 1 juli) aangepast.",
         foryou=["Controleer uw loonstrook: deel uw brutoloon door het aantal gewerkte uren en vergelijk dat met het actuele minimumuurloon op rijksoverheid.nl.",
                 "Te weinig betaald? U kunt het verschil met terugwerkende kracht vorderen."],
         source="Wet minimumloon en minimumvakantiebijslag", url="https://www.rijksoverheid.nl/onderwerpen/minimumloon"),
    dict(id="evenredigheid-raad-van-state", type="jurisprudentie", gebied="bestuursrecht", date="2022-02-02",
         datelabel="Uitspraak Raad van State, 2 februari 2022",
         title="De overheid moet rekening houden met úw situatie",
         text="De hoogste bestuursrechter (de Raad van State) oordeelde dat een rechter strenger mag toetsen of een besluit evenredig is. Ook als de overheid zich aan de regels houdt, mag de uitkomst voor u niet onredelijk zwaar zijn.",
         foryou=["Pakt een besluit voor u onevenredig hard uit, bijvoorbeeld een boete, terugvordering of sluiting? Leg in uw bezwaar concreet uit wat de gevolgen voor ú zijn.",
                 "Voeg bewijs toe, zoals inkomensgegevens, een medische verklaring of een omzetoverzicht."],
         source="ECLI:NL:RVS:2022:285 (Harderwijk)", url="https://uitspraken.rechtspraak.nl/details?id=ECLI:NL:RVS:2022:285"),
    dict(id="wet-open-overheid", type="wetgeving", gebied="bestuursrecht", date="2022-05-01",
         datelabel="In werking sinds 1 mei 2022",
         title="Overheidsinformatie opvragen? Dat is uw recht",
         text="Met de Wet open overheid (Woo) kan iedereen documenten van de overheid opvragen. U hoeft niet uit te leggen waarom. De overheid moet in principe binnen vier weken beslissen, met maximaal twee weken verlenging.",
         foryou=["Snapt u niet hoe een besluit over u tot stand kwam? Vraag de stukken op met een Woo-verzoek.",
                 "Wees zo concreet mogelijk: noem het onderwerp, de periode en het soort documenten."],
         source="Wet open overheid, art. 4.1 en 4.4", url="https://wetten.overheid.nl/BWBR0045754/"),
    dict(id="omgevingswet", type="wetgeving", gebied="bestuursrecht", date="2024-01-01",
         datelabel="In werking sinds 1 januari 2024",
         title="Omgevingswet: bouwen en verbouwen onder nieuwe regels",
         text="De Omgevingswet bundelt de regels voor bouwen, wonen, milieu en ruimtelijke ordening. Gemeenten werken nu met één omgevingsplan en u vraagt vergunningen aan via het Omgevingsloket.",
         foryou=["Gaat u verbouwen? Check eerst in het Omgevingsloket of u een vergunning nodig heeft.",
                 "Gaat de buren of een bedrijf bouwen en heeft u daar last van? Let goed op de termijnen voor een zienswijze of bezwaar. Die zijn kort."],
         source="Omgevingswet", url="https://omgevingswet.overheid.nl/"),
    dict(id="haviltex-uitleg-contract", type="jurisprudentie", gebied="contractenrecht", date="1981-03-13",
         datelabel="Uitspraak Hoge Raad, 13 maart 1981 (nog altijd leidend)",
         title="Niet alleen de tekst van een contract telt",
         text="Volgens de bekende Haviltex-uitspraak gaat het bij een contract niet alleen om de letterlijke woorden, maar ook om wat partijen redelijkerwijs van elkaar mochten verwachten. Gesprekken, e-mails en omstandigheden spelen dus mee.",
         foryou=["Leg belangrijke afspraken en bedoelingen vast, ook mondelinge, bijvoorbeeld in een bevestigende e-mail.",
                 "Onenigheid over wat er 'bedoeld' werd? Bewaar alle correspondentie: die kan doorslaggevend zijn."],
         source="ECLI:NL:HR:1981:AG4158", url="https://uitspraken.rechtspraak.nl/details?id=ECLI:NL:HR:1981:AG4158"),
    dict(id="consumentenkoop-een-jaar", type="wetgeving", gebied="contractenrecht", date="2022-01-01",
         datelabel="In werking sinds 1 januari 2022",
         title="Product binnen een jaar kapot? De verkoper moet bewijzen",
         text="Gaat een product binnen een jaar na aankoop kapot, dan gaat de wet ervan uit dat het gebrek er al was bij de levering. De verkoper moet dan bewijzen dat dit niet zo is. Vroeger gold dit maar zes maanden.",
         foryou=["Consument? Wijs de winkel op dit 'bewijsvermoeden' als hij zegt dat u het zelf kapot heeft gemaakt.",
                 "Ondernemer? Houd rekening met meer klachten in het eerste jaar en zorg dat uw garantievoorwaarden kloppen."],
         source="Art. 7:18 lid 2 BW", url="https://wetten.overheid.nl/BWBR0005290/"),
    dict(id="incassokosten-14-dagenbrief", type="wetgeving", gebied="contractenrecht", date="2012-07-01",
         datelabel="In werking sinds 1 juli 2012 (vaak over het hoofd gezien)",
         title="Geen incassokosten zonder 14-dagenbrief",
         text="Een bedrijf mag bij een consument pas incassokosten rekenen na een aanmaning waarin de consument nog 14 dagen krijgt om te betalen. Ook de hoogte van de kosten is wettelijk begrensd: 15% over de eerste € 2.500, met een minimum van € 40.",
         foryou=["Krijgt u incassokosten zonder correcte 14-dagenbrief? Dan hoeft u die kosten mogelijk niet te betalen.",
                 "Ondernemer? Gebruik een juiste aanmaning, anders blijft u zelf met de kosten zitten."],
         source="Art. 6:96 BW en Besluit vergoeding voor buitengerechtelijke incassokosten", url="https://wetten.overheid.nl/BWBR0032045/"),
    dict(id="aannemer-aansprakelijk-na-oplevering", type="wetgeving", gebied="contractenrecht", date="2024-01-01",
         datelabel="In werking sinds 1 januari 2024",
         title="Aannemer blijft aansprakelijk voor verborgen gebreken",
         text="Door de Wet kwaliteitsborging voor het bouwen blijft een aannemer ook na de oplevering aansprakelijk voor gebreken die toen niet zijn ontdekt, tenzij hij kan laten zien dat het gebrek niet aan hem ligt. Bij consumenten mag dit niet in het contract worden uitgesloten.",
         foryou=["Ontdekt u na de oplevering een gebrek? Meld het direct schriftelijk bij de aannemer, met foto's.",
                 "Aannemer? Leg uw werk goed vast in een opleverdossier, zodat u kunt aantonen wat u heeft gedaan."],
         source="Art. 7:758 lid 4 BW", url="https://wetten.overheid.nl/BWBR0005290/"),
]

from news_extra import EXTRA
NEWS += EXTRA
for _n in NEWS:
    _n.setdefault("thema", [])
    _n.setdefault("doel", None)
NEWS.sort(key=lambda n: n["date"] or "0000", reverse=True)

THEMA_NAME = {"huurrecht": "Huurrecht", "europees": "Europees & internationaal", "sociale-zekerheid": "Sociale zekerheid"}
DOEL_NAME = {"huurders": "Voor huurders", "verhuurders": "Voor verhuurders"}

def nl_date(iso):
    y, m, d = iso.split("-")
    months = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"]
    return f"{int(d)} {months[int(m)-1]} {y}"

def news_card(n, link=False, heading="h3"):
    t = n["type"]
    icon = ICON["scale"] if t == "jurisprudentie" else ICON["wet"]
    label = "Rechtspraak" if t == "jurisprudentie" else "Wet- en regelgeving"
    cls = "news-type" + (" news-type--wet" if t == "wetgeving" else "")
    title = html.escape(n["title"])
    if link:
        title = f'<a href="nieuws.html#{n["id"]}">{title}</a>'
    bullets = "".join(f"<li>{html.escape(b)}</li>" for b in n["foryou"])
    labels = [THEMA_NAME[x] for x in n["thema"]] + ([DOEL_NAME[n["doel"]]] if n["doel"] else [])
    label_html = ('<div class="news-labels">' + "".join(f'<span class="news-label">{html.escape(l)}</span>' for l in labels) + '</div>') if labels else ""
    when = f'<time datetime="{n["date"]}">{html.escape(n["datelabel"])}</time>' if n["date"] else f'<span>{html.escape(n["datelabel"])}</span>'
    return f'''<article class="news-item reveal" id="{n["id"] if not link else n["id"] + "-kort"}" data-type="{t}" data-gebied="{n["gebied"]}" data-thema="{" ".join(n["thema"])}">
  <div class="news-meta">
    <span class="{cls}" title="{label}">{icon}<span class="visually-hidden">{label}</span></span>
    <div class="news-tags"><strong>{label} · {AREA_NAME[n["gebied"]]}</strong>{when}</div>
  </div>
  {label_html}
  <{heading}>{title}</{heading}>
  <p>{html.escape(n["text"])}</p>
  <div class="for-you"><strong>Wat betekent dit voor u?</strong><ul>{bullets}</ul></div>
  <p class="news-source">Bron: <a href="{n["url"]}" rel="noopener" target="_blank">{html.escape(n["source"])}</a></p>
</article>'''

LEGEND = f'''<div class="news-legend" aria-label="Legenda">
  <span>{ICON["scale"]} Rechtspraak (uitspraken van de rechter)</span>
  <span>{ICON["wet"]} Wet- en regelgeving (nieuwe of gewijzigde regels)</span>
</div>'''

DISCLAIMER = '<p class="disclaimer">Deze berichten geven algemene informatie in begrijpelijke taal en zijn geen juridisch advies. Iedere situatie is anders: neem bij twijfel <a href="contact.html">contact</a> met ons op.</p>'

# ---------- layout ----------
NAV = [("index.html", "Home"), ("__areas__", "Rechtsgebieden"), ("nieuws.html", "Nieuws"),
       ("research.html", "Research"), ("over-ons.html", "Over ons")]

def header(current):
    items = []
    for href, label in NAV:
        if href == "__areas__":
            subs = "".join(f'<li><a href="{a}.html"{" aria-current=\"page\"" if current == a + ".html" else ""}>{n}</a></li>' for a, n, _, _ in AREAS)
            items.append(f'<li class="has-sub"><button class="nav-sub-toggle" type="button" aria-expanded="false">Rechtsgebieden ▾</button><ul class="sub">{subs}</ul></li>')
        else:
            cur = ' aria-current="page"' if current == href else ""
            items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    cur = ' aria-current="page"' if current == "contact.html" else ""
    items.append(f'<li><a class="nav-cta" href="contact.html"{cur}>Contact</a></li>')
    return f'''<a class="skip-link" href="#main">Naar de inhoud</a>
<header class="site-header">
  <div class="container">
    <a class="brand" href="index.html" aria-label="Law &amp; Research, naar de homepage">
      <img src="assets/img/logo-mark.svg" alt="" width="40" height="40">
      <span class="brand-text">Law &amp; Research</span>
    </a>
    <button class="nav-toggle" type="button" aria-controls="site-nav" aria-expanded="false"><span class="visually-hidden">Menu</span>{ICON["menu"]}</button>
    <nav class="nav" id="site-nav" aria-label="Hoofdmenu"><ul>{"".join(items)}</ul></nav>
  </div>
</header>'''

FOOTER = f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a class="brand" href="index.html"><img src="assets/img/logo-mark-white.svg" alt="" width="40" height="40"><span class="brand-text">Law &amp; Research</span></a>
        <p>Juridisch advies en bijstand in bestuursrecht, arbeidsrecht en contractenrecht.</p>
      </div>
      <div>
        <h3>Rechtsgebieden</h3>
        <ul>{"".join(f'<li><a href="{a}.html">{n}</a></li>' for a, n, _, _ in AREAS)}</ul>
      </div>
      <div>
        <h3>Kantoor</h3>
        <ul>
          <li><a href="nieuws.html">Nieuws</a></li>
          <li><a href="research.html">Research</a></li>
          <li><a href="over-ons.html">Over ons</a></li>
          <li><a href="privacy.html">Privacy &amp; disclaimer</a></li>
        </ul>
      </div>
      <div>
        <h3>Contact</h3>
        <ul>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><a href="contact.html">Contactformulier</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span data-year>2026</span> Law &amp; Research · law-research.nl</span>
      <span>Algemene informatie op deze website is geen juridisch advies.</span>
    </div>
  </div>
</footer>
<script src="assets/js/main.js" defer></script>'''

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, indent=1) + '</script>'

def breadcrumb_ld(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + "/" + (u if u != "index.html" else "")}
        for i, (u, n) in enumerate(trail)]}

def breadcrumb_html(trail):
    lis = []
    for i, (u, n) in enumerate(trail):
        if i == len(trail) - 1:
            lis.append(f'<li aria-current="page">{html.escape(n)}</li>')
        else:
            lis.append(f'<li><a href="{u}">{html.escape(n)}</a></li>')
    return f'<nav class="breadcrumb" aria-label="Kruimelpad"><ol>{"".join(lis)}</ol></nav>'

def page(fname, title, desc, body, ld=(), robots="index, follow", og_type="website"):
    url = SITE + "/" + ("" if fname == "index.html" else fname)
    lds = "\n".join(jsonld(x) for x in ld)
    doc = f'''<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="nl-NL" href="{url}">
<meta name="theme-color" content="#1b3d5c">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="nl_NL">
<meta property="og:site_name" content="Law &amp; Research">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Law &amp; Research: bestuursrecht, arbeidsrecht en contractenrecht">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{SITE}/assets/img/og-image.jpg">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="stylesheet" href="assets/css/style.css">
{lds}
</head>
<body>
{header(fname)}
<main id="main">
{body}
</main>
{FOOTER}
</body>
</html>
'''
    (OUT / fname).write_text(doc, encoding="utf-8")

ORG = {
    "@context": "https://schema.org",
    "@type": "LegalService",
    "@id": ORG_ID,
    "name": "Law & Research",
    "alternateName": "Law and Research",
    "url": SITE + "/",
    "logo": SITE + "/assets/img/icon-512.png",
    "image": SITE + "/assets/img/og-image.jpg",
    "email": EMAIL,
    "description": "Juridisch advies en bijstand voor particulieren en ondernemers in bestuursrecht, arbeidsrecht en contractenrecht.",
    "areaServed": {"@type": "Country", "name": "Nederland"},
    "availableLanguage": ["nl", "en"],
    "knowsAbout": ["Bestuursrecht", "Arbeidsrecht", "Contractenrecht", "Ambtenarenrecht", "Bezwaar en beroep", "Ontslagrecht", "Algemene voorwaarden"],
    "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Rechtsgebieden", "itemListElement": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "url": f"{SITE}/{a}.html"}} for a, n, _, _ in AREAS]},
    "contactPoint": {"@type": "ContactPoint", "contactType": "customer service", "email": EMAIL, "availableLanguage": ["Dutch", "English"]},
    # Vul hier later adres en telefoon aan (zie LEESMIJ.txt):
    # "address": {"@type": "PostalAddress", "streetAddress": "...", "postalCode": "...", "addressLocality": "...", "addressCountry": "NL"},
    # "telephone": "+31 ...",
}

def contact_aside(area=None):
    return f'''<aside class="aside-card">
  <h3>Direct uw vraag voorleggen</h3>
  <p>Beschrijf kort uw situatie. U hoort snel van ons of en hoe wij u kunnen helpen. Het eerste contact is vrijblijvend.</p>
  <a class="btn btn--light" href="contact.html{"?onderwerp=" + area if area else ""}">Neem contact op</a>
  <p style="margin-top:18px;font-size:.95rem">Of mail naar <a href="mailto:{EMAIL}">{EMAIL}</a></p>
</aside>'''

def contact_form(prefill=None):
    opts = "".join(f'<option value="{n}">{n}</option>' for _, n, _, _ in AREAS) + '<option value="Anders / weet ik niet">Anders / weet ik niet</option>'
    return f'''<form class="form" data-form action="{FORM}" method="POST" data-success="Bedankt voor uw bericht! Wij nemen zo snel mogelijk contact met u op.">
  <input type="hidden" name="_subject" value="Nieuw bericht via law-research.nl">
  <input type="hidden" name="formulier" value="Contact">
  <input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div class="form-row">
    <div class="field"><label for="naam">Naam</label><input id="naam" name="naam" autocomplete="name" required></div>
    <div class="field"><label for="email">E-mailadres</label><input id="email" name="email" type="email" autocomplete="email" required></div>
  </div>
  <div class="form-row">
    <div class="field"><label for="telefoon">Telefoonnummer <span class="opt">(optioneel)</span></label><input id="telefoon" name="telefoon" type="tel" autocomplete="tel"></div>
    <div class="field"><label for="rechtsgebied">Waar gaat uw vraag over?</label><select id="rechtsgebied" name="rechtsgebied">{opts}</select></div>
  </div>
  <div class="field"><label for="ikben">Ik ben</label><select id="ikben" name="ik_ben"><option>Particulier</option><option>Ondernemer / organisatie</option></select></div>
  <div class="field"><label for="bericht">Uw vraag</label><textarea id="bericht" name="bericht" required placeholder="Beschrijf kort wat er speelt en of er een termijn loopt (bijvoorbeeld een bezwaartermijn of ontslagdatum)."></textarea></div>
  <label class="consent"><input type="checkbox" name="toestemming" value="ja" required> Ik ga akkoord dat Law &amp; Research mijn gegevens gebruikt om contact met mij op te nemen (zie de <a href="privacy.html">privacyverklaring</a>).</label>
  <div class="form-status" role="status" aria-live="polite" hidden></div>
  <div><button class="btn btn--primary" type="submit">Verstuur bericht</button></div>
</form>
<script>
(function(){{var p=new URLSearchParams(location.search).get("onderwerp");if(!p)return;var m={{bestuursrecht:"Bestuursrecht",arbeidsrecht:"Arbeidsrecht",contractenrecht:"Contractenrecht"}};var s=document.getElementById("rechtsgebied");if(s&&m[p])s.value=m[p];}})();
</script>'''

def faq_html(faqs):
    return '<div class="faq">' + "".join(
        f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in faqs) + "</div>"

def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def hero_page(trail, eyebrow, h1, lead):
    return f'''<section class="hero hero--page">
  <img class="hero-mark" src="assets/img/logo-mark-white.svg" alt="" aria-hidden="true">
  <div class="container">
    {breadcrumb_html(trail)}
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>'''

def cta_band():
    return f'''<section class="section section--navy">
  <div class="container cta">
    <div><h2>Loopt er een termijn?</h2><p>Wacht niet te lang. Bij bezwaar, ontslag en geschillen gelden vaak korte termijnen.</p></div>
    <a class="btn btn--light" href="contact.html">Leg uw vraag voor</a>
  </div>
</section>'''

# ---------- homepage ----------
def build_home():
    picks = "".join(f'''<a href="{a}.html"><span class="icon-badge">{ICON[i]}</span><span><strong>{n}</strong><span>{d}</span></span></a>''' for a, n, i, d in AREAS)
    home_news = [n for n in NEWS if n["id"] in ("tesco-gelijk-loon", "vast-huurcontract-de-regel", "recht-op-hoorzitting")]
    body = f'''<section class="hero">
  <img class="hero-mark" src="assets/img/logo-mark-white.svg" alt="" aria-hidden="true">
  <div class="container">
    <span class="eyebrow">Rechtsbijstand &amp; juridisch onderzoek</span>
    <h1>Helder juridisch advies dat u verder helpt</h1>
    <p class="lead">Persoonlijke bijstand in bestuursrecht, arbeidsrecht en contractenrecht. Voor particulieren en ondernemers, in begrijpelijke taal en met een duidelijke aanpak.</p>
    <div class="hero-actions">
      <a class="btn btn--light" href="contact.html">Stel uw vraag</a>
      <a class="btn btn--ghost" href="#rechtsgebieden">Bekijk rechtsgebieden</a>
    </div>
    <p class="hero-note">Weten wat wij doen, is uw goed recht.</p>
  </div>
</section>

<section class="picker">
  <div class="container">
    <div class="picker-box">
      <h2>Waar gaat uw vraag over?</h2>
      <div class="picker-grid">{picks}</div>
    </div>
  </div>
</section>

<section class="section" id="rechtsgebieden">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Rechtsgebieden</span>
      <h2>Gespecialiseerd in drie rechtsgebieden</h2>
      <p class="lead">Wij richten ons bewust op drie gebieden. Zo kennen we de regels, de rechtspraak en de praktijk door en door.</p>
    </div>
    <div class="grid-3">
      <article class="card reveal"><span class="icon-badge">{ICON["bestuur"]}</span><h3>Bestuursrecht</h3>
        <p>Bent u het niet eens met een besluit van de gemeente, het UWV, de Belastingdienst of een andere overheid? Wij helpen bij bezwaar en beroep.</p>
        <ul><li>Bezwaar en beroep</li><li>Vergunningen en handhaving</li><li>Uitkeringen en toeslagen</li><li>Ambtenarenrecht</li></ul>
        <a class="more" href="bestuursrecht.html">Meer over bestuursrecht</a></article>
      <article class="card reveal"><span class="icon-badge">{ICON["arbeid"]}</span><h3>Arbeidsrecht</h3>
        <p>Voor werknemers én werkgevers. Van arbeidscontract en ziekte tot ontslag en vaststellingsovereenkomst.</p>
        <ul><li>Ontslag en vaststellingsovereenkomst</li><li>Ziekte en re-integratie</li><li>Loon en arbeidsvoorwaarden</li><li>Concurrentiebeding</li></ul>
        <a class="more" href="arbeidsrecht.html">Meer over arbeidsrecht</a></article>
      <article class="card reveal"><span class="icon-badge">{ICON["contract"]}</span><h3>Contractenrecht</h3>
        <p>Goede afspraken voorkomen problemen. Wij stellen contracten op, toetsen ze en helpen als het toch misgaat.</p>
        <ul><li>Contracten en algemene voorwaarden</li><li>Koop, huur en aanneming</li><li>Wanprestatie en ontbinding</li><li>Incasso en geschillen</li></ul>
        <a class="more" href="contractenrecht.html">Meer over contractenrecht</a></article>
    </div>
  </div>
</section>

<section class="section section--tint">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Nieuws</span>
      <h2>Wat betekent het nieuws voor u?</h2>
      <p class="lead">Korte berichten over nieuwe uitspraken en regels, met praktische tips.</p>
    </div>
    {LEGEND}
    <div class="news-list news-list--home">{"".join(news_card(n, link=True) for n in home_news)}</div>
    <p style="margin-top:28px"><a class="btn btn--outline" href="nieuws.html">Alle nieuwsberichten</a></p>
  </div>
</section>

<section class="section">
  <div class="container grid-2">
    <div class="reveal">
      <span class="eyebrow">Onze aanpak</span>
      <h2>Persoonlijk, toegewijd en duidelijk</h2>
      <p>Law &amp; Research is opgericht door mr. Blokland. Zij heeft ruim 20 jaar ervaring als jurist, manager en voormalig advocaat, onder meer bij de FNV en bij verschillende banken. Die praktijkervaring ziet u terug in ons advies: concreet en gericht op een oplossing.</p>
      <ul class="check-list">
        <li>Ruim 20 jaar juridische ervaring.</li>
        <li>U weet vooraf waar u aan toe bent, ook wat de kosten betreft.</li>
        <li>Advies in begrijpelijke taal, zonder juridisch jargon.</li>
        <li>Voor particulieren én ondernemers.</li>
      </ul>
      <a class="btn btn--primary" href="over-ons.html">Meer over ons</a>
    </div>
    <div class="card reveal">
      <span class="icon-badge">{ICON["research"]}</span>
      <h3>Research</h3>
      <p>Naast rechtsbijstand doen wij juridisch onderzoek: analyses, jurisprudentieoverzichten en praktische checklists. Een deel van dit materiaal stellen wij op aanvraag beschikbaar voor professionals en organisaties.</p>
      <a class="more" href="research.html">Toegang aanvragen</a>
    </div>
  </div>
</section>
{cta_band()}'''
    website = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/",
               "name": "Law & Research", "inLanguage": "nl-NL", "publisher": {"@id": ORG_ID}}
    page("index.html", "Law & Research | Rechtsbijstand bestuursrecht, arbeidsrecht en contractenrecht",
         "Law & Research: helder juridisch advies in bestuursrecht, arbeidsrecht en contractenrecht voor particulieren en ondernemers.",
         body, ld=(ORG, website))

# ---------- rechtsgebieden ----------
AREA_PAGES = {
 "bestuursrecht": dict(
  title="Rechtsbijstand bestuursrecht | Bezwaar en beroep | Law & Research",
  desc="Niet eens met een besluit van de gemeente, het UWV of de Belastingdienst? Law & Research helpt bij bezwaar en beroep in het bestuursrecht. Inclusief rekenhulp bezwaartermijn.",
  h1="Bestuursrecht: niet eens met de overheid?",
  lead="Als burger of ondernemer krijgt u regelmatig te maken met besluiten van de overheid. Bent u het daar niet mee eens? Dan kunt u bij ons terecht voor gedegen advies en bijstand.",
  intro='''<h2>Waarmee wij u helpen</h2>
<p>U komt in aanraking met de overheid via uw gemeente of provincie, maar ook via instanties als de Belastingdienst, het UWV, het waterschap of de Dienst Toeslagen. Is een besluit volgens u onjuist of onredelijk? Dan is het belangrijk om snel en goed te reageren.</p>''',
  particulier='''<ul class="check-list">
<li>Bezwaar tegen een besluit over uw uitkering, toeslag of belastingaanslag</li>
<li>Terugvordering of boete van een overheidsinstantie</li>
<li>Bouwplannen in uw omgeving (Omgevingswet)</li>
<li>Woo-verzoek: stukken opvragen bij de overheid</li>
<li>Ambtenarenrecht: werkt u bij het Rijk, een gemeente of onderwijsinstelling en speelt er een geschil?</li>
</ul>''',
  ondernemer='''<ul class="check-list">
<li>Vergunningen en ontheffingen, bijvoorbeeld voor (ver)bouwen, evenementen of de verkoop van alcohol</li>
<li>Handhaving: last onder dwangsom, bestuurlijke boete of sluiting</li>
<li>Subsidies: aanvraag, vaststelling en terugvordering</li>
<li>Bezwaar en beroep bij de rechtbank en de Raad van State</li>
</ul>
<p>Veel ondernemers ervaren wet- en regelgeving als een jungle. Wij helpen u de weg te vinden.</p>''',
  extra='''<h2>Rekenhulp: tot wanneer kunt u bezwaar maken?</h2>
<p>De termijn voor bezwaar is meestal <strong>zes weken</strong>. Die begint op de dag na de dag waarop het besluit is bekendgemaakt (meestal de datum van de brief).</p>
<div class="tool" id="bezwaar-calc">
  <div class="field"><label for="besluitdatum">Datum van het besluit (bekendmaking)</label><input type="date" id="besluitdatum"></div>
  <div class="tool-result" aria-live="polite" hidden></div>
  <p class="disclaimer">Indicatie op basis van art. 6:7 en 6:8 Awb en de Algemene termijnenwet. Soms geldt een andere termijn; die staat dan onder het besluit. Twijfelt u? Neem contact op.</p>
</div>''',
  faqs=[("Hoe lang heb ik om bezwaar te maken?", "Meestal zes weken, gerekend vanaf de dag na de dag waarop het besluit is bekendgemaakt. Valt de laatste dag in een weekend of op een feestdag, dan schuift de termijn op naar de eerstvolgende werkdag."),
        ("Wat gebeurt er als ik te laat ben?", "Een te laat bezwaar wordt meestal niet-ontvankelijk verklaard. Dan wordt er niet meer inhoudelijk naar gekeken. Alleen in uitzonderlijke situaties wordt een termijnoverschrijding verschoonbaar geacht. Reageer daarom altijd op tijd, desnoods met een kort 'pro forma' bezwaar."),
        ("Wat is een pro forma bezwaar?", "Een kort bezwaarschrift om de termijn veilig te stellen, waarin u aangeeft dat de gronden (de inhoudelijke argumenten) later volgen. U krijgt dan meestal een extra termijn om het bezwaar aan te vullen."),
        ("Kan ik een vergoeding krijgen voor de kosten?", "Wordt het besluit in bezwaar of beroep herroepen omdat het onrechtmatig was, dan kunt u een vergoeding van proceskosten vragen. Een rechtsbijstandsverzekering kan de kosten soms ook dekken."),
        ("Geldt voor ambtenaren nog het bestuursrecht?", "Sinds 1 januari 2020 vallen de meeste ambtenaren onder het gewone arbeidsrecht (Wet normalisering rechtspositie ambtenaren). Voor bepaalde groepen, zoals militairen en politie, gelden nog bijzondere regels. Wij kijken graag mee welke regels voor u gelden.")],
 ),
 "arbeidsrecht": dict(
  title="Rechtsbijstand arbeidsrecht | Ontslag en vaststellingsovereenkomst | Law & Research",
  desc="Juridische hulp bij arbeidsrecht voor werknemers en werkgevers: ontslag, vaststellingsovereenkomst, ziekte, loon en arbeidscontracten. Law & Research.",
  h1="Arbeidsrecht voor werknemers en werkgevers",
  lead="Het arbeidsrecht lijkt eenvoudig: werk tegen loon. Toch kunnen er in een arbeidsrelatie veel conflicten ontstaan. Wij kennen de wet, de cao-praktijk en de rechtspraak.",
  intro='''<h2>Waarmee wij u helpen</h2>
<p>Bij de afspraken tussen werkgever en werknemer spelen vaak wettelijke regels én cao-bepalingen een rol. Heeft u een conflict, of wilt u weten wat uw rechten en plichten zijn? Wij staan u bij, van advies tot procedure.</p>''',
  particulier='''<ul class="check-list">
<li>Ontslag op staande voet of een ontslagprocedure via UWV of kantonrechter</li>
<li>Beoordelen van een vaststellingsovereenkomst en onderhandelen over de vergoeding</li>
<li>Ziekte, re-integratie en een slapend dienstverband</li>
<li>Loonvordering, vakantiegeld en transitievergoeding</li>
<li>Concurrentie- en relatiebeding</li>
</ul>
<p>Mr. Blokland heeft ruim 20 jaar juridische ervaring, onder meer als jurist bij de FNV, en kent de positie van werknemers van dichtbij.</p>''',
  ondernemer='''<ul class="check-list">
<li>Opstellen van arbeidsovereenkomsten, personeelsregelingen en vaststellingsovereenkomsten</li>
<li>Advies en mediation bij arbeidsgeschillen</li>
<li>Ontslag op de juiste manier: dossieropbouw, UWV en kantonrechter</li>
<li>Zzp-constructies en schijnzelfstandigheid</li>
<li>Arbeidsrechtelijke gevolgen van een overname: neem in een vroeg stadium contact op</li>
</ul>
<p>U houdt zich bezig met uw onderneming, wij met de arbeidsrechtelijke kant ervan.</p>''',
  extra="",
  faqs=[("Moet ik een vaststellingsovereenkomst direct tekenen?", "Nee. Teken nooit onder druk. U heeft na ondertekening bovendien 14 dagen bedenktijd waarin u de overeenkomst zonder opgave van redenen kunt ontbinden. Staat die bedenktermijn niet in de overeenkomst, dan is dat drie weken. Laat de overeenkomst vóór ondertekening controleren, ook in verband met uw WW-uitkering."),
        ("Hoe snel moet ik reageren op een ontslag op staande voet?", "Snel. Wilt u het ontslag laten vernietigen, dan moet u dat binnen twee maanden na het ontslag aan de kantonrechter vragen. Protesteer daarnaast direct schriftelijk en geef aan dat u beschikbaar blijft om te werken."),
        ("Heb ik recht op een transitievergoeding?", "In de meeste gevallen wel, als de werkgever het initiatief neemt tot ontslag of een tijdelijk contract niet verlengt. Dit geldt vanaf de eerste werkdag. Bij ernstig verwijtbaar handelen van de werknemer kan het recht vervallen."),
        ("Ik ben zzp'er, maar werk eigenlijk als werknemer. Wat nu?", "Volgens de Hoge Raad (Deliveroo, 2023) gaat het om hoe er in de praktijk gewerkt wordt, niet om wat er in het contract staat. Mogelijk heeft u dan rechten als werknemer. Wij beoordelen uw situatie graag."),
        ("Wat kost juridische hulp bij arbeidsrecht?", "Dat hangt af van uw zaak. Wij bespreken vooraf wat u kunt verwachten. Bij een vaststellingsovereenkomst betaalt de werkgever vaak (een deel van) de kosten van juridisch advies. Ook een rechtsbijstandsverzekering kan de kosten dekken.")],
 ),
 "contractenrecht": dict(
  title="Rechtsbijstand contractenrecht | Contracten en algemene voorwaarden | Law & Research",
  desc="Hulp bij het opstellen en toetsen van contracten en algemene voorwaarden, en bij geschillen over koop, huur, aanneming en wanprestatie. Law & Research.",
  h1="Contractenrecht: goede afspraken, minder problemen",
  lead="Het contractenrecht (verbintenissenrecht) is de basis van alle overeenkomsten. Wij helpen u afspraken goed vast te leggen en staan u bij als een ander zich er niet aan houdt.",
  intro='''<h2>Waarmee wij u helpen</h2>
<p>Of het nu gaat om een aankoop die niet aan de verwachtingen voldoet, een huurwoning met gebreken of een leverancier die niet levert: wij denken met u mee en zoeken naar de beste oplossing, bij voorkeur zonder rechter.</p>''',
  particulier='''<ul class="check-list">
<li>Een aankoop is kapot of niet zoals beloofd en de verkoper weigert te helpen</li>
<li>Geschil met uw verhuurder of gebreken aan uw woning</li>
<li>Problemen met een aannemer of verbouwing</li>
<li>Onterechte incassokosten of een betwiste rekening</li>
</ul>''',
  ondernemer='''<ul class="check-list">
<li>Opstellen en beoordelen van contracten en algemene voorwaarden</li>
<li>Huurovereenkomsten, ontruiming en het innen van huurachterstand</li>
<li>Geschillen met klanten of leveranciers: wanprestatie, ontbinding, schadevergoeding</li>
<li>Incasso: van correcte aanmaning tot procedure</li>
</ul>''',
  extra="",
  faqs=[("Is een mondelinge afspraak ook een contract?", "Ja, in de meeste gevallen is een mondelinge afspraak net zo geldig als een schriftelijke. Het probleem zit in het bewijs. Leg belangrijke afspraken daarom altijd schriftelijk vast, al is het maar in een bevestigende e-mail."),
        ("Wat moet ik doen als de andere partij zich niet aan het contract houdt?", "Stuur een schriftelijke ingebrekestelling: een brief waarin u de ander een redelijke termijn geeft om alsnog na te komen. Pas daarna kunt u in veel gevallen schadevergoeding eisen of het contract ontbinden."),
        ("Zijn mijn algemene voorwaarden geldig?", "Alleen als u ze vóór of bij het sluiten van de overeenkomst aan de klant heeft gegeven (de informatieplicht). Bepaalde bedingen zijn bovendien verboden of vernietigbaar, zeker tegenover consumenten. Laat uw voorwaarden periodiek toetsen."),
        ("Hoe lang heb ik garantie op een product?", "De wet kent geen vaste garantietermijn: een product moet zo lang meegaan als u redelijkerwijs mag verwachten. Gaat het binnen een jaar kapot, dan moet de verkoper bewijzen dat het gebrek er bij aankoop nog niet was."),
        ("Mag een bedrijf zomaar incassokosten rekenen?", "Bij consumenten alleen na een correcte aanmaning met een betaaltermijn van 14 dagen, en tot een wettelijk maximum. Tussen bedrijven gelden andere regels.")],
 ),
}

def build_area(slug):
    p = AREA_PAGES[slug]
    name = AREA_NAME[slug]
    icon = dict((a, i) for a, _, i, _ in AREAS)[slug]
    trail = [("index.html", "Home"), (slug + ".html", name)]
    rel = [n for n in NEWS if n["gebied"] == slug][:3]
    body = f'''{hero_page(trail, name, p["h1"], p["lead"])}
<section class="section">
  <div class="container layout-aside">
    <div class="prose">
      {p["intro"]}
      <div data-tabs>
        <div class="split-tabs" role="group" aria-label="Kies uw situatie">
          <button class="chip" type="button" data-tab="tab-part" aria-pressed="true">Voor particulieren</button>
          <button class="chip" type="button" data-tab="tab-ond" aria-pressed="false">Voor ondernemers</button>
        </div>
        <div class="tab-panel" id="tab-part"><h3>Voor particulieren</h3>{p["particulier"]}</div>
        <div class="tab-panel" id="tab-ond" hidden><h3>Voor ondernemers</h3>{p["ondernemer"]}</div>
      </div>
      {p["extra"]}
      <h2>Veelgestelde vragen over {name.lower()}</h2>
      {faq_html(p["faqs"])}
    </div>
    {contact_aside(slug)}
  </div>
</section>
<section class="section section--tint">
  <div class="container">
    <div class="section-head"><span class="eyebrow">Nieuws</span><h2>Actueel in het {name.lower()}</h2></div>
    {LEGEND}
    <div class="news-list news-list--home">{"".join(news_card(n, link=True) for n in rel)}</div>
    <p style="margin-top:28px"><a class="btn btn--outline" href="nieuws.html?gebied={slug}">Al het nieuws over {name.lower()}</a></p>
  </div>
</section>
{cta_band()}'''
    service = {"@context": "https://schema.org", "@type": "Service", "name": name, "serviceType": f"Juridisch advies {name.lower()}",
               "provider": {"@id": ORG_ID}, "areaServed": {"@type": "Country", "name": "Nederland"},
               "url": f"{SITE}/{slug}.html", "description": p["desc"]}
    page(slug + ".html", p["title"], p["desc"], body, ld=(ORG, service, breadcrumb_ld(trail), faq_ld(p["faqs"])))

# ---------- nieuws ----------
def build_news():
    trail = [("index.html", "Home"), ("nieuws.html", "Nieuws")]
    items = list(NEWS)
    chips_type = "".join(f'<button class="chip" type="button" data-filter="type" data-value="{v}" aria-pressed="false">{l}</button>'
                         for v, l in [("alle", "Alles"), ("jurisprudentie", "Rechtspraak"), ("wetgeving", "Wet- en regelgeving")])
    chips_area = "".join(f'<button class="chip" type="button" data-filter="gebied" data-value="{v}" aria-pressed="false">{l}</button>'
                         for v, l in [("alle", "Alle rechtsgebieden")] + [(a, n) for a, n, _, _ in AREAS])
    chips_thema = "".join(f'<button class="chip" type="button" data-filter="thema" data-value="{v}" aria-pressed="false">{l}</button>'
                         for v, l in [("alle", "Alle onderwerpen")] + list(THEMA_NAME.items()))
    body = f'''{hero_page(trail, "Nieuws", "Juridisch nieuws in gewone taal", "Korte, praktische berichten over uitspraken en wetten in het bestuursrecht, arbeidsrecht en contractenrecht, ook uit het Europese en internationale recht. Bij elk bericht leest u: wat betekent dit voor u?")}
<section class="section section--tint">
  <div class="container">
    {LEGEND}
    <div class="filters" aria-label="Nieuws filteren">
      <div class="group" role="group" aria-label="Soort bericht">{chips_type}</div>
      <div class="group" role="group" aria-label="Rechtsgebied">{chips_area}</div>
      <div class="group" role="group" aria-label="Onderwerp">{chips_thema}</div>
    </div>
    <div class="news-list" data-news-list>{"".join(news_card(n, heading="h2") for n in items)}</div>
    <p data-news-empty hidden>Er zijn geen berichten voor deze selectie.</p>
    {DISCLAIMER}
  </div>
</section>
{cta_band()}'''
    arts = [{"@type": "Article", "headline": n["title"], "description": n["text"], "datePublished": TODAY, "dateModified": TODAY,
             "inLanguage": "nl-NL", "url": f'{SITE}/nieuws.html#{n["id"]}', "image": SITE + "/assets/img/og-image.jpg",
             "about": AREA_NAME[n["gebied"]], "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}} for n in items]
    lst = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Juridisch nieuws", "url": SITE + "/nieuws.html",
           "inLanguage": "nl-NL", "mainEntity": {"@type": "ItemList", "itemListElement": [
               {"@type": "ListItem", "position": i + 1, "item": a} for i, a in enumerate(arts)]}}
    page("nieuws.html", "Juridisch nieuws in begrijpelijke taal | Law & Research",
         "Praktisch nieuws over rechtspraak en nieuwe wetten in bestuursrecht, arbeidsrecht en contractenrecht. Steeds met de vraag: wat betekent dit voor u?",
         body, ld=(ORG, lst, breadcrumb_ld(trail)))

# ---------- research ----------
def build_research():
    trail = [("index.html", "Home"), ("research.html", "Research")]
    locked = [
        ("Van Tesco naar loontransparantie", "Europees & internationaal", "Hoe Europees recht het Nederlandse arbeidsrecht vormgeeft: van gelijk loon voor gelijkwaardig werk tot de nieuwe Europese regels voor salaristransparantie."),
        ("Jurisprudentieoverzicht ontslag op staande voet", "Arbeidsrecht", "Analyse van recente uitspraken: wanneer houdt een ontslag op staande voet stand en wanneer niet?"),
        ("Evenredigheid in het bestuursrecht na 2022", "Bestuursrecht", "Hoe toetsen rechters besluiten sinds de uitspraak van de Raad van State over het evenredigheidsbeginsel?"),
        ("Checklist algemene voorwaarden voor het mkb", "Contractenrecht", "Praktische toets van de meest voorkomende bedingen en de valkuilen bij consumenten."),
        ("Schijnzelfstandigheid na Deliveroo", "Arbeidsrecht", "Wat betekent het arrest voor opdrachtgevers en zzp'ers? Een overzicht van de lagere rechtspraak."),
        ("Onderzoek op maat", "Alle rechtsgebieden", "Heeft u een specifieke juridische onderzoeksvraag? Wij verzorgen analyses en memo's op maat."),
    ]
    cards = "".join(f'''<article class="card lock-card reveal">
  <span class="lock-pill">{ICON["lock"]} Toegang op aanvraag</span>
  <h3>{html.escape(t)}</h3>
  <p style="font-size:.9rem;color:var(--navy-600);font-weight:600">{html.escape(a)}</p>
  <p>{html.escape(d)}</p>
  <p class="blur" aria-hidden="true">Samenvatting, conclusies en bronnen zijn beschikbaar na goedkeuring van uw aanvraag.</p>
</article>''' for t, a, d in locked)
    opts = "".join(f'<label class="consent"><input type="checkbox" name="interesse" value="{n}"> {n}</label>' for _, n, _, _ in AREAS)
    body = f'''{hero_page(trail, "Research", "Juridisch onderzoek, op aanvraag beschikbaar", "Naast onze rechtsbijstand doen wij juridisch onderzoek. Analyses, jurisprudentieoverzichten en checklists stellen wij beschikbaar voor professionals, organisaties en studenten. Vraag hieronder toegang aan.")}
<section class="section">
  <div class="container">
    <div class="section-head"><span class="eyebrow">Publicaties</span><h2>Beschikbaar na goedkeuring</h2>
      <p class="lead">Na uw aanvraag beoordelen wij of wij u toegang kunnen geven. U ontvangt bericht per e-mail.</p></div>
    <div class="grid-3">{cards}</div>
  </div>
</section>
<section class="section section--tint" id="aanvragen">
  <div class="container layout-aside">
    <div>
      <span class="eyebrow">Toegang aanvragen</span>
      <h2>Vraag toegang aan tot Research</h2>
      <form class="form" data-form action="{FORM}" method="POST" data-success="Bedankt! Uw aanvraag is ontvangen. Wij beoordelen deze en sturen u bericht per e-mail.">
        <input type="hidden" name="_subject" value="Aanvraag toegang Research via law-research.nl">
        <input type="hidden" name="formulier" value="Research toegang">
        <input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
        <div class="form-row">
          <div class="field"><label for="r-naam">Naam</label><input id="r-naam" name="naam" autocomplete="name" required></div>
          <div class="field"><label for="r-email">E-mailadres</label><input id="r-email" name="email" type="email" autocomplete="email" required></div>
        </div>
        <div class="form-row">
          <div class="field"><label for="r-org">Organisatie <span class="opt">(optioneel)</span></label><input id="r-org" name="organisatie" autocomplete="organization"></div>
          <div class="field"><label for="r-rol">Ik ben</label><select id="r-rol" name="rol"><option>Advocaat / jurist</option><option>Ondernemer / HR</option><option>Overheid</option><option>Student / onderzoeker</option><option>Anders</option></select></div>
        </div>
        <fieldset class="field" style="border:0;padding:0;margin:0"><legend style="font-weight:600;color:var(--navy-800);margin-bottom:6px">Interesse in</legend><div style="display:grid;gap:6px">{opts}</div></fieldset>
        <div class="field"><label for="r-motivatie">Waarvoor wilt u het materiaal gebruiken?</label><textarea id="r-motivatie" name="motivatie" required></textarea></div>
        <label class="consent"><input type="checkbox" name="toestemming" value="ja" required> Ik ga akkoord met de verwerking van mijn gegevens voor deze aanvraag (zie de <a href="privacy.html">privacyverklaring</a>).</label>
        <div class="form-status" role="status" aria-live="polite" hidden></div>
        <div><button class="btn btn--primary" type="submit">Vraag toegang aan</button></div>
      </form>
    </div>
    <aside class="aside-card">
      <h3>Hoe werkt het?</h3>
      <ol style="padding-left:1.2em">
        <li>U vult het formulier in.</li>
        <li>Wij beoordelen uw aanvraag.</li>
        <li>Bij goedkeuring ontvangt u per e-mail toegang tot het gevraagde materiaal.</li>
      </ol>
      <p>Vragen? Mail naar <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    </aside>
  </div>
</section>'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "Research", "url": SITE + "/research.html",
          "inLanguage": "nl-NL", "publisher": {"@id": ORG_ID}, "isAccessibleForFree": False}
    page("research.html", "Juridisch onderzoek en publicaties | Research | Law & Research",
         "Juridische analyses, jurisprudentieoverzichten en checklists over bestuursrecht, arbeidsrecht en contractenrecht. Vraag toegang aan bij Law & Research.",
         body, ld=(ORG, ld, breadcrumb_ld(trail)))

# ---------- over ons ----------
def build_about():
    trail = [("index.html", "Home"), ("over-ons.html", "Over ons")]
    body = f'''{hero_page(trail, "Over ons", "Over Law &amp; Research", "Persoonlijk juridisch advies, gebouwd op gedegen onderzoek. Law &amp; Research combineert rechtsbijstand met juridisch onderzoek.")}
<section class="section">
  <div class="container grid-2">
    <div class="prose reveal">
      <h2>Ons verhaal</h2>
      <p>Law &amp; Research is opgericht door mr. Blokland. Zij heeft ruim 20 jaar ervaring als jurist, manager en voormalig advocaat, onder meer bij de FNV en bij verschillende bancaire instellingen. Met die achtergrond én juridische kennis van zaken weet zij wat er in de praktijk speelt, aan beide kanten van de tafel.</p>
      <p>Onze naam zegt waar wij voor staan: naast advies en procederen doen wij gedegen juridisch onderzoek. Die kennis komt direct ten goede aan onze cliënten.</p>
      <h2>Waar wij voor staan</h2>
      <ul class="check-list">
        <li><strong>Persoonlijk:</strong> u heeft één vast aanspreekpunt dat uw zaak kent.</li>
        <li><strong>Toegewijd:</strong> wij zetten ons volledig in voor uw belang.</li>
        <li><strong>Kwaliteit:</strong> grondig onderzoek als basis voor elk advies.</li>
        <li><strong>Duidelijk:</strong> advies in begrijpelijke taal, met vooraf heldere afspraken over de kosten.</li>
      </ul>
    </div>
    <div class="reveal">
      <div class="card">
        <h3>Stage bij Law &amp; Research</h3>
        <p>Ben je masterstudent rechten met een specialisatie in arbeidsrecht, bestuursrecht of contractenrecht? Wij bieden een leerzame praktijkstage van acht weken, met meewerken aan lopende zaken en het bijwonen van zittingen.</p>
        <a class="more" href="mailto:{EMAIL}?subject=Stage%20Law%20%26%20Research">Stuur je cv en motivatie</a>
      </div>
    </div>
  </div>
</section>
<section class="section section--navy">
  <div class="container">
    <span class="eyebrow">Rechtsgebieden</span>
    <h2>Gespecialiseerd in drie gebieden</h2>
    <div class="stats">
      <div><strong><a href="bestuursrecht.html" style="color:inherit">Bestuursrecht</a></strong>Bezwaar en beroep tegen de overheid</div>
      <div><strong><a href="arbeidsrecht.html" style="color:inherit">Arbeidsrecht</a></strong>Voor werknemers en werkgevers</div>
      <div><strong><a href="contractenrecht.html" style="color:inherit">Contractenrecht</a></strong>Contracten, voorwaarden en geschillen</div>
    </div>
  </div>
</section>'''
    ld = {"@context": "https://schema.org", "@type": "AboutPage", "name": "Over Law & Research", "url": SITE + "/over-ons.html",
          "inLanguage": "nl-NL", "about": {"@id": ORG_ID}}
    page("over-ons.html", "Over ons | Law & Research",
         "Maak kennis met Law & Research: persoonlijk juridisch advies in bestuursrecht, arbeidsrecht en contractenrecht, toegewijd en met kwaliteit.",
         body, ld=(ORG, ld, breadcrumb_ld(trail)))

# ---------- contact ----------
def build_contact():
    trail = [("index.html", "Home"), ("contact.html", "Contact")]
    body = f'''{hero_page(trail, "Contact", "Neem contact op", "Stel uw vraag via het formulier of mail ons direct. Wij reageren zo snel mogelijk, meestal binnen één werkdag.")}
<section class="section">
  <div class="container layout-aside">
    <div>
      <h2>Stuur ons een bericht</h2>
      {contact_form()}
    </div>
    <aside class="aside-card">
      <h3>Contactgegevens</h3>
      <p>{ICON["mail"].replace('<svg', '<svg style="width:20px;height:20px;display:inline;vertical-align:-4px;margin-right:6px"')}<a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p>{ICON["clock"].replace('<svg', '<svg style="width:20px;height:20px;display:inline;vertical-align:-4px;margin-right:6px"')}Afspraken in overleg, ook buiten kantooruren.</p>
      <h3 style="margin-top:24px">Loopt er een termijn?</h3>
      <p>Vermeld dat duidelijk in uw bericht, bijvoorbeeld de datum van een besluit of ontslag. Dan geven wij uw vraag voorrang.</p>
    </aside>
  </div>
</section>'''
    ld = {"@context": "https://schema.org", "@type": "ContactPage", "name": "Contact", "url": SITE + "/contact.html",
          "inLanguage": "nl-NL", "about": {"@id": ORG_ID}}
    page("contact.html", "Contact | Law & Research",
         "Neem contact op met Law & Research voor advies in bestuursrecht, arbeidsrecht of contractenrecht. Mail naar blokland@law-research.nl of gebruik het contactformulier.",
         body, ld=(ORG, ld, breadcrumb_ld(trail)))

# ---------- privacy ----------
def build_privacy():
    trail = [("index.html", "Home"), ("privacy.html", "Privacy & disclaimer")]
    body = f'''{hero_page(trail, "Juridisch", "Privacy, disclaimer en kantoorgegevens", "Hoe wij met uw gegevens omgaan en wat u van de informatie op deze website kunt verwachten.")}
<section class="section">
  <div class="container prose">
    <h2>Privacyverklaring</h2>
    <p>Law &amp; Research verwerkt persoonsgegevens die u zelf aan ons verstrekt, bijvoorbeeld via het contactformulier of per e-mail. Wij gebruiken deze gegevens alleen om uw vraag te beantwoorden, om u juridisch bij te staan en om aanvragen voor Research te beoordelen.</p>
    <ul>
      <li><strong>Formulieren:</strong> berichten via onze formulieren worden verwerkt door de dienst Formspree en daarna per e-mail aan ons doorgestuurd.</li>
      <li><strong>Bewaartermijn:</strong> wij bewaren gegevens niet langer dan nodig, met inachtneming van wettelijke bewaarplichten.</li>
      <li><strong>Cookies:</strong> deze website plaatst geen tracking- of advertentiecookies.</li>
      <li><strong>Uw rechten:</strong> u kunt ons vragen uw gegevens in te zien, te corrigeren of te verwijderen via <a href="mailto:{EMAIL}">{EMAIL}</a>. U kunt ook een klacht indienen bij de Autoriteit Persoonsgegevens.</li>
      <li><strong>Vertrouwelijkheid:</strong> wij gaan vertrouwelijk om met alle informatie die u ons toevertrouwt.</li>
    </ul>
    <h2>Disclaimer</h2>
    <p>De informatie op deze website, waaronder de nieuwsberichten, is algemeen van aard en bedoeld als eerste uitleg in begrijpelijke taal. Het is geen juridisch advies voor uw specifieke situatie. Hoewel wij de informatie met zorg samenstellen, kunnen wetten en rechtspraak veranderen. Aan de inhoud kunnen geen rechten worden ontleend.</p>
    <h2>Kantoorgegevens</h2>
    <!-- Vul deze gegevens in vóór livegang (zie LEESMIJ.txt). -->
    <ul>
      <li>Naam: Law &amp; Research</li>
      <li>E-mail: <a href="mailto:{EMAIL}">{EMAIL}</a></li>
      <li>Adres: [in te vullen]</li>
      <li>KvK-nummer: [in te vullen] · Btw-nummer: [in te vullen]</li>
      <li>Beroepsaansprakelijkheidsverzekering: [indien aanwezig, in te vullen]</li>
      <li>Algemene voorwaarden en klachtenregeling: op verzoek kosteloos verkrijgbaar via e-mail</li>
    </ul>
  </div>
</section>'''
    page("privacy.html", "Privacyverklaring en disclaimer | Law & Research",
         "Privacyverklaring, disclaimer en kantoorgegevens van Law & Research.",
         body, ld=(breadcrumb_ld(trail),))

def build_404():
    body = f'''<section class="hero hero--page"><div class="container">
  <span class="eyebrow">Fout 404</span><h1>Deze pagina bestaat niet (meer)</h1>
  <p class="lead">Misschien is de pagina verplaatst. Kijk hieronder verder of ga terug naar de homepage.</p>
  <div class="hero-actions"><a class="btn btn--light" href="/">Naar de homepage</a><a class="btn btn--ghost" href="/nieuws.html">Nieuws</a><a class="btn btn--ghost" href="/contact.html">Contact</a></div>
</div></section>'''
    page("404.html", "Pagina niet gevonden | Law & Research", "Deze pagina bestaat niet of is verplaatst.", body, robots="noindex, follow")
    # 404 wordt vanaf elke diepte getoond: maak relatieve paden absoluut
    p = OUT / "404.html"
    t = p.read_text(encoding="utf-8")
    for a in ('href="assets/', 'src="assets/', 'href="index.html', 'href="nieuws.html', 'href="research.html', 'href="over-ons.html',
              'href="contact.html', 'href="privacy.html', 'href="bestuursrecht.html', 'href="arbeidsrecht.html', 'href="contractenrecht.html'):
        t = t.replace(a, a.replace('="', '="/'))
    p.write_text(t, encoding="utf-8")

def build_meta():
    pages = [("", "1.0", "weekly"), ("bestuursrecht.html", "0.9", "monthly"), ("arbeidsrecht.html", "0.9", "monthly"),
             ("contractenrecht.html", "0.9", "monthly"), ("nieuws.html", "0.8", "weekly"), ("research.html", "0.6", "monthly"),
             ("over-ons.html", "0.6", "yearly"), ("contact.html", "0.7", "yearly"), ("privacy.html", "0.2", "yearly")]
    urls = "".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority></url>\n" for u, p, c in pages)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /404.html\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (OUT / "site.webmanifest").write_text(json.dumps({
        "name": "Law & Research", "short_name": "Law & Research", "lang": "nl", "start_url": "/", "display": "browser",
        "background_color": "#ffffff", "theme_color": "#1b3d5c",
        "icons": [{"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=1), encoding="utf-8")

if __name__ == "__main__":
    build_home()
    for a, _, _, _ in AREAS:
        build_area(a)
    build_news(); build_research(); build_about(); build_contact(); build_privacy(); build_404(); build_meta()
    print("ok")
