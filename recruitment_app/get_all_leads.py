import frappe

@frappe.whitelist()
def get_all_leads(lead_owner=None, limit_start=0, limit_page_length=20):
    """
    Fetch all Lead records with optional filter by lead_owner.
    Supports pagination and sorting by creation (DESC).
    """

    limit_start = int(limit_start)
    limit_page_length = int(limit_page_length)

    # 🧮 Count total leads
    count_query = "SELECT COUNT(*) as total FROM `tabLead`"
    count_params = []

    if lead_owner:
        count_query += " WHERE lead_owner = %s"
        count_params.append(lead_owner)

    total_count = frappe.db.sql(count_query, tuple(count_params), as_dict=True)[0]["total"]

    # 📦 Main query to fetch leads
    query = """
        SELECT
            name,
            owner,
            creation,
            modified,
            modified_by,
            naming_series,
            first_name,
            middle_name,
            last_name,
            custom_full_name,
            type,
            lead_name,
            job_title,
            gender,
            custom_phone_number,
            custom_offerings,
            custom_expected_close_date,
            custom_stage,
            lead_owner,
            status,
            request_type,
            custom_email_address,
            custom_lead_owner_name,
            company_name,
            no_of_employees,
            email_id,
            custom_expected_hiring_volume,
            annual_revenue,
            industry,
            city,
            custom_budgetinr,
            website,
            state,
            country,
            custom_estimated_hiring_,
            custom_average_salary,
            custom_fee,
            custom_deal_value,
            custom_fixed_charges,
            qualification_status,
            language,
            image,
            title,
            disabled,
            unsubscribed,
            blog_subscriber
        FROM `tabLead`
    """

    query_params = []
    if lead_owner:
        query += " WHERE lead_owner = %s"
        query_params.append(lead_owner)

    query += " ORDER BY creation DESC LIMIT %s, %s"
    query_params.extend([limit_start, limit_page_length])

    leads = frappe.db.sql(query, tuple(query_params), as_dict=True)

    # 📖 Pagination metadata
    total_pages = (total_count + limit_page_length - 1) // limit_page_length
    current_page = (limit_start // limit_page_length) + 1

    return {
        "data": leads,
        "total": total_count,
        "page": current_page,
        "page_size": limit_page_length,
        "total_pages": total_pages,
        "has_next": current_page < total_pages,
        "has_prev": current_page > 1
    }
