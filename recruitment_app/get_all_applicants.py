import frappe

@frappe.whitelist()
def get_all_applicants(owner=None, limit_start=0, limit_page_length=20):
    """
    Fetch all Job Applicant records with optional filter by owner.
    Supports pagination and sorts by creation (DESC).
    """

    limit_start = int(limit_start)
    limit_page_length = int(limit_page_length)

    # 🧮 Count total applicants
    count_query = "SELECT COUNT(*) as total FROM `tabJob Applicant`"
    count_params = []

    if owner:
        count_query += " WHERE owner = %s"
        count_params.append(owner)

    total_count = frappe.db.sql(count_query, tuple(count_params), as_dict=True)[0]["total"]

    # 📦 Fetch applicants
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
            resume_attachment,
            custom_experience,
            custom_education,
            creation,
            custom_company_name,
            owner
        FROM `tabJob Applicant`
    """

    query_params = []
    if owner:
        query += " WHERE owner = %s"
        query_params.append(owner)

    query += " ORDER BY creation DESC LIMIT %s, %s"
    query_params.extend([limit_start, limit_page_length])

    applicants = frappe.db.sql(query, tuple(query_params), as_dict=True)

    # 📖 Pagination metadata
    total_pages = (total_count + limit_page_length - 1) // limit_page_length
    current_page = (limit_start // limit_page_length) + 1

    return {
        "data": applicants,
        "total": total_count,
        "page": current_page,
        "page_size": limit_page_length,
        "total_pages": total_pages,
        "has_next": current_page < total_pages,
        "has_prev": current_page > 1
    }
