import frappe

@frappe.whitelist()
def get_all_todos(email=None, owner=None, limit_start=0, limit_page_length=20):
    """
    Fetch all ToDo records with optional filters:
    - email → filters by 'allocated_to'
    - owner → filters by 'owner'
    Includes pagination and sorting by creation (desc).
    """

    limit_start = int(limit_start)
    limit_page_length = int(limit_page_length)

    # 🧮 Count total
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

    # 📦 Main data query
    query = """
        SELECT
            name,
            description,
            status,
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
            owner
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

    # 📖 Pagination info
    total_pages = (total_count + limit_page_length - 1) // limit_page_length
    current_page = (limit_start // limit_page_length) + 1

    return {
        "data": todos,
        "total": total_count,
        "page": current_page,
        "page_size": limit_page_length,
        "total_pages": total_pages,
        "has_next": current_page < total_pages,
        "has_prev": current_page > 1
    }
