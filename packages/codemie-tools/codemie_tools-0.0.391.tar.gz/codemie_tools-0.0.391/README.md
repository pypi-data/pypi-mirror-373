# Codemie Tools

## Overview

Codemie Tools is a comprehensive toolkit designed to simplify and streamline various development tasks. This toolkit provides a set of tools for access management, notification, code quality, data management, version control, project management, research, PDF processing, and image text extraction.

## Installation

To install Codemie Tools, use the following pip command:

```bash
pip install codemie-tools
```

```bash
poetry add codemie-tools
```
For local development, clone the repository and run:

```bash
make install
```

```bash
make build
```


## Usage

### Using `get_toolkit` Function

The `get_toolkit` function is used to get the toolkit instance with the provided configuration. Here is an example of how to use this function:

```python
from codemie_tools.<toolkit_module> import <ToolkitClass>

config = {
    'email': {
        'url': 'smtp.example.com',
        'smtp_username': 'your_username',
        'smtp_password': 'your_password'
    },
    'keycloak': {
        'base_url': 'http://localhost:8080',
        'realm': 'example-realm',
        'client_id': 'example-client-id',
        'client_secret': 'example-client-secret',
        'username': 'admin',
        'password': 'password'
    },
    'sonar_creds': {
        'url': 'http://sonarqube.example.com',
        'sonar_token': 'your_sonar_token',
        'sonar_project_name': 'example_project'
    },
    'elastic': {
        'hosts': ['http://localhost:9200'],
        'username': 'elastic',
        'password': 'password'
    },
    'jira': {
        'url': 'http://jira.example.com',
        'token': 'your_jira_token'
    },
    'confluence': {
        'url': 'http://confluence.example.com',
        'token': 'your_confluence_token'
    },
    'research_config': {
        'google_search_api_key': 'your_google_search_api_key',
        'google_search_cde_id': 'your_google_search_cde_id'
    },
    'root_directory': '/path/to/root_directory',
    'user_id': 'your_user_id',
    'azure_dalle_config': {
        'api_key': 'your_azure_dalle_api_key'
    }
}

toolkit = <ToolkitClass>.get_toolkit(config)
tools = toolkit.get_tools()
```

## Toolkits

### Access Management Toolkit

```python
from codemie_tools.access_management.toolkit import AccessManagementToolkit

config = {
    'keycloak': {
        'base_url': 'http://localhost:8080',
        'realm': 'example-realm',
        'client_id': 'example-client-id',
        'client_secret': 'example-client-secret'
    }
}

toolkit = AccessManagementToolkit.get_toolkit(config)
```

### Notification Toolkit

```python
from codemie_tools.notification.toolkit import NotificationToolkit

config = {
    'email': {
        'url': 'smtp.example.com',
        'smtp_username': 'your_username',
        'smtp_password': 'your_password'
    }
}

toolkit = NotificationToolkit.get_toolkit(config)
```

### Code Toolkit

```python
from codemie_tools.code.sonar.toolkit import SonarToolkit

config = {
    'url': 'http://sonarqube.example.com',
    'sonar_token': 'your_sonar_token',
    'sonar_project_name': 'example_project'
}

toolkit = SonarToolkit.get_toolkit(config)
```

### Data Management Toolkit

```python
from codemie_tools.data_management.toolkit import DataManagementToolkit

config = {
    'elastic': {
        'url': ['http://localhost:9200'],
        'api_key': 'elastic'
    }
}

toolkit = DataManagementToolkit.get_toolkit(config)
```

### Version Control Toolkit

```python
from codemie_tools.vcs.toolkit import VcsToolkit

config = {
    'base_url': 'http://gitlab.example.com',
    'access_token': 'your_gitlab_access_token'
}

toolkit = VcsToolkit.get_toolkit(config)
```

### Project Management Toolkit

```python
from codemie_tools.project_management.toolkit import ProjectManagementToolkit

config = {
    'jira': {
        'url': 'http://jira.example.com',
        'token': 'your_jira_token'
    },
    'confluence': {
        'url': 'http://confluence.example.com',
        'token': 'your_confluence_token'
    }
}

toolkit = ProjectManagementToolkit.get_toolkit(config)
```

### Research Toolkit

```python
from codemie_tools.research.toolkit import ResearchToolkit

config = {
    'google_search_api_key': 'your_google_search_api_key',
    'google_search_cde_id': 'your_google_search_cde_id'
}

toolkit = ResearchToolkit.get_toolkit(config)
```

### File System Toolkit

```python
from codemie_tools.data_management.file_system.toolkit import FileSystemToolkit

config = {
    'root_directory': '/path/to/root_directory',
    'user_id': 'your_user_id',
    'azure_dalle_config': {
        'api_key': 'your_azure_dalle_api_key',
        ...
    }
}

toolkit = FileSystemToolkit.get_toolkit(config)
```

### PDF Processing Toolkit

```python
from codemie_tools.pdf.toolkit import PDFToolkit
from langchain_openai import ChatOpenAI

# Create a vision-capable LLM for OCR capabilities
chat_model = ChatOpenAI(model_name="gpt-4-vision-preview", max_tokens=1000)

# PDF processing without OCR
pdf_toolkit = PDFToolkit.get_toolkit(
    configs={"pdf_bytes": pdf_content_bytes}
)

# PDF processing with OCR capabilities for extracting text from images
pdf_toolkit_with_ocr = PDFToolkit.get_toolkit(
    configs={"pdf_bytes": pdf_content_bytes},
    chat_model=chat_model
)

# Get tools for extracting text, analyzing structure, and performing OCR
tools = pdf_toolkit_with_ocr.get_tools()

# Example usage:
pdf_tool = tools[0]

# Get total pages
total_pages = pdf_tool.execute(pages=[], query="Total_Pages")

# Extract text from pages 1-3
text_content = pdf_tool.execute(pages=[1, 2, 3], query="Text")

# Extract text with metadata
text_with_metadata = pdf_tool.execute(pages=[1], query="Text_with_Metadata")

# Extract text from images using OCR
image_text = pdf_tool.execute(pages=[1, 2], query="OCR_Images")

# Use the dedicated OCR tool for more control
ocr_tool = tools[1]  # Available if a chat_model was provided
specific_image_text = ocr_tool.execute(
    pages=[1],  # Process page 1
    image_indices=[0, 1]  # Only process the first two images on the page
)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
