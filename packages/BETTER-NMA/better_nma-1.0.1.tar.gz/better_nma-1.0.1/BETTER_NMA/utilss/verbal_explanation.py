import re

def get_verbal_explanation(explanation):
    
    result = []
    for i, word in enumerate(explanation):
        sanitized_word = re.sub(r'[0-9_]', '', word)
        if i == 0:
            result.append(f"**{sanitized_word}**")  # You can use bold markdown or just the word
        else:
            prev_sanitized = re.sub(r'[0-9_]', '', explanation[i - 1])
            if sanitized_word == prev_sanitized:
                continue
            result.append(f" is a part of **{sanitized_word}**")
    return ''.join(result)