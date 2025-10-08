# your_app/api/staffing_api_sql_nested.py
import frappe

@frappe.whitelist()
def get_staffing_plans_with_children(limit_start=0, limit_page_length=20):
    """
    Fetch Staffing Plan with all child table rows nested
    """
    limit_start = int(limit_start)
    limit_page_length = int(limit_page_length)

    # 1️⃣ Get parent Staffing Plans
    parents = frappe.db.sql(f"""
        SELECT *
        FROM `tabStaffing Plan`
        ORDER BY creation DESC
        LIMIT {limit_start}, {limit_page_length}
    """, as_dict=True)

    if not parents:
        return {"data": []}

    # 2️⃣ Get child rows for all parents in one query
    parent_names = tuple([p["name"] for p in parents])
    children = frappe.db.sql(f"""
        SELECT *
        FROM `tabStaffing Plan Detail`
        WHERE parent IN {parent_names}
        ORDER BY idx ASC
    """, as_dict=True)

    # 3️⃣ Nest children under their parent
    parent_map = {p["name"]: p for p in parents}
    for p in parents:
        p["staffing_details"] = []

    for child in children:
        parent_map[child["parent"]]["staffing_details"].append(child)

    return {"data": parents}
