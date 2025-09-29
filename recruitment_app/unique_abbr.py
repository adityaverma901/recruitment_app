# recruitment_app/unique_abbr.py
import frappe
from erpnext.setup.doctype.company.company import Company

class CustomCompany(Company):
    def before_validate(self):
        """Check and auto-increment abbreviation BEFORE parent validation"""
        if self.abbr:
            existing = frappe.db.get_value(
                "Company", 
                {
                    "abbr": self.abbr, 
                    "name": ["!=", self.name]
                }, 
                "name"
            )
            
            if existing:
                # Auto-increment: ipl -> ipl-1 -> ipl-2
                original_abbr = self.abbr
                counter = 1
                
                while frappe.db.exists("Company", {"abbr": self.abbr, "name": ["!=", self.name]}):
                    self.abbr = f"{original_abbr}-{counter}"
                    counter += 1
                
                frappe.msgprint(
                    f"Abbreviation '{original_abbr}' already exists. Changed to '{self.abbr}'",
                    alert=True,
                    indicator="orange"
                )
    
    def validate(self):
        # Parent validation will run AFTER our before_validate
        super().validate()