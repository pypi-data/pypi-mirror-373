from datetime import datetime
from pydantic import BaseModel

class ReleaseReaction(BaseModel):
    """Release reaction."""
    url: str
    total_count: int
    plus_one: int
    minus_one: int
    laugh: int
    confused: int
    heart: int
    hooray: int
    eyes: int
    rocket: int
    @classmethod
    def from_dict(cls, data: dict) -> ReleaseReaction:
        """From dict.

        Args:
            data: The data.

        Returns:
            The release reaction object.
        """

class ReleaseAssetUploader(BaseModel):
    """Release asset uploader."""
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool
    @classmethod
    def from_dict(cls, data: dict) -> ReleaseAssetUploader:
        """From dict.

        Args:
            data: The data.

        Returns:
            The release asset uploader object.
        """

class ReleaseAsset(BaseModel):
    """Release asset."""
    url: str
    browser_download_url: str
    id: int
    node_id: str
    name: str
    label: str | None
    state: str
    content_type: str
    size: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    uploader: ReleaseAssetUploader | None
    @classmethod
    def from_dict(cls, data: dict) -> ReleaseAsset:
        """From dict.

        Args:
            data: The data.

        Returns:
            The release asset object.
        """

class Release(BaseModel):
    """Release Model."""
    url: str
    html_url: str
    assets_url: str
    upload_url: str
    tarball_url: str | None
    zipball_url: str | None
    id: int
    node_id: str
    tag_name: str
    target_commitish: str
    name: str | None
    body: str | None
    draft: bool
    prerelease: bool
    created_at: datetime
    published_at: datetime | None
    author: ReleaseAssetUploader
    assets: list[ReleaseAsset]
    body_html: str | None
    body_text: str | None
    mentions_count: int | None
    discussion_url: str | None
    reactions: ReleaseReaction | None
    @classmethod
    def from_dict(cls, data: dict) -> Release:
        """From dict.

        Args:
            data: The data.

        Returns:
            The release object.
        """
