"""MinerU File转Markdown转换的FastMCP服务器实现。"""

import json
import re
import traceback
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional

import aiohttp
import uvicorn
from fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from pydantic import Field
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route


from . import config
from .api import MinerUClient
from .language import get_language_list

# Initialize FastMCP Server
mcp = FastMCP(
    name="MinerU File to Markdown Conversion",
    instructions="""
    A document conversion tool that converts documents into Markdown, JSON, etc. Supports various file formats including
    PDF, Word, PPT, and image formats (JPG, PNG, JPEG).

    System Tools:
    parse_documents: Parse documents (supports local files and URLs, reads content automatically)
    get_ocr_languages: Get list of supported OCR languages
    """,
)

# Global Client Instance
_client_instance: Optional[MinerUClient] = None


def create_starlette_app(mcp_server, *, debug: bool = False) -> Starlette:
    """Create Starlette app for SSE transport.

    Args:
        mcp_server: MCP server instance
        debug: Whether to enable debug mode

    Returns:
        Starlette: Configured Starlette app instance
    """
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        """Handle SSE connection request."""
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


def run_server(mode=None, port=8001, host="127.0.0.1"):
    """Run FastMCP Server.

    Args:
        mode: Run mode, supports stdio, sse, streamable-http
        port: Server port, default 8001, only valid in HTTP mode
        host: Server host, default 127.0.0.1, only valid in HTTP mode
    """
    # Ensure output directory exists
    config.ensure_output_dir(output_dir)

    # Check if API Key is set
    if not config.MINERU_API_KEY:
        config.logger.warning("WARNING: MINERU_API_KEY environment variable is not set.")
        config.logger.warning("Set it using: export MINERU_API_KEY=your_api_key")

    # Get MCP server instance
    mcp_server = mcp._mcp_server

    try:
        # Run server
        if mode == "sse":
            config.logger.info(f"Starting SSE server: {host}:{port}")
            starlette_app = create_starlette_app(mcp_server, debug=True)
            uvicorn.run(starlette_app, host=host, port=port)
        elif mode == "streamable-http":
            config.logger.info(f"Starting Streamable HTTP server: {host}:{port}")
            # Pass port argument in HTTP mode
            mcp.run(transport=mode, port=port, host=host)
        else:
            # Default stdio mode
            config.logger.info("Starting STDIO server")
            mcp.run(mode or "stdio")
    except Exception as e:
        config.logger.error(f"\n❌ Service exited with exception: {str(e)}")
        traceback.print_exc()
    finally:
        # Cleanup resources
        cleanup_resources()


def cleanup_resources():
    """Cleanup global resources."""
    global _client_instance
    if _client_instance is not None:
        try:
            # If client has close method, call it
            if hasattr(_client_instance, "close"):
                _client_instance.close()
        except Exception as e:
            config.logger.error(f"Error cleaning up client resources: {str(e)}")
        finally:
            _client_instance = None
    config.logger.info("Resource cleanup completed")


def get_client() -> MinerUClient:
    """Get singleton instance of MinerUClient. Initialize if not already initialized."""
    global _client_instance
    if _client_instance is None:
        _client_instance = MinerUClient()  # Initialization happens here
    return _client_instance


# Output directory for Markdown files
output_dir = config.DEFAULT_OUTPUT_DIR


def set_output_dir(dir_path: str):
    """Set output directory for converted files."""
    global output_dir
    output_dir = dir_path
    config.ensure_output_dir(output_dir)
    return output_dir


def parse_list_input(input_str: str) -> List[str]:
    """
    Parse string input that may contain multiple items separated by commas or newlines.
    Does NOT split on spaces to support filenames with spaces.

    Args:
        input_str: String possibly containing multiple items

    Returns:
        Liist of parsed items
    """
    if not input_str:
        return []

    # Split by comma or newline only
    items = re.split(r"[,\n]+", input_str)

    # Remove empty items and handle quoted items
    result = []
    for item in items:
        item = item.strip()
        # Remove quotes if present
        if (item.startswith('"') and item.endswith('"')) or (
            item.startswith("'") and item.endswith("'")
        ):
            item = item[1:-1]

        if item:
            result.append(item)

    return result


