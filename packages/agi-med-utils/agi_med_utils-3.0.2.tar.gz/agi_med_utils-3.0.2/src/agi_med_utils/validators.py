import os
import re
from pathlib import Path
from typing import Annotated, TypeVar
from pydantic import AfterValidator, SecretStr


Message = Annotated[str, AfterValidator(lambda msg: msg.replace("\\n", "\n"))]

PathLike = str | os.PathLike[str] | Path


def validate_existing_path(filepath: PathLike) -> PathLike:
    if not os.path.exists(filepath):
        raise ValueError(f"Path {filepath} is not exist")
    return filepath


def validate_existing_file(filepath: PathLike) -> PathLike:
    if not os.path.isfile(filepath):
        raise ValueError(f"Path {filepath} is not file")
    return filepath


def validate_existing_dir(filepath: PathLike) -> PathLike:
    if not os.path.isdir(filepath):
        raise ValueError(f"Path {filepath} is not file")
    return filepath


ExistingPath = Annotated[Path, AfterValidator(validate_existing_path)]
ExistingFile = Annotated[Path, AfterValidator(validate_existing_file)]
ExistingDir = Annotated[Path, AfterValidator(validate_existing_dir)]


def validate_not_empty(text: any) -> any:
    if not text:
        raise ValueError("Expected not empty")
    return text


StrNotEmpty = Annotated[str, AfterValidator(validate_not_empty)]
SecretStrNotEmpty = Annotated[SecretStr, AfterValidator(validate_not_empty)]


def validate_prompt(prompt: str, prompt_required_keys: set[str]) -> str:
    exist_keys: set[str] = set(re.findall(r"{(.*?)}", prompt))
    if missed_keys := prompt_required_keys.difference(exist_keys):
        raise ValueError(f"Missing required key in prompt: {missed_keys}")
    if extern_keys := exist_keys.difference(prompt_required_keys):
        raise ValueError(f"You have more keys for prompt: {extern_keys}")
    return prompt


def validate_keys(*keys):
    assert keys and all(isinstance(key, str) for key in keys)

    def validate(prompt: str) -> str:
        prompt_required_keys: set[str] = set(keys)
        exist_keys: set[str] = set(re.findall(r"{(.*?)}", prompt))
        if missed_keys := prompt_required_keys.difference(exist_keys):
            raise ValueError(f"Missing required key in prompt: {missed_keys}")
        if extern_keys := exist_keys.difference(prompt_required_keys):
            raise ValueError(f"You have more keys for prompt: {extern_keys}")
        return prompt

    return validate


K = TypeVar("K", bound=str)


class Prompt:
    # use inside pydantic models: prompt: Prompt['base_context']
    def __class_getitem__(cls, keys: K | tuple[K, ...]) -> type[str]:
        if isinstance(keys, tuple):
            keys_tuple = keys
        else:
            keys_tuple = (keys,)

        # Validate that all keys are strings
        if not all(isinstance(key, str) for key in keys_tuple):
            raise TypeError("All keys must be strings")

        return Annotated[str, AfterValidator(validate_keys(*keys_tuple))]
