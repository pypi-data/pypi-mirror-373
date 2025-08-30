from typing import NamedTuple

def main() -> None: ...

class PasswordRequirements(NamedTuple):
    length: int = 16
    decimal: int = 1
    specials: int = 1
    first_is_letter: bool = True
    allow_repeats: bool = False

    def validate(self) -> "PasswordRequirements": ...

def generate_password(config: PasswordRequirements) -> str: ...

#: The possible special characters used when generating a password.
SPECIAL_CHARACTERS: list[str] = ...

#: The possible decimal integer characters used when generating a password.
DECIMAL: list[str] = ...

#: The possible lowercase (alphabetical) letters used when generating a password.
LOWERCASE: list[str] = ...

#: The possible uppercase (alphabetical) letters used when generating a password.
UPPERCASE: list[str] = ...
