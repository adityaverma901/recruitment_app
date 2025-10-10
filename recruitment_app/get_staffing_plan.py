# # your_app/api/staffing_api_sql_nested.py
# import frappe

# @frappe.whitelist()
# def get_staffing_plans_with_children(limit_start=0, limit_page_length=20, owner=None):
#     """
#     Fetch Staffing Plan with all child table rows nested
#     Optional: pass 'owner' to filter by creator
#     """
#     limit_start = int(limit_start)
#     limit_page_length = int(limit_page_length)

#     # 🧠 Base query
#     base_query = """
#         SELECT *
#         FROM `tabStaffing Plan`
#     """

#     # 🧩 Add optional filter
#     filters = ""
#     if owner:
#         filters = f"WHERE owner = '{owner}'"

#     # 1️⃣ Get parent Staffing Plans
#     parents = frappe.db.sql(f"""
#         {base_query}
#         {filters}
#         ORDER BY creation DESC
#         LIMIT {limit_start}, {limit_page_length}
#     """, as_dict=True)

#     if not parents:
#         return {"data": []}

#     # 2️⃣ Get all child rows for these parents
#     parent_names = tuple([p["name"] for p in parents])
#     children = frappe.db.sql(f"""
#         SELECT *
#         FROM `tabStaffing Plan Detail`
#         WHERE parent IN {parent_names}
#         ORDER BY idx ASC
#     """, as_dict=True)

#     # 3️⃣ Nest children under their parent
#     parent_map = {p["name"]: p for p in parents}
#     for p in parents:
#         p["staffing_details"] = []

#     for child in children:
#         parent_map[child["parent"]]["staffing_details"].append(child)

#     return {"data": parents}



# your_app/api/staffing_api_sql_nested.py
import frappe

@frappe.whitelist()
def get_staffing_plans_with_children(limit_start=0, limit_page_length=20, owner=None):
    """
    Fetch Staffing Plan with all child table rows nested
    Optional: pass 'owner' to filter by creator
    Returns: data with pagination info
    """
    limit_start = int(limit_start)
    limit_page_length = int(limit_page_length)

    # 🔢 Get total count first
    count_query = "SELECT COUNT(*) as total FROM `tabStaffing Plan`"
    count_params = []
    
    if owner:
        count_query += " WHERE owner = %s"
        count_params.append(owner)
    
    total_count = frappe.db.sql(count_query, tuple(count_params), as_dict=True)[0]["total"]

    # 🧠 Build query with optional filter
    query = """
        SELECT *
        FROM `tabStaffing Plan`
    """
    
    query_params = []
    
    # 🧩 Add optional owner filter
    if owner:
        query += " WHERE owner = %s"
        query_params.append(owner)
    
    query += " ORDER BY creation DESC LIMIT %s, %s"
    query_params.extend([limit_start, limit_page_length])

    # 1️⃣ Get parent Staffing Plans
    parents = frappe.db.sql(query, tuple(query_params), as_dict=True)

    if not parents:
        return {
            "data": [],
            "total": total_count,
            "page": (limit_start // limit_page_length) + 1,
            "page_size": limit_page_length,
            "total_pages": 0
        }

    # 2️⃣ Get all child rows for these parents
    parent_names = tuple([p["name"] for p in parents])
    
    # Handle single item tuple syntax
    if len(parent_names) == 1:
        children_query = """
            SELECT *
            FROM `tabStaffing Plan Detail`
            WHERE parent = %s
            ORDER BY idx ASC
        """
        children = frappe.db.sql(children_query, (parent_names[0],), as_dict=True)
    else:
        children_query = """
            SELECT *
            FROM `tabStaffing Plan Detail`
            WHERE parent IN %s
            ORDER BY idx ASC
        """
        children = frappe.db.sql(children_query, (parent_names,), as_dict=True)

    # 3️⃣ Nest children under their parent
    parent_map = {p["name"]: p for p in parents}
    for p in parents:
        p["staffing_details"] = []

    for child in children:
        parent_map[child["parent"]]["staffing_details"].append(child)

    # 4️⃣ Calculate pagination metadata
    total_pages = (total_count + limit_page_length - 1) // limit_page_length
    current_page = (limit_start // limit_page_length) + 1

    return {
        "data": parents,
        "total": total_count,
        "page": current_page,
        "page_size": limit_page_length,
        "total_pages": total_pages,
        "has_next": current_page < total_pages,
        "has_prev": current_page > 1
    }