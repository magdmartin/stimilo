#!/usr/bin/env python3
"""Structural checks on the built site. Run after `bundle exec jekyll build`.

Usage: python3 tests/check_site.py [name-substring ...]
"""
import html as htmllib
import pathlib
import re
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent / "_site"
CHECKS = []


def check(fn):
    CHECKS.append(fn)
    return fn


def html(rel):
    p = SITE / rel
    assert p.exists(), f"missing _site/{rel}"
    return p.read_text(encoding="utf-8")


def exists(rel):
    assert (SITE / rel).is_file(), f"missing _site/{rel}"


def text(rel):
    """Visible text: tags stripped, entities decoded, smart quotes and spaces normalised."""
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", html(rel), flags=re.S)
    s = htmllib.unescape(re.sub(r"<[^>]+>", " ", s))
    for a, b in {"’": "'", "‘": "'", "“": '"', "”": '"',
                 " ": " ", " ": " ", "‑": "-", "–": "-"}.items():
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s)


def css():
    return html("assets/css/main.css").lower()


@check
def check_existing_post_url():
    html("notes/2026/08/08/ten-questions-before-you-feed-data-to-an-ai.html")


@check
def check_feed():
    assert "ten-questions-before-you-feed-data-to-an-ai" in html("feed.xml")


@check
def check_no_hydejack():
    hits = [str(p.relative_to(SITE)) for p in SITE.rglob("*")
            if p.is_file() and p.suffix in {".html", ".css", ".js"}
            and "hydejack" in p.read_text(encoding="utf-8", errors="ignore").lower()]
    assert not hits, f"hydejack still referenced in: {hits[:5]}"


@check
def check_theme_is_minimal_mistakes():
    assert "minimal-mistakes" in css() or ".masthead" in css(), "MM stylesheet not built"


BOOKING = "https://meeting.calendarhero.com/stimilodiscoverymartin"


@check
def check_brand_css():
    c = css()
    assert "#0056b3" in c, "brand blue missing from CSS"
    assert re.search(r"\.btn--primary\{[^}]*background-color:#0056b3", c), "primary button not blue"
    assert "sora" in c and "inter" in c, "brand fonts not set"


@check
def check_nav_en():
    h = html("notes/2026/08/08/ten-questions-before-you-feed-data-to-an-ai.html")
    assert 'href="/blog/"' in h and 'href="/contact/"' in h and 'href="/fr/"' in h, "EN nav links missing"
    assert f'class="btn btn--primary masthead__cta" href="{BOOKING}"' in h, "Book a call button missing"
    assert "Book a call" in h


@check
def check_footer():
    t = text("notes/2026/08/08/ten-questions-before-you-feed-data-to-an-ai.html")
    assert "martin@stimilo.com" in t and "LinkedIn" in t, "footer contact missing"
    assert "Powered by" not in t, "theme credit still in footer"


@check
def check_favicons():
    h = html("notes/2026/08/08/ten-questions-before-you-feed-data-to-an-ai.html")
    assert "/assets/icons/favicon.svg" in h and "/assets/icons/apple-touch-icon.png" in h
    assert "#0056B3" in html("assets/icons/favicon.svg")
    exists("assets/icons/favicon.ico")
    exists("assets/icons/apple-touch-icon.png")


# No fee amounts on the public site (Martin, 2026-09-30). AI-cost figures like "$2 a day" are proof, not prices.
PRICE_EN = re.compile(r"\$\d{1,3},\d{3}|CAD")
PRICE_FR = re.compile(r"\d{1,3} \d{3} \$")
HOME_SECTIONS = ["hero", "audience", "work", "phases", "about", "cta"]


@check
def check_home_en_structure():
    h = html("index.html")
    for s in HOME_SECTIONS:
        assert f'id="{s}"' in h, f"section #{s} missing"
    assert h.count(f'href="{BOOKING}"') == 3, "booking link: masthead, hero, CTA banner"
    assert 'href="mailto:martin@stimilo.com"' in h


