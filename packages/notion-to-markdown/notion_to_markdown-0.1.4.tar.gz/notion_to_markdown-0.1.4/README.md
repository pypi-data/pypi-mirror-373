# Notion to Markdown (Python Version)

The original author of this work is [Wei Xiang](xiangweiqaz@gmail.com), please go to the [original repository](https://github.com/SwordAndTea/notion-to-md-py) for more details.

I have only audited the code for usage within my company and made minor changes for compatibility with my code.

---

This is the **Python implementation** of nodejs version of [notion-to-md](https://github.com/souvikinator/notion-to-md),
a tool that converts Notion pages into Markdown files.

## Installation

Install the package via pip:

```bash
pip install notion-to-markdown
```

## Usage

### Sync Version

```python
from notion_to_markdown import NotionToMarkdown
from notion_client import Client

notion = Client(auth="your-auth-token")
n2m = NotionToMarkdown(notion)
md_str = n2m.GetMarkdownString("page-id")

with open("output.md", "w") as f:
    f.write(md_str)
```

### Async Version

```python
from notion_client import AsyncClient
from notion_to_markdown import NotionToMarkdownAsync

notion = AsyncClient(auth="your-auth-token")
n2m = NotionToMarkdownAsync(notion)
md_str = n2m.GetMarkdownStringAsync("page-id")

with open("output.md", "w") as f:
    f.write(md_str)
```

Replace `your-auth-token` and `page-id` with the appropriate values from your Notion account.

## Authentication with Notion API

1. Create an integration in your Notion account and get the `API key`.
2. Share your database with the integration to allow access.
3. Retrieve your `Database ID` and `Page ID` from the Notion app.

## Requirements

- Python 3.7 or later
- Notion API key

## Limitations

- The tool relies on the Notion API, and features are limited to what the API supports.
- Embedding or downloading files other than images is not supported.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the functionality or fix bugs.

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the [MIT License](LICENSE).
