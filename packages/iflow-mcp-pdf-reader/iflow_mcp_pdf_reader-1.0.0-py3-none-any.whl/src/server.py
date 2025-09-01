"""
PDF Reader MCP Server
--------------------

A Model Context Protocol (MCP) server that provides tools for reading and extracting text from PDF files.
Supports both local files and URLs, with comprehensive error handling and standardized output format.

Author: Philip Van de Walker
Email: philip.vandewalker@gmail.com
Repo: https://github.com/trafflux/pdf-reader-mcp

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This module implements an MCP server with two main tools:
- read_local_pdf: Extracts text from local PDF files
- read_pdf_url: Extracts text from PDFs accessed via URLs

The server uses FastMCP for simplified tool registration and standardized error handling.
All text extraction is done using PyPDF2 with proper error handling for various edge cases.
"""

import os
import io
import logging
from typing import Dict, Any

import PyPDF2
import requests
from mcp.server.fastmcp import FastMCP

def get_logger(name: str):
    logger = logging.getLogger(name)
    return logger

logger = get_logger(__name__)

# Create server instance using FastMCP
mcp = FastMCP("pdf-reader")

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text content from a PDF file."""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

@mcp.tool()
async def read_local_pdf(path: str) -> Dict[str, Any]:
    """Read text content from a local PDF file."""
    try:
        with open(path, 'rb') as file:
            text = extract_text_from_pdf(file)
            return {
                "success": True,
                "data": {
                    "text": text
                }
            }
    except FileNotFoundError:
        logger.error(f"PDF file not found: {path}")
        return {
            "success": False,
            "error": f"PDF file not found: {path}"
        }
    except Exception as e:
        logger.error(str(e))
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def read_pdf_url(url: str) -> Dict[str, Any]:
    """Read text content from a PDF URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        pdf_file = io.BytesIO(response.content)
        text = extract_text_from_pdf(pdf_file)
        return {
            "success": True,
            "data": {
                "text": text
            }
        }
    except requests.RequestException as e:
        logger.error(f"Failed to fetch PDF from URL: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to fetch PDF from URL: {str(e)}"
        }
    except Exception as e:
        logger.error(str(e))
        return {
            "success": False,
            "error": str(e)
        }

def main() -> None:
    """Run the MCP server."""
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise

if __name__ == "__main__":
    main()
