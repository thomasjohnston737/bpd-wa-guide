#!/usr/bin/env python3
"""Builds the WA BPD & DBT Service Guide from one shared layout + data/services.json.
Run: python3 build.py  (no dependencies). Set SITE_URL once a real address exists."""
import re, json, html, pathlib, datetime

ROOT = pathlib.Path(__file__).parent
SITE_URL = "https://thomasjohnston737.github.io/bpd-wa-guide"
SITE_NAME = "WA BPD & DBT Service Guide"
BUILT = "2026-11-04"
CRISIS_CHECKED = "2026-10-28"
e = html.escape

NAV = [("/", "Home"), ("/help-now/", "Need help now?"), ("/services/", "Services"),
       ("/getting-assessed/", "Getting assessed"), ("/costs-and-medicare/", "Costs & Medicare"), ("/private-hospital-and-insurance/", "Private hospital & insurance"), ("/from-someone-whos-been-there/", "From someone who's been there"), ("/about/", "About")]

TYPES = [("public", "Public"), ("private", "Private"), ("community", "Community"), ("youth", "Youth"),
         ("telehealth", "Phone / online"), ("aod", "Alcohol & other drugs"),
         ("general", "General mental health"), ("carers", "Families & carers")]
TYPE_LABEL = dict(TYPES)

# Every number verified on the linked official page on CRISIS_CHECKED.
CRISIS = [
    ("Emergency (police, ambulance, fire)", "000", "000", None),
    ("Lifeline (24/7)", "13 11 14", "131114", "https://www.lifeline.org.au/"),
    ("Suicide Call Back Service (24/7)", "1300 659 467", "1300659467", "https://www.suicidecallbackservice.org.au/"),
    ("Beyond Blue", "1300 22 4636", "1300224636", "https://www.beyondblue.org.au/get-support/talk-to-a-counsellor"),
    ("13YARN (Aboriginal & Torres Strait Islander crisis support)", "13 92 76", "139276", "https://www.13yarn.org.au/"),
    ("WA Mental Health Emergency Response Line: Perth metro", "1300 555 788", "1300555788", "https://www.mhc.wa.gov.au/getting-help/helplines/mental-health-emergency-response-line"),
    ("MHERL: Peel", "1800 676 822", "1800676822", "https://www.mhc.wa.gov.au/getting-help/helplines/mental-health-emergency-response-line"),
    ("Rurallink: country WA (after hours, weekends)", "1800 552 002", "1800552002", "https://www.mhc.wa.gov.au/getting-help/helplines/mental-health-emergency-response-line"),
    ("WA Alcohol and Drug Support Line (24/7): metro", "(08) 9442 5000", "0894425000", "https://admhss.mhc.wa.gov.au/get-help/alcohol-and-drug-support-line"),
    ("Alcohol and Drug Support Line: country", "1800 198 024", "1800198024", "https://admhss.mhc.wa.gov.au/get-help/alcohol-and-drug-support-line"),
]

ICONS = {
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "list": '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M8 9h8M8 13h8M8 17h5"/>',
    "steps": '<path d="M9 5h11M9 12h11M9 19h11"/><circle cx="4.5" cy="5" r="1.5"/><circle cx="4.5" cy="12" r="1.5"/><circle cx="4.5" cy="19" r="1.5"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21l7.8-7.5 1-1.1a5.5 5.5 0 0 0 0-7.8z"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
}
def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'

def crisis_box(full=False):
    items = CRISIS if full else CRISIS[:6]
    lis = "".join(
        f'<li><a class="num" href="tel:{t}">{e(n)}</a> <span>{e(l)}</span></li>' for l, n, t, _ in items)
    more = "" if full else f'<p class="more"><a href="/help-now/">More numbers, including Peel, country WA and alcohol &amp; drugs {icon("arrow","ic sm")}</a></p>'
    return f"""<aside class="crisis" aria-label="Crisis support">
<div class="crisis-head"><span class="crisis-ic">{icon("phone")}</span><h2>In danger or need to talk now?</h2></div>
<p>If you or someone else is in immediate danger, call <a class="num" href="tel:000">000</a>.</p>
<ul>{lis}</ul>{more}
</aside>"""

HEAD_RE = re.compile(r'^\s*<h1>(.*?)</h1>\s*(<p class="lede">.*?</p>)?', re.S)

