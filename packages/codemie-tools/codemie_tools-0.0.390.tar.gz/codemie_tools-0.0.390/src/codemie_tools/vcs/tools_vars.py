from codemie_tools.base.models import ToolMetadata

GITHUB_TOOL = ToolMetadata(
    name="github",
    description="""
        Advanced GitHub REST API client tool that provides comprehensive access to GitHub's public API endpoints.
        
        INPUT FORMAT:
        The tool accepts a `query` parameter containing a JSON with the following structure:
        {"query": 
            {
                "method": "GET|POST|PUT|DELETE|PATCH",
                "url": "https://api.github.com/...",
                "method_arguments": {object with request data},
                "custom_headers": {optional dictionary of additional HTTP headers}
            }
        }
        
        REQUIREMENTS:
        - `method`: HTTP method (GET, POST, PUT, DELETE, PATCH)
        - `url`: Must be a valid HTTPS URL starting with "https://api.github.com"
        - `method_arguments`: Object containing request parameters or body data
        - `custom_headers`: Optional dictionary for additional headers (authorization headers are protected)
        - The entire query must be valid JSON that passes json.loads() validation
        
        FEATURES:
        - Automatic Base64 file content decoding for GitHub file responses
        - Support for large files up to 70,000 tokens
        - Built-in authentication using configured GitHub Personal Access Token
        - Custom header support for specialized API calls
        - Comprehensive error handling and logging
        
        RESPONSE FORMAT:
        Returns the raw JSON response from GitHub API, with automatic Base64 decoding for file content.
        
        SECURITY:
        Authorization headers are automatically managed and cannot be overridden via custom_headers.
        
        EXAMPLES:
        Get user information:
        {"query": {"method": "GET", "url": "https://api.github.com/user", "method_arguments": {}}}
        
        Get repository file:
        {"query": {"method": "GET", "url": "https://api.github.com/repos/owner/repo/contents/path", "method_arguments": {}}}
        
        Create issue with custom headers:
        {"query":
            {
                "method": "POST", "url": "https://api.github.com/repos/owner/repo/issues", 
                "method_arguments": {"title": "Issue title", "body": "Issue body"},
                "custom_headers": {"X-GitHub-Media-Type": "github.v3+json"}
            }
        }
        """,
    label="Github",
    user_description="""
        Provides comprehensive access to the GitHub REST API with advanced features including automatic file content decoding and large file support. This tool enables the AI assistant to perform any GitHub operation available through the REST API.
        
        Key Capabilities:
        - Repository management (create, read, update, delete)
        - Issue and pull request operations
        - File content retrieval with automatic Base64 decoding
        - User and organization management
        - Webhook and deployment operations
        - Search across repositories, issues, and code
        - Support for large files up to 70,000 tokens
        
        Setup Requirements:
        1. GitHub Server URL (typically https://api.github.com)
        2. GitHub Personal Access Token with appropriate scopes
        
        Use this tool when you need direct access to GitHub's REST API endpoints that may not be covered by other specialized GitHub tools.
        """.strip(),
)

GITLAB_TOOL = ToolMetadata(
    name="gitlab",
    description="""
        Advanced GitLab REST API client tool that provides comprehensive access to GitLab's API endpoints.
        
        INPUT FORMAT:
        The tool accepts a `query` parameter containing a JSON with the following structure:
        {"query":
            {
                "method": "GET|POST|PUT|DELETE|PATCH",
                "url": "/api/v4/...",
                "method_arguments": {object with request data},
                "custom_headers": {optional dictionary of additional HTTP headers}
            }
        }
        
        REQUIREMENTS:
        - `method`: HTTP method (GET, POST, PUT, DELETE, PATCH)
        - `url`: Must start with "/api/v4/" (GitLab API v4 endpoint)
        - `method_arguments`: Object containing request parameters or body data
        - `custom_headers`: Optional dictionary for additional headers (authorization headers are protected)
        - The entire query must be valid JSON that passes json.loads() validation
        
        FEATURES:
        - Automatic request parameter handling (GET uses query params, others use request body)
        - Built-in authentication using configured GitLab Personal Access Token
        - Custom header support for specialized API calls
        - Detailed HTTP response logging with status codes and response bodies
        - Comprehensive error handling and validation
        
        RESPONSE FORMAT:
        Returns a formatted string containing:
        "HTTP: {method} {full_url} -> {status_code} {reason} {response_body}"
        
        This format provides complete visibility into the HTTP transaction including status and response data.
        
        SECURITY:
        Authorization headers are automatically managed and cannot be overridden via custom_headers.
        
        EXAMPLES:
        Get current user:
        {"query": {"method": "GET", "url": "/api/v4/user", "method_arguments": {}}}
        
        List project issues:
        {"query": {"method": "GET", "url": "/api/v4/projects/123/issues", "method_arguments": {"state": "opened"}}}
        
        Create merge request with custom headers:
        {"query":
            {
                "method": "POST", "url": "/api/v4/projects/123/merge_requests",
                "method_arguments": {"source_branch": "feature", "target_branch": "main", "title": "Feature"},
                "custom_headers": {"X-GitLab-Custom": "value"}
            }
        }
        """,
    label="Gitlab",
    user_description="""
        Provides comprehensive access to the GitLab REST API with detailed response formatting and flexible request handling. This tool enables the AI assistant to perform any GitLab operation available through the REST API.
        
        Key Capabilities:
        - Project and repository management
        - Issue and merge request operations
        - User and group management
        - Pipeline and job operations
        - File and commit operations
        - Wiki and snippet management
        - System administration (if token has admin privileges)
        - Detailed HTTP transaction visibility
        
        Setup Requirements:
        1. GitLab Server URL (e.g., https://gitlab.com or your self-hosted instance)
        2. GitLab Personal Access Token with appropriate scopes
        
        Response Features:
        - Complete HTTP transaction details including status codes
        - Full response body content for debugging and analysis
        - Automatic handling of different request types (GET vs POST/PUT/DELETE)
        
        Use this tool when you need direct access to GitLab's REST API endpoints that may not be covered by other specialized GitLab tools.
        """.strip(),
)