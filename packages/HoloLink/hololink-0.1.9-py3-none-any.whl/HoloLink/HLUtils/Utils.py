
import collections.abc
from google.genai import types


def isStructured(*args):
    """
    Check if any of the arguments is a list of dictionaries.
    This indicates structured input (multi-message format).
    """
    return any(
        isinstance(arg, list) and all(isinstance(i, dict) for i in arg)
        for arg in args
    )


def handleTypedFormat(role: str = "user", content: str = ""):
    """
    Format content for Google GenAI APIs.
    """
    role    = role.lower()
    allowed = {"system", "user", "model"}
    if role not in allowed:
        raise ValueError(
            f"Invalid role '{role}'. Must be one of {', '.join(allowed)}."
        )
    if role == "system":
        return types.Part.from_text(text=content)
    return types.Content(role=role, parts=[types.Part.from_text(text=content)])


def handleJsonFormat(role: str = "user", content: str = ""):
    """
    Format content for OpenAI APIs.
    """
    role    = role.lower()
    allowed = {"system", "developer", "user", "assistant"}
    if role not in allowed:
        raise ValueError(
            f"Invalid role '{role}'. Must be one of {', '.join(allowed)}."
        )
    return {'role': role, 'content': content}


def buildGoogleSafetySettings(harassment="BLOCK_NONE", hateSpeech="BLOCK_NONE", sexuallyExplicit="BLOCK_NONE", dangerousContent="BLOCK_NONE"):
    """
    Construct a list of Google GenAI SafetySetting objects.
    """
    harassment        = harassment.upper()
    hate_speech       = hateSpeech.upper()
    sexually_explicit = sexuallyExplicit.upper()
    dangerous_content = dangerousContent.upper()
    allowed_settings  = {"BLOCK_NONE", "BLOCK_LOW", "BLOCK_MEDIUM", "BLOCK_HIGH", "BLOCK_ALL"}
    for name, val in {
        "harassment": harassment, 
        "hate_speech": hate_speech, 
        "sexually_explicit": sexually_explicit, 
        "dangerous_content": dangerous_content
    }.items():
        if val not in allowed_settings:
            raise ValueError(f"Invalid {name} setting: {val}. Must be one of {', '.join(allowed_settings)}.")

    return [
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold=harassment),
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold=hate_speech),
        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold=sexually_explicit),
        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold=dangerous_content),
    ]


def handleExamples(items, formatFunc):
    """
    Format a list of items into a Google GenAI/ OpenAI compatible format.
    Each item should be a tuple of (role, value).
    The role should be a string like "user", "system", etc.
    The value can be a string, dict, or a list of strings/dicts.
    """
    def flatten(role, value):
        if value is None:
            return []
        if isinstance(value, dict):
            return [value]
        if isinstance(value, str):
            return [formatFunc(role, value)]
        if isinstance(value, (int, float, bool)):
            return [formatFunc(role, str(value))]
        if isinstance(value, collections.abc.Sequence) and not isinstance(value, (str, bytes, dict)):
            out = []
            for v in value:
                try:
                    out.extend(flatten(role, v))
                except Exception as e:
                    print(f"Warning: Skipped invalid message part for role '{role}': {v!r} ({type(v).__name__}) [{e}]")
            return out
        try:
            return [formatFunc(role, str(value))]
        except Exception as e:
            print(f"Warning: Could not handle value for role '{role}': {value!r} ({type(value).__name__}) [{e}]")
            return []

    out = []
    for role, value in items:
        out.extend(flatten(role, value))
    return out


def handleJsonExamples(items):
    """
    Format a list of items into a Google GenAI compatible format.
    Each item should be a dictionary with 'role' and 'content' keys.
    """
    # out = []
    # for role, value in items:
    #     if isinstance(value, str):
    #         out.append(handleJsonFormat(role, value))
    #     elif isinstance(value, dict):
    #         out.append(value)
    #     elif isinstance(value, list) and all(isinstance(i, dict) for i in value):
    #         out.extend(value)
    #     elif value is not None:
    #         raise ValueError(f"{role.title()} must be a string, dict, or a list of dicts.")
    # return out
    return handleExamples(items, handleJsonFormat)


def handleTypedExamples(items):
    """
    Format a list of items into a Google GenAI compatible format.
    Each item should be a dictionary with 'role' and 'content' keys.
    """
    # out = []
    # for role, value in items:
    #     if isinstance(value, str):
    #         out.append(handleTypedFormat(role, value))
    #     elif isinstance(value, dict):
    #         out.append(value)
    #     elif isinstance(value, list) and all(isinstance(i, dict) for i in value):
    #         out.extend(value)
    #     elif value is not None:
    #         raise ValueError(f"{role.title()} must be a string, dict, or a list of dicts.")
    # return out
    return handleExamples(items, handleTypedFormat)


formatExamples = handleExamples
formatTypedExamples = handleTypedExamples
formatJsonExamples = handleJsonExamples
