import string
import random
import copy
import re
from gliner import GLiNER
from faker import Faker
from ztfeatureslib.tools.pii_detection.utils.constants import (
    GLINER_MODEL,
    GLINER_MODEL_ENTITIES,
    GLINER_MODEL_THRESHOLD,
    GLINER_MODEL_MULTI_LABEL_DETECT,
)
from typing import List, Dict, Union, Any
from presidio_analyzer import AnalyzerEngine, RecognizerResult

from loguru import logger

fake = Faker()
analyzer = None
gliner_model = None
fake_br = Faker("pt_BR")

gliner_model = GLiNER.from_pretrained(GLINER_MODEL)
analyzer = AnalyzerEngine()

def extract_pii_array(text, pii_entities, top_n: int = None) -> List[Any]:
    """
    Extract pii element with two model (Microsoft presidio analyzer + Gliner model)
    @param text:  Input prompt.
    @return: pii array in list
    """
    # model 1: get result(detected pii entities) of presidio analyzer
    # presidio_results = get_presidio_result(text=text)

    # print("Presidio Results:",presidio_results)
    presidio_results= []
    # Model 2 get result(detected pii entities) from Gliner model
    gliner_model_results = get_gliner_mode_result(text=text, pii_entities=pii_entities, top_n=top_n)


    pii_array = combine_result_of_both_model(
        presidio_results=presidio_results, gliner_model_results=gliner_model_results
    )

    return pii_array

def extract_pii_elements(text, pii_entities: str, preserve_keywords: str = "", top_n: int = None) -> List[Any]:
    """
    Extract PII elements using two models (Microsoft Presidio Analyzer + Gliner model),
    while excluding preserved keywords.
    
    @param text: Input prompt
    @param pii_entities: Comma-separated string of PII entity types to detect
    @param preserve_keywords: Comma-separated string of keywords that should not be considered as PII.
    @return: PII array in list
    """
    preserve_keywords_list = [kw.strip().lower() for kw in preserve_keywords.split(",") if kw.strip()]
       
    # Convert comma-separated string to list and strip whitespace
    entities_to_detect = [entity.strip() for entity in pii_entities.split(',') if entity.strip()]
    
    # Create a case-preserving mapping of lowercase to original entities
    original_case_map = {entity.lower(): entity for entity in GLINER_MODEL_ENTITIES}
    
    # Validate and preserve original case from GLINER_MODEL_ENTITIES
    valid_entities = [
        original_case_map[entity.lower()]
        for entity in entities_to_detect 
        if entity.lower() in original_case_map
    ]
        
    if not valid_entities:
        logger.warning("No valid PII entities provided, using all supported entities")
        valid_entities = GLINER_MODEL_ENTITIES
    
    # Model 1: Get result (detected PII entities) from Presidio Analyzer
    presidio_results = get_presidio_result(text=text, presidio_entities=valid_entities)
    
    # Model 2: Get result (detected PII entities) from Gliner model
    gliner_model_results = get_gliner_mode_result(text=text, pii_entities=valid_entities, top_n=top_n)

    
    # Combine results from both models

    pii_array = combine_result_of_both_model(
        presidio_results=presidio_results, gliner_model_results=gliner_model_results
    )
    
    # Filter out preserved keywords from detected PII
    pii_array = [pii for pii in pii_array if pii[0].lower() not in preserve_keywords_list]
    
    # Ignore if just a person's name is present and no other PII
    if (
        len(pii_array) == 1
        and pii_array[0][1] == "<PERSON>"
    ):
        pii_array = []

    return pii_array

def get_presidio_analyzer():
    """
    Function to get the presidio analyzer engine instance
    @return:
    """
    global analyzer
    if not analyzer:
        analyzer = AnalyzerEngine()
    return analyzer


def get_gliner_model():
    """
    Function to get the gliner  model instance
    @return:
    """
    global gliner_model

    if not gliner_model:
        gliner_model = GLiNER.from_pretrained(GLINER_MODEL)
    return gliner_model