def layout(path, title, desc, body, noindex=False, scripts="", hero=None):
    nav = "".join(f'<li><a href="{h}"{" aria-current=page" if h == path else ""}>{e(t)}</a></li>' for h, t in NAV)
    robots = '<meta name="robots" content="noindex,nofollow">\n' if noindex else ""
    if hero is None:  # lift the page's h1 + intro into a page header band (content unchanged)
        m = HEAD_RE.match(body)
        if m:
            hero = f'<section class="pagehead"><div class="wrap"><h1>{m.group(1)}</h1>{m.group(2) or ""}</div></section>'
            body = body[m.end():]
        else:
            hero = ""
    flinks = "".join(f'<li><a href="{h}">{e(t)}</a></li>' for h, t in NAV)
    return f"""<!doctype html>
<html lang="en-AU" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}<link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_AU">
<meta name="theme-color" content="#070b1a">
<link rel="stylesheet" href="/assets/style.css">
<script>document.documentElement.className='js'</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap">In immediate danger? Call <a href="tel:000">000</a>. Need to talk? Lifeline <a href="tel:131114">13 11 14</a>. <a href="/help-now/">All help lines</a></div></div>
<header class="site"><div class="wrap bar">
<a class="brand" href="/"><span class="mark" aria-hidden="true">{icon("heart")}</span><span class="bname">WA BPD &amp; DBT <span>Service Guide</span></span></a>
<div class="hactions">
<a class="btn-urgent" href="/help-now/" aria-label="Need help now? Crisis and support lines">{icon("phone","ic sm")}<span>Help now</span></a>
<button type="button" class="nav-toggle" aria-expanded="false" aria-controls="mainnav">{icon("menu")}<span>Menu</span></button>
</div>
<nav id="mainnav" class="mainnav" aria-label="Main"><ul>{nav}</ul></nav>
</div></header>
{hero}
<main id="main"><div class="wrap">
{body}
</div></main>
<footer class="site"><div class="wrap">
<div class="fgrid">
<div><p class="fbrand"><span class="mark" aria-hidden="true">{icon("heart")}</span> {SITE_NAME}</p>
<p><strong>Please read:</strong> this is an independent guide. It is <strong>not a health service</strong> and doesn't give medical advice, diagnosis or treatment recommendations. It is <strong>not affiliated with any provider</strong> listed, and no provider has paid to be here. Details change, so always check with the service before you go. The site is built and maintained with AI assistance and checked against each service's official page on the "last checked" date shown.</p>
<p>Spotted something wrong or out of date? <a href="/about/#report">Report an error</a>.</p></div>
<nav aria-label="Footer"><ul class="flinks">{flinks}</ul></nav>
</div>
<p class="fsmall">&copy; 2026 {SITE_NAME}. Crisis numbers last checked {CRISIS_CHECKED}.</p>
</div></footer>
<script>(function(){{var b=document.querySelector('.nav-toggle'),n=document.getElementById('mainnav');if(!b||!n)return;b.addEventListener('click',function(){{var o=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',String(!o));n.classList.toggle('open',!o);}});document.addEventListener('keydown',function(ev){{if(ev.key==='Escape'&&n.classList.contains('open')){{n.classList.remove('open');b.setAttribute('aria-expanded','false');b.focus();}}}});}})();</script>
{scripts}</body>
</html>
"""

BASE_PATH = "/bpd-wa-guide"  # site lives in a subfolder on GitHub Pages

def write(rel, text):
    if rel.endswith(".html"):
        text = re.sub(r'(href|src|action)="/(?!/)', lambda m: f'{m.group(1)}="{BASE_PATH}/', text)
        text = text.replace(f'href="{BASE_PATH}{SITE_URL}', f'href="{SITE_URL}')
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

def fmt_date(d):
    return datetime.date.fromisoformat(d).strftime("%-d %b %Y")

def home(n):
    hero = f"""<section class="hero"><div class="wrap hero-in">
<div>
<p class="eyebrow">Independent · Western Australia · Free to use</p>
<h1>Finding BPD and DBT support in Western Australia</h1>
<p class="lede">A plain-English guide to services in WA for people living with borderline personality disorder (BPD), and for the people who care about them. It covers who each service is for, how to get referred, and the cost and wait where the service publishes them.</p>
<div class="cta">
<a class="btn btn-primary" href="/services/">{icon("search","ic sm")} Find a service</a>
<a class="btn btn-soft" href="/help-now/">{icon("phone","ic sm")} Need help now?</a>
</div>
</div>
<aside class="hero-side" aria-label="How this guide works">
<h2>How this guide works</h2>
<ul class="ticks">
<li>{icon("check","ic tick")}{n} WA services you can filter</li>
<li>{icon("check","ic tick")}Every listing links to its official page, with a last-checked date</li>
<li>{icon("check","ic tick")}"Not published" when a service doesn't publish cost or wait</li>
<li>{icon("check","ic tick")}No ads, paid listings or affiliate links</li>
</ul>
</aside>
</div></section>"""
    card = lambda href, ic, title, text: f'<a class="card" href="{href}"><span class="card-ic">{icon(ic)}</span><h3>{title}</h3><p>{text}</p><span class="card-go">{icon("arrow","ic sm")}</span></a>'
    body = f"""
{crisis_box()}
<h2>Quick links</h2>
<div class="cards">
{card("/services/", "list", "WA BPD &amp; DBT services", f"{n} services you can filter: public, private, community, youth, phone/online, alcohol &amp; other drugs, and families &amp; carers.")}
{card("/help-now/", "phone", "Need help now?", "Crisis and support lines for WA, open 24/7 or into the evening.")}
{card("/getting-assessed/", "steps", "Getting assessed in WA", "The usual steps from GP to psychologist or psychiatrist, what a mental health treatment plan is, and what Medicare covers.")}
{card("/costs-and-medicare/", "info", "Costs and Medicare", "What Medicare pays for psychologist and psychiatrist sessions, what a gap fee is, the Medicare Safety Net, and free options.")}
{card("/private-hospital-and-insurance/", "info", "Private hospital and health insurance", "How hospital cover works for private psychiatric care, the 2-month wait, the once-in-a-lifetime upgrade rule, and questions to ask your fund.")}
{card("/about/", "info", "About this guide", "Who makes it, how it's checked, and how to report a mistake.")}
</div>
<div class="split">
<section class="panel">
<h2>Who this is for</h2>
<ul class="ticks">
<li>{icon("check","ic tick")}People in WA with a BPD diagnosis, or who think BPD might fit, looking for support.</li>
<li>{icon("check","ic tick")}Partners, parents, family and friends trying to work out where to turn.</li>
<li>{icon("check","ic tick")}Anyone trying to make sense of public, private, youth and community options in one place.</li>
</ul>
</section>
<section class="panel">
<h2>How the information is checked</h2>
<p>Every service listing links to its official page, with the date we last checked it. If a service doesn't publish its cost or waitlist, we show <em>"Not published"</em> rather than guess. This guide doesn't recommend one service over another.</p>
</section>
</div>
"""
    write("index.html", layout("/", "WA BPD & DBT Service Guide: borderline personality disorder support in Western Australia",
        "An independent, plain-English guide to BPD and DBT services in Western Australia: public, private, youth, community and carer support, with referral steps and official links.", body, hero=hero))

