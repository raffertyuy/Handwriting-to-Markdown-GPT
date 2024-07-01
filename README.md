# Handwriting-to-Markdown-GPT
This repo reads notes from a notebook, paper, or whiteboard and converts it into Markdown (*.md) using GenAI.

This code is the next iteration of a previous [Handwriting-to-Markdown](https://github.com/raffertyuy/Handwriting-to-Markdown/tree/main) Azure Logic App which was doing something similar but using Azure AI Services - Computer Vision.
In this code, Azure OpenAI `gpt-4o` is used instead.

- `./az-function` contains the main code using python and deployed to Azure Functions
- `./az-logicapp` contains code that triggers when a photo is added in a OneDrive source folder, and creates an `.md` file in a OneDrive target folder


## Azure Function Notes
### Python Programming Model
This Azure function is developed using the [Python v2 programming model](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators) and is deployed using the [VS Code Extension: Azure Functions](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions).

> [!TIP]
> Sometimes, the function does not show up on Azure after deploying. This usually happens when there is an error in the code. For example:
> - a missing dependency in the requirements.txt file
> - a missing environment variable in Azure (that is currently in `local.settings.json`)
> - or an actual error in the code.

As this function is to be consumed by logic apps, the following implementations were applied
- Azure Logic Apps can't call Azure Functions with custom routes. For Python, this means leaving the route empty with `@app.route(route="")` as suggested in [this issue](https://github.com/Azure/azure-functions-python-worker/issues/1468).
- To call Azure Functions using managed identities, the function method must be set to anonymous.

### Authentication
To call this function from Azure Logic Apps, the function auth level should be set to `ANONYMOUS`.
Then, configure for [managed identity authentication](https://learn.microsoft.com/en-us/azure/logic-apps/call-azure-functions-from-workflows?tabs=consumption#set-authentication-function-app).


## Logic App Notes

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

This is the actual code implemented
```json
{
    "$content-type": "multipart/form-data",
    "$authentication": {
        "audience": "https://management.azure.com",
        "type": "ManagedServiceIdentity"
    },
    "$multipart": [
        {
           "body": @{triggerBody()},
           "headers": {
                "Content-Disposition": "form-data; name=image; filename=\"@{triggerOutputs()['headers']['x-ms-file-name-encoded']}\"",
                "Content-Type": "@{triggerOutputs()['headers']['Content-Type']}"
            },
            "authentication": {
                "audience": "https://management.azure.com",
                "type": "ManagedServiceIdentity"
            }
        }
    ]
}
```

> [!NOTE]
> I eventually used the **HTTP Request** connector instead of an **Azure Functions** connector.
> This is because the response body is in JSON, and the Azure Functions connector returns this in a JSON-escaped string format.