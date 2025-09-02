import httpx
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import logging
import json
import os
from dotenv import load_dotenv

from finder_enrichment_db_contracts import (
    Address,
    AddressCreate,
    FloorplanAnalyticsRunCreate,
    ImageAnalyticsRunCreate,
    ImageCreateWithData,
    Location,
    LocationCreate,
    Image,
    ImageCreateNested,
    Floorplan,
    FloorplanCreateNested,
    EstateAgent,
    EstateAgentCreate,
    Listing,
    ListingCreate,
    EnrichmentOrchestrationSet,
    EnrichmentOrchestrationSetCreate,
    EnrichmentOrchestrationRun,
    EnrichmentOrchestrationRunCreate,
    DescriptionAnalyticsRun,
    DescriptionAnalyticsRunCreate,
    ImageAnalyticsRun,
    FloorplanAnalyticsRun,
    Prompt,
    PromptCreate
)

load_dotenv()

DEFAULT_BASE_URL = os.getenv("ENRICHMENT_DB_BASE_URL", "http://localhost:8200")

class FinderEnrichmentDBAPIClient:
    """A client for interacting with the Finder Enrichment DB API."""
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, client: Optional[httpx.Client] = None):
        self.base_url = base_url or DEFAULT_BASE_URL
        self.api_key = api_key or os.getenv("LISTINGS_DB_API_KEY")
        self.client = client or httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(30.0, connect=None),
            follow_redirects=True
        )

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        
        # Set up headers
        headers = kwargs.get("headers", {})
        if "content" in kwargs:
            headers["Content-Type"] = "application/json"
        
        # Add API key authentication if provided
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        kwargs["headers"] = headers
            
        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logging.error(f"Error during request to {e.request.url}: {e}")
            raise

    def get_listings(self, skip: int = 0, limit: int = 100) -> List[Listing]:
        """
        Retrieves a list of listings.
        """
        endpoint = f"/api/listings/?skip={skip}&limit={limit}"
        response = self._request("GET", endpoint)
        return [Listing(**item) for item in response] if response else []

    def get_listing(self, listing_id: int) -> Optional[Listing]:
        """
        Retrieves a specific listing by its ID.
        """
        endpoint = f"/api/listings/{listing_id}"
        response = self._request("GET", endpoint)
        return Listing(**response) if response else None

    def create_listing(self, listing: ListingCreate) -> Listing:
        """Creates a new listing."""
        response = self._request("POST", "/api/listings/", content=listing.model_dump_json(exclude_unset=True))
        return Listing(**response)

    def get_image(self, image_id: int) -> Optional[Image]:
        """
        Retrieves a specific image by its ID.
        """
        endpoint = f"/api/images/{image_id}"
        response = self._request("GET", endpoint)
        return Image(**response) if response else None

    def add_image_to_listing(self, listing_id: int, image: ImageCreateWithData) -> Image:
        """Adds an image to a listing."""
        endpoint = f"/api/listings/{listing_id}/images/"
        response = self._request("POST", endpoint, content=image.model_dump_json(exclude_unset=True))
        return Image(**response)

    def create_estate_agent(self, estate_agent: EstateAgentCreate) -> EstateAgent:
        """Creates a new estate agent."""
        response = self._request("POST", "/api/estate-agents/", content=estate_agent.model_dump_json(exclude_unset=True))
        return EstateAgent(**response)

    def get_estate_agent(self, estate_agent_id: int) -> Optional[EstateAgent]:
        """
        Retrieves a specific estate agent by its ID.
        """
        endpoint = f"/api/estate-agents/{estate_agent_id}"
        response = self._request("GET", endpoint)
        return EstateAgent(**response) if response else None

    def get_estate_agents(self, skip: int = 0, limit: int = 100) -> List[EstateAgent]:
        """
        Retrieves a list of estate agents.
        """
        endpoint = f"/api/estate-agents/?skip={skip}&limit={limit}"
        response = self._request("GET", endpoint)
        return [EstateAgent(**agent) for agent in response] if response else []

    def create_orchestration_set(self, orchestration_set: EnrichmentOrchestrationSetCreate) -> EnrichmentOrchestrationSet:
        """Creates a new enrichment orchestration set."""
        response = self._request("POST", "/api/enrichment/orchestration-sets/", content=orchestration_set.model_dump_json(exclude_unset=True))
        return EnrichmentOrchestrationSet(**response)

    def get_orchestration_set(self, set_id: int) -> Optional[EnrichmentOrchestrationSet]:
        """Retrieves a specific enrichment orchestration set by its ID."""
        endpoint = f"/api/enrichment/orchestration-sets/{set_id}"
        response = self._request("GET", endpoint)
        return EnrichmentOrchestrationSet(**response) if response else None

    def get_orchestration_sets(self, skip: int = 0, limit: int = 100) -> List[EnrichmentOrchestrationSet]:
        """
        Retrieves a list of enrichment orchestration sets.
        """
        endpoint = f"/api/enrichment/orchestration-sets?skip={skip}&limit={limit}"
        response = self._request("GET", endpoint)
        return [EnrichmentOrchestrationSet(**item) for item in response] if response else []

    def create_orchestration_run(self, orchestration_run: EnrichmentOrchestrationRunCreate) -> EnrichmentOrchestrationRun:
        """Creates a new enrichment orchestration run."""
        response = self._request("POST", "/api/enrichment/orchestration-runs/", content=orchestration_run.model_dump_json(exclude_unset=True))
        return EnrichmentOrchestrationRun(**response)

    def get_orchestration_run(self, run_id: int) -> Optional[EnrichmentOrchestrationRun]:
        """Retrieves a specific enrichment orchestration run by its ID."""
        endpoint = f"/api/enrichment/orchestration-runs/{run_id}"
        response = self._request("GET", endpoint)
        return EnrichmentOrchestrationRun(**response) if response else None

    def get_orchestration_runs(self, skip: int = 0, limit: int = 100, order_by: str = "timestamp", desc: bool = True) -> List[EnrichmentOrchestrationRun]:
        """
        Retrieves a list of enrichment orchestration runs.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by (timestamp, created_at, updated_at, id)
            desc: Sort in descending order (newest first)
        """
        endpoint = f"/api/enrichment/orchestration-runs?skip={skip}&limit={limit}&order_by={order_by}&desc={str(desc).lower()}"
        response = self._request("GET", endpoint)
        return [EnrichmentOrchestrationRun(**item) for item in response] if response else []
    
    def create_description_analytics(self, description_analytics: DescriptionAnalyticsRunCreate) -> DescriptionAnalyticsRun:
        """Creates a new description analytics run."""
        response = self._request("POST", "/api/enrichment/description-analytics/", content=description_analytics.model_dump_json(exclude_unset=True))
        return DescriptionAnalyticsRun(**response)
    
    def get_description_analytics(self, skip: int = 0, limit: int = 100, order_by: str = "timestamp", desc: bool = True) -> List[DescriptionAnalyticsRun]:
        """
        Retrieves a list of description analytics runs.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by (timestamp, created_at, updated_at, id)
            desc: Sort in descending order (newest first)
        """
        endpoint = f"/api/enrichment/description-analytics?skip={skip}&limit={limit}&order_by={order_by}&desc={str(desc).lower()}"
        response = self._request("GET", endpoint)
        return [DescriptionAnalyticsRun(**item) for item in response] if response else []

    def get_description_analytics_by_id(self, analytics_id: int) -> Optional[DescriptionAnalyticsRun]:
        """
        Retrieves a specific description analytics run by its ID.
        """
        endpoint = f"/api/enrichment/description-analytics/{analytics_id}"
        response = self._request("GET", endpoint)
        return DescriptionAnalyticsRun(**response) if response else None
    
    def get_description_analytics_by_original_listing_id(self, original_listing_id: int) -> List[DescriptionAnalyticsRun]:
        """
        Retrieves a list of description analytics runs by their original listing ID.
        """
        endpoint = f"/api/enrichment/description-analytics/original-listing/{original_listing_id}"
        response = self._request("GET", endpoint)
        return [DescriptionAnalyticsRun(**item) for item in response] if response else []
    
    def create_image_analytics(self, image_analytics: ImageAnalyticsRunCreate) -> ImageAnalyticsRun:
        """Creates a new image analytics run."""
        response = self._request("POST", "/api/enrichment/image-analytics/", content=image_analytics.model_dump_json(exclude_unset=True))
        return ImageAnalyticsRun(**response)
    
    def get_image_analytics(self, skip: int = 0, limit: int = 100, order_by: str = "timestamp", desc: bool = True) -> List[ImageAnalyticsRun]:
        """
        Retrieves a list of image analytics runs.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by (timestamp, created_at, updated_at, id)
            desc: Sort in descending order (newest first)
        """
        endpoint = f"/api/enrichment/image-analytics?skip={skip}&limit={limit}&order_by={order_by}&desc={str(desc).lower()}"
        response = self._request("GET", endpoint)
        return [ImageAnalyticsRun(**item) for item in response] if response else []
    
    
    def get_image_analytics_with_thumbnails(self, skip: int = 0, limit: int = 100, thumbnail_size: int = 32, order_by: str = "timestamp", desc: bool = True) -> List[ImageAnalyticsRun]:
        """
        Retrieves a list of image analytics runs with thumbnails.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            thumbnail_size: Size of thumbnail images
            order_by: Field to order by (timestamp, created_at, updated_at, id)
            desc: Sort in descending order (newest first)
        """
        endpoint = f"/api/enrichment/image-analytics/with-thumbnails?skip={skip}&limit={limit}&thumbnail_size={thumbnail_size}&order_by={order_by}&desc={str(desc).lower()}"
        response = self._request("GET", endpoint)
        return [ImageAnalyticsRun(**item) for item in response] if response else []
    

    def get_image_analytics_without_images(self, skip: int = 0, limit: int = 100, order_by: str = "timestamp", desc: bool = True) -> List[ImageAnalyticsRun]:
        """
        Retrieves a list of image analytics runs without images.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by (timestamp, created_at, updated_at, id)
            desc: Sort in descending order (newest first)
        """
        endpoint = f"/api/enrichment/image-analytics/without-images?skip={skip}&limit={limit}&order_by={order_by}&desc={str(desc).lower()}"
        response = self._request("GET", endpoint)
        return [ImageAnalyticsRun(**item) for item in response] if response else []


    def get_image_analytics_by_id(self, analytics_id: int) -> Optional[ImageAnalyticsRun]:
        """
        Retrieves a specific image analytics run by its ID.
        """
        endpoint = f"/api/enrichment/image-analytics/{analytics_id}"
        response = self._request("GET", endpoint)
        return ImageAnalyticsRun(**response) if response else None

    def get_image_analytics_by_original_image_id(self, original_image_id: int) -> List[ImageAnalyticsRun]:
        """
        Retrieves a list of image analytics runs by their original image ID.
        """
        endpoint = f"/api/enrichment/image-analytics/original-image/{original_image_id}"
        response = self._request("GET", endpoint)
        return [ImageAnalyticsRun(**item) for item in response] if response else []
    
    def create_floorplan_analytics(self, floorplan_analytics: FloorplanAnalyticsRunCreate) -> FloorplanAnalyticsRun:
        """Creates a new floorplan analytics run."""
        response = self._request("POST", "/api/enrichment/floorplan-analytics/", content=floorplan_analytics.model_dump_json(exclude_unset=True))
        return FloorplanAnalyticsRun(**response)
    
    def get_floorplan_analytics(self, skip: int = 0, limit: int = 100, order_by: str = "timestamp", desc: bool = True) -> List[FloorplanAnalyticsRun]:
        """
        Retrieves a list of floorplan analytics runs.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by (timestamp, created_at, updated_at, id)
            desc: Sort in descending order (newest first)
        """
        endpoint = f"/api/enrichment/floorplan-analytics?skip={skip}&limit={limit}&order_by={order_by}&desc={str(desc).lower()}"
        response = self._request("GET", endpoint)
        return [FloorplanAnalyticsRun(**item) for item in response] if response else []

    def get_floorplan_analytics_by_id(self, analytics_id: int) -> Optional[FloorplanAnalyticsRun]:
        """Retrieves a specific floorplan analytics run by its ID."""
        endpoint = f"/api/enrichment/floorplan-analytics/{analytics_id}"
        response = self._request("GET", endpoint)
        return FloorplanAnalyticsRun(**response) if response else None

    def get_floorplan_analytics_by_original_floorplan_id(self, original_floorplan_id: int) -> List[FloorplanAnalyticsRun]:
        """
        Retrieves a list of floorplan analytics runs by their original floorplan ID.
        """
        endpoint = f"/api/enrichment/floorplan-analytics/original-floorplan/{original_floorplan_id}"
        response = self._request("GET", endpoint)
        return [FloorplanAnalyticsRun(**item) for item in response] if response else []
    
    def get_prompt(self, prompt_id: int) -> Optional[Prompt]:
        """Retrieves a specific prompt by its ID."""
        endpoint = f"/api/prompts/{prompt_id}"
        response = self._request("GET", endpoint)
        return Prompt(**response) if response else None
    
    def get_prompts_by_name(self, prompt_name: str) -> List[Prompt]:
        """Retrieves a list of prompts by their name."""
        endpoint = f"/api/prompts/name/{prompt_name}"
        response = self._request("GET", endpoint)
        return [Prompt(**item) for item in response] if response else []
    
    def get_latest_prompt_by_name(self, prompt_name: str) -> Optional[Prompt]:
        """Retrieves the latest prompt by its name."""
        endpoint = f"/api/prompts/name/{prompt_name}/latest"
        response = self._request("GET", endpoint)
        return Prompt(**response) if response else None
    
    def create_or_increment_prompt(self, prompt: PromptCreate) -> Prompt:
        """Creates a new or increments an existing prompt."""
        response = self._request("POST", "/api/prompts/", content=prompt.model_dump_json(exclude_unset=True))
        return Prompt(**response)

    def health_check(self) -> dict:
        """Performs a health check on the API."""
        response = self._request("GET", "/health")
        return response if response else {"status": "unhealthy"}

    def close(self):
        """Closes the underlying HTTP client."""
        self.client.close() 
