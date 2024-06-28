# This is an HTTP Request Azure Function
# Input is multipart/form-data containing an image
# Output is a string of extracted text from the image.
# This function uses Azure OpenAI model "gpt4o" to extract text from the image.

import azure.functions as func
import logging

import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from image_processor import execute_image_completion, execute_text_completion, read_file, save_string_to_file
import base64
import json

# Initialize
load_dotenv()
AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION=os.getenv("AZURE_OPENAI_API_VERSION")

# use 'az login' locally or managed identity when deployed on Azure
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

client = AzureOpenAI(
  azure_endpoint = AZURE_OPENAI_ENDPOINT,
  api_version=AZURE_OPENAI_API_VERSION,
  azure_ad_token_provider=token_provider
)

# Function App
app = func.FunctionApp()

@app.route(route="ExtractNotes", methods=["POST"])
def ExtractNotes(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ExtractNotes Python HTTP trigger function processed a request.')
    
    # Get the image from the request
    image = req.files['image']
    image_bytes = image.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # Identify image note type
    noteType = execute_image_completion(client, image_base64, read_file("../prompts/detectNoteType.txt"))
    logging.debug(f"Note type is {noteType}.")
    
    # Extract text from the image
    ocr_prompt_filename = "../prompts/ocrImage.txt"
    if noteType == "PAPER":
      ocr_prompt_filename = "../prompts/ocrPaper.txt"
    elif noteType == "WHITEBOARD":
      ocr_prompt_filename = "../prompts/ocrPaper.txt"
    
    extracted_text = execute_image_completion(client, image_base64, read_file(ocr_prompt_filename))
    logging.debug("""
--- 1. Initial text extracted:------------------------------------------
{extracted_text}
------------------------------------------------------------------------
""")
    
    # Post-process the extracted text
    if noteType == "PAPER" or noteType == "WHITEBOARD":
      extracted_text = execute_text_completion(client, extracted_text, read_file("../prompts/proofread.txt"))
      logging.debug("""
--- 2. Proof read:------------------------------------------------------
{extracted_text}
------------------------------------------------------------------------
""")
      
      extracted_text = execute_text_completion(client, extracted_text, read_file("../prompts/sectionHeader.txt"))
      logging.debug("""
--- 3. Section headers:-------------------------------------------------
{extracted_text}
------------------------------------------------------------------------
""")
      
    # Final response
    response_data = {
      "noteType": noteType,
      "extractedText": extracted_text
    }
    
    response_json = json.dumps(response_data)
    return func.HttpResponse(response_json, mimetype="application/json")