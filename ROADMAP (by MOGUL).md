# WA BPD & DBT Service Guide: roadmap (by MOGUL)
Updated Wed 28 Oct 2026 (AWST, Perth). Rules for every page: no medical advice, diagnosis, health claims or testimonials. Every fact links its official source with a "last checked" date. If a service doesn't publish a detail, show "not published". Crisis box on every page.

## Next pages, in priority order
1. **From someone who's been there.** Tom's own words. The placeholder is built at `/from-someone-whos-been-there/` (noindex, not in sitemap). To publish it, add Tom's text, then remove `noindex=True` in `lived()`, add the path to `seo()`.
2. **Getting assessed in WA, step by step.** GP → mental health treatment plan → psychologist or psychiatrist; MBS item 291 one-off psychiatric assessment. Quote Healthdirect and Services Australia only.
3. **Costs and Medicare.** Better Access sessions, gap fees, bulk billing, Medicare Mental Health Centres (free). Official sources only; re-check after any MBS change.
4. **Private hospital DBT and a health insurance checklist.** Psychiatric cover, waiting periods, needing an admitting psychiatrist, questions to ask your fund (Perth Clinic, Hollywood, Marian, Abbotsford). No recommendations.
5. **Families and carers guide.** Free BPD carer groups state by state: MIFWA (WA), Spectrum and BPD Community (Vic), SA Health BPD Co, plus Family Connections, Project Air carer resources, Carer Gateway.
6. **Addiction and BPD support in WA.** Plain map of WA alcohol and other drug services (ADSL, Parent and Family Drug Support Line, CADS, Next Step, private addiction programs) and how they connect with mental health services. Non-clinical, with no claims about causes or how well treatment works.
7. **While you wait.** Waitlist tips: free lines, Medicare Mental Health Centres, carer groups, asking to be put on a cancellation list. Service-sourced only.
8. **Telehealth and online options.** Which programs offer telehealth intake or groups, headspace online, national phone lines. Verify each one.
9. **Youth pathways (12 to 25).** headspace, Youth Axis, YouthLink, DBTeen, CAMHS. Who's eligible for which.
10. **Regional WA.** WACHS services, Rurallink, Bunbury and South West (the BPD Foundation lists a Bunbury DBT program; not yet verified officially).
11. **Glossary.** DBT, MHTP, GP, MHERL, CADS, catchment, day program and similar terms, in plain words with sources.
12. **How to report an error / suggest a service.** Needs a contact method (free email address, Tom to approve).

## Services still to verify before listing
- Sentiens (private, Perth): the site didn't load for the checker.
- Bunbury Mental Health DBT program (WACHS).
- Fremantle, Peel and Rockingham Kwinana DBT groups: only the BPD Foundation's Oct 2022 list mentions them. Currently listed as general community mental health, with a note saying so.
- Open Borders / Hampton Road (BPD Foundation list).
- Wanslea (children of parents with a mental illness).

## Before going live
- Replace `SITE_URL` in build.py, then rebuild.
- Set up a contact address for error reports (no sign-ups without Tom's OK).
- Re-check all crisis numbers and services (monthly check).
