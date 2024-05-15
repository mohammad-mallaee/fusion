def truncate_middle(text, max_length):
    if len(text) > max_length:
        return text[: (max_length - 3) // 2] + "..." + text[-(max_length - 3) // 2 :]
    return text


def write_log(log_level, message):
    with open("./log.txt", "a") as file:
        file.write(f"[{log_level}]\n{message}\n")