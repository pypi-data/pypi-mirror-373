

def clean_llm_response(response_text: str) -> str:
    clean_deepseek = _strip_think_tag_from_deepseek_response(_replace_role_tags_from_response(response_text))
    clean_tags = _replace_role_tags_from_response(clean_deepseek)
    return clean_tags

def _strip_think_tag_from_deepseek_response(response_text: str) -> str:
    """
    Removes any content enclosed within the "<think>" tags from the response text,
    """
    think_start = response_text.find("<think>")
    think_end = response_text.find("</think>")
    if think_start != -1 and think_end != -1:
        return response_text[think_end + 8:].strip()
    return response_text

def _replace_role_tags_from_response(response_text: str) -> str:
    return (response_text.replace("<|assistant|>", "")
            .replace("<|user|>", "")
            .replace("<|system|>", ""))