async def convert_file_url(
    url: str,
    enable_ocr: bool = False,
    language: str = "en",
    page_ranges: str | None = None,
) -> Dict[str, Any]:
    """
    Convert file from URL to Markdown format. Supports single or multiple URL processing.

    Returns:
        Success: {"status": "success", "result_path": "output directory path"}
        Failure: {"status": "error", "error": "error message"}
    """
    urls_to_process = None

    # Check if URL config is in dict or list of dicts format
    if isinstance(url, dict):
        # 单个URL配置字典
        urls_to_process = url
    elif isinstance(url, list) and len(url) > 0 and isinstance(url[0], dict):
        # List of URL config dicts
        urls_to_process = url
    elif isinstance(url, str):
        # Check if it is a JSON string of multiple URL configs
        if url.strip().startswith("[") and url.strip().endswith("]"):
            try:
                # Try to parse JSON string as URL config list
                url_configs = json.loads(url)
                if not isinstance(url_configs, list):
                    raise ValueError("JSON URL config must be a list")

                urls_to_process = url_configs
            except json.JSONDecodeError:
                # Not valid JSON, continue with string parsing
                pass

    if urls_to_process is None:
        # Parse normal URL list
        urls = parse_list_input(url)

        if not urls:
            raise ValueError("No valid URL provided")

        if len(urls) == 1:
            # Single URL processing
            urls_to_process = {"url": urls[0], "is_ocr": enable_ocr}
        else:
            # Multiple URLs, convert to URL config list
            urls_to_process = []
            for url_item in urls:
                urls_to_process.append(
                    {
                        "url": url_item,
                        "is_ocr": enable_ocr,
                    }
                )

    # Process URLs using submit_file_url_task
    try:
        result_path = await get_client().process_file_to_markdown(
            lambda urls, o: get_client().submit_file_url_task(
                urls,
                o,
                language=language,
                page_ranges=page_ranges,
            ),
            urls_to_process,
            enable_ocr,
            output_dir,
        )
        return {"status": "success", "result_path": result_path}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def convert_file_path(
    file_path: str,
    enable_ocr: bool = False,
    language: str = "en",
    page_ranges: str | None = None,
) -> Dict[str, Any]:
    """
    Convert local file to Markdown format. Supports single or multiple file batch processing.

    Returns:
        Success: {"status": "success", "result_path": "output directory path"}
        Failure: {"status": "error", "error": "error message"}
    """

    files_to_process = None

    # Check if file config is in dict or list of dicts format
    if isinstance(file_path, dict):
        # Single file config dict
        files_to_process = file_path
    elif (
        isinstance(file_path, list)
        and len(file_path) > 0
        and isinstance(file_path[0], dict)
    ):
        # List of file config dicts
        files_to_process = file_path
    elif isinstance(file_path, str):
        # Check if it is a JSON string of multiple file configs
        if file_path.strip().startswith("[") and file_path.strip().endswith("]"):
            try:
                # Try to parse JSON string as file config list
                file_configs = json.loads(file_path)
                if not isinstance(file_configs, list):
                    raise ValueError("JSON file config must be a list")

                files_to_process = file_configs
            except json.JSONDecodeError:
                # Not valid JSON, continue with string parsing
                pass

    if files_to_process is None:
        # Parse normal file path list
        file_paths = parse_list_input(file_path)

        if not file_paths:
            raise ValueError("No valid file path provided")

        if len(file_paths) == 1:
            # Process single file
            files_to_process = {
                "path": file_paths[0],
                "is_ocr": enable_ocr,
            }
        else:
            # Multiple file paths, convert to file config list
            files_to_process = []
            for i, path in enumerate(file_paths):
                files_to_process.append(
                    {
                        "path": path,
                        "is_ocr": enable_ocr,
                    }
                )

    # Process files using submit_file_task
    try:
        result_path = await get_client().process_file_to_markdown(
            lambda files, o: get_client().submit_file_task(
                files,
                o,
                language=language,
                page_ranges=page_ranges,
            ),
            files_to_process,
            enable_ocr,
            output_dir,
        )
        return {"status": "success", "result_path": result_path}
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "params": {
                "file_path": file_path,
                "enable_ocr": enable_ocr,
                "language": language,
            },
        }