@check
def check_home_en_numbers():
    t = text("index.html")
    for s in ["Punch above your weight.",
              "Turn your team's expertise into a system.",
              "a 200-investor pipeline on his own", "for under $2 a day in AI cost",
              "7 analyst hours back each week",
              "analyst time fell from 4.5 to 1.5 hours per ticket",
              "30% on signing",
              "hourly or per deliverable",
              "once the workload is predictable",
              "2 to 6 weeks", "3 to 12 months", "Optional"]:
        assert s in t, f"missing on /: {s!r}"
    assert not PRICE_EN.search(t), f"price on /: {PRICE_EN.search(t).group()!r}"


@check
def check_fr_lang_and_nav():
    h = html("fr/index.html")
    assert '<html lang="fr-CA"' in h, "FR page should be fr-CA (Québec market)"
    assert 'class="site-title" href="/fr/"' in h, "wordmark should link to /fr/"
    assert '>EN</a>' in h and '>FR</a>' not in h, "FR page should show EN toggle only"
    assert "Réserver un appel" in h
    en = html("index.html")
    assert '<html lang="en' in en and "Réserver un appel" not in en, "FR leaked into EN"


@check
def check_hreflang():
    for page in ["index.html", "fr/index.html"]:
        h = html(page)
        assert 'hreflang="en" href="https://stimilo.com/"' in h, f"{page}: en alternate"
        assert 'hreflang="fr" href="https://stimilo.com/fr/"' in h, f"{page}: fr alternate"


@check
def check_home_fr_numbers():
    t = text("fr/index.html")
    for s in ["Donner à votre équipe une plus grande portée.",
              "un pipeline de 200 investisseurs", "pour moins de 2 $ par jour en coût d'IA",
              "7 heures d'analyste récupérées chaque semaine",
              "le temps d'analyste passe de 4 h 30 à 1 h 30 par ticket",
              "30 % à la signature",
              "à l'heure ou au livrable",
              "2 à 6 semaines", "3 à 12 mois", "Optionnel"]:
        assert s in t, f"missing on /fr/: {s!r}"
    assert not PRICE_FR.search(t), f"price on /fr/: {PRICE_FR.search(t).group()!r}"
    h = html("fr/index.html")
    for s in HOME_SECTIONS:
        assert f'id="{s}"' in h, f"/fr/ section #{s} missing"


POST = "notes/2026/08/08/ten-questions-before-you-feed-data-to-an-ai.html"


@check
def check_blog_list():
    h = html("blog/index.html")
    assert f'href="/{POST}"' in h, "post missing from /blog/"
    assert "A checklist written in 2019" in text("blog/index.html"), "description missing"
    for u in ["/blog/case-studies/", "/blog/notes/"]:
        assert f'href="{u}"' in h, f"side menu link {u} missing"


@check
def check_notes_category():
    assert f'href="/{POST}"' in html("blog/notes/index.html")


@check
def check_empty_category():
    h = html("blog/case-studies/index.html")
    assert "No posts yet." in text("blog/case-studies/index.html")
    assert 'href="/blog/notes/"' in h, "side menu missing on empty category"


@check
def check_blog_html_redirect():
    h = html("blog.html")
    assert 'http-equiv="refresh"' in h and "/blog/" in h


@check
def check_post_page_clean():
    h = html(POST)
    for bad in ["author__avatar", "page__share", "page__related", "page__comments"]:
        assert bad not in h, f"post page still has {bad}"
    assert "Ten questions" in text(POST)


@check
def check_contact():
    h = html("contact/index.html")
    assert f'href="{BOOKING}"' in h and 'href="mailto:martin@stimilo.com"' in h
    assert 'href="https://www.linkedin.com/in/magdinier"' in h
    assert "<form" not in h, "no contact form"


@check
def check_404():
    t = text("404.html")
    assert "Page not found" in t and "/blog/" in html("404.html")



@check
def check_home_descriptions():
    for page in ["index.html", "fr/index.html"]:
        m = re.search(r'<meta name="description" content="([^"]*)"', html(page))
        assert m and "Montréal" in m.group(1), f"{page}: no specific meta description"



