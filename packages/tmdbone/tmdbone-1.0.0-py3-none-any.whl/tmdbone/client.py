"""The core TMDbOneClient for handling configuration and API requests."""

import asyncio
import aiohttp
import logging
from itertools import cycle
from typing import List, Set, Optional

from .exceptions import TMDbAPIError
from .resources import (
    Movie, TV, Person, Find, Discover, Collection, Company, Network,
    Search, Trending, Genre, Configuration, Keyword, Review, Certification, Credit
)

class TMDbOneClient:
    """The main asynchronous client for interacting with The Movie Database API."""
    
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(
        self,
        api_keys: List[str],
        language: Optional[str] = 'en-US',
        region: Optional[str] = None,
        retries: int = 3,
        retry_delay: int = 5,
        rate_limit_cooldown: int = 10,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Initializes the client with API keys and global settings.

        Args:
            api_keys: A list of TMDb v3 API keys to rotate through.
            language: The global ISO 639-1 language code to request data in.
            region: The global ISO 3166-1 region code for release date filtering.
            retries: The number of times to retry a failed request.
            retry_delay: The delay (in seconds) between retries.
            rate_limit_cooldown: The delay (in seconds) to wait when a rate limit is hit.
            session: An optional existing aiohttp.ClientSession.
        """
        if not api_keys:
            raise ValueError("At least one TMDb API key is required.")
        
        self.language = language
        self.region = region
        self.active_api_keys: Set[str] = set(api_keys)
        self.api_key_rotator = cycle(list(self.active_api_keys))
        
        self.retries = retries
        self.retry_delay = retry_delay
        self.rate_limit_cooldown = rate_limit_cooldown
        
        self._external_session = session is not None
        self.session = session or aiohttp.ClientSession(
            headers={'User-Agent': f'TMDbOneClient/{__import__("tmdbone").__version__}'}
        )
        
        logging.info(f"TMDbOneClient initialized with {len(self.active_api_keys)} API key(s). Global language: '{self.language}'")

    async def _api_request(self, method: str, url: str, params: Optional[dict] = None) -> Optional[dict]:
        """Core resilient request handler with key rotation, retries, and rate limit handling."""
        if params is None: params = {}
        
        if self.language: params.setdefault('language', self.language)
        if self.region: params.setdefault('region', self.region)
        
        last_error = None

        for attempt in range(self.retries):
            if not self.active_api_keys:
                raise TMDbAPIError("All API keys have been exhausted or are invalid.")
            
            current_api_key = next(self.api_key_rotator)
            request_params = params.copy()
            request_params['api_key'] = current_api_key
            
            try:
                async with self.session.request(method, url, params=request_params, ssl=False) as response:
                    if response.status == 200: return await response.json()
                    if response.status == 401:
                        logging.warning(f"API Key starting with '{current_api_key[:8]}' is invalid. Discarding.")
                        self.active_api_keys.discard(current_api_key)
                        continue
                    if response.status == 429:
                        logging.warning(f"Rate limit hit. Cooling down for {self.rate_limit_cooldown}s.")
                        await asyncio.sleep(self.rate_limit_cooldown)
                        break
                    if response.status == 404: return None
                    response.raise_for_status()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_error = e
                logging.warning(f"Network error on attempt {attempt + 1}/{self.retries}: {e}")
            if attempt < self.retries - 1: await asyncio.sleep(self.retry_delay)
        raise TMDbAPIError(f"API request failed for {url} after {self.retries} retries.", url=url)

    async def close(self):
        """Closes the aiohttp session if it was created by this client."""
        if not self._external_session and self.session and not self.session.closed:
            await self.session.close()

    def __repr__(self) -> str:
        return f"<TMDbOneClient(keys={len(self.active_api_keys)}, lang={self.language})>"

    # --- Factory Methods for API Resources ---
    def movie(self, movie_id: int) -> 'Movie': return Movie(self, movie_id)
    def tv(self, tv_id: int) -> 'TV': return TV(self, tv_id)
    def person(self, person_id: int) -> 'Person': return Person(self, person_id)
    def find(self, external_id: str) -> 'Find': return Find(self, external_id)
    def discover(self) -> 'Discover': return Discover(self)
    def collection(self, collection_id: int) -> 'Collection': return Collection(self, collection_id)
    def company(self, company_id: int) -> 'Company': return Company(self, company_id)
    def network(self, network_id: int) -> 'Network': return Network(self, network_id)
    def keyword(self, keyword_id: int) -> 'Keyword': return Keyword(self, keyword_id)
    def review(self, review_id: str) -> 'Review': return Review(self, review_id)
    def credit(self, credit_id: str) -> 'Credit': return Credit(self, credit_id)
    def search(self) -> 'Search': return Search(self)
    def trending(self) -> 'Trending': return Trending(self)
    def genre(self) -> 'Genre': return Genre(self)
    def configuration(self) -> 'Configuration': return Configuration(self)
    def certification(self) -> 'Certification': return Certification(self)
    
    # --- Top-Level Endpoint Methods ---
    async def movies_latest(self): return await self._api_request("GET", f"{self.BASE_URL}/movie/latest")
    async def movies_now_playing(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/movie/now_playing", params=kwargs)
    async def movies_popular(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/movie/popular", params=kwargs)
    async def movies_top_rated(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/movie/top_rated", params=kwargs)
    async def movies_upcoming(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/movie/upcoming", params=kwargs)
    async def tv_latest(self): return await self._api_request("GET", f"{self.BASE_URL}/tv/latest")
    async def tv_airing_today(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/tv/airing_today", params=kwargs)
    async def tv_on_the_air(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/tv/on_the_air", params=kwargs)
    async def tv_popular(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/tv/popular", params=kwargs)
    async def tv_top_rated(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/tv/top_rated", params=kwargs)
    async def people_latest(self): return await self._api_request("GET", f"{self.BASE_URL}/person/latest")
    async def people_popular(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/person/popular", params=kwargs)