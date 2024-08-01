[!WARNING]
> In this branch, I attempted to add images as few-shots in the system prompt.
> However, adding images significantly increases the token count which causes the limits to be reached so easily that it's unusable.
> Keeping these changes in the branch for now for future reference. See implementation in the `./notebooks` folder.

# Handwriting-to-Markdown-GPT
This repo reads notes from a notebook, paper, or whiteboard and converts it into Markdown (*.md) using GenAI.

This code is the next iteration of a previous [Handwriting-to-Markdown](https://github.com/raffertyuy/Handwriting-to-Markdown/tree/main) Azure Logic App which was doing something similar but using Azure AI Services - Computer Vision.
In this implementation, Azure OpenAI `gpt-4o` is used instead.
- `./az-function` contains the main code using python and deployed to Azure Functions
- `./az-logicapp` contains code that triggers when a photo is added in a OneDrive source folder, and creates an `.md` file in a OneDrive target folder

Also see this [blog post](https://raffertyuy.com/raztype/handwriting-to-second-brain-gpt/)

## Solution Flow
This solution is using Azure Logic Apps with the following flow:
1. Watch for new files in a specific OneDrive folder
2. Check for GPT-4o supported image formats
   - if the filetype is PDF, convert to JPG using [OneDrive - Convert File](https://learn.microsoft.com/en-us/connectors/onedrive/#convert-file-(preview)) (limited to the first page of the PDF file).
   - if the filetype is not supported, skip.
3. Extract the text from the image file using GPT-4o (through a Function App).
4. Copy the image and save a new markdown file output in a destination OneDrive folder.

```mermaid
flowchart LR
    H[Handwritten Notes/Image<br />from OneDrive] --> |image content| N{Detect Note Type}
    subgraph "Azure Function"
        subgraph "Azure OpenAI GPT-4o Prompts"
            N --> |Paper| P[Paper System Prompt]
            N --> |Whiteboard| W[Whiteboard System Prompt]
            N --> |Other| O[Generic System Prompt]
            P --> PR[Proof Read]
            W --> |text output| PR
            O --> PR
            PR --> S[Section<br />Headers]
            S --> ET[Extract<br />Title]
        end
         ET --> IT[Initial<br />Output]
         IT --> |add<br />metadata| Output[Final<br />Output]
    end
    Output --> |save| MD[Markdown File<br />in OneDrive]
```

> [!NOTE]
> Prompt Flow was previously attempted, but the following gaps were encountered (as of 2024-06-28):
> - Prompt Flow in VS Code doesn't support an `image` input type.
> - Prompt Flow on [AI Studio](https://ai.azure.com) doesn't support GPT-4o (but GPT-4V is available in preview)

## Azure Function Notes
### Python Programming Model
This Azure function is developed using the [Python v2 programming model](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators) and is deployed using the [VS Code Extension: Azure Functions](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions).

> [!TIP]
> Sometimes, the function does not show up on Azure after deploying. This usually happens when there is an error in the code. For example:
> - a missing dependency in the requirements.txt file
> - a missing environment variable in Azure (that is currently in `local.settings.json`)
> - or an actual error in the code.

> [!NOTE]
> There is a previous attempt to have this consumed by logic apps using the Azure Function connector and Managed Identiites. It didn't work due to complexity of using MI with `multipart/form-data`. But here are additional notes in this previous attempt:
> - To call Azure Functions using managed identities, the function method must be set to `ANONYMOUS` and configured for [managed identity authentication](https://learn.microsoft.com/en-us/azure/logic-apps/call-azure-functions-from-workflows?tabs=consumption#set-authentication-function-app)
> - Azure Logic Apps can't call Azure Functions with custom routes. For Python, this means leaving the route empty with `@app.route(route="")` as suggested in [this issue](https://github.com/Azure/azure-functions-python-worker/issues/1468).

For the current implementation, this function's `AuthLevel` is set to `FUNCTION`. Meaning, a function key is expected to be passed in the request.

## Logic App Notes

### Authentication
To authenticate with the Azure Function, a function key stored in Azure Key Vault is used.

### Sending a `multipart/form-data` HTTP POST
Since we're passing a OneDrive file to Azure Functions as a `multipart/form-data`, the HTTP request body should look like this.
```json
{
    "$content-type": "multipart/form-data",
    "$multipart": [
        {
            "body": ATTACHMENTS_CONTENT,
            "headers": {
                "Content-Disposition": "form-data; name=image; filename=\"ATTACHMENTS_NAME\"",
                "Content-Type": "ATTACHMENTS_CONTENT_TYPE"
            }
        }
    ]
}
```

> [!NOTE]
> I eventually used the **HTTP Request** connector instead of an **Azure Functions** connector.
> This is because the response body is in JSON, and the Azure Functions connector returns this in a JSON-escaped string format.
> Since I'm using Obsidian for my second brain, my final markdown image link uses `![[image_path]]` instead of the standard `![name](image_path)` format.

### Deployment
- `code.json` is the copy-pasted code from the Logic Apps's code view, for reference. This is the exact code that I personally use after using the Logic App designer.
- `azuredeploy.json` is the ARM template to be deployed to azure, generated from the resource group's "export template"

### Running Locally
- `az-logicapp` can't be run locally
- `az-function`
  - Create a file `local.settings.json` (refer to `local.settings.example.json`)
  - can be run with `func start` (requires [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local).