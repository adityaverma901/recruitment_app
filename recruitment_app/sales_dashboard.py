import frappe

@frappe.whitelist()
def get_lead_dashboard_summary(owner=None, start_date=None, end_date=None):
    """
    📊 Lead Summary API
    Returns:
      - total_leads: count of all leads
      - total_deal_value: sum of custom_deal_value
      - onboarded_count: count where status = 'Onboarded'
      - onboarded_deal_value: sum of custom_deal_value where status = 'Onboarded'
    Optional filters:
      - owner (email)
      - start_date (YYYY-MM-DD)
      - end_date (YYYY-MM-DD)
    """

    # ✅ Build dynamic filter conditions
    conditions = []
    params = []

    if owner:
        conditions.append("owner = %s")
        params.append(owner)

    if start_date and end_date:
        conditions.append("DATE(creation) BETWEEN %s AND %s")
        params.extend([start_date, end_date])
    elif start_date:
        conditions.append("DATE(creation) >= %s")
        params.append(start_date)
    elif end_date:
        conditions.append("DATE(creation) <= %s")
        params.append(end_date)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # 🧮 1️⃣ Total Leads + Total Deal Value
    total_stats = frappe.db.sql(f"""
        SELECT 
            COUNT(name) AS total_leads,
            IFNULL(SUM(custom_deal_value), 0) AS total_deal_value
        FROM `tabLead`
        {where_clause}
    """, params, as_dict=True)[0]

    # ✅ 2️⃣ Onboarded Leads + Deal Value
    onboarded_conditions = ["status = 'Onboarded'"]
    onboarded_params = []

    if owner:
        onboarded_conditions.append("owner = %s")
        onboarded_params.append(owner)

    if start_date and end_date:
        onboarded_conditions.append("DATE(creation) BETWEEN %s AND %s")
        onboarded_params.extend([start_date, end_date])
    elif start_date:
        onboarded_conditions.append("DATE(creation) >= %s")
        onboarded_params.append(start_date)
    elif end_date:
        onboarded_conditions.append("DATE(creation) <= %s")
        onboarded_params.append(end_date)

    onboarded_where = f"WHERE {' AND '.join(onboarded_conditions)}"

    onboarded_stats = frappe.db.sql(f"""
        SELECT 
            COUNT(name) AS onboarded_count,
            IFNULL(SUM(custom_deal_value), 0) AS onboarded_deal_value
        FROM `tabLead`
        {onboarded_where}
    """, onboarded_params, as_dict=True)[0]

    # 🧾 3️⃣ Combine everything
    return {
        "data": {
            "total_leads": total_stats.total_leads,
            "total_deal_value": total_stats.total_deal_value,
            "onboarded_count": onboarded_stats.onboarded_count,
            "onboarded_deal_value": onboarded_stats.onboarded_deal_value
        }
    }
