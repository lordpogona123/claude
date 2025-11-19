"""
Base Scraper Class - Provides core web scraping functionality
"""

import requests
import time
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for web scraping operations"""

    def __init__(self, config: Dict):
        """
        Initialize the scraper with configuration

        Args:
            config: Configuration dictionary from scraper_config.json
        """
        self.config = config
        self.scraping_config = config.get('scraping', {})
        self.timeout = self.scraping_config.get('timeout', 30)
        self.retry_attempts = self.scraping_config.get('retry_attempts', 3)
        self.retry_delay = self.scraping_config.get('retry_delay', 2)
        self.user_agent = self.scraping_config.get('user_agent', '')
        self.rate_limit_delay = self.scraping_config.get('rate_limit_delay', 1)

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def fetch_page(self, url: str, method: str = 'GET', **kwargs) -> Tuple[Optional[str], str, Dict]:
        """
        Fetch a web page with retry logic

        Args:
            url: URL to fetch
            method: HTTP method (GET or POST)
            **kwargs: Additional arguments for requests

        Returns:
            Tuple of (html_content, status, metadata)
        """
        metadata = {
            'url': url,
            'attempts': 0,
            'final_url': url,
            'status_code': None,
            'error': None
        }

        for attempt in range(1, self.retry_attempts + 1):
            metadata['attempts'] = attempt

            try:
                # Rate limiting
                if attempt > 1:
                    time.sleep(self.retry_delay * attempt)
                else:
                    time.sleep(self.rate_limit_delay)

                # Make request
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    **kwargs
                )

                metadata['status_code'] = response.status_code
                metadata['final_url'] = response.url

                # Check response
                if response.status_code == 200:
                    logger.info(f"Successfully fetched: {url}")
                    return response.text, 'online', metadata
                elif response.status_code == 403:
                    logger.warning(f"Access forbidden (403): {url}")
                    return None, 'blocked', metadata
                elif response.status_code == 404:
                    logger.warning(f"Page not found (404): {url}")
                    return None, 'not_found', metadata
                else:
                    logger.warning(f"HTTP {response.status_code}: {url}")
                    if attempt == self.retry_attempts:
                        return None, f'http_error_{response.status_code}', metadata

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt}/{self.retry_attempts}: {url}")
                metadata['error'] = 'timeout'
                if attempt == self.retry_attempts:
                    return None, 'timeout', metadata

            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on attempt {attempt}/{self.retry_attempts}: {url}")
                metadata['error'] = 'connection_error'
                if attempt == self.retry_attempts:
                    return None, 'connection_error', metadata

            except requests.exceptions.TooManyRedirects:
                logger.warning(f"Too many redirects: {url}")
                metadata['error'] = 'too_many_redirects'
                return None, 'redirect_error', metadata

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt}/{self.retry_attempts}: {url} - {str(e)}")
                metadata['error'] = str(e)
                if attempt == self.retry_attempts:
                    return None, 'error', metadata

        return None, 'failed', metadata

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup

        Args:
            html: HTML content as string

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')

    def extract_links(self, soup: BeautifulSoup, base_url: str, filter_pattern: Optional[str] = None) -> List[str]:
        """
        Extract links from a page

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            filter_pattern: Optional regex pattern to filter links

        Returns:
            List of absolute URLs
        """
        links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)

            # Filter if pattern provided
            if filter_pattern:
                if re.search(filter_pattern, absolute_url, re.IGNORECASE):
                    links.append(absolute_url)
            else:
                links.append(absolute_url)

        return list(set(links))  # Remove duplicates

    def search_text_in_page(self, html: str, search_terms: List[str], case_sensitive: bool = False) -> Dict:
        """
        Search for specific terms in page content

        Args:
            html: HTML content
            search_terms: List of terms to search for
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            Dictionary with search results
        """
        results = {
            'found': False,
            'matches': [],
            'count': 0,
            'evidence': []
        }

        soup = self.parse_html(html)
        text_content = soup.get_text()

        for term in search_terms:
            if case_sensitive:
                pattern = re.compile(re.escape(term))
            else:
                pattern = re.compile(re.escape(term), re.IGNORECASE)

            matches = pattern.findall(text_content)

            if matches:
                results['found'] = True
                results['matches'].extend(matches)
                results['count'] += len(matches)

                # Extract context around matches
                for match in pattern.finditer(text_content):
                    start = max(0, match.start() - 50)
                    end = min(len(text_content), match.end() + 50)
                    context = text_content[start:end].strip()
                    results['evidence'].append(context)

        results['matches'] = list(set(results['matches']))
        return results

    def find_elements_by_pattern(self, soup: BeautifulSoup, pattern: str, tag: Optional[str] = None) -> List:
        """
        Find HTML elements matching a text pattern

        Args:
            soup: BeautifulSoup object
            pattern: Regex pattern to match
            tag: Optional tag name to restrict search

        Returns:
            List of matching elements
        """
        regex = re.compile(pattern, re.IGNORECASE)

        if tag:
            elements = soup.find_all(tag, string=regex)
        else:
            elements = soup.find_all(string=regex)

        return elements

    def extract_game_links(self, soup: BeautifulSoup, base_url: str, game_terms: List[str]) -> Dict[str, str]:
        """
        Extract links to game pages

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving links
            game_terms: List of game names to look for

        Returns:
            Dictionary mapping game names to URLs
        """
        game_links = {}

        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            href = link['href']

            # Check if link text matches any game term
            for game in game_terms:
                # Normalize for comparison
                normalized_link_text = re.sub(r'[^a-z0-9]', '', link_text.lower())
                normalized_game = re.sub(r'[^a-z0-9]', '', game.lower())

                if normalized_game in normalized_link_text or normalized_link_text in normalized_game:
                    absolute_url = urljoin(base_url, href)
                    game_links[game] = absolute_url
                    break

        return game_links

    def close(self):
        """Close the session"""
        self.session.close()