@check
def check_hero_photo_no_band():
    for page in ["index.html", "fr/index.html"]:
        h = html(page)
        assert 'id="statement"' not in h and "band--blue" not in h, f"{page}: blue band still there"
        hero = h[h.index('id="hero"'):h.index('id="audience"')]
        assert 'class="hero__media"' in hero, f"{page}: no photo block in hero"
        assert re.search(r'<img src="/assets/img/Martin\.jpeg" alt="Martin Magdinier"', hero), f"{page}: hero photo missing"
        assert hero.index('class="hero__title"') < hero.index('class="hero__text"'), f"{page}: title must sit above the text/photo row"



@check
def check_home_content():
    """Lighter than the 2-pager, but keeps who-it's-for, case context and outcome support (Martin, 2026-09-30)."""
    for page, gone, kept in [
        ("index.html",
         ["Engagement.", "Fees: fixed price, 2 to 6 weeks", "end to end", "4.4", "1.6 hours", "Starting point", "What we built", "every email personalized", "It finds precedent"],
         ["Who this is for, and what you get",
          "Owners and leaders of services or operations-heavy organizations with fewer than 25 people",
          "I come in when the way the work gets done has to change: a technology shift, the arrival of AI, a new generation taking over.",
          "Example deliverables", "Key-person dependency matrix", "90/180-day roadmap", "AI agent development",
          "The process scales with the volume; governance stays with your experts.",
          "The know-how stays in the company.",
          "Canadian asset manager, $1B+.",
          "a script that scores 14,000 investor records on his own criteria, and AI that drafts his emails overnight",
          "eight ticket types became written procedures an AI agent follows",
          "An analyst reviews every fix before it goes live.",
          "Analyst know-how, turned into procedures",
          "Provider Directory, a healthcare data platform fed by 300+ Canadian registries.",
          "What we're after: fewer manual interventions",
          "fixed price. 30% on signing", "hourly or per deliverable.",
          "About me", "With more than fifteen years of experience, I combine operational analysis",
          "Co-building & shared learning"]),
        ("fr/index.html",
         ["Financement possible", "Service Québec", "ESSOR", "Intervention.", "codifi",
          "L'IA est utilisée", "Point de départ", "Ce que nous avons bâti", "chaque courriel personnalisé", "Il cherche les précédents",
          "prix fixe, 2 à 6 semaines"],
         ["À qui cela s'adresse, et ce que vous y gagnez",
          "Dirigeants d'organisations de services ou à forte composante opérationnelle",
          "J'interviens quand la façon de travailler doit changer : virage technologique, arrivée de l'IA, nouvelle génération.",
          "Exemples de livrables", "Matrice des dépendances aux personnes clés", "Création d'agents IA",
          "Un standard tenu en tout temps, inscrit dans les opérations plutôt qu'en mémoire.",
          "Gestionnaire d'actifs canadien, plus de 1 G$.",
          "un script qui classe 14 000 investisseurs selon ses propres critères",
          "huit types de tickets sont devenus des procédures écrites qu'un agent IA applique",
          "Un analyste valide chaque correction avant la mise en production.",
          "Provider Directory, répertoire de fournisseurs de soins de santé alimenté par plus de 300 registres canadiens.",
          "Le résultat recherché : moins d'interventions manuelles",
          "prix fixe. 30 % à la signature",
          "Je travaille principalement avec des structures de moins de 25 personnes",
          "À propos", "Avec plus de quinze ans d'expérience", "Apprendre ensemble"]),
    ]:
        t = text(page)
        for g in gone:
            assert g not in t, f"{page}: should be cut: {g!r}"
        for k in kept:
            assert k in t, f"{page}: missing: {k!r}"
        h = html(page)
        assert h.count('class="process__step"') == 3, f"{page}: phases should be one row of 3 steps"
        assert h.count('class="process__fees"') == 3, f"{page}: each step needs its fees line"
        for step in h.split('class="process__step"')[1:]:
            assert step.index("process__time") < step.index("process__fees") < step.index("process__summary"), f"{page}: fees should follow the duration"
        assert "process__cta" not in h, f"{page}: mid-page button should be gone"
        phases = h[h.index('id="phases"'):h.index('id="about"')]
        assert phases.count('class="deliverables__item"') == 9, f"{page}: 9 deliverable tags under the phases"
        about = h[h.index('id="about"'):h.index('id="cta"')]
        assert 'class="values"' in about and "about__text" in about, f"{page}: values belong inside About"


