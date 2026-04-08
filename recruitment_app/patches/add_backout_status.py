import frappe

def execute():
    value = "Open\nTagged\nShortlisted\nCV Rejected\nAssessment\nAssessment Rejection\nInterview to be Scheduled\nInterview\nL1 Interview Rejection\nL2 Interview Rejection\nOffered\nOffer Drop\nJoined\nBackout"
    
    if frappe.db.exists("Property Setter", "Job Applicant-status-options"):
        current = frappe.db.get_value("Property Setter", "Job Applicant-status-options", "value")
        if "Backout" not in current:
            frappe.db.set_value("Property Setter", "Job Applicant-status-options", "value", value)
            frappe.db.commit()
            frappe.clear_cache()
            print("✓ Backout status added!")
        else:
            print("✓ Backout already exists, skipping.")
    else:
        ps = frappe.get_doc({
            "doctype": "Property Setter",
            "doc_type": "Job Applicant",
            "doctype_or_field": "DocField",
            "field_name": "status",
            "property": "options",
            "value": value,
            "property_type": "Text"
        })
        ps.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache()
        print("✓ Property Setter created with Backout!")