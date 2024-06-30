import azure.functions as func
import logging

import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from image_processor import execute_image_completion, execute_text_completion, read_file
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

# A function that takes a text as input and removes possible ```markdown``` code blocks
# for example, if the text is "```markdown\n# Title\n```", it will return "# Title"
# or if the text is "```markdown # Title ```", it will return "# Title"
def remove_markdown_code_blocks(text: str) -> str:
    text = text.strip()
    if text.startswith("```markdown"):
        text = text[len("```markdown"):]
    if text.endswith("```"):
        text = text[:-len("```")]
    return text.strip()

# Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="ExtractNotes")
@app.route(route="", methods=["POST"])
def ExtractNotes(req):
    logging.info('ExtractNotes Python HTTP trigger function processed a request.')

    logging.info("Getting image from the request...")
    image = req.files['image']
    image_bytes = image.stream.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # Identify image note type
    noteType = execute_image_completion(client, image_base64, read_file("./prompts/detectNoteType.txt"), AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_VISION_TEMPERATURE)
    logging.info(f"Note type is {noteType}.")

    # Extract text from the image
    ocr_prompt_filename = "./prompts/ocrImage.txt"
    if noteType == "PAPER":
      ocr_prompt_filename = "./prompts/ocrPaper.txt"
    elif noteType == "WHITEBOARD":
      ocr_prompt_filename = "./prompts/ocrPaper.txt"

    extracted_text = execute_image_completion(client, image_base64, read_file(ocr_prompt_filename), AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_VISION_TEMPERATURE)
    logging.info("""
--- 1. Initial text extracted:------------------------------------------
{extracted_text}
------------------------------------------------------------------------
""")

    # Post-process the extracted text
    if noteType == "PAPER" or noteType == "WHITEBOARD":
      extracted_text = execute_text_completion(client, extracted_text, read_file("./prompts/proofread.txt"), AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_TEXT_TEMPERATURE)
      logging.info("""
--- 2. Proof read:------------------------------------------------------
{extracted_text}
------------------------------------------------------------------------
""")

      extracted_text = execute_text_completion(client, extracted_text, read_file("./prompts/sectionHeader.txt"), AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_TEXT_TEMPERATURE)
      logging.info("""
--- 3. Section headers:-------------------------------------------------
{extracted_text}
------------------------------------------------------------------------
""")

    extracted_text = remove_markdown_code_blocks(extracted_text)

    # Final response

    response_data = {
      "noteType": noteType,
      "extractedText": extracted_text
    }

    response_json = json.dumps(response_data)
    return response_json