#!/usr/bin/env python3
"""Builds the WA BPD & DBT Service Guide from one shared layout + data/services.json.
Run: python3 build.py  (no dependencies). Set SITE_URL once a real address exists."""
import re, json, html, pathlib, datetime

ROOT = pathlib.Path(__file__).parent
SITE_URL = "https://thomasjohnston737.github.io/bpd-wa-guide"
SITE_NAME = "WA BPD & DBT Service Guide"
BUILT = "2026-10-29"
CRISIS_CHECKED = "2026-10-28"
e = html.escape

NAV = [("/", "Home"), ("/help-now/", "Need help now?"), ("/services/", "Services"),
       ("/getting-assessed/", "Getting assessed"), ("/from-someone-whos-been-there/", "From someone who's been there"), ("/about/", "About")]

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
<meta name="theme-color" content="#0b1f3a">
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
    public = ["/", "/help-now/", "/services/", "/getting-assessed/", "/about/"]  # lived-experience page excluded until published
    urls = "".join(f"<url><loc>{SITE_URL}{p}</loc><lastmod>{BUILT}</lastmod></url>\n" for p in public)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")

if __name__ == "__main__":
    n = services(); home(n); help_now(); assessed(); lived(); about(); notfound(); seo()
    print(f"Built {SITE_NAME}: {n} services")
