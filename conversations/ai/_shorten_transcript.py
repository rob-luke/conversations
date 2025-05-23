# Description: Shorten transcript using GPT-4
from typing import List, Optional
from ._chatgpt import _num_tokens_from_messages, _content_to_message
from openai import OpenAI
from conversations.config import settings

client = OpenAI()


def _shorten_transcript(
    transcript: str,
    max_prompt_tokens: int = settings.max_prompt_tokens,
    shorten_iterations: int = 2,
) -> str:
    """Shorten a transcript using GPT-4.

    Parameters
    ----------
    transcript : str
        The transcript to shorten.
    max_prompt_tokens : int, default=settings.max_prompt_tokens
        The maximum number of tokens for text chunks and the target for the final transcript.
    shorten_iterations : int, default=2
        The number of iterations to use for shortening each chunk.

    Returns
    -------
    str
        The shortened transcript.
    """
    num_tokens = _num_tokens_from_messages(
        _content_to_message(transcript), model="gpt-4o"
    )
    print(
        f"The transcript has {num_tokens} tokens. The limit is {max_prompt_tokens} tokens."
    )
    if num_tokens <= max_prompt_tokens:
        print("Transcript is short enough, returning as is...")
        return transcript

    chunks = _chunk_transcript(transcript, max_prompt_tokens)

    summarized_chunks = []
    for chunk in chunks:
        print(f"Summarizing chunk of {len(chunk)} characters...")
        summarized_chunk = _summarise_chunk(
            chunk,
            model="gpt-4o",
            temperature=0.0,
            iterations=shorten_iterations,
        )
        summarized_chunks.append(summarized_chunk)

    shortened_transcript = "\n\n".join(summarized_chunks)  # type: ignore
    num_tokens_shortened = _num_tokens_from_messages(
        _content_to_message(shortened_transcript), model="gpt-4o"
    )
    print(f"The shortened transcript has {num_tokens_shortened} tokens.")

    if num_tokens_shortened > max_prompt_tokens:
        print("Shortened transcript is still too long, reducing chunk size...")
        return _shorten_transcript(transcript, max_prompt_tokens=max_prompt_tokens)

    return shortened_transcript


def _chunk_transcript(
    transcript: str, max_prompt_tokens: int = settings.max_prompt_tokens
) -> List[str]:
    """Split a transcript into chunks of a given token limit.

    Parameters
    ----------
    transcript : str
        The transcript to split.
    max_prompt_tokens : int, default=settings.max_prompt_tokens
        The maximum number of tokens allowed for a single chunk of text.

    Returns
    -------
    List[str]
        The list of chunks.
    """
    if (
        _num_tokens_from_messages(_content_to_message(transcript), model="gpt-4o")
        <= max_prompt_tokens
    ):
        print("Transcript is short enough, returning as is...")
        return [transcript]

    print("Transcript is too long, splitting in half...")
    transcript_chunks = []

    # Split the transcript into two halves
    half = len(transcript) // 2
    transcript_chunks.extend(_chunk_transcript(transcript[:half], max_prompt_tokens))
    transcript_chunks.extend(_chunk_transcript(transcript[half:], max_prompt_tokens))

    return transcript_chunks


def _summarise_chunk(
    chunk: str, model: str, temperature: float, iterations: int = 2
) -> Optional[str]:
    """Summarise a chunk of text using GPT-4.

    Parameters
    ----------
    chunk : str
        The chunk of text to summarise.
    model : str
        The model to use.
    temperature : float
        The temperature to use.
    iterations : int, default=2
        The number of iterations to use for shortening each chunk.

    Returns
    -------
    str
        The summarised chunk.
    """
    system_prompt = (
        "You are a meeting assistant. You have excellent language abilities. "
        "You will take a transcript and shorten the transcript without modifying the meaning of the conversation. "
        "Shorten the provided transcript by preserving all of the speakers' turns, key information, and specific guidance offered without redundancy. "
        "The resulting transcript should be clear, concise, and enable readers to understand the primary aspects of the conversation, "
        "including the important instructions or recommendations given with ease. "
        "Keep the format of the original transcript and do not skip any speaker turns, "
        "make sure every speaker turn is retained in the resulting transcript. "
        "Be sure to retain the interactions between speakers and personal information."
    )
    first_prompt = (
        f"Please shorten the following transcript to two-thirds of the original length. "
        f"You must retain all key information, action points, guidance, dates, numbers, "
        f"instructions, advice, names, personal information, and business information. \n\n {chunk}"
    )
    recursive_prompt = (
        "You shortened the transcript too much. "
        "Please reflect on the shortened transcript and determine if it removed any key advice/guidance/instruction "
        "or information from the original transcript. Please rewrite the shortened "
        "transcript to be longer and include the lost content. "
    )

    # First pass
    print("Computing first shortening pass...")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": first_prompt},
    ]
    response = client.chat.completions.create(
        model=model, temperature=temperature, messages=messages  # type: ignore
    )
    responses = [response.choices[0].message.content]

    if iterations > 1:
        for recursive_iter in range(iterations - 1):
            print(f"Computing recursive shortening pass {recursive_iter + 1}...")
            messages.append({"role": "assistant", "content": responses[-1]})  # type: ignore
            messages.append({"role": "user", "content": recursive_prompt})
            response = client.chat.completions.create(
                model=model, temperature=temperature, messages=messages  # type: ignore
            )
            responses.append(response.choices[0].message.content)

    return response.choices[0].message.content
