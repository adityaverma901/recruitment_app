# import frappe
# from collections import defaultdict

# @frappe.whitelist()
# def get_unique_candidates(owner=None):
#     """
#     Fetch unique candidates (grouped by email).
#     Each candidate will include all jobs they applied for with status, company, etc.
#     Optional: pass 'owner' to filter by creator.
#     """

#     query = """
#         SELECT
#             name,
#             applicant_name,
#             email_id,
#             phone_number,
#             country,
#             job_title,
#             designation,
#             status,
#             custom_company_name,
#             creation,
#             owner
#         FROM `tabJob Applicant`
#     """
#     query_params = []

#     if owner:
#         query += " WHERE owner = %s"
#         query_params.append(owner)

#     query += " ORDER BY creation DESC"

#     applicants = frappe.db.sql(query, tuple(query_params), as_dict=True)

#     if not applicants:
#         return {"data": [], "total": 0}

#     # Group by email_id
#     grouped = defaultdict(lambda: {
#         "applicant_name": None,
#         "email_id": None,
#         "phone_number": None,
#         "country": None,
#         "applications": []
#     })

#     for app in applicants:
#         email = app["email_id"] or "unknown"

#         if not grouped[email]["email_id"]:
#             grouped[email].update({
#                 "applicant_name": app["applicant_name"],
#                 "email_id": app["email_id"],
#                 "phone_number": app["phone_number"],
#                 "country": app["country"]
#             })

#         grouped[email]["applications"].append({
#             "job_title": app["job_title"],
#             "designation": app["designation"],
#             "status": app["status"],
#             "custom_company_name": app["custom_company_name"],
#             "creation": app["creation"],
#             "owner": app["owner"]
#         })

#     # Convert dict → list for output
#     candidates = list(grouped.values())

#     return {
#         "data": candidates,
#         "total": len(candidates)
#     }



import frappe
from collections import defaultdict

@frappe.whitelist()
def get_applicants_with_resumes(owner=None):
    """
    Fetch Job Applicants grouped by email.
    Each applicant entry includes their resume per job application.
    Optional: filter by owner.
    """

    # 1️⃣ Fetch all applicants
    query = """
        SELECT
            name,
            applicant_name,
            email_id,
            phone_number,
            country,
            job_title,
            designation,
            status,
            custom_company_name,
            resume_attachment,
            creation,
            owner
        FROM `tabJob Applicant`
    """
    params = []
    if owner:
        query += " WHERE owner = %s"
        params.append(owner)

    query += " ORDER BY creation DESC"

    applicants = frappe.db.sql(query, tuple(params), as_dict=True)

    if not applicants:
        return {"data": [], "total": 0}

    # 2️⃣ Group by email (but each job keeps its resume)
    grouped = defaultdict(lambda: {
        "applicant_name": None,
        "email_id": None,
        "phone_number": None,
        "country": None,
        "applications": []
    })

    for app in applicants:
        email = app.get("email_id") or "unknown"

        if not grouped[email]["email_id"]:
            grouped[email].update({
                "applicant_name": app.get("applicant_name"),
                "email_id": email,
                "phone_number": app.get("phone_number"),
                "country": app.get("country")
            })

        grouped[email]["applications"].append({
            "job_title": app.get("job_title"),
            "designation": app.get("designation"),
            "status": app.get("status"),
            "custom_company_name": app.get("custom_company_name"),
            "resume_attachment": app.get("resume_attachment"),  # ✅ resume per job
            "creation": app.get("creation"),
            "owner": app.get("owner"),
        })

    # 3️⃣ Convert to list
    candidates = list(grouped.values())

    return {
        "data": candidates,
        "total": len(candidates)
    }
