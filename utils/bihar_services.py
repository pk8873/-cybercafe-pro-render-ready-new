"""Curated Bihar CSC / cyber-cafe service catalog.

Each item has a bilingual label (Hindi + English), category, an emoji icon,
and a suggested operator fee in INR. Used by the dashboard quick-grid and
to pre-fill the new-service form so operators in small Bihar districts
can bill in 2 taps instead of typing.
"""

BIHAR_SERVICES = [
    # --- RTPS Bihar (most-used) ---
    {"key": "aay",        "name_en": "Aay Praman Patra",       "name_hi": "आय प्रमाण पत्र",          "cat": "RTPS",     "emoji": "💰", "fee": 50,  "portal": "https://serviceonline.bihar.gov.in"},
    {"key": "jaati",      "name_en": "Jaati Praman Patra",     "name_hi": "जाति प्रमाण पत्र",        "cat": "RTPS",     "emoji": "🪪", "fee": 50,  "portal": "https://serviceonline.bihar.gov.in"},
    {"key": "niwas",      "name_en": "Niwas Praman Patra",     "name_hi": "निवास प्रमाण पत्र",        "cat": "RTPS",     "emoji": "🏠", "fee": 50,  "portal": "https://serviceonline.bihar.gov.in"},
    {"key": "ews",        "name_en": "EWS Certificate",        "name_hi": "EWS प्रमाण पत्र",          "cat": "RTPS",     "emoji": "📜", "fee": 60,  "portal": "https://serviceonline.bihar.gov.in"},
    {"key": "obc-ncl",    "name_en": "OBC Non-Creamy Layer",   "name_hi": "OBC NCL प्रमाण पत्र",      "cat": "RTPS",     "emoji": "📜", "fee": 60,  "portal": "https://serviceonline.bihar.gov.in"},
    {"key": "birth",      "name_en": "Birth Certificate",      "name_hi": "जन्म प्रमाण पत्र",         "cat": "RTPS",     "emoji": "👶", "fee": 50,  "portal": "https://serviceonline.bihar.gov.in"},
    {"key": "death",      "name_en": "Death Certificate",      "name_hi": "मृत्यु प्रमाण पत्र",        "cat": "RTPS",     "emoji": "🕊️", "fee": 50,  "portal": "https://serviceonline.bihar.gov.in"},
    {"key": "character",  "name_en": "Character Certificate",  "name_hi": "चरित्र प्रमाण पत्र",        "cat": "RTPS",     "emoji": "🛡️", "fee": 60,  "portal": "https://serviceonline.bihar.gov.in"},

    # --- Bihar Bhumi / land ---
    {"key": "lpc",        "name_en": "LPC (Land Possession)",  "name_hi": "LPC / दाखिल-खारिज",        "cat": "Bhumi",    "emoji": "🌾", "fee": 100, "portal": "https://biharbhumi.bihar.gov.in"},
    {"key": "jamabandi",  "name_en": "Jamabandi / Khata-Khesra","name_hi": "जमाबंदी / खाता-खेसरा",     "cat": "Bhumi",    "emoji": "📒", "fee": 30,  "portal": "https://biharbhumi.bihar.gov.in"},
    {"key": "rasid",      "name_en": "Online Rasid (Lagaan)",  "name_hi": "ऑनलाइन रसीद (लगान)",       "cat": "Bhumi",    "emoji": "🧾", "fee": 30,  "portal": "https://bhulagan.bihar.gov.in"},

    # --- Identity ---
    {"key": "pan-new",    "name_en": "New PAN Card",           "name_hi": "नया पैन कार्ड",            "cat": "Identity", "emoji": "💳", "fee": 150, "portal": "https://www.onlineservices.nsdl.com"},
    {"key": "pan-correct","name_en": "PAN Correction",         "name_hi": "पैन सुधार",                "cat": "Identity", "emoji": "💳", "fee": 150, "portal": "https://www.onlineservices.nsdl.com"},
    {"key": "aadhaar",    "name_en": "Aadhaar Update",         "name_hi": "आधार अपडेट",               "cat": "Identity", "emoji": "🪪", "fee": 50,  "portal": "https://uidai.gov.in"},
    {"key": "voter",      "name_en": "Voter ID / Form 6",      "name_hi": "वोटर आईडी / फॉर्म 6",      "cat": "Identity", "emoji": "🗳️", "fee": 50,  "portal": "https://voters.eci.gov.in"},
    {"key": "passport",   "name_en": "Passport Apply",         "name_hi": "पासपोर्ट आवेदन",            "cat": "Identity", "emoji": "📘", "fee": 200, "portal": "https://www.passportindia.gov.in"},

    # --- Driving / vehicle ---
    {"key": "ll",         "name_en": "Learning Licence",       "name_hi": "लर्निंग लाइसेंस",          "cat": "Vehicle",  "emoji": "🛵", "fee": 100, "portal": "https://parivahan.gov.in"},
    {"key": "dl",         "name_en": "Driving Licence",        "name_hi": "ड्राइविंग लाइसेंस",         "cat": "Vehicle",  "emoji": "🚗", "fee": 200, "portal": "https://parivahan.gov.in"},
    {"key": "rc",         "name_en": "Vehicle RC Print",       "name_hi": "RC प्रिंट",                "cat": "Vehicle",  "emoji": "📄", "fee": 50,  "portal": "https://parivahan.gov.in"},

    # --- Welfare / pension / ration ---
    {"key": "ration",     "name_en": "Ration Card Apply",      "name_hi": "राशन कार्ड आवेदन",         "cat": "Welfare",  "emoji": "🍚", "fee": 80,  "portal": "https://epds.bihar.gov.in"},
    {"key": "pension",    "name_en": "Vridha / Vidhwa Pension","name_hi": "वृद्धा / विधवा पेंशन",     "cat": "Welfare",  "emoji": "👵", "fee": 80,  "portal": "https://www.sspmis.in"},
    {"key": "labour",     "name_en": "Labour Card",            "name_hi": "लेबर कार्ड",               "cat": "Welfare",  "emoji": "🧱", "fee": 80,  "portal": "https://bocw.bihar.gov.in"},
    {"key": "scholarship","name_en": "Scholarship (NSP/PMS)",  "name_hi": "छात्रवृत्ति आवेदन",        "cat": "Welfare",  "emoji": "🎓", "fee": 100, "portal": "https://scholarships.gov.in"},

    # --- Bills / recharge ---
    {"key": "bijli",      "name_en": "Bijli Bill (NBPDCL/SBPDCL)","name_hi": "बिजली बिल भुगतान",     "cat": "Bills",    "emoji": "💡", "fee": 20,  "portal": "https://www.bsphcl.co.in"},
    {"key": "gas",        "name_en": "Gas Booking",            "name_hi": "गैस बुकिंग",               "cat": "Bills",    "emoji": "🔥", "fee": 20,  "portal": ""},
    {"key": "mobile",     "name_en": "Mobile Recharge",        "name_hi": "मोबाइल रिचार्ज",            "cat": "Bills",    "emoji": "📱", "fee": 10,  "portal": ""},
    {"key": "dth",        "name_en": "DTH Recharge",           "name_hi": "DTH रिचार्ज",              "cat": "Bills",    "emoji": "📺", "fee": 10,  "portal": ""},

    # --- Exams / forms ---
    {"key": "bpsc",       "name_en": "BPSC / BSSC Form",       "name_hi": "BPSC / BSSC फॉर्म",        "cat": "Exam",     "emoji": "📝", "fee": 100, "portal": "https://www.bpsc.bih.nic.in"},
    {"key": "railway",    "name_en": "Railway / RRB Form",     "name_hi": "रेलवे / RRB फॉर्म",        "cat": "Exam",     "emoji": "🚆", "fee": 100, "portal": "https://www.rrbcdg.gov.in"},
    {"key": "neet",       "name_en": "NEET / JEE Form",        "name_hi": "NEET / JEE फॉर्म",         "cat": "Exam",     "emoji": "🎓", "fee": 150, "portal": "https://nta.ac.in"},
    {"key": "admit",      "name_en": "Admit Card Print",       "name_hi": "एडमिट कार्ड प्रिंट",       "cat": "Exam",     "emoji": "🖨️", "fee": 20,  "portal": ""},

    # --- Print / scan / shop ---
    {"key": "print",      "name_en": "Print (B/W per page)",   "name_hi": "प्रिंट (काला-सफ़ेद)",       "cat": "Shop",     "emoji": "🖨️", "fee": 5,   "portal": ""},
    {"key": "print-col",  "name_en": "Print (Color per page)", "name_hi": "रंगीन प्रिंट",              "cat": "Shop",     "emoji": "🌈", "fee": 15,  "portal": ""},
    {"key": "xerox",      "name_en": "Photocopy (Xerox)",      "name_hi": "फोटोकॉपी",                 "cat": "Shop",     "emoji": "📄", "fee": 2,   "portal": ""},
    {"key": "scan",       "name_en": "Scan / PDF",             "name_hi": "स्कैन / PDF",              "cat": "Shop",     "emoji": "📸", "fee": 10,  "portal": ""},
    {"key": "lamination", "name_en": "Lamination",             "name_hi": "लेमिनेशन",                 "cat": "Shop",     "emoji": "✨", "fee": 20,  "portal": ""},
    {"key": "passport-ph","name_en": "Passport Photo (8 pcs)", "name_hi": "पासपोर्ट फोटो (8)",        "cat": "Shop",     "emoji": "🤳", "fee": 50,  "portal": ""},
    {"key": "typing",     "name_en": "Form Typing / Filling",  "name_hi": "फॉर्म टाइपिंग",            "cat": "Shop",     "emoji": "⌨️", "fee": 30,  "portal": ""},

    # --- Banking / DBT ---
    {"key": "aeps",       "name_en": "AEPS Cash Withdraw",     "name_hi": "AEPS नकद निकासी",          "cat": "Bank",     "emoji": "🏧", "fee": 20,  "portal": ""},
    {"key": "money",      "name_en": "Money Transfer (DMT)",   "name_hi": "मनी ट्रांसफर (DMT)",       "cat": "Bank",     "emoji": "💸", "fee": 30,  "portal": ""},
    {"key": "csp",        "name_en": "Bank CSP Service",       "name_hi": "बैंक CSP सेवा",            "cat": "Bank",     "emoji": "🏦", "fee": 20,  "portal": ""},

    # --- Insurance / pension scheme ---
    {"key": "pmjay",      "name_en": "Ayushman / PMJAY Card",  "name_hi": "आयुष्मान कार्ड",            "cat": "Welfare",  "emoji": "🏥", "fee": 30,  "portal": "https://beneficiary.nha.gov.in"},
    {"key": "apy",        "name_en": "Atal Pension Yojana",    "name_hi": "अटल पेंशन योजना",          "cat": "Welfare",  "emoji": "👴", "fee": 30,  "portal": "https://www.npscra.nsdl.co.in"},
    {"key": "pmkisan",    "name_en": "PM-Kisan Registration",  "name_hi": "PM-किसान पंजीकरण",         "cat": "Welfare",  "emoji": "🌱", "fee": 50,  "portal": "https://pmkisan.gov.in"},
]


def by_category():
    cats = {}
    for s in BIHAR_SERVICES:
        cats.setdefault(s["cat"], []).append(s)
    # stable category order
    order = ["RTPS", "Bhumi", "Identity", "Vehicle", "Welfare", "Bills", "Exam", "Bank", "Shop"]
    return [(c, cats[c]) for c in order if c in cats]


def find(key: str):
    for s in BIHAR_SERVICES:
        if s["key"] == key:
            return s
    return None
