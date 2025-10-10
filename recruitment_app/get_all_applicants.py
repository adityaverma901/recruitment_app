import frappe

@frappe.whitelist(allow_guest=False)
def get_all_applicants(owner=None):
    """
    Fetch all Job Applicants with their experience and education details.
    Optionally filter by owner (email).
    """

    filters = {}
    if owner:
        filters["owner"] = owner

    # Fetch main applicant data
    applicants = frappe.get_all(
        "Job Applicant",
        filters=filters,
        fields=[
            "name",
            "applicant_name",
            "email_id",
            "phone_number",
            "country",
            "job_title",
            "designation",
            "status",
            "resume_attachment",
            "custom_company_name",
            "creation",
            "owner"
        ],
        order_by="creation desc"
    )

    # For each applicant, fetch child tables (experience and education)
    for applicant in applicants:
        # Fetch Experience child table
        applicant["custom_experience"] = frappe.get_all(
            "Experience",
            filters={"parent": applicant.name, "parenttype": "Job Applicant"},
            fields=[
                "company_name",
                "designation",
                "start_date",
                "current_company"
            ],
            order_by="idx asc"
        )

        # Fetch Education child table
        applicant["custom_education"] = frappe.get_all(
            "Education",
            filters={"parent": applicant.name, "parenttype": "Job Applicant"},
            fields=[
                "degree",
                "specialization",
                "institution",
                "year_of_passing",
                "percentagecgpa"
            ],
            order_by="idx asc"
        )

    return applicants
