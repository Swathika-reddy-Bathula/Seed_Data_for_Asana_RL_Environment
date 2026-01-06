"""Generate tags data."""
import random
from typing import List, Dict
from utils.helpers import generate_id


class TagGenerator:
    """Generates tags and task-tag associations."""
    
    TAG_COLORS = ["blue", "green", "orange", "red", "purple", "pink", "yellow", "turquoise"]
    
    # Common tag names for SaaS companies
    TAG_TEMPLATES = [
        "urgent", "blocked", "needs-review", "bug", "feature", "enhancement",
        "documentation", "refactor", "technical-debt", "design", "qa",
        "deployment", "on-hold", "client-request", "internal", "external",
        "security", "performance", "accessibility", "mobile", "web",
        "backend", "frontend", "api", "database", "infrastructure",
        "marketing", "sales", "customer-success", "ops", "finance",
        "q1-2024", "q2-2024", "q3-2024", "q4-2024", "high-priority",
        "low-priority", "stretch-goal", "mvp", "research", "experiment"
    ]
    
    def generate_tags(self, org_id: str, count: int = 30) -> List[Dict]:
        """Generate organization-wide tags.
        
        Args:
            org_id: Organization ID
            count: Number of tags to generate
            
        Returns:
            List of tag dictionaries
        """
        tags = []
        selected_names = random.sample(self.TAG_TEMPLATES, min(count, len(self.TAG_TEMPLATES)))
        
        for name in selected_names:
            tag = {
                "tag_id": generate_id(),
                "organization_id": org_id,
                "name": name,
                "color": random.choice(self.TAG_COLORS)
            }
            tags.append(tag)
        
        return tags
    
    def generate_task_tags(self, tasks: List[Dict], tags: List[Dict],
                          avg_tags_per_task: float = 1.2) -> List[Dict]:
        """Generate task-tag associations.
        
        Args:
            tasks: List of task dictionaries
            tags: List of tag dictionaries
            avg_tags_per_task: Average number of tags per task
            
        Returns:
            List of task-tag association tuples (task_id, tag_id)
        """
        task_tags = []
        
        for task in tasks:
            # Number of tags (weighted: most tasks have 0-2 tags)
            num_tags = random.choices(
                [0, 1, 2, 3, 4],
                weights=[0.30, 0.40, 0.20, 0.08, 0.02],
                k=1
            )[0]
            
            if num_tags > 0 and tags:
                selected_tags = random.sample(tags, min(num_tags, len(tags)))
                for tag in selected_tags:
                    task_tags.append({
                        "task_id": task["task_id"],
                        "tag_id": tag["tag_id"]
                    })
        
        return task_tags

