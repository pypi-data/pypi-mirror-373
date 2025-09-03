#!/usr/bin/env python3

"""
Web to Markdown Converter

This script fetches a webpage from a given URL, extracts its main textual content
by removing navigational and non-essential elements, converts the cleaned HTML to
Markdown format, and saves the result to a specified output file.

Usage:
    fetch_to_md.py -u "https://aider.chat/docs/usage/commands.html" -o tmp/aidercommands.md
    
    or 
    
    fetch_to_md.py --url "https://aider.chat/docs/usage/commands.html" \
        --output-file tmp/aidercommands.md \
        --log-level DEBUG \
        --timeout 20

Requirements:
    pip install requests beautifulsoup4 html2text colorama
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional

import requests
from bs4 import BeautifulSoup, Comment
import html2text
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages."""
    
    # Color mapping for different log levels
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }
    
    def format(self, record):
        # Get the original formatted message
        message = super().format(record)
        
        # Add color based on log level
        color = self.COLORS.get(record.levelname, '')
        if color:
            # Color the entire message
            message = f"{color}{message}{Style.RESET_ALL}"
        
        return message


def print_banner():
    """Print a colorful banner for the application."""
    banner = f"""
{Fore.CYAN + Style.BRIGHT}╔════════════════════════════════════════════════════════════════╗
║                    {Fore.YELLOW}Web to Markdown Converter{Fore.CYAN}                    ║
║                                                                ║
║  {Fore.WHITE}Converts web pages to clean, readable Markdown format{Fore.CYAN}      ║
║  {Fore.WHITE}Removes ads, navigation, and non-essential content{Fore.CYAN}         ║
╚════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_progress(message: str, step: int, total_steps: int):
    """Print a progress message with visual indicators."""
    percentage = (step / total_steps) * 100
    bar_length = 30
    filled_length = int(bar_length * step // total_steps)
    
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    print(f"\r{Fore.BLUE}[{bar}] {percentage:3.0f}% {Fore.WHITE}{message}{Style.RESET_ALL}", end='', flush=True)
    
    if step == total_steps:
        print()  # New line when complete


def print_success(message: str):
    """Print a success message with green checkmark."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print an error message with red X."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print a warning message with yellow triangle."""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print an info message with blue info icon."""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration with colors."""
    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with colored formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create colored formatter
    formatter = ColoredFormatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


def validate_url(url: str) -> bool:
    """Validate if the provided URL is properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def fetch_webpage(url: str, timeout: int = 30) -> Optional[requests.Response]:
    """
    Fetch webpage content from the given URL.
    
    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        requests.Response object or None if failed
    """
    logger = logging.getLogger(__name__)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print_info(f"Fetching content from: {Fore.CYAN}{url}{Style.RESET_ALL}")
        logger.debug(f"Fetching URL: {url}")
        
        # Show a simple spinner while fetching
        print(f"{Fore.YELLOW}⏳ Downloading...{Style.RESET_ALL}", end='', flush=True)
        
        response = requests.get(
            url, 
            headers=headers, 
            timeout=timeout,
            verify=True  # SSL verification enabled
        )
        
        # Clear the spinner line
        print(f"\r{' ' * 20}\r", end='')
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Show content size in a human-readable format
        content_size = len(response.content)
        if content_size < 1024:
            size_str = f"{content_size} bytes"
        elif content_size < 1024 * 1024:
            size_str = f"{content_size / 1024:.1f} KB"
        else:
            size_str = f"{content_size / (1024 * 1024):.1f} MB"
        
        print_success(f"Downloaded {Fore.CYAN}{size_str}{Fore.GREEN} successfully")
        logger.debug(f"Successfully fetched {len(response.content)} bytes from {url}")
        return response
        
    except requests.exceptions.SSLError as e:
        print_error(f"SSL certificate error: {str(e)}")
        logger.error(f"SSL certificate error for URL: {url} (error: {e})")
        return None
    except requests.exceptions.Timeout as e:
        print_error(f"Request timeout after {timeout} seconds")
        logger.error(f"Request timeout for URL: {url} (error: {e})")
        return None
    except requests.exceptions.ConnectionError as e:
        print_error(f"Connection failed: {str(e)}")
        logger.error(f"Connection error for URL: {url} (error: {e})")
        return None
    except requests.exceptions.HTTPError as e:
        print_error(f"HTTP error: {e.response.status_code} - {e.response.reason}")
        logger.error(f"HTTP error for URL: {url} (error: {e})")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        logger.error(f"Failed to fetch URL: {url} (error: {e})")
        return None


