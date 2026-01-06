"""Generate custom fields data."""
import random
import json
from typing import List, Dict
from utils.helpers import generate_id


class CustomFieldGenerator:
    """Generates custom field definitions and values."""
    
    # Common custom field types and options
    FIELD_TEMPLATES = {
        "Priority": {
            "type": "enum",
            "options": ["Low", "Medium", "High", "Critical"]
        },
        "Status": {
            "type": "enum",
            "options": ["Not Started", "In Progress", "Blocked", "Done"]
        },
        "Effort": {
            "type": "enum",
            "options": ["XS", "S", "M", "L", "XL"]
        },
        "Sprint": {
            "type": "enum",
            "options": ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Backlog"]
        },
        "Budget": {
            "type": "number",
            "options": None
        },
        "Target Date": {
            "type": "date",
            "options": None
        },
        "Owner": {
            "type": "text",
            "options": None
        },
        "Category": {
            "type": "multi_enum",
            "options": ["Feature", "Bug", "Enhancement", "Documentation", "Research"]
        }
    }
    
    def generate_custom_fields(self, projects: List[Dict]) -> List[Dict]:
        """Generate custom field definitions for projects.
        
        Not all projects have custom fields. Engineering projects more likely.
        
        Args:
            projects: List of project dictionaries
            
        Returns:
            List of custom field definition dictionaries
        """
        custom_fields = []
        
        for project in projects:
            project_id = project["project_id"]
            project_type = project.get("project_type", "engineering")
            
            # 70% of engineering projects have custom fields, 40% of others
            if project_type == "engineering":
                has_fields = random.random() < 0.70
            else:
                has_fields = random.random() < 0.40
            
            if not has_fields:
                continue
            
            # Generate 2-5 custom fields per project
            num_fields = random.randint(2, 5)
            selected_templates = random.sample(list(self.FIELD_TEMPLATES.items()), 
                                             min(num_fields, len(self.FIELD_TEMPLATES)))
            
            for field_name, field_config in selected_templates:
                custom_field = {
                    "custom_field_id": generate_id(),
                    "project_id": project_id,
                    "name": field_name,
                    "field_type": field_config["type"],
                    "enum_options": json.dumps(field_config["options"]) if field_config["options"] else None
                }
                custom_fields.append(custom_field)
        
        return custom_fields
    
    def generate_custom_field_values(self, tasks: List[Dict], 
                                    custom_field_defs: List[Dict]) -> List[Dict]:
        """Generate values for custom fields on tasks.
        
        Args:
            tasks: List of task dictionaries
            custom_field_defs: List of custom field definition dictionaries
            
        Returns:
            List of custom field value dictionaries
        """
        values = []
        
        # Group custom fields by project
        fields_by_project = {}
        for field_def in custom_field_defs:
            pid = field_def["project_id"]
            if pid not in fields_by_project:
                fields_by_project[pid] = []
            fields_by_project[pid].append(field_def)
        
        # Generate values for tasks
        for task in tasks:
            project_id = task["project_id"]
            task_id = task["task_id"]
            
            project_fields = fields_by_project.get(project_id, [])
            if not project_fields:
                continue
            
            # Not all tasks have all custom fields filled (70% fill rate)
            for field_def in project_fields:
                if random.random() > 0.70:
                    continue
                
                value_entry = {
                    "value_id": generate_id(),
                    "task_id": task_id,
                    "custom_field_id": field_def["custom_field_id"],
                    "text_value": None,
                    "number_value": None,
                    "enum_value": None,
                    "date_value": None,
                    "multi_enum_values": None
                }
                
                field_type = field_def["field_type"]
                enum_options = json.loads(field_def["enum_options"]) if field_def["enum_options"] else None
                
                if field_type == "text":
                    value_entry["text_value"] = "Sample text value"
                elif field_type == "number":
                    value_entry["number_value"] = random.uniform(1, 1000)
                elif field_type == "enum":
                    if enum_options:
                        value_entry["enum_value"] = random.choice(enum_options)
                elif field_type == "date":
                    # Use task due_date if available
                    if task.get("due_date"):
                        value_entry["date_value"] = task["due_date"]
                    else:
                        value_entry["date_value"] = None
                elif field_type == "multi_enum":
                    if enum_options:
                        selected = random.sample(enum_options, random.randint(1, min(3, len(enum_options))))
                        value_entry["multi_enum_values"] = json.dumps(selected)
                
                values.append(value_entry)
        
        return values

