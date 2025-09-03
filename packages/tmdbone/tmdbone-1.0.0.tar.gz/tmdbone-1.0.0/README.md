# TMDbOne

[![PyPI version](https://badge.fury.io/py/tmdbone.svg)](https://pypi.org/project/tmdbone/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

TMDbOne is a powerful, asynchronous Python library for interacting with The Movie Database (TMDb) API.

## Features

- **Comprehensive:** Provides access to all data retrieval endpoints from the TMDb API v3.
- **Resilient:** Transparently handles API key rotation, automatic request retries, and rate-limit cooldowns.
- **Asynchronous:** Built from the ground up with `asyncio` and `aiohttp` for high-performance applications.
- **Modern:** A clean, chainable, object-oriented interface that mirrors the TMDb API's structure.

## Installation

```bash
pip install tmdbone
```

## Quick Start

```python
import asyncio
import os
from tmdbone import TMDbOneClient, TMDbAPIError

async def main():
    # Securely load keys from an environment variable (e.g., "key1,key2")
    api_keys_str = os.getenv("TMDB_API_KEYS")
    if not api_keys_str:
        raise ValueError("TMDB_API_KEYS environment variable is not set.")
    api_keys = [key.strip() for key in api_keys_str.split(',')]

    # Initialize the client with a global language
    client = TMDbOneClient(api_keys=api_keys, language="en-US")

    try:
        # Get details for the movie "Inception" (ID: 27205)
        inception = client.movie(27205)
        
        details = await inception.details()
        print(f"Title: {details['title']}")

        # Get external IDs (like IMDb ID)
        external_ids = await inception.external_ids()
        print(f"IMDb ID: {external_ids['imdb_id']}")

    except TMDbAPIError as e:
        print(f"An API error occurred: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Usage

### Chaining for TV Shows

The interface allows for intuitive chaining to access nested resources.

```python
# Get details for Season 2, Episode 3 of "The Mandalorian"
episode_details = await client.tv(82856).season(2).episode(3).details()
print(episode_details['name'])
```

### Top-Level Endpoints

Access general API endpoints directly from the client.

```python
# Get a list of popular movies
popular_movies = await client.movies_popular(region="US")

# Get API configuration details
api_config = await client.configuration().api_details()
```