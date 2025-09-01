from secretstuff import SecretStuffPipeline

pipeline = SecretStuffPipeline()

# Process complete files
# redact_result = pipeline.process_text_file(
#     input_file="outs/test.txt",
#     output_redacted="outs/redacted.txt",
#     output_identified="outs/entities.json",
#     output_mapping="outs/mapping.json"
# )
# print(redact_result)
# # Reverse from files
# reverse_result = pipeline.reverse_from_files("outs/updated_afterCloudcall.txt", "outs/mapping.json", "outs/final.txt")
# print(reverse_result)

text = """
SERVICE AGREEMENT

This Service Agreement (“Agreement”) is entered into on this 15th day of June, 2023 at New Delhi, India, by and between:

Mr. Rajesh Kumar, S/o Mr. Mohan Kumar, residing at H-25, Lajpat Nagar-II, New Delhi - 110024, holder of Aadhaar No. 4578 1234 9087, PAN No. ABCPK2345L, and Mobile No. +91-9876543210, hereinafter referred to as the “Client”;

AND

TechNova Solutions Pvt. Ltd., a company incorporated under the Companies Act, 2013, having its registered office at Plot No. 112, Sector-62, Noida, Uttar Pradesh - 201301, CIN: U74999DL2018PTC123456, represented by its Director Ms. Anjali Sharma, holder of Passport No. N1234567, Email: anjali.sharma@technova.com
, hereinafter referred to as the “Service Provider”.

WHEREAS the Client desires to avail IT development and support services from the Service Provider, and the Service Provider agrees to provide such services subject to the terms and conditions set forth herein.

NOW, THEREFORE, the parties hereto agree as follows:

Scope of Services – The Service Provider shall design, develop, and deliver a mobile application for the Client in accordance with specifications provided in Annexure A.

Term – This Agreement shall remain valid for a period of 12 months commencing from 01 July 2023.

Confidentiality – Both parties agree to maintain strict confidentiality of all data shared under this Agreement, including but not limited to personal data, client lists, and financial information.

Termination – Either party may terminate this Agreement by giving 30 days’ written notice.

IN WITNESS WHEREOF, the parties have executed this Agreement on the day and year first written above.
"""

# Step 1: Just identify PII
entities = pipeline.identify_pii(text)
print(entities)

# Step 2: Redact when ready
redacted_text = pipeline.redact_pii(text)
print(redacted_text)


processed_text= """
SERVICE AGREEMENT

This Service Agreement (“Agreement”) is entered into on this 15th day of June, 2023, at New Delhi, India, by and between:

[NAME REDACTED3], S/o [NAME REDACTED5], residing at [ADDRESS REDACTED], holder of Aadhaar No. 0000 1111 2222, PAN No. ABCDE1234G, and Mobile No. +91-9000000000, hereinafter referred to as the “[NAME REDACTED2]” (which expression shall, unless repugnant to the context or meaning thereof, be deemed to include his heirs, successors, legal representatives, and permitted assigns);

AND

[COMPANY NAME REDACTED1][COMPANY NAME REDACTED5], a company incorporated under the Companies Act, 2013, having its registered office at Plot No. 112, Sector-62, Noida, Uttar Pradesh - 201301, CIN: U12345DL2000PLC000000, represented by its Director [NAME REDACTED1], holder of Passport No. A0000000, Email: example@mail.com
, hereinafter referred to as the “[COMPANY NAME REDACTED3]” (which expression shall, unless repugnant to the context or meaning thereof, be deemed to include its successors and permitted assigns).

RECITALS

WHEREAS, the [NAME REDACTED2] desires to avail IT development and support services from the [COMPANY NAME REDACTED3];

AND WHEREAS, the [COMPANY NAME REDACTED3] has agreed to provide such services, subject to the terms and conditions set forth herein;

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties hereto agree as follows:

1. Scope of Services

The [COMPANY NAME REDACTED3] shall design, develop, and deliver a mobile application for the [NAME REDACTED2] in accordance with the specifications provided in Annexure A.

2. Term

This Agreement shall remain valid for a period of twelve (12) months, commencing from 01 July 2023, unless terminated earlier in accordance with Clause 5.

3. Consideration

The fees, payment schedule, and related commercial terms shall be mutually agreed upon and documented in Annexure B.

4. Confidentiality

Both parties agree to maintain strict confidentiality of all information, documents, and data exchanged under this Agreement, including but not limited to sensitive personal data, business information, and financial records. No such information shall be disclosed to any third party without prior written consent, except as required by applicable law.

5. Termination

Either party may terminate this Agreement by giving thirty (30) days’ prior written notice to the other party. Upon termination, all outstanding dues for services rendered up to the effective date of termination shall become immediately payable.

6. Governing Law & Jurisdiction

This Agreement shall be governed by and construed in accordance with the laws of India. The courts at New Delhi shall have exclusive jurisdiction over any disputes arising from or relating to this Agreement.

7. Entire Agreement

This Agreement, together with its annexures, constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior discussions, negotiations, or understandings, whether oral or written.

IN WITNESS WHEREOF, the parties have executed this Agreement on the day and year first written above.

For [NAME REDACTED2]
(Signature)
Name: [NAME REDACTED3]

For [COMPANY NAME REDACTED3]
(Signature)
Name: [NAME REDACTED1]
Designation: Director
"""
# Step 3: Reverse after processing
restored_text, _, _ = pipeline.reverse_redaction(processed_text)
print(restored_text)