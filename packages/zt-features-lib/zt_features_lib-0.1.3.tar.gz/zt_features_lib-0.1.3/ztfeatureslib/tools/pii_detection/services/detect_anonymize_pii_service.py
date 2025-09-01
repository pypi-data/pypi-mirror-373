
import traceback
from typing import Dict, List
from ztfeatureslib.tools.pii_detection.schema.detect_anonymize_pii import AnonymizedPromptResponse
from ztfeatureslib.tools.pii_detection.services.detect_pii_gliner import create_pii_array_with_custom_keywords, extract_pii_elements, get_fict_pii
from ztfeatureslib.tools.pii_detection.utils.constants import ANONYMIZED_FILE_PATH, CSV_FILE, PDF_DOCX_FILE, TXT_FILE
from loguru import logger
# from fastapi import UploadFile
# import fitz
import pandas as pd
import re
from datetime import datetime
import os
import aiofiles

async def get_pii_from_user_prompt_gliner(
    prompt: str, anonymize_keywords: str, pii_entities: str, preserve_keywords: str = "", top_n: int = None
) -> dict:
    """
    Processes the input prompt, anonymizes the content, and extracts PII data.

    :param anonymize_keywords: Keywords to anonymize in the prompt.
    :param prompt: The input text to process (if provided).
    :param llm_model: The language model used to anonymize the data.
    :return: tuple

    """
    try:
        logger.info("Starting anonymization process for the prompt.")

        # Anonymize the pii using the LLM
        # anonymize_pii_llm_result = await anonymize_pii_with_llm(
        #     prompt, pii_entities, llm_model
        # )
        detected_pii_in_prompt = extract_pii_elements(prompt, pii_entities, preserve_keywords=preserve_keywords, top_n=top_n)

        # anonymize_custom_keyword_llm_result = await anonymize_custom_keyword_with_llm(
        #     prompt, anonymize_keywords, llm_model
        # )

        detected_custom_pii_prompt = await anonymize_custom_keyword_with_gliner(
                prompt, 
                anonymize_keywords,
                pii_entities=pii_entities,
                preserve_keywords=preserve_keywords,
                )
        
        logger.info(
            "Anonymization completed successfully for custom keyword and pii in prompt."
        )

        result_pii = process_pii(detected_pii_in_prompt + detected_custom_pii_prompt)
        # Process the PII data from the anonymized prompt
        pii_result_of_prompt = process_pii_data_and_generate_anonymized_prompt(
            # prompt, anonymize_pii_llm_result + anonymize_custom_keyword_llm_result
            prompt, 
            result_pii
            #detected_pii_in_prompt + detected_custom_pii_prompt
        )

        return pii_result_of_prompt

    except Exception as e:
        logger.error(
            f"An unexpected error occurred during anonymization of prompt: {e}"
        )
        raise

async def detect_pii_from_user_prompt_gliner(
    prompt: str, anonymize_keywords: str, pii_entities: str, preserve_keywords: str = "", top_n: int = None
) -> list:
    """
    Processes the input prompt, anonymizes the content, and extracts PII data.

    :param anonymize_keywords: Keywords to anonymize in the prompt.
    :param prompt: The input text to process (if provided).
    :param llm_model: The language model used to anonymize the data.
    :return: tuple

    """
    try:
        logger.info("Starting anonymization process for the prompt.")

        detected_pii_in_prompt = extract_pii_elements(prompt, pii_entities, preserve_keywords=preserve_keywords, top_n=top_n)

        detected_custom_pii_prompt = await anonymize_custom_keyword_with_gliner(
                prompt, 
                anonymize_keywords,
                pii_entities=pii_entities,
                preserve_keywords=preserve_keywords,
                )
        
        logger.info(
            "Anonymization completed successfully for custom keyword and pii in prompt."
        )

        return detected_pii_in_prompt + detected_custom_pii_prompt

    except Exception as e:
        logger.error(
            f"An unexpected error occurred during detection of prompt: {e}"
        )
        raise

def process_pii(pii_list):
    result = []
    for item in pii_list:
        if len(item) < 2:
            continue  # Skip malformed entries
        original = item[0]
        pii_type = item[1].strip('<>').upper()  # Remove angle brackets and standardize
        anonymized = get_fict_pii(pii_type)
        
        result.append({
            "Anonymized": anonymized,
            "Original": original,
            "PII_Type": pii_type
        })
    return result