async def local_parse_file(
    file_path: str,
    parse_method: str = "auto",
    language: str = "en",
) -> Dict[str, Any]:
    """
    Parse file using local or remote API based on environment settings.

    Returns:
        Success: {"status": "success", "result": result} or {"status": "success", "result_path": "output directory path"}
        Failure: {"status": "error", "error": "error message"}
    """
    file_path = Path(file_path)

    # Check if file exists
    if not file_path.exists():
        return {"status": "error", "error": f"File not found: {file_path}"}

    try:
        # Decide whether to use local API or remote API based on environment variables
        if config.USE_LOCAL_API:
            config.logger.debug(f"Using Local API: {config.LOCAL_MINERU_API_BASE}")
            return await _parse_file_local(
                file_path=str(file_path),
                parse_method=parse_method,
                language=language,
                output_dir=str(output_dir),
            )
        else:
            return {"status": "error", "error": "Remote API not configured"}
    except Exception as e:
        config.logger.error(f"Error parsing file: {str(e)}")
        return {"status": "error", "error": str(e)}


async def read_converted_file(
    file_path: str,
) -> Dict[str, Any]:
    """
    Read converted file content. Mainly supports Markdown and other text file formats.

    Returns:
        Success: {"status": "success", "content": "file content"}
        Failure: {"status": "error", "error": "error message"}
    """
    try:
        target_file = Path(file_path)
        parent_dir = target_file.parent
        suffix = target_file.suffix.lower()

        # Supported text file formats
        text_extensions = [".md", ".txt", ".json", ".html", ".tex", ".latex"]

        if suffix not in text_extensions:
            return {
                "status": "error",
                "error": f"Unsupported file type: {suffix}. Currently only supports: {', '.join(text_extensions)}",
            }

        if not target_file.exists():
            if not parent_dir.exists():
                return {"status": "error", "error": f"Directory {parent_dir} not found"}

            # Recursively search for files with same suffix in all subdirectories
            similar_files_paths = [
                str(f) for f in parent_dir.rglob(f"*{suffix}") if f.is_file()
            ]

            if similar_files_paths:
                if len(similar_files_paths) == 1:
                    # If only one file found, read and return content directly
                    alternative_file = similar_files_paths[0]
                    try:
                        with open(alternative_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        return {
                            "status": "success",
                            "content": content,
                            "message": f"File {target_file.name} not found, but found {Path(alternative_file).name}. Returned its content.",
                        }
                    except Exception as e:
                        return {
                            "status": "error",
                            "error": f"Error attempting to read alternative file: {str(e)}",
                        }
                else:
                    # If multiple files found, provide suggestion list
                    suggestion = f"Are you looking for: {', '.join(similar_files_paths)}?"
                    return {
                        "status": "error",
                        "error": f"File {target_file.name} not found. Found the following similar files in {parent_dir} and its subdirectories. {suggestion}",
                    }
            else:
                return {
                    "status": "error",
                    "error": f"File {target_file.name} not found, and no other {suffix} files found in {parent_dir} or its subdirectories.",
                }

        # Read in text mode
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "content": content}

    except Exception as e:
        config.logger.error(f"Error reading file: {str(e)}")
        return {"status": "error", "error": str(e)}


