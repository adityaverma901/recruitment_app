# import frappe

# @frappe.whitelist()
# def get_all_todos(email=None, owner=None, limit_start=0, limit_page_length=20):
#     """
#     Fetch all ToDo records with optional filters:
#     - email → filters by 'allocated_to'
#     - owner → filters by 'owner'
#     Includes pagination and sorting by creation (desc).
#     """

#     limit_start = int(limit_start)
#     limit_page_length = int(limit_page_length)

#     # 🧮 Count total
#     count_query = "SELECT COUNT(*) as total FROM `tabToDo`"
#     count_conditions = []
#     count_params = []

#     if email:
#         count_conditions.append("allocated_to = %s")
#         count_params.append(email)
#     if owner:
#         count_conditions.append("owner = %s")
#         count_params.append(owner)

#     if count_conditions:
#         count_query += " WHERE " + " AND ".join(count_conditions)

#     total_count = frappe.db.sql(count_query, tuple(count_params), as_dict=True)[0]["total"]

#     # 📦 Main data query
#     query = """
#         SELECT
#             name,
#             description,
#             status,
#             creation,
#             priority,
#             date,
#             custom_job_id,
#             allocated_to,
#             assigned_by,
#             reference_type,
#             reference_name,
#             role,
#             sender,
#             assignment_rule,
#             custom_date_assigned,
#             custom_job_title,
#             custom_department,
#             owner
#         FROM `tabToDo`
#     """

#     conditions = []
#     query_params = []

#     if email:
#         conditions.append("allocated_to = %s")
#         query_params.append(email)
#     if owner:
#         conditions.append("owner = %s")
#         query_params.append(owner)

#     if conditions:
#         query += " WHERE " + " AND ".join(conditions)

#     query += " ORDER BY creation DESC LIMIT %s, %s"
#     query_params.extend([limit_start, limit_page_length])

#     todos = frappe.db.sql(query, tuple(query_params), as_dict=True)

#     # 📖 Pagination info
#     total_pages = (total_count + limit_page_length - 1) // limit_page_length
#     current_page = (limit_start // limit_page_length) + 1

#     return {
#         "data": todos,
#         "total": total_count,
#         "page": current_page,
#         "page_size": limit_page_length,
#         "total_pages": total_pages,
#         "has_next": current_page < total_pages,
#         "has_prev": current_page > 1
#     }



import frappe

@frappe.whitelist()
def get_all_todos(email=None, owner=None, limit_start=0, limit_page_length=20):
    """
    Fetch all ToDo records with optional filters:
    - email → filters by 'allocated_to'
    - owner → filters by 'owner'
    Includes pagination, sorting by creation (desc), and filters.
    """

    limit_start = int(limit_start)
    limit_page_length = int(limit_page_length)

    # --- Count total ---
    count_query = "SELECT COUNT(*) as total FROM `tabToDo`"
    count_conditions = []
    count_params = []

    if email:
        count_conditions.append("allocated_to = %s")
        count_params.append(email)
    if owner:
        count_conditions.append("owner = %s")
        count_params.append(owner)

    if count_conditions:
        count_query += " WHERE " + " AND ".join(count_conditions)

    total_count = frappe.db.sql(count_query, tuple(count_params), as_dict=True)[0]["total"]

    # --- Main data query with pagination ---
    query = """
        SELECT
            name,
            description,
            status,
            creation,
            priority,
            date,
            custom_job_id,
            allocated_to,
            assigned_by,
            reference_type,
            reference_name,
            role,
            sender,
            assignment_rule,
            custom_date_assigned,
            custom_job_title,
            custom_department,
            owner,
            company_name,
            contact_name,
            contact_email,
            stage,
            offering
        FROM `tabToDo`
    """

    conditions = []
    query_params = []

    if email:
        conditions.append("allocated_to = %s")
        query_params.append(email)
    if owner:
        conditions.append("owner = %s")
        query_params.append(owner)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY creation DESC LIMIT %s, %s"
    query_params.extend([limit_start, limit_page_length])

    todos = frappe.db.sql(query, tuple(query_params), as_dict=True)

    # --- Filters for all data (ignore pagination) ---
    filter_query = " SELECT custom_company, allocated_to, status, custom_job_title FROM `tabToDo`"
    filter_conditions = []
    filter_params = []

    if email:
        filter_conditions.append("allocated_to = %s")
        filter_params.append(email)
    if owner:
        filter_conditions.append("owner = %s")
        filter_params.append(owner)

    if filter_conditions:
        filter_query += " WHERE " + " AND ".join(filter_conditions)

    all_records = frappe.db.sql(filter_query, tuple(filter_params), as_dict=True)

    filters = {
    "companies": list({r["custom_company"] for r in all_records if r["custom_company"]}),
    "contacts": [{"name": r["allocated_to"], "email": None} for r in all_records if r["allocated_to"]],
    "stages": list({r["status"] for r in all_records if r["status"]}),
    "offerings": list({r["custom_job_title"] for r in all_records if r["custom_job_title"]}),
    }

    # --- Pagination info ---
    total_pages = (total_count + limit_page_length - 1) // limit_page_length
    current_page = (limit_start // limit_page_length) + 1

    return {
        "data": todos,
        "total": total_count,
        "page": current_page,
        "page_size": limit_page_length,
        "total_pages": total_pages,
        "has_next": current_page < total_pages,
        "has_prev": current_page > 1,
        "filters": filters
    }
