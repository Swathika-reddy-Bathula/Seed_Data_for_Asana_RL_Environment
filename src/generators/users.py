"""Generate users data."""
import random
from faker import Faker
from typing import List, Dict
from utils.helpers import generate_id
from utils.dates import random_date
from datetime import datetime


class UserGenerator:
    """Generates realistic user data."""
    
    def __init__(self):
        """Initialize user generator."""
        self.faker = Faker()
        # Note: Faker.seed() is deprecated in newer versions
    
    def generate_users(self, count: int, org_id: str, start_date: datetime, 
                      end_date: datetime) -> List[Dict]:
        """Generate users with realistic names and attributes.
        
        Names generated using Faker (based on census data).
        Departments: Engineering (40%), Marketing (25%), Operations (20%), Sales (15%)
        
        Args:
            count: Number of users to generate
            org_id: Organization ID
            start_date: Start of simulation period
            end_date: End of simulation period
            
        Returns:
            List of user dictionaries
        """
        users = []
        used_emails = set()
        domain = "acme.com"  # keep consistent with org domain
        departments = ["Engineering", "Marketing", "Operations", "Sales", "Product", "Design", "Customer Success"]
        weights = [0.40, 0.25, 0.20, 0.15, 0.10, 0.08, 0.07]  # Weighted distribution
        
        roles = {
            "Engineering": ["Software Engineer", "Senior Engineer", "Staff Engineer", "Engineering Manager", "Tech Lead"],
            "Marketing": ["Marketing Manager", "Content Manager", "Growth Marketing", "Brand Manager", "Marketing Analyst"],
            "Operations": ["Operations Manager", "Business Analyst", "Operations Coordinator", "VP Operations"],
            "Sales": ["Sales Representative", "Account Executive", "Sales Manager", "VP Sales"],
            "Product": ["Product Manager", "Senior Product Manager", "Product Lead"],
            "Design": ["Product Designer", "UX Designer", "Design Lead"],
            "Customer Success": ["Customer Success Manager", "Support Engineer", "CS Lead"]
        }
        
        # Generate creation times with realistic distribution
        creation_times = []
        for _ in range(count):
            creation_times.append(random_date(start_date, end_date))
        creation_times.sort()
        
        for i, created_at in enumerate(creation_times):
            # Generate realistic name (Faker uses census-based distributions)
            name = self.faker.name()
            
            # Assign department with weighted distribution
            dept = random.choices(departments, weights=weights[:len(departments)], k=1)[0]
            
            # Assign role based on department
            role = random.choice(roles.get(dept, ["Team Member"]))
            
            # Generate email (realistic format)
            first_name = name.split()[0].lower()
            last_name = name.split()[-1].lower() if len(name.split()) > 1 else ""
            base_email = f"{first_name}.{last_name}@{domain}"
            email = base_email
            suffix = 1
            # Ensure unique emails to satisfy DB constraint
            while email in used_emails:
                suffix += 1
                email = f"{first_name}.{last_name}{suffix}@{domain}"
            used_emails.add(email)
            
            user = {
                "user_id": generate_id(),
                "organization_id": org_id,
                "email": email,
                "name": name,
                "role": role,
                "department": dept,
                "created_at": created_at.isoformat()
            }
            users.append(user)
        
        return users