def help_now():
    rows = "".join(
        f'<tr><td>{e(l)}</td><td><a class="num" href="tel:{t}">{e(n)}</a></td><td>{f"<a href={chr(34)}{u}{chr(34)} rel=noopener>Official page</a>" if u else "—"}</td></tr>'
        for l, n, t, u in CRISIS)
    body = f"""
<h1>Need help now?</h1>
<p class="lede">If you or someone else is in immediate danger, call <a class="num" href="tel:000">000</a>. If you're not in danger but things feel too much, you can call one of these lines. They're free and confidential, and you don't need a diagnosis or a referral.</p>
{crisis_box(full=True)}
<h2>All numbers and where we checked them</h2>
<div class="tablewrap"><table>
<thead><tr><th>Service</th><th>Number</th><th>Source</th></tr></thead>
<tbody>{rows}</tbody>
</table></div>
<p class="meta">All numbers last checked {fmt_date(CRISIS_CHECKED)} on each service's official site.</p>
<h2>Other WA lines</h2>
<ul>
<li><strong>Here For You</strong> (mental health, alcohol and other drugs, 7am to 10pm daily): <a class="num" href="tel:1800437348">1800 437 348</a>. <a href="https://www.mhc.wa.gov.au/our-initiatives/our-services" rel="noopener">WA Mental Health Commission</a>.</li>
<li><strong>Parent and Family Drug Support Line</strong> (24/7): metro <a class="num" href="tel:0894425050">(08) 9442 5050</a>, country <a class="num" href="tel:1800653203">1800 653 203</a>. <a href="https://admhss.mhc.wa.gov.au/get-help/parent-and-family-drug-support-line" rel="noopener">Official page</a>.</li>
<li><strong>Medicare Mental Health phone line</strong>: <a class="num" href="tel:1800595212">1800 595 212</a>. <a href="https://www.wapha.org.au/medicare-mental-health-centres/" rel="noopener">WAPHA</a>. Medicare Mental Health Centres are not a crisis service.</li>
</ul>
<p class="meta">Last checked {fmt_date(CRISIS_CHECKED)}.</p>
"""
    write("help-now/index.html", layout("/help-now/", "Need help now? Crisis and support lines in WA | WA BPD & DBT Service Guide",
        "Crisis and support numbers for Western Australia: 000, Lifeline 13 11 14, Suicide Call Back Service, Beyond Blue, 13YARN, the Mental Health Emergency Response Line and the Alcohol and Drug Support Line.", body))

def services():
    data = json.loads((ROOT / "data/services.json").read_text(encoding="utf-8"))
    order = {"public": 0, "private": 1, "youth": 2, "community": 3, "carers": 4, "aod": 5, "general": 6, "telehealth": 7}
    data.sort(key=lambda d: (not d["bpd"], order.get(d["types"][0], 9), d["name"]))
    cards = []
    for d in data:
        tags = "".join(f'<span class="tag t-{t}">{e(TYPE_LABEL[t])}</span>' for t in d["types"])
        badge = f'<span class="badge">{icon("check","ic xs")}BPD / DBT specific</span>' if d["bpd"] else ""
        phone = ""
        if d["phone"]:
            digits = "".join(c for c in d["phone"].split("·")[0] if c.isdigit())
            phone = f'<dt>Phone</dt><dd><a href="tel:{digits}">{e(d["phone"])}</a></dd>'
        note = f'<p class="note">{e(d["note"])}</p>' if d.get("note") else ""
        np = lambda v: f'<span class="np">{e(v)}</span>' if v.startswith("Not published") else e(v)
        cards.append(f"""<li class="svc" data-types="{' '.join(d['types'])}" data-bpd="{int(d['bpd'])}">
<p class="tags">{badge}{tags}</p><h3>{e(d['name'])}</h3>
<dl>
<dt>Who it's for</dt><dd>{e(d['who'])}</dd>
<dt>How to get in</dt><dd>{e(d['referral'])}</dd>
<dt>Cost</dt><dd>{np(d['cost'])}</dd>
<dt>Waitlist</dt><dd>{np(d['waitlist'])}</dd>
<dt>Where</dt><dd>{e(d['location'])}</dd>
{phone}
</dl>{note}
<p class="src">Source: <a href="{e(d['url'])}" rel="noopener">{e(d['source'])}</a> · Last checked {fmt_date(d['checked'])}</p>
</li>""")
    filters = "".join(f'<button type="button" class="f" data-f="{k}" aria-pressed="false">{e(v)}</button>' for k, v in TYPES)
    body = f"""
<h1>BPD and DBT services in Western Australia</h1>
<p class="lede">Programs and supports in WA for people with BPD and their families. Each listing gives who it's for, how to get in, and the cost and wait if the service publishes them. Services that aren't BPD-specific, like alcohol and drug support and general mental health services, are included because people with BPD are often referred through them.</p>
{crisis_box()}
<div class="finder">
<label class="skip" for="q">Search services</label>
<div class="searchbox">{icon("search")}<input id="q" type="search" placeholder="Search by name, suburb or word (e.g. Fremantle, carer, free)" autocomplete="off"></div>
<div class="filters" role="group" aria-label="Filter services">
<span class="flabel">Show:</span>
<button type="button" class="f" data-f="all" aria-pressed="true">All</button>
<button type="button" class="f" data-f="bpd" aria-pressed="false">BPD / DBT specific</button>
{filters}
</div>
</div>
<p class="meta count" id="count" aria-live="polite">{len(data)} services</p>
<p id="empty" hidden>No services match. Try another filter or clear the search.</p>
<ul id="list" class="svcs">
{chr(10).join(cards)}
</ul>
<div class="callout"><strong>Before you go:</strong> referral rules, catchments and program dates change. Call the service or check its official page first. Listings are information only, not recommendations. Know a service we've missed? <a href="/about/#report">Tell us</a>.</div>
"""
    write("services/index.html", layout("/services/", "WA BPD & DBT services: public, private, youth & community | WA BPD & DBT Service Guide",
        f"Filterable list of {len(data)} BPD, DBT and related services in Western Australia, with who each is for, how to get referred, cost and waitlist where published, and official links.",
        body, scripts='<script src="/assets/filter.js"></script>\n'))
    return len(data)

