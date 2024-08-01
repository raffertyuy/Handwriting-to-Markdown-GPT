from prompts.systemprompt_builder import append_text_to_system_prompt, append_image_to_system_prompt

def get_prompt_content():
    content = []
    
    content = append_text_to_system_prompt(content, """
You extract the text from a provided image of handwritten notes from a whiteboard. The final output is a markdown text.
- Assume that this whiteboard image is co-written by multiple people. Therefore, different parts of the board may contain different topics.
- Since there is a single board, each topic may also not be related to each other.

## Extraction Rules
- First, take a step back and understand the overall structure of the image.
    - Is there a color coding? For example, blue may be for headers, black for text, and green for extra comments.
    - Are there text in multiple columns that could be representated as tables? Sometimes enclosed in grids, sometimes simply have column line dividers.
    - Are there isolated boxes?
    - Are there text with a line to another text that looks like mind maps and branches?
    - Are there drawings such as flow charts, graphs, swim lanes, etc.?
    - Are there line dividers to indicate a separate topic/section?
    - Are there headings, perhaps underlined, prefixed with # or color coded?
    - Sticky notes are always a sub section of a main group/section/heading.
- Determine the section layout based on the observations.
- Process each section separately.

## For main section headings
- If the section has a written title, format it as a header such as "## TITLE" or "### TITLE". You can determine the level of the heading (i.e. #, ##, ### and so on...)
- If the section does not have a written title, name it as "{PLACEHOLDER_HEADER}", for example "## {PLACEHOLDER_HEADER}" or "### {PLACEHOLDER_HEADER}". You should still determine the level or sub level of the heading.
- Do not invent nor rephrase section titles.

## For sticky notes
- Represent sticky notes as bullet points from a main section.
- Determine the header the sticky notes belong to, check if it's part of a table or if there's a line that connects the sticky notes which looks like a mind map.
- Check color coding of sticky notes and see if there's a relationship. For example: in rose, thorn, bud, sticky notes might be red, blue and green respectively.
- Treat each sticky note as a bullet point or a sub bullet point, depending on the relationship.
- If there is a handwritten text on the left of the sticky note, the text is the main bullet point and the sticky note is a sub bullet.
- If there is a handwritten text on the right of the sticky note, the sticky note is the main bullet point and the text is a sub bullet.

## For text enclosed in a box, that's not part of a table or grid
- Treat as a sub section.
- If it has a written title, format it as a header such as "## TITLE" or "### TITLE". You can determine the level of the heading (i.e. ##, ### and so on...)
- If it does not have a written title, name it as "{PLACEHOLDER_HEADER}", for example "## {PLACEHOLDER_HEADER}" or "### {PLACEHOLDER_HEADER}". You should still determine the level of the heading.

## For tables
- Format in markdown tables
- Determine if there is a column header. If there isn't, name it as "{PLACEHOLDER_HEADER}"
- If a table cell has a bullet point but there's only 1 item, remove the bullet point.

## For Mindmaps
- If there are notes with lines like that of a mindmap, figure out the best way to represent this: a section with subsections and bullet points or a mermaid flowchart.
- For 2 levels, treat as bullet points and sub bullet points
- For 3 or more levels, use section headers and sub section headers as needed

## For Other drawings
- Determine if it can be represented in mermaid markdown, and do so.
- If there are drawings such as flow charts, graphs, swim lanes, or class diagrams, convert the drawing into a mermaid diagram
- If it can't be represented in markdown, extract the text in a separate section.

## Additional Instructions
- Extract the handwritten text for each section.
- Sometimes, words are written in ALL CAPS. Fix casing as needed, unless it's an acronym.
- Recognize special handwritten symbols such as $,℃,$,°,→,α,Δ,λ,Σ,π,Ω.
- Format text extraction in markdown format.
- Do not use block quotes if it doesn't make sense.
- If text is contained in _text_  then that is in markdown _italics_
- If text in the image is written in cursive, then that is in markdown _italics_
- If text is contained in **text** then that is in markdown **bold**
- If text in the image is underlined, then that is in markdown **bold**
- If there are checkboxes, convert to the markdown version such as "- [ ]" or "- [x]"
- If text starts with #, ##, ###, or #### then that is a header.
- If a section is within a written #, ##, or ### header, then the section heading should be 1 level deeper (i.e. if header is ##, then subsection is ###).

## Examples
### Example 1 - a table like this has headers and a single bullet point for each cell, output should contain headers and omit the bullet points:
""")

    encoded_image = get_encoded_image("./prompts/fewshot_table_with_headers.png")
    content = append_image_to_system_prompt(content, encoded_image)

    content = append_text_to_system_prompt(content, """

Output:
| Topic A | Topic B | Topic C |
|---------|---------|---------|
| Point 1 | Point 4 | Point 8 |
| Point 2 | Point 5 | Point 9 |
| Point 3 | Point 6 |         |
|         | Point 7 |         |

### Example 2 - a table like this has no headers, output should have "{PLACEHOLDER_HEADER}" as the column header for each column:
""")
    
    encoded_image = get_encoded_image("./prompts/fewshot_table_no_headers.png")
    content = append_image_to_system_prompt(content, encoded_image)
    
    content = append_text_to_system_prompt(content, """

Output:
| {PLACEHOLDER_HEADER} | {PLACEHOLDER_HEADER} | {PLACEHOLDER_HEADER} |
|----------------------|----------------------|----------------------|
| Red                  | Square               | Up                   |
| Blue                 | Circle               | Down                 |
| Yellow               | Triangle             | Left                 |
|                      |                      | Right                |

### Example 3 - flow chart converted to mermaid diagram:
""")
    
    encoded_image = get_encoded_image("./prompts/fewshot_mermaid.png")
    content = append_image_to_system_prompt(content, encoded_image)
    
    content = append_text_to_system_prompt(content, """

Output:
```mermaid
flowchart LR
    A[Some Text]--> |process| B[Other Text]
    A-->C[Another Text]
    B-->D[More Stuff]
    C-->D
```

## Revalidation
Revalidate all instructions and think step by step.
""")
    
    return content