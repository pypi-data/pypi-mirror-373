def replace_placeholders(prompt_string, placeholder_dict):
    result = prompt_string

    for placeholder, replacement in placeholder_dict.items():
        result = result.replace(placeholder, str(replacement))

    return result