def lived():
    sec = lambda h, hint: f'<section class="placeholder"><h2>{h}</h2><p class="meta">[Coming soon: {hint}]</p></section>'
    body = f"""
<h1>From someone who's been there</h1>
<div class="callout framing"><strong>One person's experience, not medical advice.</strong> What helped me may not suit you; talk to your GP or a mental health professional.</div>
{crisis_box()}
{sec("What helped me", "in the author's own words")}
{sec("Who helped with what", "practical notes, e.g. which kind of service helped with which kind of problem")}
{sec("What didn't help", "in the author's own words")}
{sec("What I wish I'd known", "in the author's own words")}
"""
    write("from-someone-whos-been-there/index.html", layout("/from-someone-whos-been-there/",
        "From someone who's been there | WA BPD & DBT Service Guide",
        "One person's lived experience of finding BPD support in WA. Not medical advice.", body, noindex=True))

ASSESS_CHECKED = "2026-10-29"

def assessed():
    c = fmt_date(ASSESS_CHECKED)
    src = lambda url, name: f'<p class="src">Source: <a href="{url}" rel="noopener">{name}</a> · Last checked {c}</p>'
    HD_BPD = "https://www.healthdirect.gov.au/borderline-personality-disorder-bpd"
    HD_MH = "https://www.healthdirect.gov.au/australian-mental-health-services"
    SA = "https://www.servicesaustralia.gov.au/mental-health-care-and-medicare"
    MBS = "https://www9.health.gov.au/mbs/fullDisplay.cfm?type=item&amp;q=291"
    body = f"""
<h1>Getting assessed in WA, step by step</h1>
<p class="lede">How the usual path works in Australia if you think BPD might fit, or you want a proper assessment: from your GP, to a mental health treatment plan, to a psychologist or psychiatrist. This page explains the system only. It can't tell you whether you have BPD; only a qualified professional can assess that.</p>
{crisis_box()}
<div class="callout"><strong>Not medical advice.</strong> Everything below is taken from official government health pages, linked under each section. Rules and fees change, so check the source or ask your GP.</div>

<h2>Step 1: See a GP</h2>
<p>Healthdirect, the government's health information service, says the first step is to see your doctor. You don't need a referral to see a GP. Your GP can talk through what's going on, tell you about services near you, refer you to other mental health professionals and prepare a mental health treatment plan.</p>
<p>Healthdirect also says you should be assessed by a mental health professional who has experience with BPD, such as a psychologist or psychiatrist, and that they make the diagnosis based on your symptoms and experiences.</p>
<p><strong>A tip for the appointment:</strong> book a longer appointment if the clinic offers one, and say up front that you'd like to talk about your mental health. Writing a few notes beforehand can help if it's hard to say out loud.</p>
{src(HD_BPD, "Healthdirect: Borderline personality disorder")}
{src(HD_MH, "Healthdirect: Australian mental health services")}

<h2>Step 2: A mental health treatment plan</h2>
<p>If you have a diagnosed mental health disorder, your GP can write a mental health treatment plan with goals you agree on, treatment options, referrals, support services, and review and follow-up. Your information stays private unless you agree to share it.</p>
<p>According to Services Australia, a plan lets you claim Medicare rebates for:</p>
<ul>
<li>up to <strong>10 individual and 10 group sessions</strong> each calendar year with an eligible mental health professional (such as a psychologist, occupational therapist or social worker)</li>
<li>referrals for <strong>up to 6 sessions at a time</strong>, with your doctor deciding whether to refer you for more</li>
<li>video telehealth sessions, which can also be claimed</li>
</ul>
<p>Health professionals set their own fees, so Medicare may only cover part of the cost. Ask when you book how much you'll pay and how much Medicare will cover. If they bulk bill, you pay nothing.</p>
<p>A carer can sometimes attend up to 2 sessions a year as part of the person's plan, without the person there, if the person agrees and their health professional recommends it. These count towards the 10 individual sessions.</p>
{src(SA, "Services Australia: Mental health care and Medicare")} 

<h2>Step 3: Psychologist or psychiatrist</h2>
<p>Healthdirect says you don't always need a referral to see a mental health professional, but you <strong>do need one to get a Medicare rebate</strong>. Seeing a psychiatrist in a public hospital or community health service usually costs nothing, but there's usually a wait.</p>
<p>To find a psychiatrist, Services Australia points to Healthdirect's service finder and the <a href="https://www.yourhealthinmind.org/find-a-psychiatrist" rel="noopener">Your Health in Mind find-a-psychiatrist tool</a>. Our <a href="/services/">WA services list</a> covers public, private and community options.</p>
{src(HD_MH, "Healthdirect: Australian mental health services")}
{src(SA, "Services Australia: Mental health care and Medicare")}

<h2>The one-off psychiatrist assessment (Medicare item 291)</h2>
<p>Medicare has a specific item, number 291, for a one-off assessment by a consultant psychiatrist. In plain words, the official item description says:</p>
<ul>
<li>your GP (or a participating nurse practitioner) refers you for it</li>
<li>it's a single appointment of more than 45 minutes, including a full diagnostic assessment</li>
<li>within 2 weeks, the psychiatrist sends your GP a written report with the assessment and a 12-month management plan, so your GP can manage your ongoing care</li>
<li>if appropriate, the psychiatrist explains it to you and gives you a copy (and your carer, if you agree)</li>
<li>it can be claimed once in any 12 months; your GP can ask for one review of the plan within that year (item 293)</li>
<li>a video version exists (item 92435)</li>
</ul>
<div class="tablewrap"><table>
<thead><tr><th>Item 291</th><th>Amount</th></tr></thead>
<tbody>
<tr><td>Schedule fee</td><td>$549.90</td></tr>
<tr><td>Medicare benefit (85%)</td><td>$467.45</td></tr>
<tr><td>What the psychiatrist actually charges</td><td><span class="np">Not published (each psychiatrist sets their own fee; ask when booking)</span></td></tr>
</tbody></table></div>
<p class="meta">The schedule fee was last updated on 1 Jul 2026, according to MBS Online.</p>
{src(MBS, "MBS Online: Item 291")}

<h2>Free options while you sort it out</h2>
<p>Medicare Mental Health Centres are free and confidential. You don't need an appointment, a referral, a Medicare card or Australian citizenship. You can call Medicare Mental Health on <a class="num" href="tel:1800595212">1800 595 212</a> to find your nearest centre. These centres aren't a crisis service.</p>
{src(SA, "Services Australia: Mental health care and Medicare")}

<h2>Questions you could ask</h2>
<ul>
<li>Your GP: "Can we do a mental health treatment plan today?" and "Who do you refer people to who has experience with BPD?"</li>
<li>When booking a psychologist or psychiatrist: "What's your fee, what's the Medicare rebate and what's the gap?" and "How long is the wait?"</li>
<li>For a psychiatrist: "Do you do item 291 assessments?"</li>
</ul>
<p class="meta">Whole page last checked {c} against the official sources linked above. These are suggested questions, not recommendations.</p>
"""
    write("getting-assessed/index.html", layout("/getting-assessed/",
        "Getting assessed for BPD in WA, step by step: GP, treatment plan, Medicare | WA BPD & DBT Service Guide",
        "Plain-English steps to getting a mental health assessment in WA: seeing a GP, mental health treatment plans (10 Medicare sessions), psychologists, psychiatrists and Medicare item 291. Official sources only.", body))