async def find_and_read_markdown_content(result_path: str) -> Dict[str, Any]:
    """
    Find and read Markdown file content in the given path.
    Searches all possible file locations and returns all valid content found.

    Args:
        result_path: Result directory path

    Returns:
        Dict[str, Any]: Dictionary containing all file contents or error messages
    """
    if not result_path:
        return {"status": "warning", "message": "未提供有效的结果路径"}

    base_path = Path(result_path)
    if not base_path.exists():
        return {"status": "warning", "message": f"结果路径不存在: {result_path}"}

    # Use set to store file paths to ensure uniqueness
    unique_files = set()

    # Add common filenames
    common_files = [
        base_path / "full.md",
        base_path / "full.txt",
        base_path / "output.md",
        base_path / "result.md",
    ]
    for f in common_files:
        if f.exists():
            unique_files.add(str(f))

    # Add common filenames in subdirectories
    for subdir in base_path.iterdir():
        if subdir.is_dir():
            subdir_files = [
                subdir / "full.md",
                subdir / "full.txt",
                subdir / "output.md",
                subdir / "result.md",
            ]
            for f in subdir_files:
                if f.exists():
                    unique_files.add(str(f))

    # Find all .md and .txt files
    for md_file in base_path.glob("**/*.md"):
        unique_files.add(str(md_file))
    for txt_file in base_path.glob("**/*.txt"):
        unique_files.add(str(txt_file))

    # Convert set back to list of Path objects
    possible_files = [Path(f) for f in unique_files]

    config.logger.debug(f"Found {len(possible_files)} possible files")

    # Collect all valid file contents found
    found_contents = []

    # Try to read each possible file
    for file_path in possible_files:
        if file_path.exists():
            result = await read_converted_file(str(file_path))
            if result["status"] == "success":
                config.logger.debug(f"Successfully read file content: {file_path}")
                found_contents.append(
                    {"file_path": str(file_path), "content": result["content"]}
                )

    # If file contents found
    if found_contents:
        config.logger.debug(f"Found {len(found_contents)} readable files in result directory")
        # If only one file found, keep backward compatible return format
        if len(found_contents) == 1:
            return {
                "status": "success",
                "content": found_contents[0]["content"],
                "file_path": found_contents[0]["file_path"],
            }
        # If multiple files found, return content list
        else:
            return {"status": "success", "contents": found_contents}

    # If no valid files found
    return {
        "status": "warning",
        "message": f"Could not find readable Markdown files in result directory: {result_path}",
    }