def get_presidio_result(text: str, presidio_entities: list = []) -> List[Dict]:
    """
    Function to analyze the given text for Personally Identifiable Information (PII) entities using
    Presidio analyzer.
    @param text: The text to be analyzed for PII entities.
    @param presidio_entities: Comma-separated string of PII entity types to detect
    @return: List[Dict]: A list of PII entities found in the text. Each entity is represented as a dictionary.
    """
    # Create a case-preserving mapping for Presidio entities
    entities_map = {
        "person": "PERSON",
        "phone number": "PHONE_NUMBER",
        "email": "EMAIL_ADDRESS",
        "email address": "EMAIL_ADDRESS"
    }

    # Process requested entities
    valid_entities = []
    if presidio_entities:
        requested_entities = [entity.strip().lower() for entity in presidio_entities if entity.strip()]
        valid_entities = [
            entities_map[entity]
            for entity in requested_entities
            if entity in entities_map
        ]

    # Call analyzer to get results - only pass entities if valid ones were found
    analyze_kwargs = {"text": text, "language": "en"}
    presidio_results = []
    
    if valid_entities:
        analyze_kwargs["entities"] = valid_entities
        presidio_results = analyzer.analyze(**analyze_kwargs)
        # Postprocessing Results
        presidio_results = add_substrings_in_presidio_result(
            results=presidio_results, 
            full_string=text
        )

    return presidio_results


def add_substrings_in_presidio_result(
    results: List[RecognizerResult], full_string: str
) -> List[Dict]:
    """
    Function to Enhance each result dictionary in a list with a substring extracted from a provided full string.
    @param results: Each dictionary contains 'start' and 'end' indices along with other data.:
    @param  full_string: The string from which substrings are extracted based on indices.
    @return:
    """
    processed_results: list = list()
    global analyzer
    analyzer = get_presidio_analyzer()

    # Loop through each result in the list
    for result in results:
        # Extract the substring using the 'start' and 'end' indices

        result = result.__dict__
        if "start" in result and "end" in result:
            # Python strings are 0-indexed, ensure end is inclusive
            substring = full_string[result["start"] : result["end"]]
            # Add the substring to the dictionary
            result["extracted_value"] = substring
            processed_results.append(copy.deepcopy(result))

    return processed_results




def get_gliner_mode_result(text: str, pii_entities: list, top_n: int = None) -> List[Dict]:
    """
    Function to analyze the given text for Personally Identifiable Information (PII) entities using gliner model.
    If top_n is provided, stops after top_n entities are found and returns only top_n.
    @param text: The text to be analyzed for PII entities.
    @param pii_entities: List of PII entity types to detect
    @param top_n: Maximum number of entities to return (optional)
    @return: List[Dict]: A list of PII entities found in the text. Each entity is represented as a dictionary.
    """
    gliner_model_results: list = list()
    chunk_size = 1800

    def process_chunk(text_chunk):
        entities = gliner_model.predict_entities(
            text_chunk,
            pii_entities,
            threshold=GLINER_MODEL_THRESHOLD,
            multi_label=GLINER_MODEL_MULTI_LABEL_DETECT,
        )
        return entities

    text_chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    for chunk in text_chunks:
        entities = process_chunk(chunk)
        if top_n is not None:
            remaining = top_n - len(gliner_model_results)
            if remaining <= 0:
                break
            if len(entities) >= remaining:
                gliner_model_results.extend(entities[:remaining])
                break
            else:
                gliner_model_results.extend(entities)
        else:
            gliner_model_results.extend(entities)
    return gliner_model_results if top_n is None else gliner_model_results[:top_n]


