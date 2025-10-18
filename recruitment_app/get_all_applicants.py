


# import frappe
# from collections import defaultdict

# @frappe.whitelist()
# def get_unique_candidates(owner=None):
#     """
#     Fetch Job Applicants grouped by email.
#     Each applicant entry includes their resume per job application and activity log.
#     Optional: filter by owner.
#     """

#     # 1️⃣ Fetch all applicants
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
#             resume_attachment,
#             creation,
#             owner
#         FROM `tabJob Applicant`
#     """
#     params = []
#     if owner:
#         query += " WHERE owner = %s"
#         params.append(owner)

#     query += " ORDER BY creation DESC"

#     applicants = frappe.db.sql(query, tuple(params), as_dict=True)

#     if not applicants:
#         return {"data": [], "total": 0}

#     # 2️⃣ Get activity log child table data for all applicants
#     applicant_names = [app["name"] for app in applicants]
    
#     # Fetch activity log child table data
#     activity_log_data = frappe.db.sql("""
#         SELECT 
#             parent,
#             name,
#             activity_name,
#             datetime
#         FROM `tabstatus log table`
#         WHERE parent IN %s
#         ORDER BY idx
#     """, [applicant_names], as_dict=True)

#     # 3️⃣ Group activity log data by parent
#     activity_log_by_applicant = defaultdict(list)
    
#     for activity in activity_log_data:
#         activity_log_by_applicant[activity.parent].append(activity)

#     # 4️⃣ Group by email (but each job keeps its resume and activity log)
#     grouped = defaultdict(lambda: {
#         "applicant_name": None,
#         "email_id": None,
#         "phone_number": None,
#         "country": None,
#         "applications": []
#     })

#     for app in applicants:
#         email = app.get("email_id") or "unknown"
#         applicant_name = app.get("name")

#         if not grouped[email]["email_id"]:
#             grouped[email].update({
#                 "applicant_name": app.get("applicant_name"),
#                 "email_id": email,
#                 "phone_number": app.get("phone_number"),
#                 "country": app.get("country")
#             })

#         # Prepare application with activity log data
#         application_data = {
#             "job_title": app.get("job_title"),
#             "designation": app.get("designation"),
#             "status": app.get("status"),
#             "custom_company_name": app.get("custom_company_name"),
#             "resume_attachment": app.get("resume_attachment"),
#             "creation": app.get("creation"),
#             "owner": app.get("owner"),
#             # Add only activity log to each application
#             "custom_activity_log": activity_log_by_applicant.get(applicant_name, [])
#         }

#         grouped[email]["applications"].append(application_data)

#     # 5️⃣ Convert to list
#     candidates = list(grouped.values())

#     return {
#         "data": candidates,
#         "total": len(candidates)
#     }


import frappe

@frappe.whitelist()
def get_job_applicant_details(applicant_id):
    """
    Fetch complete Job Applicant data including child tables.
    Returns full document structure with all nested data.
    """
    
    if not applicant_id:
        frappe.throw("Applicant ID is required")
    
    # ✅ Fetch the complete document with all child tables
    applicant = frappe.get_doc("Job Applicant", applicant_id)
    
    # ✅ Convert to dict with all fields and child tables
    applicant_dict = applicant.as_dict()
    
    return {
        "data": applicant_dict
    }


@frappe.whitelist()
def get_all_job_applicants_full(owner=None, limit_start=0, limit_page_length=20):
    """
    Fetch all Job Applicants with complete data including child tables.
    Optional: filter by owner.
    Supports pagination.
    """
    
    # Build filters
    filters = {}
    if owner:
        filters["owner"] = owner
    
    # ✅ Fetch all applicant names first
    applicants = frappe.get_all(
        "Job Applicant",
        filters=filters,
        fields=["name"],
        order_by="creation DESC",
        limit_start=limit_start,
        limit_page_length=limit_page_length
    )
    
    if not applicants:
        return {"data": [], "total": 0}
    
    # ✅ Fetch complete documents with all child tables
    full_data = []
    for app in applicants:
        try:
            doc = frappe.get_doc("Job Applicant", app.name)
            full_data.append(doc.as_dict())
        except Exception as e:
            frappe.log_error(f"Error fetching applicant {app.name}: {str(e)}")
            continue
    
    # Get total count
    total = frappe.db.count("Job Applicant", filters)
    
    return {
        "data": full_data,
        "total": total,
        "limit_start": limit_start,
        "limit_page_length": limit_page_length
    }


@frappe.whitelist()
def get_all_job_applicants_raw(owner=None):
    """
    Fetch ALL Job Applicants at once (no pagination) - USE WITH CAUTION for large datasets.
    Includes all child table data.
    """
    
    # Build filters
    filters = {}
    if owner:
        filters["owner"] = owner
    
    # ✅ Fetch all applicant names
    applicants = frappe.get_all(
        "Job Applicant",
        filters=filters,
        fields=["name"],
        order_by="creation DESC"
    )
    
    if not applicants:
        return {"data": [], "total": 0}
    
    # ✅ Fetch complete documents
    full_data = []
    for app in applicants:
        try:
            doc = frappe.get_doc("Job Applicant", app.name)
            full_data.append(doc.as_dict())
        except Exception as e:
            frappe.log_error(f"Error fetching applicant {app.name}: {str(e)}")
            continue
    
    return {
        "data": full_data,
        "total": len(full_data)
    }