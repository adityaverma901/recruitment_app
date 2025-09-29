# import frappe
# import json

# @frappe.whitelist(allow_guest=False)  # allow_guest=False -> sirf logged in ya API key/secret se chalega
# def bulk_create_assessments(applicants, scheduled_on, from_time, to_time, assessment_link, assessment_round="Mechanical"):
#     """
#     Create multiple assessments for a list of applicants
#     """
#     try:
#         # Convert JSON string to Python list
#         if isinstance(applicants, str):
#             applicants = json.loads(applicants)

#         created_docs = []

#         for applicant in applicants:
#             doc = frappe.get_doc({
#                 "doctype": "Assessment",
#                 "assessment_round": assessment_round,
#                 "job_applicant": applicant,
#                 "scheduled_on": scheduled_on,
#                 "from_time": from_time,
#                 "to_time": to_time,
#                 "assessment_link": assessment_link,
#                 "custom_expected_average_rating": 4,
#                 "interviewers": [
#                     {"interviewer": "Administrator"}
#                 ]
#             })
#             doc.insert(ignore_permissions=True)
#             created_docs.append(doc.name)

#         frappe.db.commit()
#         return {"status": "success", "created_assessments": created_docs}

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Bulk Create Assessments Error")
#         return {"status": "error", "message": str(e)}  



import frappe
import json

@frappe.whitelist(allow_guest=False)
def bulk_create_assessments(applicants, scheduled_on, from_time, to_time, assessment_link, assessment_round="Mechanical", interviewers=None):
    """
    Create multiple assessments for a list of applicants
    """
    try:
        # Convert JSON string to Python list
        if isinstance(applicants, str):
            applicants = json.loads(applicants)

        if isinstance(interviewers, str):
            interviewers = json.loads(interviewers)

        created_docs = []

        for applicant in applicants:
            doc = frappe.get_doc({
                "doctype": "Assessment",
                "assessment_round": assessment_round,
                "job_applicant": applicant,
                "scheduled_on": scheduled_on,
                "from_time": from_time,
                "to_time": to_time,
                "assessment_link": assessment_link,
                "custom_expected_average_rating": 4,
                "interviewers": interviewers
            })
            doc.insert(ignore_permissions=True)
            created_docs.append(doc.name)

        frappe.db.commit()
        return {"status": "success", "created_assessments": created_docs}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Bulk Create Assessments Error")
        return {"status": "error", "message": str(e)}