COSTS_CHECKED = "2026-10-30"

def costs():
    c = fmt_date(COSTS_CHECKED)
    src = lambda url, name: f'<p class="src">Source: <a href="{url}" rel="noopener">{name}</a> · Last checked {c}</p>'
    SA = "https://www.servicesaustralia.gov.au/mental-health-care-and-medicare"
    SN = "https://www.servicesaustralia.gov.au/what-are-medicare-safety-nets-thresholds"
    M110 = "https://www9.health.gov.au/mbs/fullDisplay.cfm?type=item&amp;q=80110"
    M010 = "https://www9.health.gov.au/mbs/fullDisplay.cfm?type=item&amp;q=80010"
    M291 = "https://www9.health.gov.au/mbs/fullDisplay.cfm?type=item&amp;q=291"
    MMH = "https://www.health.gov.au/our-work/medicare-mental-health-centres"
    HD = "https://www.healthdirect.gov.au/australian-mental-health-services"
    np = lambda t: f'<span class="np">{t}</span>'
    body = f"""
<h1>Costs and Medicare: what you'll pay</h1>
<p class="lede">How Medicare helps with the cost of seeing a psychologist or psychiatrist in Australia, what a "gap fee" is, how the Medicare Safety Net works, and which options are free. Figures come straight from official government pages, linked under each section.</p>
{crisis_box()}
<div class="callout"><strong>Not financial or medical advice.</strong> Fees change, usually each 1 July and 1 January. Always ask the clinic what you'll pay before you book.</div>

<h2>The short version</h2>
<ul>
<li>With a mental health treatment plan and a referral, Medicare pays part of the cost of up to <strong>10 individual and 10 group sessions</strong> each calendar year.</li>
<li>Health professionals set their own fees. If they charge more than Medicare pays, you pay the difference (the <strong>gap</strong>). If they <strong>bulk bill</strong>, you pay nothing.</li>
<li><strong>Medicare Mental Health Centres</strong> and the Medicare Mental Health phone line are free, with no referral needed.</li>
<li>Public mental health services in hospitals and community clinics usually cost nothing, but there's usually a wait.</li>
</ul>

<h2>What Medicare pays per session</h2>
<p>These are the official Medicare amounts for a standard individual session of at least 50 minutes, in person, with a referral. The <em>schedule fee</em> is the amount the government sets for the service; Medicare pays 85% of it. What the professional actually charges is up to them.</p>
<div class="tablewrap"><table>
<thead><tr><th>Who you see</th><th>Medicare item</th><th>Schedule fee</th><th>Medicare pays</th><th>What they charge</th></tr></thead>
<tbody>
<tr><td>Psychologist (registered), 50+ minutes</td><td><a href="{M110}" rel="noopener">80110</a></td><td>$119.45</td><td>$101.55</td><td>{np("Not published (each sets their own fee)")}</td></tr>
<tr><td>Clinical psychologist, 50+ minutes</td><td><a href="{M010}" rel="noopener">80010</a></td><td>$175.30</td><td>$149.05</td><td>{np("Not published (each sets their own fee)")}</td></tr>
<tr><td>Psychiatrist one-off assessment</td><td><a href="{M291}" rel="noopener">291</a></td><td>$549.90</td><td>$467.45</td><td>{np("Not published (each sets their own fee)")}</td></tr>
</tbody></table></div>
<p class="meta">MBS Online says these schedule fees were last updated on 1 Jul 2026. Shorter sessions, video and phone sessions, and group sessions have different item numbers and amounts. Our <a href="/getting-assessed/">Getting assessed</a> page explains item 291.</p>
{src(M110, "MBS Online: Item 80110")}
{src(M010, "MBS Online: Item 80010")}
{src(M291, "MBS Online: Item 291")}

<h2>Working out your gap</h2>
<p>Your gap is the fee charged minus what Medicare pays. Here's how the sum works, using a <strong>made-up example fee</strong> (not a real price from any clinic):</p>
<div class="tablewrap"><table>
<thead><tr><th>Example only</th><th>Amount</th></tr></thead>
<tbody>
<tr><td>Example fee a registered psychologist might charge</td><td>$200.00 (made-up)</td></tr>
<tr><td>Medicare pays for item 80110</td><td>$101.55</td></tr>
<tr><td>Your gap</td><td>$98.45</td></tr>
</tbody></table></div>
<p>If you pay the full fee on the day, you can claim the Medicare part back, or the clinic can claim it for you.</p>
{src(SA, "Services Australia: Mental health care and Medicare")}

<h2>The rules that catch people out</h2>
<ul>
<li><strong>The referral has to come from the right doctor.</strong> MBS Online says Medicare only pays if your referral comes from the GP practice where you're registered with MyMedicare, your usual GP (the practice that's given you most of your care over the past year, or will over the next year), or a psychiatrist or paediatrician.</li>
<li><strong>The plan isn't the referral.</strong> A mental health treatment plan isn't the same thing as a referral; you need a written referral too.</li>
<li><strong>Six at a time.</strong> The first referral covers up to 6 individual sessions. After that you need a review and a new referral for the rest of your 10.</li>
<li><strong>Plans don't expire.</strong> You don't need a new plan every year, just a new referral when you've used the sessions you were referred for.</li>
<li><strong>Medicare or your health fund, not both.</strong> You can't use private health insurance extras to top up the Medicare rebate on the same session. Once your Medicare sessions for the year are used up, you may be able to claim from your fund if you have psychology cover.</li>
<li><strong>Not for public services.</strong> These Medicare items don't apply to services already funded by the state or Commonwealth, or if you're an admitted hospital patient.</li>
<li><strong>Check how many you've used.</strong> You can see your care plan history in your Medicare online account through myGov, or call Medicare on <a class="num" href="tel:132011">132 011</a>.</li>
</ul>
{src(M110, "MBS Online: Item 80110 and Better Access explanatory notes")}

<h2>The Medicare Safety Net</h2>
<p>If your out-of-pocket costs for out-of-hospital services add up over the calendar year, you start getting more back once you pass a threshold. Gap fees for Medicare-eligible mental health sessions count towards it; costs for services Medicare doesn't cover don't.</p>
<div class="tablewrap"><table>
<thead><tr><th>2026 threshold</th><th>Who it's for</th><th>Amount</th></tr></thead>
<tbody>
<tr><td>Original Medicare Safety Net</td><td>Everyone in Medicare</td><td>$594.40 in gap amounts</td></tr>
<tr><td>Extended Medicare Safety Net: general</td><td>Everyone in Medicare</td><td>$2,699.10 out of pocket</td></tr>
<tr><td>Extended Medicare Safety Net: concessional</td><td>Concession card holders and families getting Family Tax Benefit Part A</td><td>$861.20 out of pocket</td></tr>
</tbody></table></div>
<p>Once you pass the Extended threshold, Medicare pays back 80% of out-of-pocket costs, up to a cap for each item (for example, MBS Online lists a cap of $358.35 for item 80110). Only payments you've actually made count. Families and couples can register together to combine their costs.</p>
{src(SN, "Services Australia: Medicare Safety Nets thresholds")}
{src(M110, "MBS Online: Item 80110 and Better Access explanatory notes")}

<h2>Free options</h2>
<ul>
<li><strong>Medicare Mental Health Centres</strong>: free for anyone in Australia. No appointment, referral or diagnosis needed; you can walk in. They're open extended hours. They aren't a crisis service.</li>
<li><strong>Medicare Mental Health phone line</strong>: <a class="num" href="tel:1800595212">1800 595 212</a>, 8:30am to 5pm weekdays (excluding public holidays; the government page doesn't say which time zone). A trained professional can help you find free or low-cost local services.</li>
<li><strong>Medicare Mental Health Check In</strong>: free online tools for people 16 and over, for mild mental health challenges, with telehealth support if needed.</li>
<li><strong>Bulk-billing professionals</strong>: you pay nothing. Healthdirect's service finder can show which ones bulk bill.</li>
<li><strong>Public mental health services</strong>: usually no cost, usually a wait. See our <a href="/services/">WA services list</a>.</li>
<li><strong>Centrelink social workers</strong>: free short-term counselling and referrals. Ask for one through the Centrelink employment services line or at a service centre.</li>
</ul>
{src(MMH, "Department of Health, Disability and Ageing: Medicare Mental Health")}
{src(SA, "Services Australia: Mental health care and Medicare")}
{src(HD, "Healthdirect: Australian mental health services")}

<h2>For carers</h2>
<p>A carer or family member can attend up to 2 sessions a year as part of the person's plan, without the person there, if the person agrees and their health professional recommends it. These count towards the person's 10 sessions. Centrelink also has Carer Payment and Carer Supplement for people who give constant care.</p>
{src(SA, "Services Australia: Mental health care and Medicare")}

<h2>Questions to ask before you book</h2>
<ul>
<li>"What's your fee, how much will Medicare pay back, and what's my gap?"</li>
<li>"Do you bulk bill anyone, for example concession card holders?"</li>
<li>"Do you need a referral from my usual GP before the first session?"</li>
<li>"Can I pay just the gap on the day, or do I pay the full fee and claim later?"</li>
</ul>
<p class="meta">Whole page last checked {c} against the official sources linked above. These are suggested questions, not recommendations.</p>
"""
    write("costs-and-medicare/index.html", layout("/costs-and-medicare/",
        "Costs and Medicare for mental health care: rebates, gap fees, Safety Net | WA BPD & DBT Service Guide",
        "What Medicare pays for psychologist and psychiatrist sessions (2026 amounts), how gap fees and the Medicare Safety Net work, Better Access referral rules, and free options. Official sources only.", body))