async def _process_conversion_result(
    result: Dict[str, Any], source: str, is_url: bool = False
) -> Dict[str, Any]:
    """
    Process conversion results and format output uniformly.

    Args:
        result: Result returned by conversion function
        source: Source file path or URL
        is_url: Whether it is a URL

    Returns:
        Formatted result dictionary
    """
    filename = source.split("/")[-1]
    if is_url and "?" in filename:
        filename = filename.split("?")[0]
    elif not is_url:
        filename = Path(source).name

    base_result = {
        "filename": filename,
        "source_url" if is_url else "source_path": source,
    }

    if result["status"] == "success":
        # Get result_path, could be string or dict
        result_path = result.get("result_path")

        # Log debug info
        config.logger.debug(f"Processing result_path type: {type(result_path)}")

        if result_path:
            # Case 1: result_path is dict and contains results field (batch processing result)
            if isinstance(result_path, dict) and "results" in result_path:
                config.logger.debug("Batch processing result format detected")

                # Find result matching current source file
                for item in result_path.get("results", []):
                    if item.get("filename") == filename or (
                        not is_url and Path(source).name == item.get("filename")
                    ):
                        # Return matching item status directly, whether success or error
                        if item.get("status") == "success" and "content" in item:
                            base_result.update(
                                {
                                    "status": "success",
                                    "content": item.get("content", ""),
                                }
                            )
                            # If extract_path exists, add it too
                            if "extract_path" in item:
                                base_result["extract_path"] = item["extract_path"]
                            return base_result
                        elif item.get("status") == "error":
                            # Process failed files, return error status directly
                            base_result.update(
                                {
                                    "status": "error",
                                    "error_message": item.get(
                                        "error_message", "File processing failed"
                                    ),
                                }
                            )
                            return base_result

                # If no matching result found, but extract_dir exists, try reading from there
                if "extract_dir" in result_path:
                    config.logger.debug(
                        f"Attempting to read from extract_dir: {result_path['extract_dir']}"
                    )
                    try:
                        content_result = await find_and_read_markdown_content(
                            result_path["extract_dir"]
                        )
                        if content_result.get("status") == "success":
                            base_result.update(
                                {
                                    "status": "success",
                                    "content": content_result.get("content", ""),
                                    "extract_path": result_path["extract_dir"],
                                }
                            )
                            return base_result
                    except Exception as e:
                        config.logger.error(f"Error reading content from extract_dir: {str(e)}")

                # If all above methods fail, return error
                base_result.update(
                    {
                        "status": "error",
                        "error_message": "Could not find matching content in batch processing results",
                    }
                )

            # Case 2: result_path is string (legacy format)
            elif isinstance(result_path, str):
                config.logger.debug(f"Processing legacy format result path: {result_path}")
                content_result = await find_and_read_markdown_content(result_path)
                if content_result.get("status") == "success":
                    base_result.update(
                        {
                            "status": "success",
                            "content": content_result.get("content", ""),
                            "extract_path": result_path,
                        }
                    )
                else:
                    base_result.update(
                        {
                            "status": "error",
                            "error_message": f"Could not read conversion result: {content_result.get('message', '')}",
                        }
                    )

            # Case 3: result_path is other type of dict (try to process)
            elif isinstance(result_path, dict):
                config.logger.debug(f"Processing other dict format: {result_path}")
                # Try to extract possible paths from dict
                extract_path = (
                    result_path.get("extract_dir")
                    or result_path.get("path")
                    or result_path.get("dir")
                )
                if extract_path and isinstance(extract_path, str):
                    try:
                        content_result = await find_and_read_markdown_content(
                            extract_path
                        )
                        if content_result.get("status") == "success":
                            base_result.update(
                                {
                                    "status": "success",
                                    "content": content_result.get("content", ""),
                                    "extract_path": extract_path,
                                }
                            )
                            return base_result
                    except Exception as e:
                        config.logger.error(f"Error reading content from extract_path: {str(e)}")

                # If no valid path found, return error
                base_result.update(
                    {"status": "error", "error_message": "Unrecognized conversion result format"}
                )
            else:
                # Case 4: result_path is other type (error)
                base_result.update(
                    {
                        "status": "error",
                        "error_message": f"Unrecognized result_path type: {type(result_path)}",
                    }
                )
        else:
            base_result.update(
                {"status": "error", "error_message": "Conversion successful but returned no result path"}
            )
    else:
        base_result.update(
            {"status": "error", "error_message": result.get("error", "Unknown error")}
        )

    return base_result


