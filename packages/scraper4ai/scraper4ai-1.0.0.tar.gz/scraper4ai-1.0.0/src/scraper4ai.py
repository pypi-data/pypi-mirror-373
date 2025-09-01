import logging
import asyncio
import sys
from curl_cffi import requests
from curl_cffi.requests import AsyncSession, Session
from bs4 import BeautifulSoup
from crawl4ai import DefaultMarkdownGenerator
from urllib.parse import urljoin
from typing import List, Tuple, Optional

from models import ScrapedResult, ImageData, LinkData, VideoData

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebScraperError(Exception):
    pass

class WebScraper:
    def __init__(self, log_level=logging.ERROR):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
        self._default_ignore_tag: list[str] = ["script", "style", "iframe", "noscript", "aside", "form", "svg", "nav", "footer"]
        self._tag_to_remove: list[str] = []
        self._css_to_remove: list[str] = []
        self._session: Optional[Session] = None
        
    def ignore_these_tags_in_markdown(self, tags: list[str]):
        self._tag_to_remove = tags
    
    def ignore_these_css_in_markdown(self, css: list[str]):
        self._css_to_remove = css

    def _get_session(self, mobile: bool=False) -> Session:
        if self._session is None:
            impersonate = "chrome136_android" if mobile else "chrome136"
            self._session = Session(impersonate=impersonate)
        return self._session
    
    def _fetch_html(self, url: str, timeout: int=10, retries: int=3, mobile: bool=False) -> Tuple[str, int]:
        if not url or not url.startswith(('http://', 'https://')):
            raise WebScraperError(f"Invalid URL: {url}")
        
        session = self._get_session(mobile)
        
        for attempt in range(retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{retries} to fetch {url}")
                response = session.get(url, timeout=timeout)
                response.raise_for_status()
                self.logger.info(f"Successfully fetched {url} with status code {response.status_code}")
                return response.text, response.status_code
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == retries - 1:
                    self.logger.error(f"Failed to fetch content from {url} after {retries} retries.")
                    raise WebScraperError(f"Failed to fetch content after {retries} retries: {e} - {url}") from e
                import time
                time.sleep(0.5 * (attempt + 1))
                
    async def _fetch_html_async(self, session: AsyncSession, url: str, timeout: int=10, retries: int=3, mobile: bool=False) -> Tuple[str, int]:
        if not url or not url.startswith(('http://', 'https://')):
            raise WebScraperError(f"Invalid URL: {url}")

        for attempt in range(retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{retries} to fetch {url} asynchronously")
                response = await session.get(url, timeout=timeout)
                response.raise_for_status()
                self.logger.info(f"Successfully fetched {url} with status code {response.status_code}")
                return response.text, response.status_code
            except Exception as e:
                self.logger.warning(f"Async attempt {attempt + 1} failed for {url}: {e}")
                if attempt == retries - 1:
                    self.logger.error(f"Failed to fetch content from {url} asynchronously after {retries} retries.")
                    raise WebScraperError(f"Failed to fetch content after {retries} retries: {e} - {url}") from e
                await asyncio.sleep(0.5 * (attempt + 1))

        raise WebScraperError(f"Failed to fetch content after {retries} retries - {url}")

    def _clean_html(self, html_content: str, use_default_ignore_tags: bool=True) -> str:
        if not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            ignore_tags = self._tag_to_remove
            ignore_css = self._css_to_remove
            
            if use_default_ignore_tags: ignore_tags += self._default_ignore_tag
            
            for tag in ignore_tags:
                for element in soup.find_all(tag):
                    element.decompose()
            
            for css in ignore_css:
                for element in soup.select(css):
                    element.decompose()
                    
            return str(soup)
        
        except Exception as e:
            raise WebScraperError(f"Fail to clean-up html. {e}")
        
    def _html_to_markdown(self, html_content: str, base_url: str) -> str:
        try:
            markdown_generator = DefaultMarkdownGenerator()
            markdown = markdown_generator.generate_markdown(
                input_html=html_content,
                base_url=base_url,
            )
            return markdown.raw_markdown
        except Exception as e:
            raise WebScraperError(f"Failed to convert to Markdown: {e}")
        
    def _extract_links(self, html: str, base_url: str) -> List[LinkData]:
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = urljoin(base_url, a_tag["href"])
            text = a_tag.get_text(strip=True) or None
            links.append(LinkData(url=href, text=text))
        return links

    def _extract_images(self, html: str, base_url: str) -> List[ImageData]:
        soup = BeautifulSoup(html, "html.parser")
        images = []
        for img_tag in soup.find_all("img"):
            src = (
                img_tag.get("src") or
                img_tag.get("data-src") or
                img_tag.get("data-original") or
                img_tag.get("data-lazy")
            )

            if not src: continue

            src = src.strip()

            if src in ("", "#", "about:blank") or src.startswith("javascript:"):
                continue

            full_url = urljoin(base_url, src)
            alt = img_tag.get("alt", None)
            images.append(ImageData(url=full_url, alt_text=alt))
        return images

    def _extract_videos(self, html: str, base_url: str) -> List[VideoData]:
        soup = BeautifulSoup(html, "html.parser")
        videos = []

        for video_tag in soup.find_all("video"):
            if video_tag.has_attr("src"):
                src = urljoin(base_url, video_tag["src"])
                title = video_tag.get("title") or video_tag.get("aria-label") or video_tag.get_text(strip=True) or None
                videos.append(VideoData(url=src, title=title))

            for source_tag in video_tag.find_all("source", src=True):
                src = urljoin(base_url, source_tag["src"])
                title = video_tag.get("title") or video_tag.get("aria-label") or video_tag.get_text(strip=True) or None
                videos.append(VideoData(url=src, title=title))

        return videos

    def invoke(
        self, 
        url: str,
        timeout: int = 10,
        retries: int = 2,
        mobile: bool = False,
        use_default_ignore_tags: bool = True
    ) -> ScrapedResult:
        self.logger.info(f"Starting to process URL: {url}")
        try:
            raw_html, status_code = self._fetch_html(url, timeout, retries, mobile)

            links = self._extract_links(raw_html, url)
            images = self._extract_images(raw_html, url)
            videos = self._extract_videos(raw_html, url)
            
            cleaned_html = self._clean_html(raw_html, use_default_ignore_tags)
            markdown_text = self._html_to_markdown(cleaned_html, url)
            
            self.logger.info(f"Successfully processed {url}")
            return ScrapedResult(
                url=url,
                status_code=status_code,
                raw_html=raw_html,
                markdown=markdown_text,
                links=links,
                image_links=images,
                video_links=videos
            )
        except Exception as e:
            self.logger.error(f"An error occurred while processing {url}: {e}")
            status_code = -1
            if hasattr(e, '__cause__') and hasattr(e.__cause__, 'response') and hasattr(e.__cause__.response, 'status_code'):
                status_code = e.__cause__.response.status_code

            return ScrapedResult(
                url=url,
                status_code=status_code,
                raw_html=None,
                markdown=None,
                links=None,
                image_links=None,
                video_links=None
            )

    async def _invoke_single_async(
        self,
        session: AsyncSession,
        url: str,
        timeout: int,
        retries: int,
        mobile: bool,
        use_default_ignore_tags: bool
    ) -> ScrapedResult:
        self.logger.info(f"Starting to process URL asynchronously: {url}")
        try:
            raw_html, status_code = await self._fetch_html_async(session, url, timeout, retries, mobile)
            
            links = self._extract_links(raw_html, url)
            images = self._extract_images(raw_html, url)
            videos = self._extract_videos(raw_html, url)
            
            cleaned_html = self._clean_html(raw_html, use_default_ignore_tags)
            markdown_text = self._html_to_markdown(cleaned_html, url)

            self.logger.info(f"Successfully processed {url} asynchronously")
            return ScrapedResult(
                url=url,
                status_code=status_code,
                raw_html=raw_html,
                markdown=markdown_text,
                links=links,
                image_links=images,
                video_links=videos
            )
        except Exception as e:
            self.logger.error(f"An error occurred while processing {url} asynchronously: {e}")
            status_code = -1
            if hasattr(e, '__cause__') and hasattr(e.__cause__, 'response') and hasattr(e.__cause__.response, 'status_code'):
                status_code = e.__cause__.response.status_code
                
            return ScrapedResult(
                url=url,
                status_code=status_code,
                raw_html=None,
                markdown=None,
                links=None,
                image_links=None,
                video_links=None
            )

    def invoke_all(
        self,
        urls: List[str],
        timeout: int = 10,
        retries: int = 2,
        mobile: bool = False,
        use_default_ignore_tags: bool = True
    ) -> List[ScrapedResult]:
        async def main():
            self.logger.info(f"Starting to process a batch of {len(urls)} URLs.")
            impersonate = "chrome136_android" if mobile else "chrome136"
            
            async with AsyncSession(
                impersonate=impersonate,
                max_clients=min(len(urls), 10)
            ) as session:
                tasks = [
                    self._invoke_single_async(session, url, timeout, retries, mobile, use_default_ignore_tags)
                    for url in urls
                ]
                results = await asyncio.gather(*tasks, return_exceptions=False)
                self.logger.info("Finished processing batch.")
                return results

        return asyncio.run(main())
    
    def close(self):
        """Close the session to free resources"""
        if self._session:
            self._session.close()
            self._session = None