from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from a2a.types import AgentCard  


class AgentMetadata(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    long_description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    rating: Optional[float] = None
    installs: Optional[int] = None
    user_id: Optional[str] = None
    icon_name: Optional[str] = None
    screenshots: Optional[List[str]] = None
    repo_url: Optional[str] = None
    agent_card: Optional[Dict[str, Any]] = None
    featured: Optional[bool] = None
    trending: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    docker_image: Optional[str] = None