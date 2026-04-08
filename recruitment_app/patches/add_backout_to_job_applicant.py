import frappe

def execute():
    """Add Backout to Job Applicant status options"""
    
    # Check if property setter exists
    if frappe.db.exists("Property Setter", "Job Applicant-status-options"):
        # Update existing
        current_value = frappe.db.get_value("Property Setter", "Job Applicant-status-options", "value")
        if "Backout" not in current_value:
            new_value = current_value + "\nBackout"
            frappe.db.set_value("Property Setter", "Job Applicant-status-options", "value", new_value)
            frappe.db.commit()
    else:
        # Create new property setter
        ps = frappe.get_doc({
            "doctype": "Property Setter",
            "doc_type": "Job Applicant",
            "doctype_or_field": "DocField",
            "field_name": "status",
            "property": "options",
            "property_type": "Text",
            "value": "Open\nTagged\nShortlisted\nCV Rejected\nAssessment\nAssessment Rejection\nInterview to be Scheduled\nInterview\nL1 Interview Rejection\nL2 Interview Rejection\nOffered\nOffer Drop\nJoined\nBackout"
        })
        ps.insert(ignore_permissions=True)
        frappe.db.commit()
    
    frappe.clear_cache()
    print("✓ Backout added to Job Applicant status")