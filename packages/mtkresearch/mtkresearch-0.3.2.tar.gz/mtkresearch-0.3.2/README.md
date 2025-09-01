# MTK Research Package

# Setup

```
$ pip install mtkresearch
```

# MRPromptV3

`MRPromptV3` is a class designed to facilitate the creation and management of prompts for conversational AI systems. This class provides methods to generate prompts based on a series of conversations, including support for function calls and handling various types of user inputs such as text and image.

## Initialization
To initialize an instance of `MRPromptV3`, simply import the class and create an instance:

```python
from mtkresearch.llm.prompt import MRPromptV3
prompt = MRPromptV3()
```

## Methods

### `get_prompt`

Generates a prompt based on the provided conversations and optional functions.

```markdown
Parameters:
* `conversations` (list): A list of conversation dictionaries, each containing role and content.
* `functions` (list, optional): A list of function definitions that the assistant can use. Default is `None`.
* `add_bos_token` (bool, optional): Whether to add a beginning-of-sequence token. Default is `False`.
* `training` (bool, optional): Whether the prompt is for training purposes. Default is `False`.

Returns:
* `str`: The generated prompt.
```

Example:
```python
python
conversations = [
    {"role": "user", "content": "What is the weather of Boston?"}
]
functions = [
    {
        'name': 'get_current_weather',
        'description': 'Get the current weather',
        'parameters': {
            'type': 'object',
            'properties': {
                'location': {'type': 'string', 'description': 'The city and state, e.g. San Francisco, CA'},
                'unit': {'type': 'string', 'enum': ['celsius', 'fahrenheit']}
            },
            'required': ['location']
        }
    }
]

result = prompt.get_prompt(conversations, functions)
print(result)
```

### `parse_generated_str`

Parses a generated string to extract the role and content, including function calls.

```markdown
Parameters:
* `generated_str` (str): The generated string to parse.

Returns:
* `dict`: A dictionary containing the parsed role and content.
```

Example:

```python
generated_str = "<|use_tool|>[get_current_weather(location='Boston, MA')]<|eot_id|>"
parsed_result = prompt.parse_generated_str(generated_str)
print(parsed_result)
# Expected: 
# {
#     'role': 'assistant',
#     'tool_calls': [
#         {
#             'type': 'function',
#             'function': {
#                 'name': 'get_current_weather',
#                 'arguments': '{"location": "Boston, MA"}'
#             }
#         }
#     ]
# }
```

## Structure of `conversations`

### Basic Structure

Each message in the `conversations` list has the following basic structure:

```python
{
    "role": string ("system" | "user" | "assistant" | "tool"),
    "content": string | list,
    ...
}
```

* `role`: Specifies the role of the speaker. It can be one of the following:
    * "system": Represents system messages, usually providing context or instructions.
    * "user": Represents messages from the user.
    * "assistant": Represents messages from the assistant.
    * "tool": Represents responses from tools or functions called by the assistant.
* `content`: The content of the message. It can be a string or a list of dictionaries, depending on the type of message.

### System Message

A system message provides context or instructions for the conversation.

```python
{
    "role": "system",
    "content": "YOUR SYSTEM MESSAGE"
}
```

### User Message

A user message contains the user's input.

```python
{
    "role": "user",
    "content": "YOUR PROBLEM"
}
```

### User Message with Image

A user message containing text, an image, and bounding box information.

```python
{
    "role": "user",
    "content": [
        {
            "type": "image",
            "image_path": "/path/to/image.png",
        },
        {
            "type": "text",
            "text": "In the above image, how many dogs in "
        },
        {
            "type": "bbox",
            "width": 1024,
            "height": 768,
            "coords": [[0, 0, 512, 384]]
        },
        {
            "type": "text",
            "text": " ?"
        }
    ]
}
```

* `type`: Specifies the type of content. It can be "text", "image", or "bbox".
* `text`: The text content (for "text" types).
* `image_path`: The path to the image file (for "image" type).
* `width and height`: The dimensions of the image.
* `coords`: The coordinates of the bounding box (for "bbox" type).

### Assistant Message

An assistant message contains the assistant's response.

```python
{
    "role": "assistant",
    "content": "RESPONSE"
}
```

### Tool Call

A tool call message contains information about a function call made by the assistant.

```python
{
    "role": "assistant",
    "tool_calls": [
        {
            'id': 'call_8jLWqlXaY3OisD24IHJLwD3G',
            'type': 'function',
            'function': {
                'arguments': "{\"location\": \"Boston, MA\"}",
                'name': 'get_current_weather'
            }
        }
    ]
}
```

### Tool Response

A tool response message contains the response from a tool or function.

```python
{
    "role": "tool",
    "tool_call_id": "call_8jLWqlXaY3OisD24IHJLwD3G",
    "name": "get_current_weather",
    "content": "{\"temperature\": \"22 celsius\"}"
}
```

## Structure of `functions`

### Basic Structure

Each function description in the `functions` list has the following basic structure:

```python
{
    "name": str,
    "description": str,
    "parameters": dict,
    "required": list
}
```

* `name`: The name of the function, which should be short, clear, and descriptive of its core functionality. The format must be a string without spaces or special characters. For examples, "get_weather", "calculate_shipping", "translate_text".
* `description`: A concise text explaining the purpose and function of the API. Use natural language. Be brief but complete, avoiding unnecessary technical jargon or ambiguity.
* `parameters`: Defines the parameters and their structure required by the function, following the JSON Schema standard. Format as following:
    * `type`: Must be `"object"`.
    * `properties`: Defines the specific attributes of each parameter, including name, type, and description. Each parameter definition includes:
        * `type`: The data type of the parameter (`"string"`, `"number"`, `"boolean"`, `"array"`, `"object"`).
        * `description`: Explains the purpose of the parameter.
        * Optional attributes such as `"enum"`, `"default"`, etc.
* `required`: Lists the names of all required parameters (optional).

For example:
```json
{
  "name": "get_weather",
  "description": "Fetches the current weather for a specific location.",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The name of the city or geographic coordinates (latitude,longitude)."
      },
      "unit": {
        "type": "string",
        "description": "The unit of temperature measurement. Options are 'metric' (Celsius), 'imperial' (Fahrenheit), or 'standard' (Kelvin).",
        "enum": ["metric", "imperial", "standard"],
        "default": "metric"
      },
      "language": {
        "type": "string",
        "description": "The language code for the weather description (e.g., 'en' for English, 'fr' for French).",
        "default": "en"
      }
    },
    "required": ["location"]
  }
}
```