@check
def check_fr_numbers_dont_wrap():
    h = html("fr/index.html")
    for n in ["14\u00a0000", "1\u00a0G$", "2\u00a0$", "4\u00a0h\u00a030", "1\u00a0h\u00a030", "30\u00a0%", "7\u00a0heures"]:
        assert n in h, f"FR number should use non-breaking spaces: {n!r}"


@check
def check_no_justified_text():
    # Theme ships an unused .text-justify utility; only our home rules matter
    c = css()
    rules = re.findall(r"([^{}]*)\{([^{}]*text-align:justify[^{}]*)\}", c)
    ours = [sel.strip() for sel, _ in rules if sel.strip() != ".text-justify"]
    assert not ours, f"justified text removed (Martin, 2026-09-30): {ours}"


@check
def check_phase_rows_align():
    assert "subgrid" in css(), "phase steps should share rows (subgrid) so fees lines align"



# ---- Search and discovery --------------------------------------------------

@check
def check_sitemap_and_robots():
    sm = html("sitemap.xml")
    for u in ["https://stimilo.com/", "https://stimilo.com/fr/", "https://stimilo.com/blog/", f"https://stimilo.com/{POST}"]:
        assert f"<loc>{u}</loc>" in sm, f"sitemap missing {u}"
    assert "404" not in sm, "404 page should not be in the sitemap"
    assert "case-studies" not in sm, "empty case-studies page stays out of the sitemap until the first one ships"
    assert "Sitemap: https://stimilo.com/sitemap.xml" in html("robots.txt")


@check
def check_home_keywords_and_location():
    for page, eyebrow in [("index.html", "Operations, Process & AI Consultant · Montréal"),
                          ("fr/index.html", "Consultant en opérations, processus et IA · Montréal")]:
        hero = text(page)
        assert eyebrow in hero, f"{page}: keyword + location line missing in hero"
        assert "Montréal" in text(page).split("Let's talk")[0] or "Montréal" in hero


@check
def check_structured_data():
    for page in ["index.html", "fr/index.html"]:
        h = html(page)
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
        import json
        data = [json.loads(b) for b in blocks]
        svc = [d for d in data if d.get("@type") == "ProfessionalService"]
        assert svc, f"{page}: no ProfessionalService JSON-LD"
        d = svc[0]
        assert d["address"]["addressLocality"] == "Montréal" and d["founder"]["name"] == "Martin Magdinier" and d["founder"]["jobTitle"] in ("Operations, Process & AI Consultant", "Consultant en opérations, processus et IA")
        assert "sameAs" not in d, f"{page}: LinkedIn belongs to the founder, not the business"
        assert "https://www.linkedin.com/in/magdinier" in d["founder"]["sameAs"]
        assert "Montréal" in d["description"], f"{page}: business description should say where"
        assert all(x.get("name") for x in data), f"{page}: JSON-LD block with empty name: {data}"


@check
def check_hreflang_x_default():
    for page in ["index.html", "fr/index.html"]:
        assert 'hreflang="x-default" href="https://stimilo.com/"' in html(page), f"{page}: x-default missing"


@check
def check_page_descriptions():
    default = "Operations, Process &amp; AI Consultant — Montréal"
    for page in ["blog/index.html", "blog/case-studies/index.html", "blog/notes/index.html", "contact/index.html"]:
        m = re.search(r'<meta name="description" content="([^"]*)"', html(page))
        assert m and m.group(1) != default and len(m.group(1)) > 40, f"{page}: needs its own description"