PRIV_CHECKED = "2026-11-04"

def private_hospital():
    c = fmt_date(PRIV_CHECKED)
    src = lambda url, name: f'<p class="src">Source: <a href="{url}" rel="noopener">{name}</a> · Last checked {c}</p>'
    WP = "https://www.privatehealth.gov.au/health_insurance/howitworks/waiting_periods.htm"
    EX = "https://www.health.gov.au/topics/private-health-insurance/what-private-health-insurance-covers/waiting-periods-and-exemptions"
    TIERS = "https://www.privatehealth.gov.au/health_insurance/howitworks/producttiers.htm"
    COMPARE = "https://www.privatehealth.gov.au/"
    data = json.loads((ROOT / "data/services.json").read_text(encoding="utf-8"))
    priv = sorted((d for d in data if "private" in d["types"]), key=lambda d: d["name"])
    np = lambda v: f'<span class="np">{e(v)}</span>' if v.startswith("Not published") else e(v)
    rows = "".join(f'<tr><td><a href="{e(d["url"])}" rel="noopener">{e(d["name"])}</a></td><td>{e(d["referral"])}</td><td>{np(d["cost"])}</td><td>{np(d["waitlist"])}</td><td>{fmt_date(d["checked"])}</td></tr>' for d in priv)
    body = f"""
<h1>Private hospital DBT and health insurance: a checklist</h1>
<p class="lede">Some private hospitals in Perth run DBT day programs and inpatient care. Most people pay for these through private health insurance. This page explains, in plain words, how hospital cover works for psychiatric care, the waiting periods, and what to ask your fund and the hospital before you start. It doesn't recommend any fund, policy or hospital.</p>
{crisis_box()}
<div class="callout"><strong>Not financial or medical advice.</strong> Everything below comes from official government pages and each hospital's own website, linked under each section. Your policy documents and your fund have the final say on what you're covered for.</div>

<h2>The short version</h2>
<ul>
<li>Private hospital psychiatric care is paid for under <strong>hospital cover</strong>, not extras.</li>
<li>Every hospital policy (Basic, Bronze, Silver, Gold) has to include <strong>hospital psychiatric services</strong>, but only <strong>Gold</strong> must cover them fully. Basic, Bronze and Silver policies are allowed to cover them on a <strong>restricted</strong> basis, which can leave big out-of-pocket costs in a private hospital.</li>
<li>The longest waiting period a fund can set for hospital psychiatric care is <strong>2 months</strong>, even if the condition is pre-existing.</li>
<li>If you're on restricted psychiatric cover and have held hospital cover for 2 months, you can upgrade to higher psychiatric cover <strong>without another wait, once in your lifetime</strong>.</li>
<li>Perth's private programs listed on this site all ask for a <strong>GP or specialist referral</strong>, and most need you to be under, or assessed by, one of their psychiatrists.</li>
</ul>

<h2>Restricted vs full cover for psychiatric care</h2>
<p>Since April 2020 every hospital policy in Australia is sorted into one of four tiers: Gold, Silver, Bronze or Basic. The government's table of tiers says:</p>
<div class="tablewrap"><table>
<thead><tr><th>Tier</th><th>Hospital psychiatric services</th></tr></thead>
<tbody>
<tr><td>Basic</td><td>Must be included, but can be restricted</td></tr>
<tr><td>Bronze</td><td>Must be included, but can be restricted</td></tr>
<tr><td>Silver</td><td>Must be included, but can be restricted</td></tr>
<tr><td>Gold</td><td>Must be included, unrestricted</td></tr>
</tbody></table></div>
<p>A <strong>restricted</strong> benefit, in the government's words, means you're partly covered for hospital costs as a private patient in a <em>public</em> hospital, and "you may incur significant expenses in a private room or private hospital". Some funds sell "Plus" policies (like Bronze Plus or Silver Plus) that cover more than the minimum for their tier, so a Plus policy might include unrestricted psychiatric cover. The only way to know is to check the policy itself.</p>
{src(TIERS, "privatehealth.gov.au (Commonwealth Ombudsman): Product tiers")}

<h2>Waiting periods</h2>
<p>The government sets the most a fund can make you wait before claiming hospital benefits after you join or upgrade:</p>
<ul>
<li><strong>2 months</strong> for psychiatric care, rehabilitation and palliative care, even for a pre-existing condition.</li>
<li><strong>12 months</strong> for other pre-existing conditions and for pregnancy and birth.</li>
<li><strong>2 months</strong> for everything else.</li>
</ul>
<p>Waiting periods for extras (like psychology on your extras cover) are set by each fund, not the government.</p>
{src(WP, "privatehealth.gov.au (Commonwealth Ombudsman): Waiting periods")}

<h2>The once-in-a-lifetime mental health upgrade</h2>
<p>The Department of Health explains the rule like this:</p>
<ul>
<li>If you've finished a 2-month waiting period on a policy with limited psychiatric benefits, you can upgrade to higher psychiatric cover <strong>without serving another waiting period</strong>.</li>
<li>You can do this at any time, but only <strong>once in your lifetime</strong>. Each person on a policy has their own once-only exemption.</li>
<li>It covers hospital (or hospital-substitute) care for mental health and for drug and alcohol treatment.</li>
<li>You can upgrade with your current fund or switch to any other fund, as long as you've held some hospital cover for 2 months with your current fund.</li>
<li>If you upgrade within 5 days of going into hospital, you may be covered for treatment from before the upgrade. After 5 days, cover starts from the upgrade date.</li>
<li>You only "use up" the exemption if you claim the higher benefits for mental health treatment within 2 months of upgrading.</li>
<li>Your old excess or co-payment may still apply until the normal 2 months has passed, and the new, higher premium starts from the day you upgrade. You can drop back to lower cover later.</li>
<li>If a hospital can't confirm your cover while you're upgrading, it may ask for an upfront fee; whether that's refunded is up to the hospital.</li>
</ul>
{src(EX, "Department of Health, Disability and Ageing: Waiting periods and exemptions")}

<h2>Perth private programs on this site</h2>
<p>This is what each hospital publishes about referral, cost and wait. For full details, see the <a href="/services/">services list</a> or the hospital's own page.</p>
<div class="tablewrap"><table>
<thead><tr><th>Program</th><th>How to get in</th><th>Cost</th><th>Wait</th><th>Last checked</th></tr></thead>
<tbody>{rows}</tbody>
</table></div>
<p class="meta">Listed in alphabetical order. Being listed here isn't a recommendation.</p>

<h2>Checklist: questions to ask your health fund</h2>
<ul class="ticks">
<li>{icon("check","ic tick")}"Is hospital psychiatric cover on my policy <strong>restricted or unrestricted</strong>?"</li>
<li>{icon("check","ic tick")}"Have I served the 2-month waiting period for psychiatric care? When did it end?"</li>
<li>{icon("check","ic tick")}"Have I already used my once-in-a-lifetime mental health upgrade exemption?"</li>
<li>{icon("check","ic tick")}"Does my policy cover <strong>day programs</strong> (like a weekly DBT group) as well as overnight stays?"</li>
<li>{icon("check","ic tick")}"Do you have an agreement with [hospital name]? What's my excess or co-payment there?"</li>
<li>{icon("check","ic tick")}"What will I pay out of pocket for the hospital, and for the psychiatrist's fees?"</li>
</ul>

<h2>Checklist: questions to ask the hospital</h2>
<ul class="ticks">
<li>{icon("check","ic tick")}"Do I need a referral from my GP, or from a psychiatrist? Who is an admitting psychiatrist here?"</li>
<li>{icon("check","ic tick")}"Is there an intake assessment, and is there a charge for it?"</li>
<li>{icon("check","ic tick")}"How long is the wait for the next program?"</li>
<li>{icon("check","ic tick")}"Can you check my cover with my fund and tell me my out-of-pocket costs before I start?"</li>
<li>{icon("check","ic tick")}"What's the price if I pay for it myself (no insurance)?"</li>
</ul>

<h2>If you don't have private cover</h2>
<p>Public mental health services and Medicare Mental Health Centres don't need private insurance. Our <a href="/costs-and-medicare/">Costs and Medicare</a> page covers what Medicare pays and the free options, and the <a href="/services/">services list</a> includes public and community programs. The hospitals above also list DVA, WorkCover or paying for yourself as options where they publish it.</p>
<p>To compare policies, the government runs a free comparison site at <a href="{COMPARE}" rel="noopener">privatehealth.gov.au</a>. This guide doesn't compare or recommend funds and doesn't earn anything from them.</p>
<p class="meta">Whole page last checked {c} against the official sources linked above. Hospital details come from each hospital's page on the date shown in the table. These are suggested questions, not recommendations.</p>
"""
    write("private-hospital-and-insurance/index.html", layout("/private-hospital-and-insurance/",
        "Private hospital DBT and health insurance checklist for WA | WA BPD & DBT Service Guide",
        "How private health insurance covers psychiatric care: restricted vs Gold cover, the 2-month waiting period, the once-in-a-lifetime mental health upgrade, Perth private DBT programs and questions to ask. Official sources only.", body))

