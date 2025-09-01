# DOCX Edit Server

A Model Context Protocol (MCP) server that provides DOCX document editing capabilities for Large Language Models (LLMs).

## Features

- **Content Insertion**: Insert headings, paragraphs, images, and tables at specified placeholder positions
- **Document Reading**: Read and extract document outline structure
- **Rich Formatting**: Support for styled headings, formatted text with bold/italic, and image captions
- **Table Support**: Create formatted tables with headers and data rows
- **Image Processing**: Automatic image conversion to PNG format with customizable width
- **Document Comparison**: Track changes between document versions

## Tools Provided

- `docx_insert`: Insert content (headings, paragraphs, images, tables) at specified placeholder positions in DOCX files
- `read_docx`: Read and extract the outline structure of DOCX documents

## Content Types Supported

### Headings
- Levels 1-4 supported
- Customizable font size
- Automatic styling with SimHei font

### Paragraphs
- Support for markdown-style formatting (*italic*, **bold**)
- Automatic text formatting and indentation

### Images
- Automatic PNG conversion
- Customizable width (in inches)
- Optional captions with center alignment

### Tables
- Header row support
- Automatic grid styling
- Center-aligned headers, left-aligned data
- Optional table captions

## Configuration Options

- `--workspace-path`: Set the workspace directory (default: ./workspace)

## Server Configuration

To use this server with MCP clients, add the following configuration to your MCP settings:

For development or when using `uv`:

```json
{
  "mcpServers": {
    "docx-edit-server": {
      "command": "uv",
      "args": ["--directory", "directory_of_docx-edit-server", "run", "docx-edit-server", "--workspace-path", "/path/to/your/workspace"],
      "env": {}
    }
  }
}
```

## Usage Examples

### Inserting Content
```python
# Insert a heading and paragraph at placeholder "{{SECTION_1}}"
await docx_insert(
    docx_path="/path/to/document.docx",
    placeholder="{{SECTION_1}}",
    contents=[
        {
            "type": "heading",
            "text": "Introduction",
            "level": 1,
            "size": 16
        },
        {
            "type": "paragraph", 
            "text": "This is a **bold** paragraph with *italic* text."
        }
    ]
)
```

### Reading Document Structure
```python
# Read document outline
outline = await read_docx("/path/to/document.docx")
```

## Safety Features

- **File Validation**: Checks for file existence before operations
- **Content Validation**: Validates content structure and types
- **Error Handling**: Comprehensive error reporting with detailed messages
- **Document Backup**: Tracks changes with before/after comparison

## License

MIT License - see LICENSE file for details.