def combine_result_of_both_model(
    presidio_results: List[Dict], gliner_model_results: list[Dict]
):
    """
    Function take result of both model and input and combine both model results and return pii array
    we get gliner model_result and if ('PERSON', 'PHONE_NUMBER', 'EMAIL_ADDRESS', 'URL) not
    found in gliner result then take it from presidio results
    @param presidio_results:
    @param gliner_model_results:
    """
    label_mapping = {
        "email": "EMAIL_ADDRESS",
        "email address": "EMAIL_ADDRESS",
        "gmail": "EMAIL_ADDRESS",
        "person": "PERSON",
        "organization": "ORG",
        "phone number": "PHONE_NUMBER",
        "address": "LOCATION",
        "passport number": "US_PASSPORT",
        "credit card number": "CREDIT_CARD",
        "social security number": "US_SSN",
        "health insurance id number": "MEDICAL_LICENSE",
        "itin": "US_ITIN",
        "date time": "DATE_TIME",
        "US passport_number": "US_PASSPORT",
        "date": "DATE_TIME",
        "time": "DATE_TIME",
        "Crypto Currency number": "CRYPTO",
        "url": "URL",
        "date of birth": "DATE_TIME",
        "mobile phone number": "PHONE_NUMBER",
        "bank account number": "US_BANK_NUMBER",
        "medication": "MEDICATION",
        "cpf": "CPF",
        "driver's license number": "US_DRIVER_LICENSE",
        "tax identification number": "TAX_IDENTIFICATION_NUMBER",
        "medical condition": "MEDICAL_CONDITION",
        "identity card number": "IDENTITY_CARD_NUMBER",
        "national id number": "NATIONAL_ID_NUMBER",
        "ip address": "IP_ADDRESS",
        "iban": "IBAN_CODE",
        "credit card expiration date": "CREDIT_CARD_EXPIRATION_DATE",
        "username": "PERSON",
        "health insurance number": "HEALTH_INSURANCE_NUMBER",
        "registration number": "REGISTRATION_NUMBER",
        "student id number": "STUDENT_ID_NUMBER",
        "insurance number": "INSURANCE_NUMBER",
        "flight number": "FLIGHT_NUMBER",
        "landline phone number": "PHONE_NUMBER",
        "blood type": "BLOOD_TYPE",
        "cvv": "CVV",
        "reservation number": "RESERVATION_NUMBER",
        "digital signature": "DIGITAL_SIGNATURE",
        "social media handle": "SOCIAL_MEDIA_HANDLE",
        "license plate number": "LICENSE_PLATE_NUMBER",
        "cnpj": "CNPJ",
        "postal code": "POSTAL_CODE",
        "serial number": "SERIAL_NUMBER",
        "vehicle registration number": "VEHICLE_REGISTRATION_NUMBER",
        "credit card brand": "CREDIT_CARD",
        "fax number": "FAX_NUMBER",
        "visa number": "VISA_NUMBER",
        "insurance company": "INSURANCE_COMPANY",
        "identity document number": "IDENTITY_DOCUMENT_NUMBER",
        "transaction number": "TRANSACTION_NUMBER",
        "national health insurance number": "NATIONAL_HEALTH_INSURANCE_NUMBER",
        "cvc": "CVC",
        "birth certificate number": "BIRTH_CERTIFICATE_NUMBER",
        "train ticket number": "TRAIN_TICKET_NUMBER",
        "passport expiration date": "PASSPORT_EXPIRATION_DATE",
        "social_security_number": "US_SSN",
        "medical license": "MEDICAL_LICENSE",
    }
    pii_array: list = list()
    # Initialize a set to store found labels with gliner model
    found_labels: set = set()

    # Iterate through gliner_model_results
    for item in gliner_model_results:
        label = label_mapping.get(item["label"])
        pii_array.append([item["text"], f"<{label}>"])

        # Add the label to found_labels
        found_labels.add(label)

    # Check for missing labels(we only take 'PERSON', 'PHONE_NUMBER', 'EMAIL_ADDRESS', 'URL'
    # from presidio result if those enetities is not found with gliner model)
    missing_labels = {"PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS"} - found_labels
    
    # Iterate through presidio_results to add missing labels
    for pres_item in presidio_results:
        if pres_item["entity_type"] in missing_labels:
            # Append the entity to pii_array
            pii_array.append(
                [pres_item["extracted_value"], f'<{pres_item["entity_type"]}>']
            )

    return pii_array 