def clean_html_content(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Remove non-essential elements from HTML content.
    
    Args:
        soup: BeautifulSoup object containing the HTML
        
    Returns:
        Cleaned BeautifulSoup object
    """
    logger = logging.getLogger(__name__)
    
    print_info("Cleaning HTML content...")
    
    # Elements to remove completely
    elements_to_remove = [
        'nav', 'header', 'footer', 'aside', 'script', 'style', 'noscript',
        'iframe', 'embed', 'object', 'applet', 'form', 'input', 'button',
        'select', 'textarea', 'fieldset', 'legend'
    ]
    
    removed_count = 0
    
    # Remove elements by tag name
    for tag_name in elements_to_remove:
        elements = soup.find_all(tag_name)
        for element in elements:
            logger.debug(f"Removing element: {tag_name}")
            element.decompose()
            removed_count += 1
    
    # Remove elements by class/id patterns (common ad and navigation patterns)
    patterns_to_remove = [
        {'class_': lambda x: x and any(pattern in ' '.join(x).lower() for pattern in [
            'nav', 'menu', 'sidebar', 'ad', 'advertisement', 'banner', 'popup',
            'modal', 'footer', 'header', 'social', 'share', 'comment', 'widget'
        ])},
        {'id': lambda x: x and any(pattern in x.lower() for pattern in [
            'nav', 'menu', 'sidebar', 'ad', 'advertisement', 'banner', 'popup',
            'modal', 'footer', 'header', 'social', 'share', 'comment', 'widget'
        ])}
    ]
    
    for pattern in patterns_to_remove:
        elements = soup.find_all(attrs=pattern)
        for element in elements:
            # Skip elements that don't have attributes (like text nodes)
            if not hasattr(element, 'attrs') or element.attrs is None:
                continue
            
            try:
                attr_key = list(pattern.keys())[0]
                attr_value = element.get(attr_key, '')
                element_desc = f"{element.name} with {attr_key}='{attr_value}'"
                logger.debug(f"Removing pattern-matched element: {element_desc}")
                element.decompose()
                removed_count += 1
            except Exception as e:
                logger.warning(f"Skipped element during pattern removal: {e}")
                continue
    
    # Remove HTML comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        logger.debug("Removing HTML comment")
        comment.extract()
        removed_count += 1
    
    # Remove empty elements that might be left behind
    empty_removed = 0
    for element in soup.find_all():
        if not element.get_text(strip=True) and not element.find_all(['img', 'br', 'hr']):
            logger.debug(f"Removing empty element: {element.name}")
            element.decompose()
            empty_removed += 1
    
    removed_count += empty_removed
    
    if removed_count > 0:
        print_success(f"Removed {Fore.CYAN}{removed_count}{Fore.GREEN} non-essential elements")
    else:
        print_info("No non-essential elements found to remove")
    
    return soup


def extract_main_content(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Extract the main content from the cleaned HTML.
    
    Args:
        soup: Cleaned BeautifulSoup object
        
    Returns:
        BeautifulSoup object containing main content
    """
    logger = logging.getLogger(__name__)
    
    print_info("Extracting main content...")
    
    # Try to find main content using semantic HTML5 tags
    main_content_selectors = [
        ('main', 'Main content tag'),
        ('article', 'Article tag'),
        ('[role="main"]', 'Main role attribute'),
        ('.main-content', 'Main content class'),
        ('.content', 'Content class'),
        ('.post-content', 'Post content class'),
        ('.entry-content', 'Entry content class'),
        ('#main-content', 'Main content ID'),
        ('#content', 'Content ID')
    ]
    
    for selector, description in main_content_selectors:
        main_element = soup.select_one(selector)
        if main_element and main_element.get_text(strip=True):
            print_success(f"Found main content using: {Fore.CYAN}{description}{Style.RESET_ALL}")
            logger.debug(f"Found main content using selector: {selector}")
            # Create a new soup with just the main content
            new_soup = BeautifulSoup('<div></div>', 'html.parser')
            new_soup.div.replace_with(main_element)
            return new_soup
    
    # If no main content found, use the body or the entire document
    body = soup.find('body')
    if body:
        print_warning("No specific main content found, using entire body")
        logger.debug("Using body content as main content")
        return body
    else:
        print_warning("No body tag found, using entire document")
        logger.warning("No body tag found, using entire document")
        return soup


def convert_to_markdown(html_content: str, base_url: str = "") -> str:
    """
    Convert HTML content to Markdown format.
    
    Args:
        html_content: HTML content as string
        base_url: Base URL for relative links
        
    Returns:
        Markdown formatted string
    """
    logger = logging.getLogger(__name__)
    
    print_info("Converting to Markdown format...")
    
    try:
        # Configure html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        h.body_width = 0  # Don't wrap lines
        h.protect_links = True
        h.wrap_links = False
        
        # Set base URL for relative links
        if base_url:
            h.baseurl = base_url
        
        # Convert to markdown
        markdown_content = h.handle(html_content)
        
        # Clean up excessive whitespace
        lines = markdown_content.split('\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            line = line.rstrip()
            is_empty = len(line.strip()) == 0
            
            # Skip multiple consecutive empty lines
            if is_empty and prev_empty:
                continue
                
            cleaned_lines.append(line)
            prev_empty = is_empty
        
        result = '\n'.join(cleaned_lines).strip()
        
        # Calculate statistics
        char_count = len(result)
        word_count = len(result.split())
        line_count = len(cleaned_lines)
        
        print_success(f"Converted to Markdown: {Fore.CYAN}{char_count:,}{Fore.GREEN} characters, {Fore.CYAN}{word_count:,}{Fore.GREEN} words, {Fore.CYAN}{line_count:,}{Fore.GREEN} lines")
        logger.debug(f"Converted {len(html_content)} characters of HTML to {len(result)} characters of Markdown")
        
        return result
        
    except Exception as e:
        print_error(f"Failed to convert HTML to Markdown: {str(e)}")
        logger.error(f"Failed to convert HTML to Markdown: {e}")
        return ""


def ensure_output_directory(output_file: str) -> bool:
    """
    Ensure the output directory exists.
    
    Args:
        output_file: Path to the output file
        
    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        output_path = Path(output_file)
        output_dir = output_path.parent
        
        if not output_dir.exists():
            logger.debug(f"Creating output directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)
        
        return True
        
    except PermissionError as e:
        logger.error(f"Permission denied when creating directory for {output_file}: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to create directory for {output_file}: {e}")
        return False


def save_markdown(content: str, output_file: str) -> bool:
    """
    Save Markdown content to file.
    
    Args:
        content: Markdown content to save
        output_file: Path to output file
        
    Returns:
        True if saved successfully, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Ensure output directory exists
        if not ensure_output_directory(output_file):
            return False
        
        print_info(f"Saving to: {Fore.CYAN}{output_file}{Style.RESET_ALL}")
        
        # Write content to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Get file size for display
        file_size = os.path.getsize(output_file)
        if file_size < 1024:
            size_str = f"{file_size} bytes"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        print_success(f"Saved {Fore.CYAN}{size_str}{Fore.GREEN} to {Fore.CYAN}{output_file}{Style.RESET_ALL}")
        logger.info(f"Saved Markdown content to {output_file}")
        return True
        
    except PermissionError as e:
        print_error(f"Permission denied: {str(e)}")
        logger.error(f"Permission denied when writing to {output_file}: {e}")
        return False
    except Exception as e:
        print_error(f"Failed to save file: {str(e)}")
        logger.error(f"Failed to save content to {output_file}: {e}")
        return False


def main():
    """Main function to orchestrate the web-to-markdown conversion process."""
    parser = argparse.ArgumentParser(
        description="Convert webpage content to Markdown format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url https://example.com --output-file ./example.md
  %(prog)s --url https://blog.example.com/post --output-file ./posts/post.md --log-level DEBUG
        """
    )
    
    parser.add_argument(
        '--url',
        '-u',
        required=True,
        help='URL of the webpage to convert (e.g., https://example.com)'
    )
    
    parser.add_argument(
        '--output-file',
        '-o',
        required=True,
        help='Path to save the Markdown output (e.g., ./output.md)'
    )
    
    parser.add_argument(
        '--log-level',
        '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--timeout',
        '-t',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.log_level)
    
    # Validate URL
    if not validate_url(args.url):
        logger.error(f"Invalid URL format: {args.url}")
        sys.exit(1)
    
    logger.debug(f"Starting processing for URL: {args.url}")
    
    # Fetch webpage
    response = fetch_webpage(args.url, args.timeout)
    if response is None:
        sys.exit(1)
    
    # Parse HTML
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        logger.debug("Successfully parsed HTML content")
    except Exception as e:
        logger.error(f"Failed to parse HTML content: {e}")
        sys.exit(1)
    
    # Clean HTML content
    try:
        cleaned_soup = clean_html_content(soup)
        main_content_soup = extract_main_content(cleaned_soup)
        logger.debug("Successfully cleaned HTML content")
    except Exception as e:
        logger.error(f"Failed to clean HTML content: {e}")
        sys.exit(1)
    
    # Convert to Markdown
    html_content = str(main_content_soup)
    markdown_content = convert_to_markdown(html_content, args.url)
    
    if not markdown_content:
        logger.error("Failed to generate Markdown content")
        sys.exit(1)
    
    # Save to file
    success = save_markdown(markdown_content, args.output_file)
    if not success:
        sys.exit(1)
    
    logger.info(f"Successfully converted {args.url} to Markdown format")
    logger.debug(f"Process completed successfully")


if __name__ == "__main__":
    main()
