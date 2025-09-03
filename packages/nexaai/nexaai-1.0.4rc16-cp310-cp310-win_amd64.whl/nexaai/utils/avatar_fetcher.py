"""Utility for fetching avatar URLs from HuggingFace."""

import logging
from typing import Dict, Optional
import httpx

logger = logging.getLogger(__name__)


def fetch_avatar_urls_from_hf_api(query: str, custom_endpoint: Optional[str] = None) -> Dict[str, str]:
    """
    Fetch avatar URLs from HuggingFace models-json endpoint.
    
    Args:
        query: Search query to fetch models for
        custom_endpoint: Optional custom HuggingFace endpoint
        
    Returns:
        Dictionary mapping author names to avatar URLs
    """
    avatar_map = {}
    try:
        # Use the base URL from the configured endpoint
        base_url = custom_endpoint if custom_endpoint else "https://huggingface.co"
        
        # Build the URL with query parameter
        url = f"{base_url}/models-json?sort=trending&search={query}&withCount=true"
        
        # Make the HTTP request with a timeout
        with httpx.Client(timeout=2.0) as client:
            response = client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                
                # Build a map of author names to avatar URLs
                for model in models:
                    author = model.get("author")
                    author_data = model.get("authorData", {})
                    avatar_url = author_data.get("avatarUrl")
                    
                    if author and avatar_url:
                        # Handle relative URLs by prepending appropriate base URL
                        if avatar_url.startswith("/"):
                            avatar_url = f"{base_url}{avatar_url}"
                        avatar_map[author] = avatar_url
                
                logger.debug(f"Fetched {len(avatar_map)} avatar URLs from HuggingFace API")
            else:
                logger.warning(f"Failed to fetch avatar URLs: HTTP {response.status_code}")
                
    except Exception as e:
        logger.warning(f"Error fetching avatar URLs from HuggingFace API: {e}")
        # Return empty map on error - we'll fall back to default behavior
    
    return avatar_map


def get_avatar_url_for_repo(repo_id: str, search_query: Optional[str] = None, 
                            custom_endpoint: Optional[str] = None) -> Optional[str]:
    """
    Get avatar URL for a repository ID.
    
    This method tries multiple strategies:
    1. If search_query is provided, fetch from HuggingFace API with that query
    2. Try fetching with the full repo_id as query
    3. Try fetching with just the organization name as query
    4. Fall back to CDN URL pattern
    
    Args:
        repo_id: Repository ID in format "owner/repo"
        search_query: Optional search query to use for fetching avatars
        custom_endpoint: Optional custom HuggingFace endpoint
        
    Returns:
        Avatar URL or None if not found
    """
    if "/" not in repo_id:
        return None
        
    org_name = repo_id.split("/")[0]
    
    # Try with search query if provided
    if search_query:
        avatar_map = fetch_avatar_urls_from_hf_api(search_query, custom_endpoint)
        avatar_url = avatar_map.get(org_name)
        if avatar_url:
            return avatar_url
    
    # Try with full repo_id
    avatar_map = fetch_avatar_urls_from_hf_api(repo_id, custom_endpoint)
    avatar_url = avatar_map.get(org_name)
    if avatar_url:
        return avatar_url
    
    # Try with just organization name
    avatar_map = fetch_avatar_urls_from_hf_api(org_name, custom_endpoint)
    avatar_url = avatar_map.get(org_name)
    if avatar_url:
        return avatar_url
    
    # Fallback to CDN URL pattern
    return f"https://cdn-thumbnails.huggingface.co/social-thumbnails/{org_name}.png"
