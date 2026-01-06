"""Generate teams data."""
import random
from typing import List, Dict
from utils.helpers import generate_id
from utils.dates import random_date
from datetime import datetime


class TeamGenerator:
    """Generates realistic team data."""
    
    # Team names based on common SaaS team structures
    TEAM_NAME_TEMPLATES = [
        "Product Engineering",
        "Platform Team",
        "Frontend Team",
        "Backend Services",
        "Infrastructure",
        "Data Engineering",
        "Mobile Engineering",
        "QA & Testing",
        "Product Marketing",
        "Growth Marketing",
        "Content Marketing",
        "Brand Marketing",
        "Demand Generation",
        "Sales Operations",
        "Customer Success",
        "Support Engineering",
        "Product Management",
        "UX Design",
        "DevOps",
        "Security",
        "Finance",
        "People Operations",
        "Legal",
        "Business Operations"
    ]
    
    def generate_teams(self, count: int, org_id: str, start_date: datetime, 
                      end_date: datetime) -> List[Dict]:
        """Generate teams.
        
        Team sizes based on industry benchmarks:
        - Small teams (3-7 members): 40%
        - Medium teams (8-15 members): 40%
        - Large teams (16-30 members): 20%
        
        Args:
            count: Number of teams to generate
            org_id: Organization ID
            start_date: Start of simulation period
            end_date: End of simulation period
            
        Returns:
            List of team dictionaries
        """
        teams = []
        
        # Select team names
        selected_names = random.sample(self.TEAM_NAME_TEMPLATES, min(count, len(self.TEAM_NAME_TEMPLATES)))
        if count > len(self.TEAM_NAME_TEMPLATES):
            # Add numbered variations
            for i in range(count - len(self.TEAM_NAME_TEMPLATES)):
                selected_names.append(f"Team {i+1}")
        
        for i, name in enumerate(selected_names[:count]):
            created_at = random_date(start_date, end_date)
            
            team = {
                "team_id": generate_id(),
                "organization_id": org_id,
                "name": name,
                "description": f"{name} team responsible for core initiatives.",
                "created_at": created_at.isoformat()
            }
            teams.append(team)
        
        return teams

