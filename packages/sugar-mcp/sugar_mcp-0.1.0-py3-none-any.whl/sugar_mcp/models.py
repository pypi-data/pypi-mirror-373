from typing import Optional

from sugar.token import Token as S_Token
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Token(S_Token):
    wrapped_token_address: Optional[str] = None