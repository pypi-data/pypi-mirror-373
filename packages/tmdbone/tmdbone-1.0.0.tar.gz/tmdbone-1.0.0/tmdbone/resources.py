"""
Defines all TMDb resource classes which map to the available API endpoints,
providing the library's clean, chainable, object-oriented interface.
"""
from typing import Optional, List, Literal

class TMDbOneClient: pass

class _Resource:
    """Base class for all TMDb resources, handling path construction and requests."""
    def __init__(self, client: "TMDbOneClient", path_segments: List[str]):
        self._client = client
        self._path = "/" + "/".join(map(str, path_segments))
    async def _get(self, path_suffix: str = "", params: Optional[dict] = None) -> Optional[dict]:
        url = f"{self._client.BASE_URL}{self._path}{path_suffix}"
        return await self._client._api_request("GET", url, params)

class Movie(_Resource):
    """Represents a specific movie on TMDb."""
    def __init__(self, client: "TMDbOneClient", movie_id: int): super().__init__(client, ["movie", movie_id])
    async def details(self, **kwargs): return await self._get(params=kwargs)
    async def alternative_titles(self, **kwargs): return await self._get("/alternative_titles", params=kwargs)
    async def credits(self, **kwargs): return await self._get("/credits", params=kwargs)
    async def external_ids(self, **kwargs): return await self._get("/external_ids", params=kwargs)
    async def images(self, **kwargs): return await self._get("/images", params=kwargs)
    async def keywords(self, **kwargs): return await self._get("/keywords", params=kwargs)
    async def lists(self, **kwargs): return await self._get("/lists", params=kwargs)
    async def recommendations(self, **kwargs): return await self._get("/recommendations", params=kwargs)
    async def release_dates(self, **kwargs): return await self._get("/release_dates", params=kwargs)
    async def reviews(self, **kwargs): return await self._get("/reviews", params=kwargs)
    async def similar(self, **kwargs): return await self._get("/similar", params=kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", params=kwargs)
    async def videos(self, **kwargs): return await self._get("/videos", params=kwargs)
    async def watch_providers(self, **kwargs): return await self._get("/watch/providers", params=kwargs)

class TV(_Resource):
    """Represents a specific TV show on TMDb."""
    def __init__(self, client: "TMDbOneClient", tv_id: int): super().__init__(client, ["tv", tv_id]); self.tv_id = tv_id
    def season(self, season_number: int): return Season(self._client, self.tv_id, season_number)
    async def details(self, **kwargs): return await self._get(params=kwargs)
    async def aggregate_credits(self, **kwargs): return await self._get("/aggregate_credits", params=kwargs)
    async def alternative_titles(self, **kwargs): return await self._get("/alternative_titles", params=kwargs)
    async def content_ratings(self, **kwargs): return await self._get("/content_ratings", params=kwargs)
    async def credits(self, **kwargs): return await self._get("/credits", params=kwargs)
    async def external_ids(self, **kwargs): return await self._get("/external_ids", params=kwargs)
    async def images(self, **kwargs): return await self._get("/images", params=kwargs)
    async def keywords(self, **kwargs): return await self._get("/keywords", params=kwargs)
    async def recommendations(self, **kwargs): return await self._get("/recommendations", params=kwargs)
    async def reviews(self, **kwargs): return await self._get("/reviews", params=kwargs)
    async def screened_theatrically(self, **kwargs): return await self._get("/screened_theatrically", params=kwargs)
    async def similar(self, **kwargs): return await self._get("/similar", params=kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", params=kwargs)
    async def videos(self, **kwargs): return await self._get("/videos", params=kwargs)
    async def watch_providers(self, **kwargs): return await self._get("/watch/providers", params=kwargs)

class Season(_Resource):
    """Represents a specific season of a TV show."""
    def __init__(self, client: "TMDbOneClient", tv_id: int, season_number: int): super().__init__(client, ["tv", tv_id, "season", season_number]); self.tv_id, self.season_number = tv_id, season_number
    def episode(self, episode_number: int): return Episode(self._client, self.tv_id, self.season_number, episode_number)
    async def details(self, **kwargs): return await self._get(params=kwargs)
    async def aggregate_credits(self, **kwargs): return await self._get("/aggregate_credits", params=kwargs)
    async def credits(self, **kwargs): return await self._get("/credits", params=kwargs)
    async def external_ids(self, **kwargs): return await self._get("/external_ids", params=kwargs)
    async def images(self, **kwargs): return await self._get("/images", params=kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", params=kwargs)
    async def videos(self, **kwargs): return await self._get("/videos", params=kwargs)

class Episode(_Resource):
    """Represents a specific episode of a TV season."""
    def __init__(self, client: "TMDbOneClient", tv_id: int, season_number: int, episode_number: int): super().__init__(client, ["tv", tv_id, "season", season_number, "episode", episode_number])
    async def details(self, **kwargs): return await self._get(params=kwargs)
    async def credits(self, **kwargs): return await self._get("/credits", params=kwargs)
    async def external_ids(self, **kwargs): return await self._get("/external_ids", params=kwargs)
    async def images(self, **kwargs): return await self._get("/images", params=kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", params=kwargs)
    async def videos(self, **kwargs): return await self._get("/videos", params=kwargs)

class Person(_Resource):
    """Represents a specific person (cast or crew) on TMDb."""
    def __init__(self, client: "TMDbOneClient", person_id: int): super().__init__(client, ["person", person_id])
    async def details(self, **kwargs): return await self._get(params=kwargs)
    async def images(self, **kwargs): return await self._get("/images", params=kwargs)
    async def movie_credits(self, **kwargs): return await self._get("/movie_credits", params=kwargs)
    async def tv_credits(self, **kwargs): return await self._get("/tv_credits", params=kwargs)
    async def combined_credits(self, **kwargs): return await self._get("/combined_credits", params=kwargs)
    async def external_ids(self, **kwargs): return await self._get("/external_ids", params=kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", params=kwargs)

class Collection(_Resource):
    """Represents a movie collection on TMDb."""
    def __init__(self, client: "TMDbOneClient", collection_id: int): super().__init__(client, ["collection", collection_id])
    async def details(self, **kwargs): return await self._get(params=kwargs)
    async def images(self, **kwargs): return await self._get("/images", params=kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", params=kwargs)

class Company(_Resource):
    """Represents a production company on TMDb."""
    def __init__(self, client: "TMDbOneClient", company_id: int): super().__init__(client, ["company", company_id])
    async def details(self, **kwargs): return await self._get(params=kwargs)
    async def alternative_names(self, **kwargs): return await self._get("/alternative_names", params=kwargs)
    async def images(self, **kwargs): return await self._get("/images", params=kwargs)

class Network(_Resource):
    """Represents a TV network on TMDb."""
    def __init__(self, client: "TMDbOneClient", network_id: int): super().__init__(client, ["network", network_id])
    async def details(self, **kwargs): return await self._get(params=kwargs)
    async def images(self, **kwargs): return await self._get("/images", params=kwargs)
    async def alternative_names(self, **kwargs): return await self._get("/alternative_names", params=kwargs)

class Keyword(_Resource):
    """Represents a keyword on TMDb."""
    def __init__(self, client: "TMDbOneClient", keyword_id: int): super().__init__(client, ["keyword", keyword_id])
    async def details(self, **kwargs): return await self._get(params=kwargs)
    async def movies(self, **kwargs): return await self._get("/movies", params=kwargs)

class Review(_Resource):
    """Represents a user review on TMDb."""
    def __init__(self, client: "TMDbOneClient", review_id: str): super().__init__(client, ["review", review_id])
    async def details(self, **kwargs): return await self._get(params=kwargs)

class Credit(_Resource):
    """Represents a specific credit record on TMDb."""
    def __init__(self, client: "TMDbOneClient", credit_id: str): super().__init__(client, ["credit", credit_id])
    async def details(self, **kwargs): return await self._get(params=kwargs)

class Find(_Resource):
    """Represents the /find endpoint for finding TMDb IDs from external IDs."""
    def __init__(self, client: "TMDbOneClient", external_id: str): super().__init__(client, ["find", external_id])
    async def by(self, source: str = "imdb_id", **kwargs): params = kwargs; params['external_source'] = source; return await self._get(params=params)

class Discover(_Resource):
    """Represents the /discover endpoint for advanced filtering."""
    def __init__(self, client: "TMDbOneClient"): super().__init__(client, ["discover"])
    async def movie(self, **kwargs): return await self._get("/movie", params=kwargs)
    async def tv(self, **kwargs): return await self._get("/tv", params=kwargs)

class Search(_Resource):
    """Represents the /search endpoint."""
    def __init__(self, client: "TMDbOneClient"): super().__init__(client, ["search"])
    async def movie(self, query: str, **kwargs): params=kwargs; params['query']=query; return await self._get("/movie", params=params)
    async def tv(self, query: str, **kwargs): params=kwargs; params['query']=query; return await self._get("/tv", params=params)
    async def person(self, query: str, **kwargs): params=kwargs; params['query']=query; return await self._get("/person", params=params)
    async def company(self, query: str, **kwargs): params=kwargs; params['query']=query; return await self._get("/company", params=params)
    async def collection(self, query: str, **kwargs): params=kwargs; params['query']=query; return await self._get("/collection", params=params)
    async def keyword(self, query: str, **kwargs): params=kwargs; params['query']=query; return await self._get("/keyword", params=params)
    async def multi(self, query: str, **kwargs): params=kwargs; params['query']=query; return await self._get("/multi", params=params)

class Trending(_Resource):
    """Represents the /trending endpoint."""
    def __init__(self, client: "TMDbOneClient"): super().__init__(client, ["trending"])
    async def all(self, time_window: Literal["day", "week"] = "day"): return await self._get(f"/all/{time_window}")
    async def movie(self, time_window: Literal["day", "week"] = "day"): return await self._get(f"/movie/{time_window}")
    async def tv(self, time_window: Literal["day", "week"] = "day"): return await self._get(f"/tv/{time_window}")
    async def person(self, time_window: Literal["day", "week"] = "day"): return await self._get(f"/person/{time_window}")

class Genre(_Resource):
    """Represents the /genre endpoints for listing genres."""
    def __init__(self, client: "TMDbOneClient"): super().__init__(client, ["genre"])
    async def movie_list(self, **kwargs): return await self._get("/movie/list", params=kwargs)
    async def tv_list(self, **kwargs): return await self._get("/tv/list", params=kwargs)

class Configuration(_Resource):
    """Represents the /configuration endpoints for API-wide settings."""
    def __init__(self, client: "TMDbOneClient"): super().__init__(client, ["configuration"])
    async def api_details(self): return await self._get()
    async def countries(self): return await self._get("/countries")
    async def jobs(self): return await self._get("/jobs")
    async def languages(self): return await self._get("/languages")
    async def primary_translations(self): return await self._get("/primary_translations")
    async def timezones(self): return await self._get("/timezones")

class Certification(_Resource):
    """Represents the /certification endpoints for content ratings."""
    def __init__(self, client: "TMDbOneClient"): super().__init__(client, ["certification"])
    async def movie_list(self): return await self._get("/movie/list")
    async def tv_list(self): return await self._get("/tv/list")