from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel

class CreateDocumentRequest(BaseRequestModel):
    """Create document request model."""
    title: str
    folder_parent_id: str | None

class GetDocumentRequest(BaseRequestModel):
    """Get document request model."""
    document_id: str
    suggestions_view_mode: str | None

class BatchUpdateDocumentRequest(BaseRequestModel):
    """Batch update document request model."""
    document_id: str
    requests: list[dict]
    write_control: dict | None

class GetListDocumentsRequest(BaseRequestModel):
    """Get document list request model."""
    query: str | None
    page_size: int | None
    page_token: str | None
    order_by: str | None

class UpdateDocumentMarkdownRequest(BaseRequestModel):
    """Update document request model."""
    document_id: str
    markdown_content: str
