# Handwriting-to-Markdown-GPT
This repo reads notes from a notebook, paper, or whiteboard and converts it into Markdown (*.md) using GenAI.

This code is the next iteration of a previous [Handwriting-to-Markdown](https://github.com/raffertyuy/Handwriting-to-Markdown/tree/main) Azure Logic App which was doing something similar but using Azure AI Services - Computer Vision.
In this implementation, Azure OpenAI `gpt-4o` is used instead.
- `./az-function` contains the main code using python and deployed to Azure Functions
- `./az-logicapp` contains code that triggers when a photo is added in a OneDrive source folder, and creates an `.md` file in a OneDrive target folder

## Use Case
- Watch for new files in a specific OneDrive folder (using Azure Logic Apps)
- Process the files using GPT-4o (through a Function App)
- Copy the image and save a new markdown file output in a destination oneDrive folder.

## Limitations / TODOs
- [ ] GPT-4o only accepts image files. Add error handling for unsupported file types.
- [ ] Add a new Azure Function for converting PDF to image files using this sample code (with revisions to save individual image files to OneDrive)
    ```python
    # import module
    from pdf2image import convert_from_path

    # Store Pdf with convert_from_path function
    images = convert_from_path('example.pdf')

    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save('page'+ str(i) +'.jpg', 'JPEG')
    ```

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
- `azuredeploy.json` is the ARM template to be deployed to azure.
- `code.json` is the copy-paste from the Logic Apps's code view, after building with the Logic App designer.