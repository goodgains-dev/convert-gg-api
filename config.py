# config.py

# Default configuration for dental clinics example
DEFAULT_CONFIG = {
    "BASE_URL": "https://www.opencare.com/dentists/new-york-ny/",
    "CSS_SELECTOR": "div[data-test='search-result-card']",  # Updated selector for OpenCare dental listings
    "REQUIRED_KEYS": [
        "name",
        "location",
        "description",
        "rating",
    ],
    # Optional fields that can be enabled/disabled
    "OPTIONAL_KEYS": [
        "phone",
        "website",
        "hours",
        "specialties",
        "reviews",
        "price",
    ],
    # Crawler settings
    "CRAWLER_CONFIG": {
        "MULTI_PAGE": True,  # Set to False for single page scraping
        "MAX_PAGES": 5,  # Maximum number of pages to scrape (ignored if MULTI_PAGE is False)
        "DELAY_BETWEEN_PAGES": 2,  # Delay in seconds between page requests
        "HEADLESS": False,  # Run browser in visible mode for debugging
        "CACHE_ENABLED": False,  # Enable/disable caching
        "VERBOSE_LOGGING": True,  # Enable detailed logging
    },
    # LLM Configuration
    "LLM_CONFIG": {
        "PROVIDER": "groq/deepseek-r1-distill-llama-70b",
        "EXTRACTION_TYPE": "schema",
        "INPUT_FORMAT": "markdown",
        "INSTRUCTION": """
        Extract dental clinic information from the content. For each clinic, find:

        Required information:
        - Name: The full name of the dental clinic or dentist's practice
        - Location: The complete address of the clinic
        - Description: A brief description of the clinic, their services, or the dentist's expertise
        - Rating: The numerical rating (out of 5 stars) if available

        Additional information if present:
        - Phone number
        - Website URL
        - Operating hours
        - List of dental specialties or services offered
        - Number of reviews
        - Price range or insurance information

        Extract this information for each dental clinic card or listing found in the content.
        """,
    }
}

import os

# Example configurations for different use cases
CONFIGS = {
    "dental": DEFAULT_CONFIG,
    "minimal": {
        **DEFAULT_CONFIG,
        "CRAWLER_CONFIG": {
            **DEFAULT_CONFIG["CRAWLER_CONFIG"],
            "MULTI_PAGE": False,
            "VERBOSE_LOGGING": False,
            "HEADLESS": True,
        },
        "OPTIONAL_KEYS": [],  # Only collect required fields
    },
    "detailed": {
        **DEFAULT_CONFIG,
        "CRAWLER_CONFIG": {
            **DEFAULT_CONFIG["CRAWLER_CONFIG"],
            "MAX_PAGES": 10,
            "DELAY_BETWEEN_PAGES": 3,
        },
        "REQUIRED_KEYS": DEFAULT_CONFIG["REQUIRED_KEYS"] + ["phone", "website"],
    },
    "test": {
        **DEFAULT_CONFIG,
        "BASE_URL": "file:///" + os.path.abspath("test_products.html").replace("\\", "/"),
        "CSS_SELECTOR": "div.product",
        "REQUIRED_KEYS": [
            "title",
            "price",
            "url"
        ],
        "OPTIONAL_KEYS": [
            "description"
        ],
        "CRAWLER_CONFIG": {
            **DEFAULT_CONFIG["CRAWLER_CONFIG"],
            "MULTI_PAGE": False,
            "HEADLESS": False,
            "VERBOSE_LOGGING": True
        },
        "LLM_CONFIG": {
            **DEFAULT_CONFIG["LLM_CONFIG"],
            "INSTRUCTION": """
            Extract information from each product. For each item, find:

            Required information:
            - Title: The product title (h2.title text)
            - Price: The price text
            - URL: The product URL (a.url href)

            Additional information if present:
            - Description: The product description

            Extract this information for each product found in the content.
            """
        }
    }
}
