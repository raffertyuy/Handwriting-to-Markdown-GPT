import azure.functions as func
import logging

import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

import prompts.ocrPaper as ocrPaper
import prompts.ocrWhiteboard as ocrWhiteboard
from prompts.systemprompt_builder import read_file
from image_processor import execute_image_completion, execute_text_completion
from post_processor import remove_markdown_code_blocks, add_datestamp

import base64
import json

# Initialize
logging.info("Initialize - Getting environment variables...")
AZURE_OPENAI_ENDPOINT=os.environ["AzureOpenAiEndpoint"]
AZURE_OPENAI_API_VERSION=os.environ["AzureOpenAiApiVersion"]
AZURE_OPENAI_DEPLOYMENT=os.environ["AzureOpenAiDeployment"]
AZURE_OPENAI_VISION_TEMPERATURE=float(os.environ["AzureOpenAiVisionTemperature"])
AZURE_OPENAI_TEXT_TEMPERATURE=float(os.environ["AzureOpenAiTextTemperature"])

# use 'az login' locally or managed identity when deployed on Azure
logging.info("Getting Azure AD token provider...")
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

logging.info("Creating Azure OpenAI client...")
client = AzureOpenAI(
  azure_endpoint = AZURE_OPENAI_ENDPOINT,
  api_version=AZURE_OPENAI_API_VERSION,
  azure_ad_token_provider=token_provider
)

# Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name(name="ExtractNotes")
@app.route(route="", methods=["POST"])
def ExtractNotes(req):
    logging.info('ExtractNotes Python HTTP trigger function processed a request.')

    image = req.files['image']
    image_bytes = image.stream.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # Identify image note type
    noteType = execute_image_completion(client, image_base64, read_file("./prompts/detectNoteType.txt"), AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_VISION_TEMPERATURE)

    # Extract text from the image
    if noteType == "PAPER":
        system_prompt = ocrPaper.get_prompt_content()
    elif noteType == "WHITEBOARD":
        system_prompt = ocrWhiteboard.get_prompt_content()
    else:
        system_prompt = read_file("./prompts/ocrImage.txt")

    extracted_text = execute_image_completion(client, image_base64, system_prompt, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_VISION_TEMPERATURE)

    # Post-process the extracted text
    if noteType == "PAPER" or noteType == "WHITEBOARD":
      extracted_text = execute_text_completion(client, extracted_text, read_file("./prompts/proofread.txt"), AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_TEXT_TEMPERATURE)
      extracted_text = execute_text_completion(client, extracted_text, read_file("./prompts/sectionHeader.txt"), AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_TEXT_TEMPERATURE)

    extracted_text = remove_markdown_code_blocks(extracted_text)
    
    extracted_title = execute_text_completion(client, extracted_text, read_file("./prompts/extractMainTitle.txt"), AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_TEXT_TEMPERATURE)
    extracted_title = add_datestamp(extracted_title)

    # Final response
    response_data = {
      "noteType": noteType,
      "extractedTitle": extracted_title,
      "extractedText": extracted_text
    }

    response_json = json.dumps(response_data)
    return response_json