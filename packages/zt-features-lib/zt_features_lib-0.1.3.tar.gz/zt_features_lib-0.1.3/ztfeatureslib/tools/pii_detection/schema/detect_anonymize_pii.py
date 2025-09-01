from pydantic import BaseModel, Field, root_validator
from typing import Annotated, List, Optional
# from fastapi import File, Form, UploadFile

class AnonymizePromptRequest(BaseModel):
    """
    A request model for handling anonymization of sensitive information (PII) from both a user-provided prompt and
    an optional uploaded file using a Large Language Model (LLM).
    """

    pii_entities: str = Field(
        ...,
        description="List of PII entities to identify. Example: ['First Name', 'SSN ("
        "Social Security Number)','Credit Card Number', 'Phone Number']",
    )
    prompt: str = Field(
        ...,
        description="Input prompt containing sensitive data. Example: 'Firstname,Lastname,SSN,"
        "CreditCard,DOB, John,Doe,123-45-6789,4111 1111 1111 1111,01/01/1985'",
    )
    anonymize_keywords: Optional[str] = Field(
        default=str,
        description="List of keywords that need to be anonymized in "
        "the text. Example: ['sql', 'query']",
    )
    deanonymize_keywords: Optional[str] = Field(
        default=str,
        description="List of keywords that need to be deanonymized in "
        "the text. Example: ['John Doe', 'johndoe@gmail.com']",
    )
    keyword_safeguard: Optional[str] = Field(
        default=str,
        description="List of keywords that should trigger special "
        "safeguarding or monitoring. Example: ['bomb', "
        "'exp']",
    )
    # uploaded_file: Optional[UploadFile] = File(
    #     None, description="File uploaded by the user for PII extraction"
    # )
    client_api_key: str = Field(default=str, description="client api key for llm model")
    llm: str = Field(default=str, description="name of llm model")

class AnonymizedPromptResponse(BaseModel):
    """
    A response model representing the result of the anonymization process for both user-provided prompts and uploaded files.

    """

    anonymized_prompt: Optional[str] = Field(
        "", description="The anonymized version of the original prompt."
    )
    highlighted_original_prompt: Optional[str] = Field(
        "", description="The original prompt with highlights."
    )
    highlighted_anonymized_prompt: Optional[str] = Field(
        "", description="The anonymized prompt with highlights."
    )
    pii_list: Optional[List[List[str]]] = Field(
        [], description="List of PII items with their corresponding types."
    )
    pii_entities: Optional[List[List[str]]] = Field(
        [], description="List of detected PII entities with their types."
    )
    safe_guard_error_message: Optional[str] = Field(
        "", description="when  safe guard word detected in prompt"
    )
    file_location: Optional[str] = Field(
        "", description="The file location of the uploaded file."
    )
    file_pii_array: Optional[List[List[str]]] = Field(
        [], description="List of PII items with their corresponding " "types."
    )

class AnonymizePromptResponse(BaseModel):
    """
    Response model for detected PII entities and their types.
    """

    success: bool = Field(..., example=True)
    data: Optional[AnonymizedPromptResponse] = Field(
        {}, description="Detailed response including anonymized prompt and PII details."
    )
    error_message: Optional[str] = Field("", description="Error message, if any.")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "success": True,
                    "data": {
                        "anonymized_prompt": "This is an anonymized prompt.",
                        "highlighted_original_prompt": "This is the original prompt with highlights.",
                        "highlighted_anonymized_prompt": "This is the anonymized prompt with highlights.",
                        "pii_list": [
                            ["John", "First Name"],
                            ["Smith", "Last Name"],
                            ["123-45-6789", "SSN"],
                            ["4111 1111 1111 1111", "Credit Card Number"],
                            ["123", "CVV"],
                        ],
                        "pii_entities": [
                            ["John", "First Name"],
                            ["Smith", "Last Name"],
                            ["123-45-6789", "SSN"],
                            ["4111 1111 1111 1111", "Credit Card Number"],
                            ["123", "CVV"],
                        ],
                        "safe_guard_error_message": "Sensitive keyword detected.",
                    },
                    "errorMessage": "",
                }
            ]
        }

class DetectedPromptResponse(BaseModel):
    """
    A response model representing the result of the detection process for both user-provided prompts and uploaded files.

    """

    pii_entities: Optional[List[List[str]]] = Field(
        [], description="List of detected PII entities with their types."
    )

class DetectPromptResponse(BaseModel):
    """
    Response model for detected PII entities and their types.
    """

    success: bool = Field(..., example=True)
    data: Optional[DetectedPromptResponse] = Field(
        {}, description="Detailed response including detected prompt and PII details."
    )
    error_message: Optional[str] = Field("", description="Error message, if any.")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "success": True,
                    "data": {
                        "pii_entities": [
                            ["John", "First Name"],
                            ["Smith", "Last Name"],
                            ["123-45-6789", "SSN"],
                            ["4111 1111 1111 1111", "Credit Card Number"],
                            ["123", "CVV"],
                        ],
                        "safe_guard_error_message": "Sensitive keyword detected.",
                    },
                    "errorMessage": "",
                }
            ]
        }