@check
def check_title_is_consultant():
    """Title settled as Operations & Transformation Consultant; fractional is only part of the offer (Martin, 2026-09-30)."""
    assert "<title>Operations, Process &amp; AI Consultant in Montréal - stimilo</title>" in html("index.html")
    assert "<title>Consultant en opérations, processus et IA à Montréal - stimilo</title>" in html("fr/index.html")
    for page in ["index.html", "fr/index.html", "blog/index.html", "blog/case-studies/index.html", "blog/notes/index.html", "contact/index.html"]:
        h = html(page).lower()
        assert "fractional" not in h and "temps partagé" not in h and "transformation consultant" not in h and "opérations et transformation" not in h, f"{page}: old title still present"



@check
def check_home_meta_descriptions_full():
    for page, want in [("index.html", "Operations, Process & AI Consultant in Montréal. I turn your team's expertise into a system"),
                       ("fr/index.html", "Consultant en opérations, processus et IA à Montréal. Je transforme l'expertise de votre équipe en système")]:
        m = re.search(r'<meta name="description" content="([^"]*)"', html(page))
        got = htmllib.unescape(m.group(1)).replace("\u2019", "'")
        assert got.startswith(want), f"{page}: description is {got!r}"
    m = re.search(r'<meta name="description" content="([^"]*)"', html("blog/index.html"))
    assert "case studies" not in m.group(1).lower(), "blog description shouldn't promise case studies yet"


@check
def check_phase3_not_optional_twice():
    assert "An optional phase" not in text("index.html") and "Volet optionnel" not in text("fr/index.html")
    assert "Support your operations over time" in text("index.html")
    assert "Soutenir vos opérations dans la durée" in text("fr/index.html")



@check
def check_fr_contact():
    h = html("fr/contact/index.html")
    assert '<html lang="fr-CA"' in h
    assert f'href="{BOOKING}"' in h and 'href="mailto:martin@stimilo.com"' in h
    assert 'href="https://www.linkedin.com/in/magdinier"' in h and "<form" not in h
    t = text("fr/contact/index.html")
    assert "Réserver un appel de 45 minutes" in t and "Écrivez-moi" in t
    assert 'href="/fr/contact/"' in html("fr/index.html"), "FR nav Contact should go to /fr/contact/"
    for page in ["contact/index.html", "fr/contact/index.html"]:
        c = html(page)
        assert 'hreflang="en" href="https://stimilo.com/contact/"' in c and 'hreflang="fr" href="https://stimilo.com/fr/contact/"' in c, f"{page}: hreflang"
        assert "ProfessionalService" not in c, f"{page}: business JSON-LD belongs on the home pages only"
    assert "<loc>https://stimilo.com/fr/contact/</loc>" in html("sitemap.xml")



@check
def check_no_phone_number():
    """Phone number removed from the public site (Martin, 2026-09-30)."""
    hits = [str(p.relative_to(SITE)) for p in SITE.rglob("*")
            if p.is_file() and p.suffix in {".html", ".xml", ".json", ".txt"}
            and re.search(r"514.?559.?4563|tel:|telephone", p.read_text(encoding="utf-8", errors="ignore"))]
    assert not hits, f"phone number still on: {hits}"



@check
def check_post_toc_opt_in():
    h = html(POST)
    assert 'class="sidebar__right sticky"' in h and "toc__menu" in h, "long post should have the sticky right-hand contents menu"
    assert 'href="#hard-limits"' in h and 'href="#6-under-what-licence-is-the-data-available"' in h, "TOC should list sections and the numbered questions"
    for page in ["contact/index.html", "fr/contact/index.html", "404.html"]:
        assert "toc__menu" not in html(page), f"{page}: TOC is opt-in per post"


if __name__ == "__main__":
    only = sys.argv[1:]
    failed = 0
    for fn in CHECKS:
        if only and not any(o in fn.__name__ for o in only):
            continue
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
    sys.exit(1 if failed else 0)
