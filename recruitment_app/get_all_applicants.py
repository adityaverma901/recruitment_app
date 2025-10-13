# import frappe

# @frappe.whitelist()
# def get_all_applicants(owner=None, limit_start=0, limit_page_length=20):
#     """
#     Fetch Job Applicants with their experience and education.
#     Supports pagination and optional owner filter.
#     """

#     limit_start = int(limit_start)
#     limit_page_length = int(limit_page_length)

#     # 1️⃣ Total count
#     count_query = "SELECT COUNT(*) as total FROM `tabJob Applicant`"
#     count_params = []
#     if owner:
#         count_query += " WHERE owner = %s"
#         count_params.append(owner)
#     total_count = frappe.db.sql(count_query, tuple(count_params), as_dict=True)[0]["total"]

#     # 2️⃣ Fetch main applicant data
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
#             resume_attachment,
#             custom_company_name,
#             creation,
#             owner
#         FROM `tabJob Applicant`
#     """
#     query_params = []
#     if owner:
#         query += " WHERE owner = %s"
#         query_params.append(owner)

#     query += " ORDER BY creation DESC LIMIT %s, %s"
#     query_params.extend([limit_start, limit_page_length])

#     applicants = frappe.db.sql(query, tuple(query_params), as_dict=True)

#     if not applicants:
#         total_pages = (total_count + limit_page_length - 1) // limit_page_length
#         return {
#             "data": [],
#             "total": total_count,
#             "page": (limit_start // limit_page_length) + 1,
#             "page_size": limit_page_length,
#             "total_pages": total_pages,
#             "has_next": False,
#             "has_prev": False
#         }

#     # 3️⃣ Fetch child tables for all applicants
#     applicant_names = tuple([a["name"] for a in applicants])

#     # Experience child table
#     if len(applicant_names) == 1:
#         experiences = frappe.db.sql("""
#             SELECT *
#             FROM `tabExperience`
#             WHERE parent=%s AND parentfield='custom_experience' AND parenttype='Job Applicant'
#             ORDER BY idx ASC
#         """, (applicant_names[0],), as_dict=True)
#     else:
#         experiences = frappe.db.sql("""
#             SELECT *
#             FROM `tabExperience`
#             WHERE parent IN %s AND parentfield='custom_experience' AND parenttype='Job Applicant'
#             ORDER BY idx ASC
#         """, (applicant_names,), as_dict=True)

#     # Education child table
#     if len(applicant_names) == 1:
#         educations = frappe.db.sql("""
#             SELECT *
#             FROM `tabEducation`
#             WHERE parent=%s AND parentfield='custom_education' AND parenttype='Job Applicant'
#             ORDER BY idx ASC
#         """, (applicant_names[0],), as_dict=True)
#     else:
#         educations = frappe.db.sql("""
#             SELECT *
#             FROM `tabEducation`
#             WHERE parent IN %s AND parentfield='custom_education' AND parenttype='Job Applicant'
#             ORDER BY idx ASC
#         """, (applicant_names,), as_dict=True)

#     # 4️⃣ Nest child tables under parent
#     parent_map = {a["name"]: a for a in applicants}
#     for a in applicants:
#         a["custom_experience"] = []
#         a["custom_education"] = []

#     for exp in experiences:
#         parent_map[exp["parent"]]["custom_experience"].append(exp)

#     for edu in educations:
#         parent_map[edu["parent"]]["custom_education"].append(edu)

#     # 5️⃣ Pagination metadata
#     total_pages = (total_count + limit_page_length - 1) // limit_page_length
#     current_page = (limit_start // limit_page_length) + 1

#     return {
#         "data": applicants,
#         "total": total_count,
#         "page": current_page,
#         "page_size": limit_page_length,
#         "total_pages": total_pages,
#         "has_next": current_page < total_pages,
#         "has_prev": current_page > 1
#     }




import frappe
from collections import defaultdict

@frappe.whitelist()
def get_unique_candidates(owner=None):
    """
    Fetch unique candidates (grouped by email).
    Each candidate will include all jobs they applied for with status, company, etc.
    Optional: pass 'owner' to filter by creator.
    """

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
            creation,
            owner
        FROM `tabJob Applicant`
    """
    query_params = []

    if owner:
        query += " WHERE owner = %s"
        query_params.append(owner)

    query += " ORDER BY creation DESC"

    applicants = frappe.db.sql(query, tuple(query_params), as_dict=True)

    if not applicants:
        return {"data": [], "total": 0}

    # Group by email_id
    grouped = defaultdict(lambda: {
        "applicant_name": None,
        "email_id": None,
        "phone_number": None,
        "country": None,
        "applications": []
    })

    for app in applicants:
        email = app["email_id"] or "unknown"

        if not grouped[email]["email_id"]:
            grouped[email].update({
                "applicant_name": app["applicant_name"],
                "email_id": app["email_id"],
                "phone_number": app["phone_number"],
                "country": app["country"]
            })

        grouped[email]["applications"].append({
            "job_title": app["job_title"],
            "designation": app["designation"],
            "status": app["status"],
            "custom_company_name": app["custom_company_name"],
            "creation": app["creation"],
            "owner": app["owner"]
        })

    # Convert dict → list for output
    candidates = list(grouped.values())

    return {
        "data": candidates,
        "total": len(candidates)
    }
