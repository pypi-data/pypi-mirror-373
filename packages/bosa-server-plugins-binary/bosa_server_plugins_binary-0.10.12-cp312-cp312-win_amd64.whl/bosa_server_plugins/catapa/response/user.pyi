from pydantic import BaseModel

class Employee(BaseModel):
    """Catapa employee response."""
    id: str
    name: str

class Role(BaseModel):
    """Catapa role response."""
    id: str
    name: str
    active: bool

class UserInfo(BaseModel):
    """Catapa user response."""
    id: str
    email: str
    username: str
    employee: Employee
    roles: list[Role]
