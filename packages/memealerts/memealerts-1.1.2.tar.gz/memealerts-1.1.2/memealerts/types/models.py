from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field, NonNegativeFloat, NonNegativeInt, field_validator
from pydantic_core.core_schema import ValidationInfo

from memealerts.types.user_id import UserID


class Supporter(BaseModel):
    _id: UserID
    balance: NonNegativeInt
    welcome_bonus_earned: bool = Field(default=False, alias="welcomeBonusEarned")
    newbie_action_used: bool = Field(default=False, alias="newbieActionUsed")
    spent: NonNegativeInt
    purchased: (
        NonNegativeInt | NonNegativeFloat
    )  # Suddenly: Input should be a valid integer, got a number with a fractional part [type=int_from_float, input_value=11217.1, input_type=float]
    joined: datetime
    last_support: datetime | None = Field(None, alias="lastSupport")
    supporter_name: str = Field(..., alias="supporterName")
    supporter_avatar: AnyHttpUrl | None = Field(None, alias="supporterAvatar")
    supporter_link: str | None = Field(None, alias="supporterLink")
    supporter_id: UserID = Field(..., alias="supporterId")
    mutes: list
    muted_by_streamer: bool = Field(..., alias="mutedByStreamer")

    @field_validator("supporter_avatar", mode="before")
    def put_full_avatar_link(cls, v: AnyHttpUrl | str, _: ValidationInfo) -> AnyHttpUrl | str | None:  # noqa: N805
        if isinstance(v, str) and v.startswith("media/"):
            return AnyHttpUrl("https://memealerts.com/" + v)
        if isinstance(v, str) and v == "":
            return None
        return v


class SupportersList(BaseModel):
    data: list[Supporter]
    total: NonNegativeInt


class User(BaseModel):
    """User in /user/find"""

    _id: UserID
    id: UserID
    name: str
    username: str
    avatar: AnyHttpUrl
    created_at: datetime = Field(..., alias="createdAt")
    channel: dict  # TODO: describe schema
    last_visit: datetime = Field(..., alias="lastVisit")
    avatar_assets: dict = Field(..., alias="avatarAssets")  # TODO: Describe schema
    voice: dict  # TODO: Describe schema

    @field_validator("avatar", mode="before")
    def put_full_avatar_link(cls, v: AnyHttpUrl | str, _: ValidationInfo) -> AnyHttpUrl | str:  # noqa: N805
        if isinstance(v, str) and v.startswith("media/"):
            return AnyHttpUrl("https://memealerts.com/" + v)
        return v


class Balance(BaseModel):
    balance: int
    newbie_action_used: bool = Field(..., alias="newbieActionUsed")
    welcome_bonus_earned: bool = Field(..., alias="welcomeBonusEarned")
