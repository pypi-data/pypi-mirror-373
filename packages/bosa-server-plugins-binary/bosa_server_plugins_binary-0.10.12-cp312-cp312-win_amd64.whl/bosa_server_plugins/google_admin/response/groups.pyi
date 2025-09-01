from pydantic import BaseModel

class Group(BaseModel):
    """Google Admin SDK Group Response."""
    id: str
    email: str
    name: str
    description: str
    admin_created: bool
    direct_members_count: str
    kind: str
    etag: str
    aliases: list[str]
    non_editable_aliases: list[str]
