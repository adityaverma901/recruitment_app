import frappe

@frappe.whitelist()
def get_staffing_plans_with_children(owner=None):
    """
    Fetch all Staffing Plans with all child table rows nested.
    Optional: pass 'owner' to filter by creator.
    Returns: full data without pagination.
    """

    # 🧠 Build query with optional owner filter
    query = "SELECT * FROM `tabStaffing Plan`"
    query_params = []

    if owner:
        query += " WHERE owner = %s"
        query_params.append(owner)

    query += " ORDER BY creation DESC"

    # 1️⃣ Get parent Staffing Plans
    parents = frappe.db.sql(query, tuple(query_params), as_dict=True)

    if not parents:
        return {
            "data": [],
            "total": 0
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

    # 4️⃣ Return final data
    return {
        "data": parents,
        "total": len(parents)
    }
