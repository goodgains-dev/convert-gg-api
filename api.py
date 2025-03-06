from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uvicorn
import os
from dotenv import load_dotenv

from config import CONFIGS
from utils.scraper_utils import get_browser_config, get_llm_strategy
from crawl4ai import AsyncWebCrawler
from utils.scraper_utils import fetch_and_process_page

load_dotenv()

# API Key security
API_KEY_NAME = "X-API-Key"
API_KEY = os.environ.get("API_KEY", "default_api_key_change_me")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="Invalid API Key"
    )

app = FastAPI(
    title="DeepSeek Web Crawler API",
    description="API for web crawling with LLM-powered data extraction",
    version="1.0.0"
)

class CrawlerRequest(BaseModel):
    config_name: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None

class CrawlerResponse(BaseModel):
    items: List[Dict[str, Any]]
    stats: Dict[str, Any]

@app.post("/crawl", response_model=CrawlerResponse)
async def crawl(request: CrawlerRequest, api_key: APIKey = Depends(get_api_key)):
    """
    Crawl a website using either a predefined configuration or a custom configuration.
    
    Args:
        request: CrawlerRequest containing either config_name or custom_config
    
    Returns:
        CrawlerResponse containing extracted items and usage statistics
    """
    if not request.config_name and not request.custom_config:
        raise HTTPException(
            status_code=400,
            detail="Either config_name or custom_config must be provided"
        )

    # Get configuration
    if request.config_name:
        if request.config_name not in CONFIGS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown configuration: {request.config_name}"
            )
        config = CONFIGS[request.config_name]
    else:
        config = request.custom_config

    # Initialize configurations
    browser_config = get_browser_config(config["CRAWLER_CONFIG"])
    llm_strategy = get_llm_strategy(config["LLM_CONFIG"])
    session_id = "api_crawl_session"

    # Initialize state variables
    page_number = 1
    all_items = []
    seen_titles = set()
    
    required_keys = config["REQUIRED_KEYS"]
    multi_page = config["CRAWLER_CONFIG"]["MULTI_PAGE"]
    max_pages = config["CRAWLER_CONFIG"].get("MAX_PAGES", 1)
    delay = config["CRAWLER_CONFIG"].get("DELAY_BETWEEN_PAGES", 2)

    # Start the web crawler context
    async with AsyncWebCrawler(config=browser_config) as crawler:
        while True:
            # Fetch and process data from the current page
            items, no_results_found = await fetch_and_process_page(
                crawler,
                page_number,
                config["BASE_URL"],
                config["CSS_SELECTOR"],
                llm_strategy,
                session_id,
                required_keys,
                seen_titles,
            )

            if no_results_found:
                break

            if not items:
                break

            # Add the items from this page to the total list
            all_items.extend(items)
            
            # Check if we should continue to next page
            if not multi_page or page_number >= max_pages:
                break
                
            page_number += 1
            await asyncio.sleep(delay)

    # Get LLM usage statistics
    usage_stats = llm_strategy.get_usage_stats()

    return CrawlerResponse(
        items=all_items,
        stats={
            "total_items": len(all_items),
            "pages_crawled": page_number,
            "llm_usage": usage_stats
        }
    )

@app.get("/configs")
async def list_configs(api_key: APIKey = Depends(get_api_key)):
    """List all available predefined configurations."""
    return {
        "configs": [
            {
                "name": name,
                "description": "Custom configuration" if name not in ["dental", "minimal", "detailed"] else f"For {name} scraping"
            }
            for name in CONFIGS.keys()
        ]
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
