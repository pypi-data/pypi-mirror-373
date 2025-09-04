#!/usr/bin/env python3
"""
WebFetch tool implementation for Archer.
Fetches and processes web content with support for text, markdown, and HTML formats.
"""

import logging
import time
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from html.parser import HTMLParser
import urllib.request
import urllib.error
from io import StringIO

# Cache for storing fetched content (15-minute expiry)
_cache: Dict[str, tuple[str, float]] = {}
CACHE_EXPIRY_SECONDS = 900  # 15 minutes

MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5MB
DEFAULT_TIMEOUT = 30  # seconds
MAX_TIMEOUT = 120  # seconds


class HTMLToText(HTMLParser):
    """Simple HTML to text converter that strips tags and scripts."""
    
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip_tags = {'script', 'style', 'noscript', 'iframe', 'object', 'embed'}
        self.skip_content = False
        self.current_tag = None
    
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()
        if self.current_tag in self.skip_tags:
            self.skip_content = True
        elif tag in ('p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'li'):
            # Add newline for block elements
            if self.text and not self.text[-1].endswith('\n'):
                self.text.append('\n')
    
    def handle_endtag(self, tag):
        if tag.lower() in self.skip_tags:
            self.skip_content = False
        elif tag in ('p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            if self.text and not self.text[-1].endswith('\n'):
                self.text.append('\n')
    
    def handle_data(self, data):
        if not self.skip_content:
            # Clean up whitespace but preserve structure
            cleaned = ' '.join(data.split())
            if cleaned:
                self.text.append(cleaned)
                if self.current_tag not in ('span', 'a', 'b', 'i', 'em', 'strong'):
                    self.text.append(' ')
    
    def get_text(self):
        return ''.join(self.text).strip()


class HTMLToMarkdown(HTMLParser):
    """Convert HTML to Markdown format."""
    
    def __init__(self):
        super().__init__()
        self.markdown = []
        self.skip_tags = {'script', 'style', 'meta', 'link', 'noscript'}
        self.skip_content = False
        self.list_stack = []
        self.link_text = []
        self.link_href = None
        self.in_link = False
        self.in_code = False
        self.in_pre = False
        
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        
        if tag in self.skip_tags:
            self.skip_content = True
            return
            
        if self.skip_content:
            return
            
        attrs_dict = dict(attrs)
        
        if tag == 'h1':
            self.markdown.append('\n# ')
        elif tag == 'h2':
            self.markdown.append('\n## ')
        elif tag == 'h3':
            self.markdown.append('\n### ')
        elif tag == 'h4':
            self.markdown.append('\n#### ')
        elif tag == 'h5':
            self.markdown.append('\n##### ')
        elif tag == 'h6':
            self.markdown.append('\n###### ')
        elif tag == 'p':
            self.markdown.append('\n\n')
        elif tag == 'br':
            self.markdown.append('  \n')
        elif tag == 'hr':
            self.markdown.append('\n---\n')
        elif tag == 'ul':
            self.list_stack.append('ul')
        elif tag == 'ol':
            self.list_stack.append('ol')
        elif tag == 'li':
            self.markdown.append('\n')
            indent = '  ' * (len(self.list_stack) - 1)
            if self.list_stack and self.list_stack[-1] == 'ul':
                self.markdown.append(f'{indent}- ')
            elif self.list_stack and self.list_stack[-1] == 'ol':
                self.markdown.append(f'{indent}1. ')
        elif tag == 'a':
            self.in_link = True
            self.link_href = attrs_dict.get('href', '#')
            self.link_text = []
        elif tag == 'img':
            alt = attrs_dict.get('alt', '')
            src = attrs_dict.get('src', '')
            self.markdown.append(f'![{alt}]({src})')
        elif tag == 'code':
            if not self.in_pre:
                self.markdown.append('`')
                self.in_code = True
        elif tag == 'pre':
            self.markdown.append('\n```\n')
            self.in_pre = True
        elif tag in ('strong', 'b'):
            self.markdown.append('**')
        elif tag in ('em', 'i'):
            self.markdown.append('*')
        elif tag == 'blockquote':
            self.markdown.append('\n> ')
    
    def handle_endtag(self, tag):
        tag = tag.lower()
        
        if tag in self.skip_tags:
            self.skip_content = False
            return
            
        if self.skip_content:
            return
            
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.markdown.append('\n')
        elif tag == 'p':
            self.markdown.append('\n')
        elif tag == 'ul' or tag == 'ol':
            if self.list_stack:
                self.list_stack.pop()
        elif tag == 'a' and self.in_link:
            link_text = ''.join(self.link_text)
            self.markdown.append(f'[{link_text}]({self.link_href})')
            self.in_link = False
            self.link_text = []
            self.link_href = None
        elif tag == 'code' and self.in_code:
            self.markdown.append('`')
            self.in_code = False
        elif tag == 'pre':
            self.markdown.append('\n```\n')
            self.in_pre = False
        elif tag in ('strong', 'b'):
            self.markdown.append('**')
        elif tag in ('em', 'i'):
            self.markdown.append('*')
    
    def handle_data(self, data):
        if self.skip_content:
            return
            
        if self.in_link:
            self.link_text.append(data)
        else:
            # Clean up whitespace but preserve code blocks
            if self.in_pre or self.in_code:
                self.markdown.append(data)
            else:
                cleaned = ' '.join(data.split())
                if cleaned:
                    self.markdown.append(cleaned)
    
    def get_markdown(self):
        result = ''.join(self.markdown)
        # Clean up multiple newlines
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()


def clean_cache():
    """Remove expired entries from the cache."""
    global _cache
    current_time = time.time()
    expired_keys = [
        key for key, (_, timestamp) in _cache.items()
        if current_time - timestamp > CACHE_EXPIRY_SECONDS
    ]
    for key in expired_keys:
        del _cache[key]


def webfetch(input_data: Dict[str, Any]) -> str:
    """
    Fetch content from a URL and return it in the specified format.
    
    Args:
        input_data: Dictionary containing:
            - url: The URL to fetch
            - format: Output format ('text', 'markdown', or 'html')
            - timeout: Optional timeout in seconds (max 120)
    
    Returns:
        The fetched content in the specified format
    """
    url = input_data.get('url', '')
    output_format = input_data.get('format', 'markdown')
    timeout = input_data.get('timeout', DEFAULT_TIMEOUT)
    
    # Validate URL
    if not url:
        return "Error: URL is required"
    
    # Parse and validate URL format
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return "Error: URL must start with http:// or https://"
    except Exception as e:
        return f"Error: Invalid URL format: {e}"
    
    # Validate timeout
    timeout = min(timeout, MAX_TIMEOUT)
    
    # Clean expired cache entries
    clean_cache()
    
    # Check cache
    cache_key = f"{url}:{output_format}"
    if cache_key in _cache:
        content, timestamp = _cache[cache_key]
        if time.time() - timestamp < CACHE_EXPIRY_SECONDS:
            logging.info(f"WebFetch: Returning cached content for {url}")
            return content
    
    logging.info(f"WebFetch: Fetching {url} with format={output_format}, timeout={timeout}s")
    
    try:
        # Create request with headers
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 
                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        request.add_header('Accept', 
                          'text/html,application/xhtml+xml,application/xml;q=0.9,'
                          'image/avif,image/webp,image/apng,*/*;q=0.8')
        request.add_header('Accept-Language', 'en-US,en;q=0.9')
        
        # Fetch the content
        with urllib.request.urlopen(request, timeout=timeout) as response:
            # Check content length
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > MAX_RESPONSE_SIZE:
                return "Error: Response too large (exceeds 5MB limit)"
            
            # Read content
            content_bytes = response.read(MAX_RESPONSE_SIZE + 1)
            if len(content_bytes) > MAX_RESPONSE_SIZE:
                return "Error: Response too large (exceeds 5MB limit)"
            
            # Detect encoding from headers or default to UTF-8
            content_type = response.headers.get('Content-Type', '')
            encoding = 'utf-8'
            if 'charset=' in content_type:
                charset_match = re.search(r'charset=([^;]+)', content_type)
                if charset_match:
                    encoding = charset_match.group(1).strip()
            
            # Decode content
            try:
                content = content_bytes.decode(encoding)
            except UnicodeDecodeError:
                # Fallback to latin-1 which accepts all byte values
                content = content_bytes.decode('latin-1')
            
            # Process content based on format
            is_html = 'text/html' in content_type or content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html')
            
            if output_format == 'html':
                result = content
            elif output_format == 'text':
                if is_html:
                    parser = HTMLToText()
                    parser.feed(content)
                    result = parser.get_text()
                else:
                    result = content
            elif output_format == 'markdown':
                if is_html:
                    parser = HTMLToMarkdown()
                    parser.feed(content)
                    result = parser.get_markdown()
                else:
                    # Wrap non-HTML content in code block
                    result = f"```\n{content}\n```"
            else:
                result = content
            
            # Cache the result
            _cache[cache_key] = (result, time.time())
            
            logging.info(f"WebFetch: Successfully fetched {len(result)} characters from {url}")
            return result
            
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP Error {e.code}: {e.reason}"
        logging.error(f"WebFetch failed for {url}: {error_msg}")
        return f"Error: {error_msg}"
    except urllib.error.URLError as e:
        error_msg = f"URL Error: {e.reason}"
        logging.error(f"WebFetch failed for {url}: {error_msg}")
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Failed to fetch URL: {str(e)}"
        logging.error(f"WebFetch failed for {url}: {error_msg}")
        return f"Error: {error_msg}"