def check_keywords_in_prompt_case_insensitive(
    prompt: str, comma_separated_keywords: str, preserve_keywords: str = ""
) -> list:
    """
    Checks for the presence of keywords in a prompt in a case-insensitive manner.

    :param prompt: The text prompt to search for keywords.
    :param comma_separated_keywords: A string of comma-separated keywords to check against the prompt.
    :return: A list of keywords that were found in the prompt.
    """
    try:
        # Split the comma-separated string into a list of keywords
        keywords = (
            [word.strip().lower() for word in comma_separated_keywords.split(",")]
            if comma_separated_keywords
            else []
        )
        preserve_keywords_list = (
            [word.strip().lower() for word in preserve_keywords.split(",")]
            if preserve_keywords
            else []
        )
        
        # Convert the prompt to lowercase for case-insensitive matching
        prompt_lower = prompt.lower()

        # Check for presence of each keyword in the prompt
        custom_keyword_found_in_prompt = [
            word for word in keywords if word in prompt_lower and word not in preserve_keywords_list
        ]

        logger.info(
            f"Custom keywords found : {custom_keyword_found_in_prompt} in the prompt, excluding preserved keywords: {preserve_keywords_list}."
        )

        return custom_keyword_found_in_prompt

    except Exception as e:
        logger.error(f"Error checking keywords in prompt: {e}")
        return []

async def anonymize_custom_keyword_with_gliner(
    prompt: str, anonymize_keywords: str, pii_entities, preserve_keywords: str = ""
) -> list:
    """
    Anonymizes the input custom keyword by checking for PII entities and keywords using the specified language model.
    :param anonymize_keywords:
    :param llm_model: The language model used for anonymization.
    :param prompt: The input text prompt to be anonymized.
    :return: A dictionary containing the anonymized prompt and associated PII data.

    """
    try:
        custom_keyword_anonymize_result: list = list()
        anonymize_keywords_in_prompt = check_keywords_in_prompt_case_insensitive(
            prompt, anonymize_keywords, preserve_keywords=preserve_keywords
        )

        result_pii = {}
        if anonymize_keywords_in_prompt:
            # Get the PII detection and anonymization prompt template
            # formatted_anon_prompt = get_anonymize_custom_keyword_prompt_template()
            custom_keyword_anonymize_result = create_pii_array_with_custom_keywords(anonymize_keywords, prompt, pii_entities=pii_entities)

            # invoke_params = {"customized_keywords": anonymize_keywords_in_prompt}

            # # Use the common function to execute the LLM chain
            # logger.info(
            #     f"Sending prompt to LLM model for get anonymize custom keyword ...{invoke_params}"
            # )
            # custom_keyword_anonymize_llm_result = await execute_llm_chain(
            #     prompt=formatted_anon_prompt,
            #     llm_model=llm_model,
            #     invoke_params=invoke_params,
            # )

            # custom_keyword_anonymize_result = json.loads(
            #     custom_keyword_anonymize_llm_result.content
            # ).get("custom_data", [])

            # result_pii = convert_list_to_dict(custom_keyword_anonymize_result)
            logger.info("Got pii for custom keywords")
            logger.info(
                f"Anonymized custom keyword result: {custom_keyword_anonymize_result}"
            )

        return custom_keyword_anonymize_result
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during anonymization of custom_keyword: {e}"
        )
        logger.error(traceback.format_exc())
        raise

