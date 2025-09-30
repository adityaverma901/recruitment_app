# import frappe
# import json
# # In your Frappe backend
# @frappe.whitelist()
# def create_bulk_applicants(applicants):
#     """Create multiple job applicants at once"""
#     results = []
#     for applicant_data in json.loads(applicants):
#         try:
#             doc = frappe.get_doc({
#                 "doctype": "Job Applicant",
#                 **applicant_data
#             })
#             doc.insert()
#             results.append({"success": True, "name": doc.name})
#         except Exception as e:
#             results.append({"success": False, "error": str(e)})
    
#     return {"results": results}




import frappe
import json

@frappe.whitelist()
def create_bulk_applicants():
    """Read JSON body directly"""
    raw_data = frappe.local.form_dict.get("data") or frappe.local.request.get_data()
    
    # If it's already a list, don't load
    if isinstance(raw_data, (str, bytes, bytearray)):
        data = json.loads(raw_data)
    else:
        data = raw_data  # already a list

    results = []
    for applicant_data in data:
        try:
            doc = frappe.get_doc({
                "doctype": "Job Applicant",
                **applicant_data
            })
            doc.insert()
            results.append({"success": True, "name": doc.name})
        except Exception as e:
            results.append({"success": False, "error": str(e)})

    return {"results": results}
