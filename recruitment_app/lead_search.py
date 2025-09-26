import frappe

@frappe.whitelist(allow_guest=False)
def search_lead(search_term=None):
    """
    Search leads by custom_full_name, company_name, custom_phone_number, or custom_email_address.
    Returns lead details including contact, company, industry, offerings, hiring metrics, etc.
    """
    try:
        if not search_term:
            return {
                "status": "error",
                "message": "Please provide a search term",
                "data": []
            }

        values = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]

        query = """
            SELECT
                l.name,
                l.custom_full_name,
                l.company_name,
                l.industry,
                l.custom_offerings,
                l.custom_expected_hiring_volume,
                l.custom_estimated_hiring_,
                l.custom_average_salary,
                l.custom_fee,
                l.custom_deal_value,
                l.custom_expected_close_date,
                l.custom_phone_number,
                l.custom_email_address
            FROM `tabLead` l
            WHERE (
                l.custom_full_name LIKE %s
                OR l.company_name LIKE %s
                OR l.custom_phone_number LIKE %s
                OR l.custom_email_address LIKE %s
            )
            AND l.custom_stage IN ('Contract', 'Onboarded','Follow-Up / Relationship Management')

            ORDER BY l.creation DESC
            LIMIT 50
        """

        leads = frappe.db.sql(query, values, as_dict=True)

        # ✅ Auto calculate custom_deal_value if missing
        for lead in leads:
            fee = lead.get("custom_fee") or 0
            hiring = lead.get("custom_estimated_hiring_") or 0
            salary = lead.get("custom_average_salary") or 0
            if not lead.get("custom_deal_value"):
                lead["custom_deal_value"] = (fee / 100) * hiring * salary  # since fee is percent

        return {
            "status": "success",
            "message": f"Found {len(leads)} leads",
            "data": leads
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Lead Search API Error")
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "data": []
        }
