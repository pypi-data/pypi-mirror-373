"""A demonstration of the key features of the tmdbone library."""

import asyncio
import logging
import os
from tmdbone import TMDbOneClient, TMDbAPIError

# Configure logging to see the library's resilience and other output.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    """Showcases various features of the TMDbOneClient."""
    
    # Load API keys from the TMDB_API_KEYS environment variable.
    api_keys_str = os.getenv("TMDB_API_KEYS")
    
    if not api_keys_str:
        logging.error("FATAL: The TMDB_API_KEYS environment variable is not set.")
        logging.error("Example usage: export TMDB_API_KEYS=\"key1,key2\"")
        return

    api_keys = [key.strip() for key in api_keys_str.split(',')]

    print("--- Initializing TMDbOneClient ---")
    client = TMDbOneClient(api_keys=api_keys, language="en-US")

    try:
        # --- 1. Get Movie Details & Keywords ---
        print("\n--- 1. Fetching Movie Details & Keywords ---")
        dune_movie = client.movie(438631)
        details = await dune_movie.details()
        if details: print(f"Successfully fetched: {details['title']}")
        
        keywords = await dune_movie.keywords()
        if keywords: print(f"Keywords for Dune: {[kw['name'] for kw in keywords['keywords'][:3]]}")

        # --- 2. Chaining to get deep TV data ---
        print("\n--- 2. Fetching TV Episode data in a different language ---")
        mando_episode = await client.tv(82856).season(1).episode(1).details(language='de-DE')
        if mando_episode: print(f"German title for The Mandalorian S01E01: '{mando_episode['name']}'")

        # --- 3. Using Top-Level Endpoints ---
        print("\n--- 3. Using Top-Level Endpoints ---")
        popular_movies = await client.movies_popular(region="US")
        if popular_movies: print(f"One of the most popular movies now in the US is: {popular_movies['results']['title']}")
        
        config = await client.configuration().api_details()
        if config: print(f"TMDb Base Image URL: {config['images']['secure_base_url']}")

        # --- 4. Get a specific Keyword's details ---
        print("\n--- 4. Fetching details for a specific Keyword (ID: 1721 'slasher') ---")
        slasher_keyword = await client.keyword(1721).details()
        if slasher_keyword: print(f"Keyword name: {slasher_keyword['name']}")

    except TMDbAPIError as e:
        logging.error(f"An unrecoverable API error occurred: {e}")
    finally:
        print("\n--- Closing client session ---")
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())