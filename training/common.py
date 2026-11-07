PROMPT = "Command: {text}\nJSON: "


def build_prompt(text):
    return PROMPT.format(text=text)
