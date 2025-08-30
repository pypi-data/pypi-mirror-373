from typing import List

from pydantic import BaseModel


class DeleteUserV0(BaseModel):
    password: str


class LogoutAppsV0(BaseModel):
    app_names: List[str]


class ValidateEmailVerificationCodeV0(BaseModel):
    verification_code: str


class SendResetPasswordEmailV0(BaseModel):
    username: str
