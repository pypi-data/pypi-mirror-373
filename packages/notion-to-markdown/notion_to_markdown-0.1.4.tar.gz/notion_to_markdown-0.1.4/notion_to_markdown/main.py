import asyncio
from notion_client import Client
from .base import NotionToMarkdown, NotionToMarkdownAsync


class MarkdownProvider:
    def __init__(self, notion: Client):
        self.notion = notion

    def GetMarkdownString(self, page_id: str) -> str:
        n2m = NotionToMarkdown(self.notion)

        md_blocks = n2m.page_to_markdown(page_id)
        md_str = n2m.to_markdown_string(md_blocks).get("parent")

        return md_str

    def GetMarkdownStringAsync(self, page_id: str) -> str:
        n2m = NotionToMarkdownAsync(self.notion)

        md_blocks = asyncio.run(n2m.page_to_markdown(page_id))
        md_str = n2m.to_markdown_string(md_blocks).get("parent")

        return md_str
