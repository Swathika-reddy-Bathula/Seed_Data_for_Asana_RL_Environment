"""Generate projects data."""
import random
from typing import List, Dict, Tuple
from utils.helpers import generate_id
from utils.dates import random_date
from datetime import datetime
from scrapers.company_scraper import CompanyScraper


class ProjectGenerator:
    """Generates realistic project data."""
    
    PROJECT_COLORS = ["blue", "green", "orange", "red", "purple", "pink", "yellow", "turquoise"]
    
    # Standard sections for projects
    STANDARD_SECTIONS = ["To Do", "In Progress", "In Review", "Done"]
    
    def __init__(self):
        """Initialize project generator."""
        self.scraper = CompanyScraper()
    
    def generate_projects(self, count: int, teams: List[Dict], users: List[Dict],
                         start_date: datetime, end_date: datetime) -> Tuple[List[Dict], List[Dict]]:
        """Generate projects and their sections.
        
        Project types:
        - Engineering: 50%
        - Marketing: 30%
        - Operations: 20%
        
        Args:
            count: Number of projects to generate
            teams: List of team dictionaries
            users: List of user dictionaries
            start_date: Start of simulation period
            end_date: End of simulation period
            
        Returns:
            Tuple of (projects list, sections list)
        """
        projects = []
        sections = []
        
        project_types = ["engineering", "marketing", "operations"]
        type_weights = [0.50, 0.30, 0.20]
        
        # Get project name templates
        engineering_templates = self.scraper.get_project_name_templates("engineering")
        marketing_templates = self.scraper.get_project_name_templates("marketing")
        operations_templates = self.scraper.get_project_name_templates("operations")
        
        creation_times = []
        for _ in range(count):
            creation_times.append(random_date(start_date, end_date))
        creation_times.sort()
        
        for i, created_at in enumerate(creation_times):
            # Assign project type
            project_type = random.choices(project_types, weights=type_weights, k=1)[0]
            
            # Select name from templates
            if project_type == "engineering":
                name_pool = engineering_templates
            elif project_type == "marketing":
                name_pool = marketing_templates
            else:
                name_pool = operations_templates
            
            # Add variation to names
            base_name = random.choice(name_pool)
            if random.random() < 0.3:  # 30% add year/quarter
                variations = [f"{base_name} 2024", f"{base_name} Q1", f"{base_name} Q2"]
                name = random.choice(variations)
            else:
                name = base_name
            
            # Assign to random team
            team = random.choice(teams)
            
            # Select creator (random user)
            creator = random.choice(users) if users else None
            
            project = {
                "project_id": generate_id(),
                "team_id": team["team_id"],
                "name": name,
                # Use a helper to generate a slightly varied but still synthetic description
                "description": self._generate_project_description(name, project_type),
                "project_type": project_type,
                "color": random.choice(self.PROJECT_COLORS),
                "archived": False if random.random() > 0.15 else True,  # 15% archived
                "created_at": created_at.isoformat(),
                "created_by": creator["user_id"] if creator else None
            }
            projects.append(project)
            
            # Generate sections for this project
            project_sections = self._generate_sections(project["project_id"], created_at)
            sections.extend(project_sections)
        
        return projects, sections

    def _generate_project_description(self, name: str, project_type: str) -> str:
        """Generate a non‑identical but simple description for a project.

        This intentionally stays template‑based (no LLM) so that it works
        even when external APIs are disabled, but it avoids every row
        having exactly the same description text.
        """
        project_type = project_type.lower()

        common_templates = [
            "Project for {name} focusing on {ptype} initiatives.",
            "Track and coordinate key {ptype} work for {name}.",
            "Central hub for planning and executing {ptype} work related to {name}.",
            "Organize tasks, milestones, and updates for {name} ({ptype}).",
            "Scope, deliverables, and progress tracking for {name} ({ptype} project).",
        ]

        # Light project‑type specific flavor
        engineering_suffixes = [
            "Includes backlog grooming, implementation, and QA.",
            "Covers design, implementation, and technical review.",
            "Focuses on feature delivery, reliability, and performance.",
        ]
        marketing_suffixes = [
            "Includes campaign planning, content, and performance tracking.",
            "Covers creative production, approvals, and launch activities.",
            "Focuses on audience targeting, messaging, and reporting.",
        ]
        operations_suffixes = [
            "Includes process improvements, documentation, and coordination.",
            "Covers internal workflows, tooling, and compliance tasks.",
            "Focuses on reliability, standardization, and efficiency.",
        ]

        base = random.choice(common_templates).format(
            name=name,
            ptype=project_type,
        )

        if project_type == "engineering":
            suffix_pool = engineering_suffixes
        elif project_type == "marketing":
            suffix_pool = marketing_suffixes
        elif project_type == "operations":
            suffix_pool = operations_suffixes
        else:
            suffix_pool = []

        # 60% of the time add a small type‑specific suffix for extra variation
        if suffix_pool and random.random() < 0.6:
            return f"{base} {random.choice(suffix_pool)}"

        return base
    
    def _generate_sections(self, project_id: str, created_at: datetime) -> List[Dict]:
        """Generate standard sections for a project.
        
        Args:
            project_id: Project ID
            created_at: Project creation time
            
        Returns:
            List of section dictionaries
        """
        sections = []
        for i, section_name in enumerate(self.STANDARD_SECTIONS):
            section = {
                "section_id": generate_id(),
                "project_id": project_id,
                "name": section_name,
                "position": i,
                "created_at": created_at.isoformat()
            }
            sections.append(section)
        return sections