async def get_anonymize_prompt_gliner(form_data) -> AnonymizedPromptResponse:
    """
    Processes the form data to anonymize sensitive information (PII) from both the uploaded file and the user prompt
    using the specified LLM (Large Language Model) and handles safeguard keywords.

    :param form_data:
    form_data: Form data containing:
        - prompt: The user input that may contain PII.
        - pii_entities: The types of PII to extract and anonymize (e.g., names, phone numbers, etc.).
        - anonymize_keywords: Keywords that should be anonymized in the content.
        - keyword_safeguard: List of safeguard keywords that should trigger an error if detected.
        - uploaded_file: File that may contain PII to be anonymized.
        - llm: The name of the language model to use.
        - client_api_key: API key to access the LLM model.

    :return:
    AnonymizedPromptResponse: The result of the anonymization process, containing:
        - Anonymized prompt.
        - Highlighted original and anonymized prompts.
        - List of detected PII entities in the prompt and file.
        - File location of the anonymized content (if a file was uploaded).
    """
    # Initialize dictionary to store PII detection results from the uploaded file
    pii_result_of_file: dict = dict()

    # Variable to store file location of the anonymized content
    file_location: str = str()

    try:
        # Extract values from form data
        prompt = form_data.prompt
        pii_entities = form_data.pii_entities
        anonymize_keywords = form_data.anonymize_keywords
        deanonymize_keywords = form_data.deanonymize_keywords
        keyword_safeguard = form_data.keyword_safeguard
        # uploaded_file = form_data.uploaded_file
        # llm_name = form_data.llm
        # client_api_key = form_data.client_api_key

        logger.info("Received anonymization request for prompt and file.")

        # Get the LLM model by its name and API key
        # llm_model = get_llm_model_by_name_and_key(client_api_key, llm_name)
        # logger.info(f"Using LLM model: {llm_name}")

        # If a file is uploaded, process it
        # if uploaded_file:
        #     # TODO: Move this code into separate function (handle file anonymization)
        #     logger.info("Processing uploaded file for PII detection and anonymization.")

        #     # Extract text content from the uploaded file
        #     extracted_text = extract_text_from_file(uploaded_file)

        #     # Check for safeguard keywords in the prompt
        #     file_safeguard_result = check_safeguard_keyword(
        #         extracted_text, keyword_safeguard
        #     )

        #     # If safeguard keywords are found, return an error response
        #     if file_safeguard_result:
        #         logger.warning(
        #             f"Safeguard keyword detected in uploaded file: {file_safeguard_result}"
        #         )
        #         return AnonymizedPromptResponse(
        #             safe_guard_error_message=f"Safeguard keyword detected in the content of "
        #             f"uploaded file: {file_safeguard_result}"
        #         )

        #     logger.info("Anonymizing file content using model.")
        #     # Get PII from the file content and anonymize it using the LLM model
        #     pii_result_of_file = await get_pii_from_file_content_gliner(
        #         extracted_text, anonymize_keywords, pii_entities, preserve_keywords=deanonymize_keywords
        #     )

        #     logger.info("Saving file content.")
        #     file_location = await save_anonymized_file(
        #         pii_result_of_file["anonymized_prompt"]
        #     )
        #     logger.info(f"Anonymized file saved at location: {file_location}")

        # TODO: Move this code into separate function(handle prompt anonymization)
        logger.info("Checking safeguard keywords in the user prompt.")
        text_safeguard_result = check_safeguard_keyword(prompt, keyword_safeguard)

        if text_safeguard_result:
            logger.warning(
                f"Safeguard keyword detected in prompt: {text_safeguard_result}"
            )
            return AnonymizedPromptResponse(
                safe_guard_error_message=f"Your organization’s AI policy prevents the use of the following keywords: {text_safeguard_result}. Contact your administrator if you have any questions."
            )

        logger.info("Anonymizing prompt with LLM.")
        # Get PII from the prompt and anonymize
        pii_result_of_prompt = await get_pii_from_user_prompt_gliner(
            prompt, anonymize_keywords, pii_entities, preserve_keywords=deanonymize_keywords
        )
        logger.info("Anonymization process for the prompt completed successfully.")

        # Return the final anonymized prompt response with highlighted and anonymized content
        return AnonymizedPromptResponse(
            anonymized_prompt=pii_result_of_prompt["anonymized_prompt"],
            highlighted_original_prompt=pii_result_of_prompt[
                "highlighted_original_prompt"
            ],
            highlighted_anonymized_prompt=pii_result_of_prompt[
                "highlighted_anonymized_prompt"
            ],
            pii_list=pii_result_of_prompt["pii_list"],
            pii_entities=pii_result_of_prompt["pii_entities"],
            file_pii_array=pii_result_of_file["pii_list"] if pii_result_of_file else [],
            file_location=file_location if file_location else "",
        )

    except Exception as e:
        logger.error(f"An error occurred during the anonymization process: {str(e)}")
        traceback.print_exc()
        raise e
    

async def save_anonymized_file(anonymized_content: str) -> str:
    """
    Saves anonymized content to a specified directory, generating a unique file name with a timestamp.
    :param anonymized_content: The content to be saved in the file.
    :return: The full file path where the anonymized content is saved.
    """
    try:
        # Generate a unique file name with a timestamp
        cur_timestamp = datetime.now()
        file_name = f"file_{cur_timestamp.strftime('%y%m%d%H%M%S')}.txt"
        file_location = os.path.join(ANONYMIZED_FILE_PATH, file_name)

        logger.info(f"Saving anonymized content to {file_location}")

        parent_directory = os.path.dirname(file_location)
        if parent_directory and not os.path.exists(parent_directory):
            os.makedirs(parent_directory, exist_ok=True)  # Create the directory if it doesn't exist

        # Write the anonymized content to the file asynchronously
        async with aiofiles.open(file_location, "wb") as file_object:
            await file_object.write(anonymized_content.encode(encoding="utf-8"))

        logger.info(f"Anonymized content successfully saved at {file_location}")

        return file_location

    except Exception as e:
        logger.error(
            f"Failed to save anonymized content to {ANONYMIZED_FILE_PATH}. Error: {str(e)}"
        )
        raise e
    