@mcp.tool()
async def parse_documents(
    file_sources: Annotated[
        str,
        Field(
            description="""File path or URL, supporting the following formats:
            - Single path or URL: "/path/to/file.pdf" or "https://example.com/document.pdf"
            - Multiple paths or URLs (comma separated): "/path/to/file1.pdf, /path/to/file2.pdf" or
              "https://example.com/doc1.pdf, https://example.com/doc2.pdf"
            - Mixed paths and URLs: "/path/to/file.pdf, https://example.com/document.pdf"
            (Supports pdf, ppt, pptx, doc, docx, and image formats jpg, jpeg, png)"""
        ),
    ],
    # General parameters
    enable_ocr: Annotated[bool, Field(description="Enable OCR recognition, default False")] = False,
    language: Annotated[
        str, Field(description='Document language, default "en" (English), optional "ch" (Chinese), etc.')
    ] = "en",
    # Remote API parameters
    page_ranges: Annotated[
        str | None,
        Field(
            description='Specify page ranges as comma-separated string. E.g., "2,4-6": pages 2, 4 to 6; "2--2": page 2 to second to last. (Remote API only), default None'
        ),
    ] = None,
) -> Dict[str, Any]:
    """
    Unified interface to convert files to Markdown format. Supports local files and URLs, automatically selects method based on USE_LOCAL_API configuration.

    When USE_LOCAL_API=true:
    - Filters out http/https URL paths
    - Uses local API to parse local files

    When USE_LOCAL_API=false:
    - Uses convert_file_url for http/https paths
    - Uses convert_file_path for other paths

    After processing, automatically attempts to read the converted file content and return it.

    Returns:
        Success: {"status": "success", "content": "file content"} or {"status": "success", "results": [result list]}
        Failure: {"status": "error", "error": "error message"}
    """
    # Parse path list
    sources = parse_list_input(file_sources)
    if not sources:
        return {"status": "error", "error": "No valid file path or URL provided"}

    config.logger.debug(f"Unique file paths: {sources}")

    # Log deduplication info
    original_count = len(parse_list_input(file_sources))
    unique_count = len(sources)
    if original_count > unique_count:
        config.logger.debug(
            f"Duplicate paths detected, automatically deduplicated: {original_count} -> {unique_count}"
        )

    # Classify paths
    url_paths = []
    file_paths = []

    for source in sources:
        if source.lower().startswith(("http://", "https://")):
            url_paths.append(source)
        else:
            file_paths.append(source)

    results = []

    # Decide processing method based on USE_LOCAL_API
    if config.USE_LOCAL_API:
        # 在本地API模式下，只处理本地文件路径
        if not file_paths:
            return {
                "status": "warning",
                "message": "Cannot process URL in local API mode, and no valid local file path provided",
            }

        config.logger.info(f"Processing {len(file_paths)} files using local API")

        # Process local files one by one
        for path in file_paths:
            try:
                # Skip non-existent files
                if not Path(path).exists():
                    results.append(
                        {
                            "filename": Path(path).name,
                            "source_path": path,
                            "status": "error",
                            "error_message": f"File not found: {path}",
                        }
                    )
                    continue

                result = await local_parse_file(
                    file_path=path,
                    parse_method=(
                        "ocr" if enable_ocr else "txt"
                    ),  # If OCR enabled, use ocr, otherwise use txt
                    language=language,
                )

                # Add filename info
                result_with_filename = {
                    "filename": Path(path).name,
                    "source_path": path,
                    **result,
                }
                results.append(result_with_filename)

            except Exception as e:
                # Handle file processing exception, log error but continue with next file
                config.logger.error(f"Error processing file {path}: {str(e)}")
                results.append(
                    {
                        "filename": Path(path).name,
                        "source_path": path,
                        "status": "error",
                        "error_message": f"Exception processing file: {str(e)}",
                    }
                )

    else:
        # In remote API mode, process URL and local file paths separately
        if url_paths:
            config.logger.info(f"Processing {len(url_paths)} URLs using remote API")

            try:
                # Call convert_file_url to process URLs
                url_result = await convert_file_url(
                    url=",".join(url_paths),
                    enable_ocr=enable_ocr,
                    language=language,
                    page_ranges=page_ranges,
                )

                if url_result["status"] == "success":
                    # Generate corresponding results for each URL
                    for url in url_paths:
                        result_item = await _process_conversion_result(
                            url_result, url, is_url=True
                        )
                        results.append(result_item)
                else:
                    # Conversion failed, add error result for all URLs
                    for url in url_paths:
                        results.append(
                            {
                                "filename": url.split("/")[-1].split("?")[0],
                                "source_url": url,
                                "status": "error",
                                "error_message": url_result.get("error", "URL processing failed"),
                            }
                        )

            except Exception as e:
                config.logger.error(f"Error processing URL: {str(e)}")
                for url in url_paths:
                    results.append(
                        {
                            "filename": url.split("/")[-1].split("?")[0],
                            "source_url": url,
                            "status": "error",
                            "error_message": f"Exception processing URL: {str(e)}",
                        }
                    )

        if file_paths:
            config.logger.info(f"Processing {len(file_paths)} local files using remote API")

            # Filter existing files
            existing_files = []
            for file_path in file_paths:
                if not Path(file_path).exists():
                    results.append(
                        {
                            "filename": Path(file_path).name,
                            "source_path": file_path,
                            "status": "error",
                            "error_message": f"File not found: {file_path}",
                        }
                    )
                else:
                    existing_files.append(file_path)

            if existing_files:
                try:
                    # Call convert_file_path to process local files
                    file_result = await convert_file_path(
                        file_path=",".join(existing_files),
                        enable_ocr=enable_ocr,
                        language=language,
                        page_ranges=page_ranges,
                    )

                    config.logger.debug(f"file_result: {file_result}")

                    if file_result["status"] == "success":
                        # Generate corresponding results for each file
                        for file_path in existing_files:
                            result_item = await _process_conversion_result(
                                file_result, file_path, is_url=False
                            )
                            results.append(result_item)
                    else:
                        # Conversion failed, add error result for all files
                        for file_path in existing_files:
                            results.append(
                                {
                                    "filename": Path(file_path).name,
                                    "source_path": file_path,
                                    "status": "error",
                                    "error_message": file_result.get(
                                        "error", "File processing failed"
                                    ),
                                }
                            )

                except Exception as e:
                    config.logger.error(f"Error processing local file: {str(e)}")
                    for file_path in existing_files:
                        results.append(
                            {
                                "filename": Path(file_path).name,
                                "source_path": file_path,
                                "status": "error",
                                "error_message": f"Exception processing file: {str(e)}",
                            }
                        )

    # Handle empty results
    if not results:
        return {"status": "error", "error": "No files processed"}

    # Calculate success and failure statistics
    success_count = len([r for r in results if r.get("status") == "success"])
    error_count = len([r for r in results if r.get("status") == "error"])
    total_count = len(results)

    # Use single result format if only one file (backward compatibility)
    if len(results) == 1:
        result = results[0].copy()
        # Remove added fields for backward compatibility
        if "filename" in result:
            del result["filename"]
        if "source_path" in result:
            del result["source_path"]
        if "source_url" in result:
            del result["source_url"]
        return result

    # Return detailed list for multiple files
    # Determine overall status based on counts
    overall_status = "success"
    if success_count == 0:
        # All files failed
        overall_status = "error"
    elif error_count > 0:
        # Partial failure
        overall_status = "partial_success"

    return {
        "status": overall_status,
        "results": results,
        "summary": {
            "total_files": total_count,
            "success_count": success_count,
            "error_count": error_count,
        },
    }


