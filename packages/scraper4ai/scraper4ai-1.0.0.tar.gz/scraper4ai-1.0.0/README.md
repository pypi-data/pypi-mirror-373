# scraper4ai

`scraper4ai` is a powerful and easy-to-use Python library for web scraping, specifically designed to prepare web content for AI and Large Language Model (LLM) applications. It fetches web pages, cleans the HTML, and converts the main content into clean, structured Markdown. It also extracts valuable data like links, images, and videos. The library is built with asynchronous support from the ground up, allowing for efficient scraping of multiple URLs concurrently.

## Features

*   **AI-Ready Content**: Converts messy HTML into clean Markdown, perfect for LLM processing.
*   **Asynchronous Support**: Scrape multiple URLs concurrently with `invoke_all` for high performance.
*   **Rich Data Extraction**: Extracts not just the main content, but also hyperlinks, images, and video sources.
*   **JA3/TLS Fingerprint Spoofing**: Uses `curl_cffi` to impersonate real browser profiles (like Chrome 136), helping to bypass many anti-bot measures.
*   **Optimized Performance**: Session reuse and connection pooling for improved efficiency and reduced overhead.
*   **Customizable Cleaning**: Easily specify which HTML tags or CSS selectors to remove before Markdown conversion.
*   **Resource Management**: Automatic session handling with proper cleanup methods.
*   **Simple API**: Get started in just a few lines of code with an intuitive API.

## Installation

```bash
pip install scraper4ai
```

## Usage

### Basic Usage

Here's a simple example of how to scrape a single URL and get the clean Markdown content.

```python
from scraper4ai import WebScraper

# Initialize the scraper
scraper = WebScraper()

# Scrape a single URL
url = "https://example.com"
result = scraper.invoke(url)

if result.status_code == 200:
    print(result.markdown)
else:
    print(f"Failed to scrape {url}. Status code: {result.status_code}")
```

### Batch Scraping

Use `invoke_all` to efficiently process a list of URLs concurrently.

```python
from scraper4ai import WebScraper

# Initialize the scraper
scraper = WebScraper()

urls = ["https://www.python.org/", "https://github.com/"]

# Scrape all URLs concurrently
results = scraper.invoke_all(urls)

for result in results:
    if result.status_code == 200:
        print(f"--- Content from {result.url} ---")
        print(result.markdown)
        print("-" * 20)
    else:
        print(f"Failed to scrape {result.url}. Status code: {result.status_code}")
```

### Customizing HTML Cleaning

You can easily remove unwanted HTML tags or elements matching CSS selectors before the content is converted to Markdown.

```python
from scraper4ai import WebScraper

scraper = WebScraper()

# Add custom rules to remove navigation and footer elements
scraper.ignore_these_tags_in_markdown(["nav", "footer"])
# Add custom rule to remove any element with class="cookie-banner"
scraper.ignore_these_css_in_markdown([".cookie-banner"])

# These rules will be applied to all subsequent .invoke() or .invoke_all() calls
result = scraper.invoke("https://example.com")
print(result.markdown)

# Don't forget to close the session when done to free resources
scraper.close()
```

## The `ScrapedResult` Object

The `invoke()` and `invoke_all()` methods return `ScrapedResult` objects (or a list of them). This object contains all the data you've scraped.

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class LinkData:
    url: str
    text: Optional[str] = None

@dataclass
class ImageData:
    url: str
    alt_text: Optional[str] = None

@dataclass
class VideoData:
    url: str
    title: Optional[str] = None

@dataclass
class ScrapedResult:
    url: str
    status_code: int
    raw_html: Optional[str]
    markdown: Optional[str]
    links: Optional[List[LinkData]] = field(default_factory=list)
    image_links: Optional[List[ImageData]] = field(default_factory=list)
    video_links: Optional[List[VideoData]] = field(default_factory=list)
```

*   `url` (str): The original URL that was scraped.
*   `status_code` (int): The HTTP status code of the response. On failure, this will be `-1` or the actual error code.
*   `raw_html` (Optional[str]): The original, unmodified HTML content of the page. `None` on failure.
*   `markdown` (Optional[str]): The cleaned, converted Markdown content. `None` on failure.
*   `links` (Optional[List[LinkData]]): A list of all hyperlinks found on the page. `None` on failure.
*   `image_links` (Optional[List[ImageData]]): A list of all images found on the page. `None` on failure.
*   `video_links` (Optional[List[VideoData]]): A list of all videos found on the page. `None` on failure.

## Advanced Features

### Browser Impersonation

The library uses the latest Chrome 136 browser fingerprints for maximum compatibility and anti-bot detection avoidance. The impersonation automatically adapts for mobile devices when needed.

### Retry Logic

Intelligent retry mechanism with exponential backoff to handle temporary network issues gracefully without overwhelming servers.

## Error Handling

If the scraper fails to fetch a URL after several retries, it **will not raise an exception**. Instead, it returns a `ScrapedResult` object where:
*   `status_code` is set to `-1` (or the actual HTTP error status code if one was received).
*   `raw_html`, `markdown`, and the link lists are set to `None`.

This design allows you to handle failures gracefully without crashing, especially during batch processing.

## Performance Tips

- **Session Reuse**: The WebScraper automatically reuses HTTP sessions for better performance when making multiple sequential requests.
- **Batch Processing**: Use `invoke_all()` for concurrent processing of multiple URLs with optimized connection pooling.
- **Resource Cleanup**: Call `scraper.close()` when finished to properly release session resources.
- **Connection Limits**: The async session limits concurrent connections to prevent overwhelming target servers.

```python
from scraper4ai import WebScraper

# Create scraper instance
scraper = WebScraper()

# Process multiple URLs efficiently
results = scraper.invoke_all([
    "https://example1.com",
    "https://example2.com",
    "https://example3.com"
])

# Clean up resources
scraper.close()
```
