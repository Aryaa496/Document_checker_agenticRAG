"""
Test question set for RAG hallucination benchmark.
Domain: UK Skilled Worker & Graduate visa routes (Immigration Rules Appendix Skilled Worker / Appendix Graduate)

Categories:
- answerable: directly stated in one part of the rulebook
- synthesis: requires combining info from 2+ sections/routes
- unanswerable_trick: plausible-sounding but not covered, or deliberately crosses routes incorrectly

Each question includes an expected_answer (for scoring) and a source reference.
"""

test_questions = [
    # CATEGORY 1: ANSWERABLE (directly stated) — 27 questions
    {
        "question": "What is the minimum salary threshold under Option A for a Skilled Worker visa?",
        "expected_answer": "£41,700 per year",
        "category": "answerable",
        "source": "SW 4.2 Option A",
    },
    {
        "question": "What is the minimum salary threshold under Option D (Immigration Salary List) for a Skilled Worker?",
        "expected_answer": "£33,400 per year, plus the going rate for the occupation",
        "category": "answerable",
        "source": "SW 4.2 Option D",
    },
    {
        "question": "What is the minimum salary threshold under Option K for health or education occupations?",
        "expected_answer": "£25,000 per year, plus the going rate",
        "category": "answerable",
        "source": "SW 4.2 Option K",
    },
    {
        "question": "How many total points must a Skilled Worker applicant be awarded?",
        "expected_answer": "50 points",
        "category": "answerable",
        "source": "SW 4.1",
    },
    {
        "question": "How many mandatory points are awarded for sponsorship?",
        "expected_answer": "20 points",
        "category": "answerable",
        "source": "SW 5.7 / SW 4.1",
    },
    {
        "question": "What English language level is required for a Skilled Worker applicant?",
        "expected_answer": "Level B2 (or B1 in certain continuing cases)",
        "category": "answerable",
        "source": "SW 7.1, SW 4.1",
    },
    {
        "question": "How many points are awarded for meeting the English language requirement?",
        "expected_answer": "10 points",
        "category": "answerable",
        "source": "SW 7.3",
    },
    {
        "question": "How far in advance of the application date must a Certificate of Sponsorship be issued?",
        "expected_answer": "No more than 3 months (90 days) before the date of application",
        "category": "answerable",
        "source": "SW 1.2(d)",
    },
    {
        "question": "What is the minimum age for a Skilled Worker applicant?",
        "expected_answer": "18 years old on the date of application",
        "category": "answerable",
        "source": "SW 1.3",
    },
    {
        "question": "What sponsor rating is required for a Skilled Worker sponsor?",
        "expected_answer": "A-rated (unless continuing with the same sponsor as their last permission)",
        "category": "answerable",
        "source": "SW 5.3",
    },
    {
        "question": "If a Skilled Worker applicant works more than 48 hours a week, how is their salary calculated for threshold purposes?",
        "expected_answer": "Only the salary for the first 48 hours a week counts toward the salary threshold",
        "category": "answerable",
        "source": "SW 14.3",
    },
    {
        "question": "Does salary for Skilled Worker purposes include overtime or bonus pay?",
        "expected_answer": "No — additional pay such as shift, overtime, or bonus pay does not count, whether or not guaranteed",
        "category": "answerable",
        "source": "SW 14.2(b)",
    },
    {
        "question": "Does salary for Skilled Worker purposes include employer pension contributions?",
        "expected_answer": "No — employer pension and employer National Insurance contributions do not count",
        "category": "answerable",
        "source": "SW 14.2(c)",
    },
    {
        "question": "Does salary for Skilled Worker purposes include accommodation allowances?",
        "expected_answer": "No — allowances such as accommodation or cost of living allowances do not count",
        "category": "answerable",
        "source": "SW 14.2(d)",
    },
    {
        "question": "What is the minimum amount of personal funds a Skilled Worker applicant must show if not certified by their sponsor?",
        "expected_answer": "At least £1,270",
        "category": "answerable",
        "source": "SW 15.2(a)",
    },
    {
        "question": "For how long must a Skilled Worker applicant have held the required funds, if relying on personal savings?",
        "expected_answer": "A 28-day period",
        "category": "answerable",
        "source": "SW 15.3",
    },
    {
        "question": "What is the maximum period a Skilled Worker's certificate of sponsorship can run for?",
        "expected_answer": "Up to a maximum of 5 years after the start date",
        "category": "answerable",
        "source": "SW 18.1",
    },
    {
        "question": "How many years of continuous residence are required for settlement as a Skilled Worker?",
        "expected_answer": "5 years",
        "category": "answerable",
        "source": "SW 21.1",
    },
    {
        "question": "Does the Skilled Worker route lead to settlement?",
        "expected_answer": "Yes — after 5 years",
        "category": "answerable",
        "source": "SW 21.1 / overview text",
    },
    {
        "question": "What is the minimum amount of funds required for a dependent partner of a Skilled Worker?",
        "expected_answer": "£285",
        "category": "answerable",
        "source": "SW 33.3(a)",
    },
    {
        "question": "What is the minimum amount of funds required for the first dependent child of a Skilled Worker?",
        "expected_answer": "£315",
        "category": "answerable",
        "source": "SW 33.3(b)",
    },
    {
        "question": "How many points must a Graduate route applicant be awarded?",
        "expected_answer": "70 points, all from the successful course completion requirement",
        "category": "answerable",
        "source": "GR 3.1",
    },
    {
        "question": "Does the Graduate route require a sponsor?",
        "expected_answer": "No — the Graduate route is unsponsored",
        "category": "answerable",
        "source": "Graduate appendix overview",
    },
    {
        "question": "Is the Graduate route a route to settlement?",
        "expected_answer": "No — the Graduate route is not a route to settlement",
        "category": "answerable",
        "source": "Graduate appendix overview",
    },
    {
        "question": "How long is permission granted for a Graduate route applicant with a PhD or other doctoral qualification?",
        "expected_answer": "3 years",
        "category": "answerable",
        "source": "GR 8.1",
    },
    {
        "question": "How long is permission granted for a bachelor's or master's degree graduate applying before 1 January 2027?",
        "expected_answer": "2 years",
        "category": "answerable",
        "source": "GR 8.1",
    },
    {
        "question": "How long is permission granted for a bachelor's or master's degree graduate applying on or after 1 January 2027?",
        "expected_answer": "18 months",
        "category": "answerable",
        "source": "GR 8.1",
    },
    {
        "question": "For a Graduate route course longer than 12 months, what is the minimum period of Student permission that must have been spent studying in the UK?",
        "expected_answer": "At least 12 months",
        "category": "answerable",
        "source": "GR 6.1",
    },
    # CATEGORY 2: SYNTHESIS (requires combining 2+ sections) — 18 questions
    {
        "question": "Is the salary threshold the same for every Skilled Worker applicant, or does it depend on their circumstances?",
        "expected_answer": "It depends on circumstances — options A through K each have different thresholds (e.g. £41,700 for Option A, £33,400 for Options B/D, £25,000 for Option K), not one flat number",
        "category": "synthesis",
        "source": "SW 4.2 (all options)",
    },
    {
        "question": "If a Skilled Worker is being sponsored for a job on the Immigration Salary List, what salary applies?",
        "expected_answer": "At least £33,400 per year AND the going rate for the occupation (Option D)",
        "category": "synthesis",
        "source": "SW 4.2 Option D",
    },
    {
        "question": "How is a Skilled Worker's required salary adjusted if they work part-time, e.g. 30 hours a week instead of 37.5?",
        "expected_answer": "The going rate is pro-rated: going rate × (weekly hours ÷ 37.5)",
        "category": "synthesis",
        "source": "SW 14.4",
    },
    {
        "question": "Does a new entrant Skilled Worker under Option E need to meet the same salary threshold as an experienced worker under Option A?",
        "expected_answer": "No — Option E requires at least £33,400 and 70% of the going rate, lower than Option A's £41,700 and full going rate",
        "category": "synthesis",
        "source": "SW 4.2 Options A and E",
    },
    {
        "question": "If a Skilled Worker applicant has a relevant PhD in a STEM subject, what salary do they need compared to someone without a PhD?",
        "expected_answer": "A lower salary — at least £33,400 and 80% of the going rate (Option C), versus £41,700 and full going rate without a PhD (Option A)",
        "category": "synthesis",
        "source": "SW 4.2 Options A and C",
    },
    {
        "question": "Does a Skilled Worker applying for settlement need to meet the same salary threshold as when they first applied?",
        "expected_answer": "Not necessarily the same figure — settlement has its own salary table (SW 24.3) with thresholds from £25,000 to £41,700 depending on circumstances, which may differ from the original application thresholds",
        "category": "synthesis",
        "source": "SW 24.3 vs SW 4.2",
    },
    {
        "question": "If a Skilled Worker is sponsored for a job requiring a criminal record certificate, does this requirement also apply to their dependent partner?",
        "expected_answer": "Yes, if the Skilled Worker is sponsored in one of the listed SOC codes, the dependent partner applying for entry clearance must also provide a criminal record certificate",
        "category": "synthesis",
        "source": "SW 16.1 and SW 34.1",
    },
    {
        "question": "Do both a Skilled Worker and their dependent partner need to independently meet the financial requirement, or can funds be combined?",
        "expected_answer": "Funds can be held collectively by the applicant, the Skilled Worker, and (for a dependent child) their parent — they don't need to be independently met",
        "category": "synthesis",
        "source": "SW 33.2(a)",
    },
    {
        "question": "How does the settlement salary requirement differ for someone on the Immigration Salary List compared to someone in a health or education occupation?",
        "expected_answer": "Immigration Salary List (row B): £33,400 minimum; health/education occupation in Table 3 (row D): £25,000 minimum — different thresholds",
        "category": "synthesis",
        "source": "SW 24.3 rows B and D",
    },
    {
        "question": "Would someone who completed a PGCE qualify for the Graduate route in the same way as someone with a bachelor's degree?",
        "expected_answer": "Yes — a PGCE is listed as a relevant qualification for the Graduate route qualification requirement, alongside bachelor's and postgraduate degrees",
        "category": "synthesis",
        "source": "GR 5.2(e)",
    },
    {
        "question": "If a Graduate route applicant's course was renamed by their sponsor but the content stayed the same, does this affect their eligibility?",
        "expected_answer": "No — this does not prevent them meeting the qualification requirement, as long as the course content remained the same",
        "category": "synthesis",
        "source": "GR 5.3",
    },
    {
        "question": "Can a dependent child of a Graduate route applicant who was born in the UK qualify as a dependant even if they weren't previously a Student dependant?",
        "expected_answer": "Yes — a child born in the UK to a Graduate who holds existing Graduate route permission can qualify",
        "category": "synthesis",
        "source": "GR 9.4A(d)",
    },
    {
        "question": "Is the salary threshold calculation method (e.g. pro-rating for part-time work) the same for the Skilled Worker and Graduate routes?",
        "expected_answer": "Not comparable — the Graduate route has no salary threshold at all, so pro-rating rules under SW 14 don't apply to it",
        "category": "synthesis",
        "source": "SW 14.4 vs Graduate appendix (no salary requirement)",
    },
    {
        "question": "If someone was previously a Tier 2 (General) Migrant sponsored in a specific SOC 2010 code, could transitional salary arrangements affect their current threshold?",
        "expected_answer": "Yes — if certain conditions are met (continuous sponsorship in the code, application before 1 December 2026), different going rates from the transitional table apply instead of the standard going rates",
        "category": "synthesis",
        "source": "SW 14.5",
    },
    {
        "question": "Does a Skilled Worker applicant who has been in the UK for over 12 months need to show £1,270 in funds?",
        "expected_answer": "No — if applying for permission to stay and has been in the UK with permission for 12+ months, they automatically meet the financial requirement without needing to show funds",
        "category": "synthesis",
        "source": "SW 15.1",
    },
    {
        "question": "Can a dependent partner of a Skilled Worker be granted permission for longer than the Skilled Worker's own permission?",
        "expected_answer": "Only in specific cases — a partner gets permission ending with the Skilled Worker's permission, unless the Skilled Worker is granted settlement, in which case the partner gets 3 years",
        "category": "synthesis",
        "source": "SW 36.1",
    },
    {
        "question": "If a Graduate route dependent partner's Graduate-route partner gets settlement on a different route later, does their permission automatically extend?",
        "expected_answer": "Not addressed this way — a Graduate route dependent partner's permission ends on the same date as the Graduate's permission; the Graduate route itself doesn't lead to settlement",
        "category": "synthesis",
        "source": "GR 16.1 and Graduate appendix overview",
    },
    {
        "question": "Would a Skilled Worker sponsored in a listed health occupation and a Skilled Worker sponsored in a non-listed occupation have the same criminal record certificate requirement?",
        "expected_answer": "No — the criminal record certificate is only required for applicants sponsored in the specific SOC codes listed in SW 16.1, which includes many health/education/care roles but not all occupations",
        "category": "synthesis",
        "source": "SW 16.1",
    },
    
    # CATEGORY 3: UNANSWERABLE / TRICK — 25 questions
    {
        "question": "What SOC 2020 occupation code is required for a Graduate route application?",
        "expected_answer": "Not applicable — the Graduate route does not require a SOC occupation code (that's a Skilled Worker requirement)",
        "category": "unanswerable_trick",
        "source": "N/A — Graduate route has no SOC requirement",
    },
    {
        "question": "What salary must a Graduate route applicant earn to qualify?",
        "expected_answer": "Not applicable — the Graduate route has no salary threshold requirement",
        "category": "unanswerable_trick",
        "source": "N/A — Graduate route is unsponsored with no salary requirement",
    },
    {
        "question": "Which sponsor must a Graduate route applicant have a Certificate of Sponsorship from?",
        "expected_answer": "Not applicable — the Graduate route is unsponsored; there is no Certificate of Sponsorship requirement",
        "category": "unanswerable_trick",
        "source": "N/A — Graduate route is unsponsored",
    },
    {
        "question": "How many years of residence are needed before a Graduate route holder can apply for settlement?",
        "expected_answer": "Not applicable — the Graduate route is not a route to settlement at all",
        "category": "unanswerable_trick",
        "source": "N/A — Graduate route is not a settlement route",
    },
    {
        "question": "What is the going rate salary for a Skilled Worker sponsored in SOC code '2461 Social workers'?",
        "expected_answer": "Not stated in this document — the going rate tables (Appendix Skilled Occupations) are referenced but not included in this rulebook extract",
        "category": "unanswerable_trick",
        "source": "N/A — Appendix Skilled Occupations not included in this rulebook",
    },
    {
        "question": "What is the application fee for a Skilled Worker visa?",
        "expected_answer": "Not stated in this document — fee amounts are not included in the Appendix Skilled Worker rulebook extract",
        "category": "unanswerable_trick",
        "source": "N/A — fee schedule not included",
    },
    {
        "question": "How long does it typically take to process a Skilled Worker visa application?",
        "expected_answer": "Not stated in this document — processing times are not covered by the Immigration Rules text",
        "category": "unanswerable_trick",
        "source": "N/A — not covered in this rulebook",
    },
    {
        "question": "Can a Skilled Worker visa holder apply for British citizenship directly, without going through settlement first?",
        "expected_answer": "Not stated in this document — citizenship requirements are governed by separate British Nationality Act rules, not the Skilled Worker appendix",
        "category": "unanswerable_trick",
        "source": "N/A — citizenship rules not covered in this rulebook",
    },
    {
        "question": "What is the Immigration Health Surcharge amount for a Skilled Worker applicant?",
        "expected_answer": "Not stated in this document — while the Immigration Health Charge is referenced as a requirement to pay, the specific amount is not included in this rulebook extract",
        "category": "unanswerable_trick",
        "source": "N/A — IHS amount not included",
    },
    {
        "question": "Does the Graduate route allow the applicant to switch into the Skilled Worker route without leaving the UK?",
        "expected_answer": "Not directly stated in this document — switching rules between routes are not covered in this rulebook extract",
        "category": "unanswerable_trick",
        "source": "N/A — switching rules not covered",
    },
    {
        "question": "What is the required going rate for a Skilled Worker sponsored as '2211 Generalist medical practitioner' under Option A?",
        "expected_answer": "Not stated in this document — while SW 18.1A specifically mentions this occupation code for grant period purposes, the going rate figure itself is in Appendix Skilled Occupations, not included here",
        "category": "unanswerable_trick",
        "source": "N/A — going rate table not included, though the occupation code is mentioned for a different purpose (grant period)",
    },
    {
        "question": "Is a dependent partner of a Graduate route applicant allowed to work in the UK?",
        "expected_answer": "Yes — work (including self-employment and voluntary work) is permitted, except as a professional sportsperson or sports coach",
        "category": "unanswerable_trick",
        "source": "GR 16.3(b) — NOTE: this one is actually answerable; included as a check that the system doesn't over-flag real answers as unanswerable",
    },
    {
        "question": "Can a Skilled Worker applicant's sponsor charge them for the Immigration Skills Charge?",
        "expected_answer": "Not directly answered — the rulebook states the sponsor must have paid the Immigration Skills Charge in full, but doesn't state whether they can pass this cost to the applicant",
        "category": "unanswerable_trick",
        "source": "N/A — cost-passing rules not covered in SW 5.4",
    },
    {
        "question": "What happens if a Skilled Worker's sponsor loses their sponsor licence while the applicant is mid-visa?",
        "expected_answer": "Not stated in this document — this scenario and its consequences are not covered in this rulebook extract",
        "category": "unanswerable_trick",
        "source": "N/A — not covered in this rulebook",
    },
    {
        "question": "Does a Graduate route applicant need to pass an English language test?",
        "expected_answer": "Not stated in this document — unlike the Skilled Worker route (which explicitly requires B2/B1 English), no English language requirement is mentioned in the Graduate appendix",
        "category": "unanswerable_trick",
        "source": "N/A — no English requirement stated for Graduate route in this rulebook",
    },
    {
        "question": "What is the maximum number of times a Skilled Worker applicant can renew their visa before needing to apply for settlement?",
        "expected_answer": "Not stated in this document — this specific limit is not addressed in the rulebook extract",
        "category": "unanswerable_trick",
        "source": "N/A — not covered in this rulebook",
    },
    {
        "question": "Can a Graduate route holder's dependent child attend a UK state school without additional permission?",
        "expected_answer": "Not stated in this document — study conditions cover the Graduate/dependant themselves, but school attendance for minors specifically is not addressed",
        "category": "unanswerable_trick",
        "source": "N/A — not covered in this rulebook",
    },
    {
        "question": "Under Option F of the Skilled Worker points table, what salary is required?",
        "expected_answer": "Not stated in this document — this rulebook extract covers Options A through E and K explicitly, but does not include full details for Option F",
        "category": "unanswerable_trick",
        "source": "N/A — Option F details not included in this extract; note SW 14.5 references Options F-J for transitional cases without giving their base definitions",
    },
    {
        "question": "Is there an age limit for a Graduate route applicant?",
        "expected_answer": "Not stated in this document — unlike the Skilled Worker route (which requires the applicant to be 18+), no age requirement is mentioned for the main Graduate applicant in this rulebook extract",
        "category": "unanswerable_trick",
        "source": "N/A — no age requirement stated for Graduate route in this rulebook",
    },
    {
        "question": "Does a Skilled Worker visa holder need to inform the Home Office if they change address?",
        "expected_answer": "Not stated in this document — general reporting obligations are not covered in this rulebook extract",
        "category": "unanswerable_trick",
        "source": "N/A — not covered in this rulebook",
    },
    {
        "question": "What is the going rate for SOC code '2113 Physical scientists' under the transitional arrangements?",
        "expected_answer": "£27,190 (£13.94 per hour) for options F and I",
        "category": "unanswerable_trick",
        "source": "SW 14.5(c) table — NOTE: this one IS answerable; included as a check the system doesn't over-flag real answers as unanswerable",
    },
    {
        "question": "Can a Skilled Worker applicant include their unmarried partner of less than 2 years as a dependant?",
        "expected_answer": "Not directly stated in this document — the rulebook references 'Appendix Relationship with Partner' for the detailed relationship requirement, but that appendix's content is not included here",
        "category": "unanswerable_trick",
        "source": "N/A — Appendix Relationship with Partner not included in this rulebook",
    },
    {
        "question": "Does a Skilled Worker on the Graduate route need an ATAS certificate to study a sensitive subject?",
        "expected_answer": "This question conflates two separate routes — 'Skilled Worker on the Graduate route' is not a valid combination; each route has its own separate ATAS condition",
        "category": "unanswerable_trick",
        "source": "N/A — deliberately conflates two distinct routes",
    },
    {
        "question": "What is the minimum salary threshold for a Graduate route applicant's dependent partner to bring their own dependent child?",
        "expected_answer": "Not applicable — dependants of the Graduate route are not subject to salary thresholds; that concept only applies to the Skilled Worker route",
        "category": "unanswerable_trick",
        "source": "N/A — salary thresholds don't apply to Graduate route dependants",
    },
    {
        "question": "If a Skilled Worker's certificate of sponsorship states a start date more than 3 months after the application date, is the application still valid?",
        "expected_answer": "No — the certificate must have a start date no more than 3 months after the date of application, per SW 5.1",
        "category": "unanswerable_trick",
        "source": "SW 5.1 — NOTE: this one IS answerable; included as a check the system doesn't over-flag real answers as unanswerable",
    },
]
