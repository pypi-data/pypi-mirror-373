"""Default PII labels configuration for GLiNER model."""

DEFAULT_LABELS = [
    "work",
    "booking number", 
    "personally identifiable information",
    "driver licence",
    "person",
    "book",
    "full address",
    "company",
    "actor",
    "character",
    "email",
    "passport number",
    "Social Security Number",
    "phone number",

    # India-specific IDs (citizen & finance)
    "Aadhaar number",
    "Aadhaar Enrolment ID",
    "Aadhaar Virtual ID",
    "PAN number",
    "Voter ID number",
    "EPIC number",
    "Bank account number",
    "IFSC code",
    "MICR code",
    "SWIFT/BIC code",
    "UPI ID",
    "Credit card number",
    "Debit card number",
    "Cheque number",
    "Demand draft number",

    # Corporate & tax registrations
    "CIN number",
    "LLPIN",
    "GSTIN",
    "TAN number",
    "TIN number",
    "IEC number",
    "Udyam registration number",
    "DIN",

    # Court & police ecosystem
    "Case number",
    "CNR number",
    "Diary number",
    "Filing number",
    "Court order number",
    "Writ petition number",
    "Criminal appeal number",
    "FIR number",
    "Crime number",
    "GD/DD entry number",
    "Charge sheet number",
    "Arrest memo number",
    "Seizure memo number",
    "MLC number",

    # Vehicle & transport
    "Vehicle registration number",
    "RC number",
    "Chassis number",
    "Engine number",
    "e-challan number",
    "PUC certificate number",
    "driving licence number",

    # Social welfare & health
    "Ration card number",
    "ABHA number",
    "PMJAY URN",
    "Medical record number",
    "Insurance policy number",
    "UDID number",

    # Employment & pensions
    "Employee ID",
    "UAN",
    "ESIC IP number",
    "PRAN",
    "PPO number",

    # Property & land records
    "Property registration number",
    "Survey number",
    "Khasra number",
    "Khata number",
    "Khatauni number",
    "CTS number",
    "Gata number",
    "Patta number",
    "Mutation number",
    "ROR number",
    "Encumbrance certificate number",
    "Building plan approval number",
    "Property tax assessment number",

    # Education identifiers
    "Student roll number",
    "Enrollment number",
    "School admission number",

    # Professional licences
    "Bar Council enrolment number",
    "Medical registration number",
    "CA membership number",
    "FSSAI license number",
    "Drug license number",
    "Trade license number",

    # Immigration & travel
    "Passport file number",
    "Visa number",
    "OCI card number",
    "FRRO registration number",

    # Utilities & subscriber accounts
    "Electricity consumer number",
    "Water connection number",
    "LPG consumer number",
    "LPG ID",

    # Cyber/telecom/device identifiers
    "IP address",
    "MAC address",
    "IMEI number",
    "IMSI number",
    "ICCID number",
    "Device serial number",

    # Civil status & certificates
    "Caste certificate number",
    "Income certificate number",
    "Domicile certificate number",
    "EWS certificate number",
    "Marriage certificate number",
    "Birth certificate number",
    "Death certificate number",

    # Relational/person details often present in Indian filings
    "father's name",
    "mother's name",
    "spouse name",
    "guardian name",
    "minor's name",
    "date of birth",
    "place of birth",
    "age",

    # Sensitive biometrics/media
    "photograph",
    "signature",
    "biometric data",
    "fingerprint data",
    "iris scan data",
    "DNA profile"
]