def get_fict_pii(pii_type: str) -> str:
    """
    Generate fictitious PII data based on the given PII type.
    @param pii_type:The type of PII entity to generate fictitious data for.
    @return: The generated fictitious PII data.
    """
    # Generate fake data for each entity
    pii_generators = {
        "EMAIL_ADDRESS": fake.email(),
        "PERSON": fake.name(),
        "ORG": fake.company(),
        "PHONE_NUMBER": fake.phone_number(),
        "LOCATION": re.sub(r"\n", " ", fake.address()),
        "US_PASSPORT": fake.passport_number(),
        "CREDIT_CARD": fake.credit_card_number(),
        "US_SSN": fake.ssn(),
        "MEDICAL_LICENSE": fake.license_plate(),
        "US_ITIN": fake.itin(),
        "DATE_TIME": fake.date_time().strftime("%b-%d-%Y"),
        "CRYPTO": str(random.randint(0, 10)),
        "URL": fake.image_url(),
        "US_BANK_NUMBER": fake.iban(),
        "MEDICATION": fake.word(),
        "CPF": fake_br.cpf(),
        "US_DRIVER_LICENSE": fake_us_driver_license(),
        "TAX_IDENTIFICATION_NUMBER": fake.itin(),
        "MEDICAL_CONDITION": fake.word(),
        "IDENTITY_CARD_NUMBER": fake.ssn(),
        "NATIONAL_ID_NUMBER": fake.ssn(),
        "IP_ADDRESS": fake.ipv4(),
        "IBAN_CODE": fake.iban(),
        "CREDIT_CARD_EXPIRATION_DATE": fake.credit_card_expire(),
        "HEALTH_INSURANCE_NUMBER": fake.ssn(),
        "REGISTRATION_NUMBER": fake.ean(length=13),
        "STUDENT_ID_NUMBER": fake.ean(length=8),
        "INSURANCE_NUMBER": fake.ssn(),
        "FLIGHT_NUMBER": fake.ean(length=13),
        "BLOOD_TYPE": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
        "CVV": str(random.randint(101, 9999)),
        "RESERVATION_NUMBER": fake.ean(length=13),
        "DIGITAL_SIGNATURE": fake.sha256(),
        "SOCIAL_MEDIA_HANDLE": fake.user_name(),
        "LICENSE_PLATE_NUMBER": fake.license_plate(),
        "CNPJ": fake.ean(length=8),
        "POSTAL_CODE": fake.postcode(),
        "SERIAL_NUMBER": fake.ssn(),
        "VEHICLE_REGISTRATION_NUMBER": fake.license_plate(),
        "FAX_NUMBER": fake.phone_number(),
        "VISA_NUMBER": fake.credit_card_number(card_type="visa"),
        "INSURANCE_COMPANY": fake.company(),
        "IDENTITY_DOCUMENT_NUMBER": fake.ssn(),
        "TRANSACTION_NUMBER": str(random.randint(101, 9999)),
        "NATIONAL_HEALTH_INSURANCE_NUMBER": str(random.randint(101, 9999)),
        "BIRTH_CERTIFICATE_NUMBER": fake.ssn(),
        "TRAIN_TICKET_NUMBER": fake.ean(length=13),
        "PASSPORT_EXPIRATION_DATE": fake.date_this_century().strftime("%b-%d-%Y"),
    }

    fake_data = pii_generators.get(pii_type)
    if not fake_data:
        fake_data = 'XXXXXXXXX'
    return fake_data


def fake_us_driver_license() -> str:
    """
    Generate a fictitious US driver's license number.
    @return: The generated US driver's license number.
    """
    letter_part = random.choice(string.ascii_uppercase)
    digit_part = "".join(random.choices(string.digits, k=8))
    return f"{letter_part}{digit_part}"


def create_pii_array_with_custom_keywords(words: str, prompt : str, pii_entities: str):
    """
    Analyze a comma-separated string of words to detect PII entities using spaCy's NLP model.

    @param words:  A comma-separated string of words to be analyzed.
    @return: A list of lists, where each inner list contains a word and its detected PII type.
    """
    completed_pii_array: list = list()

    extract_phrase = lambda  phrase, text: (
        next(
            (text[start:end] for start in range(len(text))
            for end in range(start + len(phrase), len(text) + 1)
            if ' '.join(text[start:end].split()).lower() == ' '.join(phrase.split()).lower()),
            None
        )
    )  

    words_list = words.split(",")
    if words_list is None or len(words_list) <= 0:
        return completed_pii_array

    pii_array = []

    # Convert comma-separated string to list and strip whitespace
    entities_to_detect = [entity.strip() for entity in pii_entities.split(',') if entity.strip()]
    
    # Create a case-preserving mapping of lowercase to original entities
    original_case_map = {entity.lower(): entity for entity in GLINER_MODEL_ENTITIES}
    
    # Validate and preserve original case from GLINER_MODEL_ENTITIES
    valid_entities = [
        original_case_map[entity.lower()]
        for entity in entities_to_detect 
        if entity.lower() in original_case_map
    ]
        
    if not valid_entities:
        logger.warning("No valid PII entities provided, using all supported entities")
        valid_entities = GLINER_MODEL_ENTITIES

    # Use a list comprehension to directly create the pii_array
    pii_array = [
        extract_pii_array(word.strip(), pii_entities=valid_entities)[0] if extract_pii_array(word.strip(), pii_entities=valid_entities) 
        else [extract_phrase(word.strip(), prompt).strip(), '<ORG>']
        for word in words_list
        if len(word.strip()) > 2 and (extract_pii_array(word.strip(), pii_entities=valid_entities) or extract_phrase(word.strip(), prompt))
    ]

    return pii_array