async def get_pii_from_file_content_gliner(
    file_content: str, anonymize_keywords: str, pii_entities, preserve_keywords: str = "", top_n: int = None
) -> dict:
    """
    Processes the input prompt or file, anonymizes the content, and checks for safeguard keywords.
    :param:
        file_content (str): The input text extracted from the file to be processed.
        pii_entities (str): A string representing the list of PII entities to identify (e.g., 'First Name', 'SSN').
        anonymize_keywords (str): Keywords that should be anonymized in the content of the file.
        llm_model: The language model used for PII detection and anonymization.

    :return: A tuple containing:
            - pii_result_of_prompt (List[List[str]]): A list of detected PII entities and their types.
            - anonymized_file_content (str): The content of the file after PII anonymization.

    """
    try:

        if not file_content:
            raise ValueError(
                "The provided file content is empty.Please provide a valid file content."
            )

        # Anonymize the prompt using the models
        anonymize_prompt_result = await anonymize_file_content_with_gliner(
            file_content, pii_entities, top_n=top_n
        )

        anonymize_custom_keyword_result = await anonymize_custom_keyword_with_gliner(
            file_content, anonymize_keywords, pii_entities=pii_entities, preserve_keywords=preserve_keywords
        )
        logger.info(
            "Anonymization completed successfully for custom keyword and pii in prompt."
        )

        logger.info(f"Getting pii from file content : {anonymize_prompt_result}, {anonymize_custom_keyword_result}")
        logger.info(f"Types of  pii from file content : {type(anonymize_prompt_result)}, {type(anonymize_custom_keyword_result)}")
        result_pii = process_pii(anonymize_prompt_result + anonymize_custom_keyword_result)
        # Process the PII data from the anonymized prompt
        pii_result_of_file = process_pii_data_and_generate_anonymized_prompt(
            file_content,
            result_pii,
            # anonymize_prompt_result + anonymize_custom_keyword_result,
        )

        return pii_result_of_file

    except ValueError as ve:
        logger.error(f"ValueError during PII extraction from file: {ve}")
        raise

    except Exception as e:
        logger.error(f"An error occurred during PII processing for file content: {e}")
        traceback.print_exc()
        raise e

def process_pii_data_and_generate_anonymized_prompt(
    prompt: str, pii_data: list
) -> Dict[str, List[List[str]]]:
    """
    Process a list of PII data to group anonymized and original values by PII type,
    and to create a list of PII entities with their types, and also generate anonymized prompts.

    :param prompt: The original prompt that contains PII data.
    :param pii_data:  A list of dictionaries containing PII details.
                                       Each dictionary should have keys 'PII_Type', 'Anonymized', and 'Original'.
    :return: A dictionary containing:
             - 'pii_list': List of lists with grouped unique anonymized and original PII values.
             - 'pii_entities': List of PII entities with their corresponding types.
             - 'anonymized_prompt': The prompt with original PII values replaced by anonymized values.
             - 'highlighted_original_prompt': The prompt with original values wrapped in <pii_text> tags.
             - 'highlighted_anonymized_prompt': The prompt with anonymized values wrapped in <pii_text> tags.

    """
    try:

        # Initialize list to store unique values by PII type and entities
        pii_list: list = list()
        pii_entities: list = list()

        # Initialize prompt variables
        anonymized_prompt = prompt
        highlighted_original_prompt = prompt
        highlighted_anonymized_prompt = prompt

        for item in pii_data:
            anonymized = item["Anonymized"]
            original = item["Original"]
            pii_type = item["PII_Type"]

            # Appending to pii_list
            pii_list.append([original, anonymized])

            # Appending to pii_entities
            pii_entities.append([original, pii_type])

            # Use regex to replace original values with anonymized values (matching word boundaries)
            anonymized_prompt = re.sub(
                r"\b" + re.escape(original) + r"\b", anonymized, anonymized_prompt
            )

            # Wrap original values in <pii_text> tags for tagged prompt
            highlighted_original_prompt = re.sub(
                r"\b" + re.escape(original) + r"\b",
                f"<pii_text>{original}</pii_text>",
                highlighted_original_prompt,
            )

            # Wrap original values in <pii_text> tags for highlighted prompt
            highlighted_anonymized_prompt = re.sub(
                r"\b" + re.escape(original) + r"\b",
                f"<pii_text>{anonymized}</pii_text>",
                highlighted_anonymized_prompt,
            )

        logger.info(
            f"Processed PII data successfully: {len(pii_list)}PII items found. and anonymized prompt with wrapping tag"
        )

        final_anonymized_result = {
            "pii_list": pii_list,
            "pii_entities": pii_entities,
            "anonymized_prompt": anonymized_prompt,
            "highlighted_original_prompt": highlighted_original_prompt,
            "highlighted_anonymized_prompt": highlighted_anonymized_prompt,
        }
        return final_anonymized_result
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while processing PII data, generating the anonymized prompt, and wrapping "
            f"it with tags: {e}"
        )
        raise e