def about():
    body = """
<h1>About this guide</h1>
<p class="lede">This guide is made by someone in Perth with lived experience of BPD, who found that working out where to go in WA was harder than it should be.</p>
""" + crisis_box() + """
<section class="placeholder"><h2>Why this exists</h2><p class="meta">[Coming soon: the founder's story, in their own words]</p></section>
<h2>What this guide is, and isn't</h2>
<ul>
<li>It <strong>is</strong> a directory of services and how to reach them, drawn from each service's own official information.</li>
<li>It <strong>isn't</strong> a health service, and it doesn't give medical advice, diagnose anything, or recommend one treatment or provider over another.</li>
<li>It's independent and not affiliated with any provider. There are no ads, paid listings or affiliate links.</li>
<li>It's built with AI assistance. Every service detail links to its source with a "last checked" date.</li>
</ul>
<h2 id="report">Report an error or a missing service</h2>
<p>If something is wrong, out of date or missing, please let us know and we'll fix it. <em>[Contact address coming soon]</em></p>
"""
    write("about/index.html", layout("/about/", "About | WA BPD & DBT Service Guide",
        "Who makes the WA BPD & DBT Service Guide, how information is checked, and how to report an error.", body))

def notfound():
    write("404.html", layout("/404.html", "Page not found | WA BPD & DBT Service Guide", "Page not found.",
        '<h1>Page not found</h1><p>Try the <a href="/services/">services list</a> or <a href="/">home page</a>.</p>' + crisis_box(), noindex=True))

def seo():
    public = ["/", "/help-now/", "/services/", "/getting-assessed/", "/costs-and-medicare/", "/private-hospital-and-insurance/", "/about/"]  # lived-experience page excluded until published
    urls = "".join(f"<url><loc>{SITE_URL}{p}</loc><lastmod>{BUILT}</lastmod></url>\n" for p in public)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")

if __name__ == "__main__":
    n = services(); home(n); help_now(); assessed(); costs(); private_hospital(); lived(); about(); notfound(); seo()
    print(f"Built {SITE_NAME}: {n} services")
