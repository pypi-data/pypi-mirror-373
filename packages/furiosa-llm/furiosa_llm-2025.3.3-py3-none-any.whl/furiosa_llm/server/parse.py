# type: ignore
# Adapted from vllm

from typing import List, Literal, Sequence, TypedDict, TypeVar, Union, overload

from furiosa_llm.server.utils import is_list_of

T = TypeVar("T")


class ParsedText(TypedDict):
    content: str
    is_tokens: Literal[False]


class ParsedTokens(TypedDict):
    content: List[int]
    is_tokens: Literal[True]


@overload
def parse_and_batch_prompt(prompt: Union[str, List[str]]) -> Sequence[ParsedText]: ...


@overload
def parse_and_batch_prompt(prompt: Union[List[int], List[List[int]]]) -> Sequence[ParsedTokens]: ...


def parse_and_batch_prompt(
    prompt: Union[str, List[str], List[int], List[List[int]]],
) -> Union[Sequence[ParsedText], Sequence[ParsedTokens]]:
    if isinstance(prompt, str):
        # case 1: a string
        return [ParsedText(content=prompt, is_tokens=False)]

    if isinstance(prompt, list):
        if len(prompt) == 0:
            raise ValueError("please provide at least one prompt")

        if is_list_of(prompt, str):
            # case 2: array of strings
            return [ParsedText(content=elem, is_tokens=False) for elem in prompt]
        if is_list_of(prompt, int):
            # case 3: array of tokens
            return [ParsedTokens(content=prompt, is_tokens=True)]
        if is_list_of(prompt, list):
            if len(prompt[0]) == 0:
                raise ValueError("please provide at least one prompt")

            if is_list_of(prompt[0], int):
                # case 4: array of token arrays
                return [ParsedTokens(content=elem, is_tokens=True) for elem in prompt]

    raise ValueError(
        "prompt must be a string, array of strings, " "array of tokens, or array of token arrays"
    )