@mcp.tool()
async def get_ocr_languages() -> Dict[str, Any]:
    """
    Get list of supported OCR languages.

    Returns:
        Dict[str, Any]: Dictionary containing list of all supported OCR languages
    """
    try:
        # Get language list from language module
        languages = get_language_list()
        return {"status": "success", "languages": languages}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def _parse_file_local(
    file_path: str,
    parse_method: str = "auto",
    language: str = "en",
    output_dir: str = None,
) -> Dict[str, Any]:
    """
    Parse file using local API.

    Args:
        file_path: Path of the file to parse
        parse_method: Parsing method
        output_dir: Output directory

    Returns:
        Dict[str, Any]: Dictionary containing parsing results
    """
    # API URL path
    api_url = f"{config.LOCAL_MINERU_API_BASE}/file_parse"

    # Use Path object to ensure file path is correct
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read binary file data
    with open(file_path_obj, "rb") as f:
        file_data = f.read()

    # Prepare form data for file upload
    file_type = file_path_obj.suffix.lower()
    form_data = aiohttp.FormData()
    # Note: API expects field name "files", not "file"
    form_data.add_field(
        "files", file_data, filename=file_path_obj.name, content_type=file_type
    )
    form_data.add_field("parse_method", parse_method)
    
    # Add language list
    form_data.add_field("lang_list", language)
    
    # Add output directory
    if output_dir:
         form_data.add_field("output_dir", str(output_dir))


    config.logger.debug(f"Sending local API request to: {api_url}")
    config.logger.debug(f"Uploading file: {file_path_obj.name} (Size: {len(file_data)} bytes)")

    # Send request
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, data=form_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    config.logger.error(
                        f"API returned error status: {response.status}, Error: {error_text}"
                    )
                    raise RuntimeError(f"API returned error: {response.status}, {error_text}")

                result = await response.json()

                config.logger.debug(f"Local API response: {result}")

                # Process response
                if "error" in result:
                    return {"status": "error", "error": result["error"]}

                return {"status": "success", "result": result}
    except aiohttp.ClientError as e:
        error_msg = f"Error communicating with local API: {str(e)}"
        config.logger.error(error_msg)
        raise RuntimeError(error_msg)
