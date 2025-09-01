GET_ANONYMIZED_PROMPTS_WITH_MODELS = "/get-anonymized-prompts-with-models"
GET_DETECTED_PIIS = "/get-detected-piis"

PDF_DOCX_FILE = ["pdf", "docx"]
XML_FILE = "xml"
CSV_FILE = "csv"
TXT_FILE = ["txt"]

ANONYMIZED_FILE_PATH = "app/files"


GLINER_MODEL = "urchade/gliner_multi_pii-v1"
GLINER_MODEL_THRESHOLD = 0.20
GLINER_MODEL_MULTI_LABEL_DETECT = False
GLINER_MODEL_ENTITIES = ["email",
                         "email address",
                         "gmail",
                         "person",
                         "organization",
                         "phone number",
                         "address",
                         "passport number",
                         "credit card number",
                         "social security number",
                         "health insurance id number",
                         "itin",
                         "date time",
                         "US passport_number",
                         "date",
                         "time",
                         "Crypto Currency number",
                         "url",
                         "date of birth",
                         "mobile phone number",
                         "bank account number",
                         "medication",
                         "cpf",
                         "driver's license number",
                         "tax identification number",
                         "medical condition",
                         "identity card number",
                         "national id number",
                         "ip address",
                         "iban",
                         "credit card expiration date",
                         "username",
                         "health insurance number",
                         "registration number",
                         "student id number",
                         "insurance number",
                         "flight number",
                         "landline phone number",
                         "blood type",
                         "cvv",
                         "reservation number",
                         "digital signature",
                         "social media handle",
                         "license plate number",
                         "cnpj",
                         "postal code",
                         "serial number",
                         "vehicle registration number",
                         "credit card brand",
                         "fax number",
                         "visa number",
                         "insurance company",
                         "identity document number",
                         "transaction number",
                         "national health insurance number",
                         "cvc", "birth certificate number",
                         "train ticket number",
                         "passport expiration date",
                         "social_security_number",
                         "medical license"]