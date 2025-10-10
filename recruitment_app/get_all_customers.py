import frappe

@frappe.whitelist()
def get_all_customers(owner=None, limit_start=0, limit_page_length=20):
    """
    Fetch all Customer records with optional filter by owner.
    Supports pagination and sorting by creation (DESC).
    """

    limit_start = int(limit_start)
    limit_page_length = int(limit_page_length)

    # 🧮 Total count
    count_query = "SELECT COUNT(*) as total FROM `tabCustomer`"
    count_params = []

    if owner:
        count_query += " WHERE owner = %s"
        count_params.append(owner)

    total_count = frappe.db.sql(count_query, tuple(count_params), as_dict=True)[0]["total"]

    # 📦 Fetch customers
    query = """
        SELECT
            name,
            customer_name,
            customer_group,
            territory,
            customer_type,
            mobile_no,
            email_id,
            owner,
            creation,
            modified
        FROM `tabCustomer`
    """

    query_params = []

    if owner:
        query += " WHERE owner = %s"
        query_params.append(owner)

    query += " ORDER BY creation DESC LIMIT %s, %s"
    query_params.extend([limit_start, limit_page_length])

    customers = frappe.db.sql(query, tuple(query_params), as_dict=True)

    # 📖 Pagination info
    total_pages = (total_count + limit_page_length - 1) // limit_page_length
    current_page = (limit_start // limit_page_length) + 1

    return {
        "data": customers,
        "total": total_count,
        "page": current_page,
        "page_size": limit_page_length,
        "total_pages": total_pages,
        "has_next": current_page < total_pages,
        "has_prev": current_page > 1
    }
