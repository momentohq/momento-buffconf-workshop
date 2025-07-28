import tiktoken


def truncate_text(text: str, max_tokens: int = 8192) -> str:
    encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    tokens = encoding.encode(text)
    truncated_tokens = tokens[:max_tokens]
    truncated_text = encoding.decode(truncated_tokens)

    return truncated_text