async def anonymize_file_content_with_gliner(
    file_content: str, pii_entities
):
    """
    Anonymizes the content of a file by detecting PII entities and applying anonymization keywords using an LLM model.
    :param file_content: The content of the file to be anonymized.
    :param pii_entities: A string representing the list of PII entities to identify (e.g., 'First Name', 'SSN').
    :param llm_model: The language model used for PII detection and anonymization.
    :return:  dict: The result of the anonymization process containing the PII data and other relevant information.

    """
    try:
        logger.info("Received request to anonymize file content")
        # Get the PII detection and anonymization prompt template
        # formatted_anon_prompt_for_file = get_anonymize_prompt_template()

        # invoke_params = {"pii_entities": pii_entities, "prompt": file_content}

        # # Use the common function to execute the LLM chain
        # logger.info(
        #     f"Sending prompt to LLM model for get anonymize prompt api for file...{invoke_params}"
        # )
        # detect_anonymize_result_file = await execute_llm_chain(
        #     prompt=formatted_anon_prompt_for_file,
        #     llm_model=llm_model,
        #     invoke_params=invoke_params,
        # )
        # detect_anonymize_pii_result_file = detect_anonymize_result_file.content
        # logger.info(
        #     f"Anonymization result from LLM for file: {len(detect_anonymize_pii_result_file)}"
        # )
        detect_anonymize_pii_result_file = extract_pii_elements(file_content, pii_entities=pii_entities)
        # result_pii = await convert_list_to_dict(detect_anonymize_pii_result_file)
        logger.info("Got pii for file contents")
        return detect_anonymize_pii_result_file
        # return (
        #     detect_anonymize_pii_result_file
        #     if detect_anonymize_pii_result_file
        #     else []
        # )

    except Exception as e:
        logger.error(f"An error occurred during processing of file content using models: {e}")
        raise e

def check_safeguard_keyword(prompt: str, keyword_safeguard: str) -> List:
    """
    Check if any keywords from the list are found in the prompt.
    :param prompt: The string prompt to be checked for keywords.
    :param keyword_safeguard: A list of keywords to safeguard against.
    :return:
    """

    # Find all keywords that are present in the prompt
    found_keywords = (
        [
            keyword
            for keyword in keyword_safeguard.split(",")
            if keyword.strip().lower() in prompt.lower()
        ]
        if keyword_safeguard
        else []
    )

    return found_keywords

# def extract_text_from_file(uploaded_file: UploadFile) -> str:
#     """
#     Extracts text from a PDF, DOCX, CSV, XLS, XML, or TXT file uploaded via FastAPI UploadFile.

#     :param uploaded_file: The uploaded file to extract text from.
#     :return: Extracted text from the file.
#     """
#     file_text: str = str()

#     try:
#         # Identify file type based on content type or file extension
#         file_extension = uploaded_file.filename.split(".")[-1].lower()
#         logger.info(f"Uploaded file: {file_extension}")

#         # Handle PDF/DOCX files
#         if file_extension in PDF_DOCX_FILE:
#             document = fitz.open(
#                 stream=uploaded_file.file.read(), filetype=file_extension
#             )
#             for page in document:
#                 file_text += page.get_text()
#             document.close()

#         # Handle CSV files
#         elif file_extension == CSV_FILE:
#             df = pd.read_csv(uploaded_file.file)
#             file_text = df.to_string()

#         # Handle TXT files
#         elif file_extension in TXT_FILE:
#             file_text = uploaded_file.file.read().decode("utf-8")

#         else:
#             logger.info(f"File extension not supported: {file_extension}")
#             raise ValueError(f"Unsupported file format: {file_extension}")

#         logger.info(
#             f"Extracted text from {uploaded_file.filename} file: {len(file_text)}"
#         )
#         return file_text

#     except Exception as e:
#         logger.error(
#             f"Error occurred while extracting text from {uploaded_file.filename}"
#         )
#         raise e
    