import frappe

@frappe.whitelist()
def get_issues_with_attachments(owner=None, status=None, priority=None):
    """
    ⚡ Lightning-fast Issue fetcher using JOIN
    """
    
    # 🏎️ Single query with LEFT JOIN - fetch everything at once!
    query = """
        SELECT 
            i.*,
            img.name as img_name,
            img.image as img_image,
            img.idx as img_idx,
            img.creation as img_creation,
            img.modified as img_modified
        FROM `tabIssue` i
        LEFT JOIN `tabImage Attachements` img ON img.parent = i.name
        WHERE 1=1
    """
    
    conditions = []
    params = []
    
    if owner:
        conditions.append("AND i.owner = %s")
        params.append(owner)
    
    if status:
        conditions.append("AND i.status = %s")
        params.append(status)
    
    if priority:
        conditions.append("AND i.priority = %s")
        params.append(priority)
    
    query += " ".join(conditions)
    query += " ORDER BY i.creation DESC, img.idx ASC"
    
    # Execute single query
    results = frappe.db.sql(query, tuple(params), as_dict=True)
    
    if not results:
        return {"data": [], "total": 0}
    
    # 🧩 Group results by parent issue
    issues_dict = {}
    
    for row in results:
        issue_name = row["name"]
        
        # First time seeing this issue
        if issue_name not in issues_dict:
            # Extract parent fields (all fields starting with 'i.')
            issue_data = {k: v for k, v in row.items() if not k.startswith("img_")}
            issue_data["custom_image_attachements"] = []
            issues_dict[issue_name] = issue_data
        
        # Add attachment if exists
        if row.get("img_name"):
            issues_dict[issue_name]["custom_image_attachements"].append({
                "name": row["img_name"],
                "image": row["img_image"],
                "idx": row["img_idx"],
                "creation": row["img_creation"],
                "modified": row["img_modified"],
                "parent": issue_name
            })
    
    issues = list(issues_dict.values())
    
    return {
        "data": issues,
        "total": len(issues)
    }