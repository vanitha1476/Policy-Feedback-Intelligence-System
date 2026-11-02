"""
Synthetic e-Consultation Comment Generator for Ministry of Corporate Affairs (MCA)
Draft Digital Competition Bill (CDCL 2024).

Generates a realistic multi-stakeholder dataset with:
- Explicit section citations vs implicit topical mentions vs unlinked feedback
- Stance ground-truth (support, oppose, neutral)
- Stakeholder personas (Big Tech, Startups, MSMEs, Legal, Consumers, Citizens)
- Hinglish noise & sarcastic/emotional tone variations
- Seeded near-duplicate Astroturfing campaigns with controlled burst windows
"""

import os
import json
import random
import datetime
from typing import List, Dict, Any
import pandas as pd

from src.ingest.cleaner import normalize_text, scrub_pii


def load_sections(sections_path: str) -> List[Dict[str, Any]]:
    with open(sections_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Core arguments library per section and stance
ARGUMENT_BANK = {
    "SEC-03": {
        "oppose": [
            "Ex-ante designation under Section 3 is overly punitive and deviates from proven ex-post antitrust frameworks.",
            "The criteria for designating SSDEs are too vague, leaving immense arbitrary discretion to the Commission.",
            "Designating digital platforms prematurely will disincentivize companies from scaling their investments in India.",
        ],
        "support": [
            "Section 3 is the cornerstone of modern digital governance; ex-ante designation is essential before monopolies harm markets.",
            "Traditional antitrust investigations take years; Section 3 allows the CCI to proactively enforce fair competition.",
            "Clear ex-ante designation under Section 3 will protect Indian consumers and emergent domestic innovators.",
        ],
        "neutral": [
            "We request the MCA to clarify the timeline and formal hearing procedures before an SSDE designation under Section 3 is finalized.",
            "Section 3 designation should include an annual review mechanism to account for rapidly shifting digital market shares.",
        ]
    },
    "SEC-04": {
        "oppose": [
            "The INR 4,000 crore turnover and USD 30 billion global threshold under Section 4 is far too low and captures growth-stage companies.",
            "Section 4 thresholds penalize global tech firms whose actual revenues inside India remain a modest fraction of their global book.",
            "Gross Merchandise Value (GMV) of INR 16,000 crore is an inappropriate metric because GMV does not reflect operating profitability.",
            "The 1 crore user threshold will easily drag popular consumer platforms into severe compliance obligations prematurely.",
        ],
        "support": [
            "The financial and user thresholds in Section 4 are well-calibrated to capture true digital gatekeepers who control the Indian market.",
            "Section 4 thresholds are necessary to ensure that dominant multinational tech gatekeepers cannot escape regulatory oversight.",
            "We strongly welcome Section 4; digital platforms with millions of active Indian users wield massive systemic leverage.",
        ],
        "neutral": [
            "Clarification is needed under Section 4 regarding whether active users are calculated on monthly active (MAU) or daily active (DAU) basis.",
            "The Ministry should establish an inflation-adjusted indexation mechanism for the quantitative thresholds under Section 4.",
        ]
    },
    "SEC-05": {
        "oppose": [
            "Section 5 gives subjective qualitative powers to the CCI that could result in unpredictable regulatory overreach.",
            "Qualitative factors such as 'network effects' and 'access to capital' are ill-defined and will create legal uncertainty.",
        ],
        "support": [
            "Section 5 is crucial because dynamic tech monopolies often possess market power without meeting static balance sheet numbers.",
            "Qualitative assessment under Section 5 prevents gatekeepers from structuring subsidiaries specifically to dodge numerical caps.",
        ],
        "neutral": [
            "We suggest framing objective empirical guidelines before exercising qualitative discretion under Section 5.",
        ]
    },
    "SEC-06": {
        "oppose": [
            "Extending SSDE obligations to associate and group entities under Section 6 imposes excessive liability across independent corporate vehicles.",
            "Section 6 will discourage multinational conglomerates from establishing separate joint ventures or localized research units in India.",
        ],
        "support": [
            "Section 6 is indispensable; otherwise global tech giants will simply route anti-competitive operations through sister entities.",
            "Holding corporate groups jointly responsible under Section 6 closes loophole-ridden corporate shielding.",
        ],
        "neutral": [
            "Section 6 should clearly delineate between passive minority shareholdings and active operational control.",
        ]
    },
    "SEC-07": {
        "oppose": [
            "The requirement for fair dealing under Section 7 is broad and invites frivolous litigation from disgruntled merchants.",
            "Algorithmic transparency under Section 7 risks exposing proprietary trade secrets and search ranking IP.",
        ],
        "support": [
            "Arbitrary suspension of merchant accounts without due process has devastated countless Indian MSMEs; Section 7 is a godsend.",
            "Section 7 mandates much-needed transparency in algorithmic rankings and protects business users from sudden unilateral policy shifts.",
        ],
        "neutral": [
            "Standard operating procedures (SOPs) for merchant account deactivations should be explicitly notified under Section 7.",
        ]
    },
    "SEC-10": {
        "oppose": [
            "Anti-steering provisions in Section 10 undermine the platform business model and will increase transaction fraud risks.",
            "Prohibiting platforms from restricting external links under Section 10 compromises user safety and payment dispute handling.",
        ],
        "support": [
            "Section 10's prohibition on anti-steering is transformative; it stops gatekeepers from forcing 30% developer commissions.",
            "Startups must have the freedom to inform consumers about discounted prices on external websites; Section 10 delivers this.",
            "Section 10 breaks the predatory commission monopoly that app marketplaces have maintained over Indian software entrepreneurs.",
        ],
        "neutral": [
            "Section 10 should balance developer freedom with clear guidelines on who bears liability for off-platform payment defaults.",
        ]
    },
    "SEC-11": {
        "oppose": [
            "Section 11's ban on self-preferencing will harm consumers who benefit from high-quality, affordable private label goods.",
            "Restricting marketplaces from promoting their own services ignores basic retail economics practiced worldwide.",
        ],
        "support": [
            "Section 11 directly addresses platform bias where e-commerce giants prioritize their own private labels over third-party sellers.",
            "Algorithmic self-preferencing is an existential threat to Indian retailers; Section 11 levels the playing field completely.",
            "We strongly back Section 11; platforms that act as both umpire and player inevitably rig the game against independent merchants.",
        ],
        "neutral": [
            "We request clear safe-harbor rules under Section 11 distinguishing between organic sponsored search and unfair algorithmic self-preferencing.",
        ]
    },
    "SEC-12": {
        "oppose": [
            "Restricting data cross-use under Section 12 will severely degrade personalized recommendations and advertising efficiency.",
            "Prohibiting internal data analytics under Section 12 limits platforms from innovating new features and improving consumer safety.",
        ],
        "support": [
            "Section 12 puts an end to gatekeepers mining confidential merchant sales data to launch copycat competitor products.",
            "Protecting consumer data privacy and prohibiting unauthorized cross-platform profiling under Section 12 is essential.",
            "Section 12 ensures that market dominators cannot weaponize aggregated platform telemetry against their own ecosystem partners.",
        ],
        "neutral": [
            "Section 12 should harmonize definitions of user consent with the Digital Personal Data Protection (DPDP) Act, 2023.",
        ]
    },
    "SEC-13": {
        "oppose": [
            "Forced technical interoperability under Section 13 creates massive cyber-security vulnerabilities and compromises proprietary code.",
            "Section 13 interoperability requirements could lead to intellectual property theft and system instability.",
        ],
        "support": [
            "Section 13 ensures open standards, dismantles walled gardens, and allows emergent Indian apps to interoperate with dominant OS ecosystems.",
            "Interoperability under Section 13 fosters true innovation and prevents big platforms from trapping consumers in closed silos.",
        ],
        "neutral": [
            "Technical architecture and API specifications under Section 13 must be developed through industry-led standard-setting bodies.",
        ]
    },
    "SEC-14": {
        "oppose": [
            "Mandating sideloading and third-party app stores in Section 14 exposes millions of citizens to malware, spyware, and financial scams.",
            "Section 14 forces operating system vendors to dismantle vetted app verification security architectures.",
        ],
        "support": [
            "Section 14 liberates app distribution; device owners should have the fundamental right to install applications of their choice.",
            "Alternative app stores under Section 14 will spur competition, lower developer distribution costs, and break mobile OS monopolies.",
        ],
        "neutral": [
            "Section 14 should permit operating systems to maintain notarization and basic malware scanning for sideloaded packages.",
        ]
    },
    "SEC-17": {
        "oppose": [
            "The 15-day dispute resolution window under Section 17 is operationally unrealistic for complex technical or antitrust grievances.",
            "Mandating localized dispute infrastructure in India will add substantial administrative overhead for international service providers.",
        ],
        "support": [
            "Section 17 ensures that Indian business users finally have access to a speedy, time-bound 15-day grievance redressal mechanism.",
            "Having a designated Chief Compliance Officer in India under Section 17 ensures accountability and responsive grievance resolution.",
        ],
        "neutral": [
            "Section 17 should allow mediation and escalation tiers before imposing formal penalties for missed 15-day resolution windows.",
        ]
    },
    "SEC-21": {
        "oppose": [
            "The penalty of up to 10% of global turnover in Section 21 is draconian, disproportionate, and unconstitutional.",
            "Penalizing global revenue under Section 21 rather than India-derived revenue will trigger severe international legal challenges and chill FDI.",
            "Section 21 penalties are excessive and fail to differentiate between inadvertent compliance errors and willful anti-competitive misconduct.",
        ],
        "support": [
            "Section 21's 10% global turnover fine is the only deterrent digital monopolies will respect; trivial fines are treated as minor business costs.",
            "Without the teeth of Section 21, dominant platforms will flagrantly violate ex-ante regulations; strong sanctions are non-negotiable.",
            "We strongly commend Section 21; stringent penalties are necessary to enforce compliance against multi-trillion dollar tech giants.",
        ],
        "neutral": [
            "Section 21 must incorporate detailed sentencing guidelines, mitigating factors, and a clear cap on compounding penalties.",
        ]
    }
}

GENERAL_COMMENTS = [
    {"text": "The entire ex-ante regulatory framework proposed by the MCA is forward-looking and essential for a trillion-dollar digital economy.", "stance": "support"},
    {"text": "Over-regulation of the internet sector will choke Indian startup entrepreneurship and cause capital flight to Dubai and Singapore.", "stance": "oppose"},
    {"text": "While we welcome the initiative to promote fair competition, the Ministry must ensure that compliance costs do not crush growing businesses.", "stance": "neutral"},
    {"text": "Digital markets require swift regulatory intervention. Traditional antitrust remedies under the 2002 Act are simply too sluggish.", "stance": "support"},
    {"text": "India should follow light-touch regulation. Heavy-handed rules mimicking the EU Digital Markets Act will stifle innovation in the Global South.", "stance": "oppose"},
    {"text": "The consultation paper is comprehensive, but extensive capacity-building inside the Competition Commission of India is needed before enactment.", "stance": "neutral"},
    {"text": "Ex-ante rules ensure that our vibrant local developers get a fair shot against foreign monopoly giants. Full support to the Government.", "stance": "support"},
    {"text": "The draft bill creates too many regulatory hurdles. We urge the committee to adopt a voluntary industry code of conduct instead.", "stance": "oppose"}
]

HINGLISH_SNIPPETS = [
    "Compliance burden bahut zyada cumbersome ho jayega small companies ke liye.",
    "Desi startups aur Indian merchants ke liye ye draft bohot accha step hai.",
    "Bhai agar 10% global turnover ka fine lagaya toh foreign investors sab bhaag jayenge.",
    "Gatekeeper platforms ka monopoly todna compulsory hai, bilkul sahi move hai.",
    "Ye draft rules implement karne se pehle industry consultations aur badhao please."
]

SARCASTIC_SNIPPETS = [
    "Brilliant idea! Let's enact 500 pages of rules and wonder why no tech company wants to incorporate in India.",
    "Kudos to the committee for thinking a 15-day dispute window works when government courts take 15 years.",
    "What a surprise, global monopolies crying about regulatory compliance while banking billions in profit."
]


def generate_astroturfing_campaign(campaign_id: str, section_id: str, stance: str, count: int, 
                                   start_date: datetime.date, days_spread: int = 5) -> List[Dict[str, Any]]:
    """Generate near-duplicate campaign submissions with synonym perturbations and date clustering."""
    records = []
    
    if campaign_id == "CAMP-BIGTECH-SEC04":
        templates = [
            "We strongly urge the Ministry to reconsider the arbitrary quantitative thresholds under Section 4 and the disproportionate penalties under Section 21. Such measures will stifle foreign direct investment and harm India's digital innovation ecosystem.",
            "We respectfully submit that the arbitrary quantitative thresholds under Section 4 and disproportionate penalties under Section 21 require urgent reconsideration. These provisions will curb foreign investment and severely hurt India's tech ecosystem.",
            "We earnestly request the Ministry to revisit the quantitative thresholds in Section 4 and the 10% global penalty in Section 21. Imposing these rigid rules will discourage international capital and undermine India's digital economic ambitions.",
            "Our organization urges the Ministry to re-evaluate Section 4 turnover thresholds and Section 21 global turnover sanctions. These harsh provisions will dampen investor sentiment and harm India's technology ecosystem.",
            "We strongly advise reconsidering the arbitrary turnover criteria of Section 4 along with Section 21 penalties. These restrictive measures risk stifling technological progress and foreign direct investments in India."
        ]
        stakeholder = "Big Tech Lobby / Industry Association"
        source = "Coordinated Email Campaign"
    elif campaign_id == "CAMP-MSME-SEC11":
        templates = [
            "We wholeheartedly endorse Section 11 prohibiting self-preferencing of private labels and Section 10 stopping unfair anti-steering fees. Gatekeeper platforms have suppressed small Indian traders for far too long.",
            "We strongly support Section 11 against private label self-preferencing and Section 10 banning anti-steering practices. Independent Indian sellers have suffered under discriminatory gatekeeper policies for years.",
            "Our trade union fully backs Section 11 outlawing algorithmic self-preferencing and Section 10 barring anti-steering charges. Big tech gatekeepers must not be allowed to crush local small businesses.",
            "We welcome Section 11 to stop platform self-preferencing and Section 10 against anti-steering restrictions. Fair competition is essential to save millions of Indian micro-merchants.",
            "Full support for Section 11 and Section 10. Prohibiting private label bias and anti-steering commissions will ensure a level playing field for grassroots Indian retail enterprises."
        ]
        stakeholder = "MSME Retailers Association"
        source = "Merchant Portal Coalition"
    elif campaign_id == "CAMP-PRIV-SEC12":
        templates = [
            "Section 12 restricting unauthorized data cross-use and merchant data exploitation is vital to protect digital citizens' fundamental privacy and prevent anticompetitive profiling.",
            "We strongly endorse Section 12. Banning cross-service data profiling and misuse of confidential merchant metrics is crucial for consumer privacy and fair market conduct.",
            "Section 12 is essential for digital sovereignty; preventing dominant platforms from weaponizing proprietary merchant data and user profiles safeguards fair competition.",
            "We fully support Section 12 restrictions on combining personal data and exploiting commercial data. This provision protects consumer privacy and ends surveillance capitalism.",
            "Section 12 prohibiting data cross-use and merchant data abuse is necessary to protect citizen privacy and stop monopolistic algorithmic exploitation."
        ]
        stakeholder = "Digital Rights & Consumer Coalition"
        source = "Citizen Petition Form"
    else:
        templates = ["Standard submission supporting regulatory clarity and fair public participation."]
        stakeholder = "Public Interest Group"
        source = "e-Consultation Portal"

    for i in range(count):
        base_tmpl = random.choice(templates)
        # Minor variation: add slight greeting or closing
        intros = ["", "To the Joint Secretary, MCA: ", "Respected Committee Members, ", "Submission regarding Draft Bill: ", "Dear Sir/Madam, "]
        outros = ["", " Yours sincerely.", " Respectfully submitted.", " Awaiting prompt positive consideration.", " Submitted on behalf of our members."]
        full_text = random.choice(intros) + base_tmpl + random.choice(outros)
        
        # Date perturbation within burst window
        day_offset = random.randint(0, days_spread)
        hour = random.randint(8, 20)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        dt = datetime.datetime.combine(start_date + datetime.timedelta(days=day_offset), datetime.time(hour, minute, second))
        
        records.append({
            "text": full_text,
            "true_section_id": section_id,
            "true_stance": stance,
            "stakeholder_type": stakeholder,
            "source": source,
            "is_campaign": True,
            "campaign_id": campaign_id,
            "citation_style": "explicit_cite",
            "timestamp": dt.isoformat(),
            "has_hinglish": False
        })
    return records


def build_synthetic_dataset(sections_path: str, output_csv: str, total_count: int = 5000, seed: int = 42) -> pd.DataFrame:
    """Generate the complete 5,000-comment consultation dataset."""
    random.seed(seed)
    sections = load_sections(sections_path)
    section_map = {s["section_id"]: s for s in sections}
    
    records = []
    
    # 1. Seed Campaign Bursts (Orchestrated mass comments)
    # Campaign A: Big Tech anti-Section 4 (350 comments, Week 3: March 18-22, 2024)
    camp_a = generate_astroturfing_campaign("CAMP-BIGTECH-SEC04", "SEC-04", "oppose", 350, datetime.date(2024, 3, 18), days_spread=4)
    records.extend(camp_a)
    
    # Campaign B: MSME pro-Section 11 (250 comments, Week 4: March 25-29, 2024)
    camp_b = generate_astroturfing_campaign("CAMP-MSME-SEC11", "SEC-11", "support", 250, datetime.date(2024, 3, 25), days_spread=4)
    records.extend(camp_b)
    
    # Campaign C: Privacy coalition pro-Section 12 (150 comments, Week 2: March 11-14, 2024)
    camp_c = generate_astroturfing_campaign("CAMP-PRIV-SEC12", "SEC-12", "support", 150, datetime.date(2024, 3, 11), days_spread=3)
    records.extend(camp_c)
    
    campaign_count = len(records)
    remaining_count = total_count - campaign_count
    
    # Timeline parameters for background comments: 2024-03-01 to 2024-04-12 (42 days)
    start_timeline = datetime.date(2024, 3, 1)
    
    stakeholders = [
        "Tech Startup Founder", "MSME Retailer", "Big Tech Corporate", 
        "Legal Scholar / Law Firm", "Consumer Advocate", "Individual Citizen", "Anonymous"
    ]
    sources = ["e-Consultation Portal", "Email Submission", "Trade Body Memorandum"]
    
    # 2. Generate remaining non-campaign individual comments
    for i in range(remaining_count):
        # 12% General unlinked comments, 88% Section-linked
        if random.random() < 0.12:
            gen_item = random.choice(GENERAL_COMMENTS)
            text = gen_item["text"]
            sec_id = "GENERAL"
            stance = gen_item["stance"]
            cite_style = "unlinked_general"
        else:
            sec = random.choice(sections)
            sec_id = sec["section_id"]
            sec_num = sec["section_number"]
            stance = random.choices(["oppose", "support", "neutral"], weights=[0.38, 0.44, 0.18])[0]
            core_arg = random.choice(ARGUMENT_BANK[sec_id][stance])
            
            cite_mode = random.choices(["explicit", "topical"], weights=[0.55, 0.45])[0]
            if cite_mode == "explicit":
                prefixes = [
                    f"With reference to Section {sec_num}: ",
                    f"Regarding Clause {sec_num} of the proposed bill, ",
                    f"In connection with Section {sec_num} ({sec['section_title']}): ",
                    f"Our submission on Section {sec_num} is as follows: ",
                    f"Looking at sub-clause provisions in Section {sec_num}, "
                ]
                text = random.choice(prefixes) + core_arg
                cite_style = "explicit_cite"
            else:
                # Topical mention (uses keywords from section without explicit section number)
                text = core_arg
                cite_style = "topical_mention"
        
        # Inject occasional Hinglish noise or Sarcasm
        has_hinglish = False
        rand_val = random.random()
        if rand_val < 0.07:
            text = text + " " + random.choice(HINGLISH_SNIPPETS)
            has_hinglish = True
        elif rand_val < 0.12:
            text = text + " " + random.choice(SARCASTIC_SNIPPETS)
            
        # Optional PII artifact to test cleaning pipeline (emails/phones in 3% of submissions)
        if random.random() < 0.03:
            fake_email = f"user_{random.randint(100,999)}@domain.in"
            fake_phone = f"+91 98{random.randint(10000000, 99999999)}"
            text += f" Contact our legal counsel at {fake_email} or {fake_phone} for full depositions."

        # Random timestamp across the 42-day window with slight bell-curve concentration
        day_offset = int(random.triangular(0, 42, 22))
        hour = random.randint(7, 22)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        dt = datetime.datetime.combine(start_timeline + datetime.timedelta(days=day_offset), datetime.time(hour, minute, second))
        
        records.append({
            "text": text,
            "true_section_id": sec_id,
            "true_stance": stance,
            "stakeholder_type": random.choice(stakeholders),
            "source": random.choice(sources),
            "is_campaign": False,
            "campaign_id": None,
            "citation_style": cite_style,
            "timestamp": dt.isoformat(),
            "has_hinglish": has_hinglish
        })

    # Shuffle to interleave campaigns with organic comments
    random.shuffle(records)
    
    # Assign sequential comment IDs and clean text
    for idx, r in enumerate(records):
        r["comment_id"] = f"MCA-2024-{idx+1:05d}"
        r["clean_text"] = normalize_text(r["text"])
        r["is_synthetic"] = True
        
    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"Generated {len(df)} simulated comments successfully saved to {output_csv}")
    return df


if __name__ == "__main__":
    sections_file = os.path.join("data", "draft_sections", "mca_draft_sections.json")
    out_file = os.path.join("data", "processed", "simulated_mca_comments.csv")
    build_synthetic_dataset(sections_file, out_file)
