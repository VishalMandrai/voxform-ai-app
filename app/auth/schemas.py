from pydantic import BaseModel, EmailStr, Field

from app.auth.models import Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class SignUpRequest(BaseModel):
    full_name: str
    org_name: str
    email: EmailStr
    password: str = Field(min_length=8)
    
    
class UserRead(BaseModel):
    id: str
    org_id: str
    role: Role

    model_config = {"from_attributes": False}


class UserFullDetails(BaseModel):
    id: str
    org_id: str
    org_name: str = Field(default="")
    email: EmailStr
    full_name: str
    role: Role

    model_config = {"from_attributes": False}


class InviteCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    role: Role


class InviteRead(BaseModel):
    token: str
    email: str
    full_name: str
    role: Role
    expires_at: str

    model_config = {"from_attributes": True}


class InviteTokenDetails(BaseModel):
    full_name: str
    org_name: str
    role: Role

    model_config = {"from_attributes": True}


class InviteAccept(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)


class InviteStats(BaseModel):
    total_invites: int
    org_id: str
