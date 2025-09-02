from dataclasses import dataclass
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class RequestTokenDTO(ABBaseDTO):
    grantType: str
    clientId: str
    clientSecret: str
    redirectUri: str
    exsitedUrl: str


@dataclass(kw_only=True)
class RefreshTokenDTO(ABBaseDTO):
    grantType: str = "refresh_token"
    refreshToken: str
    clientId: str
    clientSecret: str
    redirectUri: str


@dataclass(kw_only=True)
class TokenResponseDTO(ABBaseDTO):
    accessToken: str = None
    refreshToken: str = None