def get_fict_pii(pii_type: str) -> str:
    """
    Generate fictitious PII data based on the given PII type.
    @param pii_type:The type of PII entity to generate fictitious data for.
    @return: The generated fictitious PII data.
    """
    # Generate fake data for each entity
    pii_generators = {
        "EMAIL_ADDRESS": fake.email(),
        "PERSON": fake.name(),
        "ORG": fake.company(),
        "PHONE_NUMBER": fake.phone_number(),
        "LOCATION": re.sub(r"\n", " ", fake.address()),
        "US_PASSPORT": fake.passport_number(),
        "CREDIT_CARD": fake.credit_card_number(),
        "US_SSN": fake.ssn(),
        "MEDICAL_LICENSE": fake.license_plate(),
        "US_ITIN": fake.itin(),
        "DATE_TIME": fake.date_time().strftime("%b-%d-%Y"),
        "CRYPTO": str(random.randint(0, 10)),
        "URL": fake.image_url(),
        "US_BANK_NUMBER": fake.iban(),
        "MEDICATION": fake.word(),
        "CPF": fake_br.cpf(),
        "US_DRIVER_LICENSE": fake_us_driver_license(),
        "TAX_IDENTIFICATION_NUMBER": fake.itin(),
        "MEDICAL_CONDITION": fake.word(),
        "IDENTITY_CARD_NUMBER": fake.ssn(),
        "NATIONAL_ID_NUMBER": fake.ssn(),
        "IP_ADDRESS": fake.ipv4(),
        "IBAN_CODE": fake.iban(),
        "CREDIT_CARD_EXPIRATION_DATE": fake.credit_card_expire(),
        "HEALTH_INSURANCE_NUMBER": fake.ssn(),
        "REGISTRATION_NUMBER": fake.ean(length=13),
        "STUDENT_ID_NUMBER": fake.ean(length=8),
        "INSURANCE_NUMBER": fake.ssn(),
        "FLIGHT_NUMBER": fake.ean(length=13),
        "BLOOD_TYPE": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
        "CVV": str(random.randint(101, 9999)),
        "RESERVATION_NUMBER": fake.ean(length=13),
        "DIGITAL_SIGNATURE": fake.sha256(),
        "SOCIAL_MEDIA_HANDLE": fake.user_name(),
        "LICENSE_PLATE_NUMBER": fake.license_plate(),
        "CNPJ": fake.ean(length=8),
        "POSTAL_CODE": fake.postcode(),
        "SERIAL_NUMBER": fake.ssn(),
        "VEHICLE_REGISTRATION_NUMBER": fake.license_plate(),
        "FAX_NUMBER": fake.phone_number(),
        "VISA_NUMBER": fake.credit_card_number(card_type="visa"),
        "INSURANCE_COMPANY": fake.company(),
        "IDENTITY_DOCUMENT_NUMBER": fake.ssn(),
        "TRANSACTION_NUMBER": str(random.randint(101, 9999)),
        "NATIONAL_HEALTH_INSURANCE_NUMBER": str(random.randint(101, 9999)),
        "BIRTH_CERTIFICATE_NUMBER": fake.ssn(),
        "TRAIN_TICKET_NUMBER": fake.ean(length=13),
        "PASSPORT_EXPIRATION_DATE": fake.date_this_century().strftime("%b-%d-%Y"),
    }

    fake_data = pii_generators.get(pii_type)
    if not fake_data:
        fake_data = 'XXXXXXXXX'
    return fake_data