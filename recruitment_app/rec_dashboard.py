import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_companies_by_user(email):
    """
    Fetch all unique company names from ToDo where allocated_to = given email.
    """
    if not email:
        frappe.throw(_("Email is required"))

    companies = frappe.get_all(
        "ToDo",
        filters={"allocated_to": email},
        fields=["distinct custom_company as company"],
        order_by="custom_company asc"
    )

    # Remove empty or null companies
    companies = [c.company for c in companies if c.company]

    return {"companies": companies}



@frappe.whitelist(allow_guest=False)
def get_job(email):
    """
    Fetch all job titles from ToDo where allocated_to = given email.
    Includes duplicates.
    """
    if not email:
        frappe.throw(_("Email is required"))

    jobs = frappe.get_all(
        "ToDo",
        filters={"allocated_to": email},
        fields=["custom_job_title"],
        order_by="custom_job_title asc"
    )

    # Extract the job titles and remove empty/null ones
    jobs = [j.custom_job_title for j in jobs if j.custom_job_title]

    return {"job_titles": jobs}





@frappe.whitelist(allow_guest=False)
def get_jobs_by_company(email, company=None):
    """
    Fetch all job titles from ToDo where allocated_to = given email, optionally filtered by company.
    """
    if not email:
        frappe.throw(_("Email is required"))

    filters = {"allocated_to": email}
    if company:
        filters["custom_company"] = company

    todos = frappe.get_all(
        "ToDo",
        filters=filters,
        fields=["custom_company", "custom_job_title"],
        order_by="custom_company asc"
    )

    result = {}
    for todo in todos:
        comp = todo.custom_company or "Unknown Company"
        job_title = todo.custom_job_title or "No Job Title"

        if comp not in result:
            result[comp] = []
        result[comp].append(job_title)

    return {"jobs_by_company": result}



import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_tagged_applicants(email):
    """
    Fetch all job applicants where status = 'Tagged' and owner = given email.
    """
    if not email:
        frappe.throw(_("Email is required"))

    applicants = frappe.get_all(
        "Job Applicant",
        filters={
            "status": "Tagged",
            "owner": email  # Use 'allocated_to' if your workflow assigns differently
        },
        fields=[
            "name",
            "applicant_name",
            "email_id",
            "phone_number",
            "country",
            "job_title",
            "designation",
            "notes",
            "resume_attachment",
            "resume_link",
            "lower_range",
            "upper_range"
        ],
        order_by="creation desc"
    )

    return {"tagged_applicants": applicants}






# @frappe.whitelist(allow_guest=False)
# def get_tagged_applicants_by_company(email, company=None):
#     """
#     Fetch all job applicants where status = 'Tagged' and owner = given email,
#     optionally filtered by company.
#     """
#     if not email:
#         frappe.throw(_("Email is required"))

#     # Get all tagged applicants for the user
#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={
#             "status": "Tagged",
#             "owner": email
#         },
#         fields=[
#             "name",
#             "applicant_name",
#             "email_id",
#             "phone_number",
#             "country",
#             "job_title",
#             "designation",
#             "notes",
#             "resume_attachment",
#             "resume_link",
#             "lower_range",
#             "upper_range"
#         ],
#         order_by="creation desc"
#     )

#     result = {}

#     for applicant in applicants:
#         company_name = "Unknown Company"
#         if applicant.job_title:
#             job = frappe.get_doc("Job Opening", applicant.job_title)
#             company_name = job.company if job.company else "Unknown Company"

#         # Skip if company filter is provided and does not match
#         if company and company_name != company:
#             continue

#         if company_name not in result:
#             result[company_name] = []

#         result[company_name].append(applicant)

#     return {"applicants_by_company": result}




@frappe.whitelist(allow_guest=False)
def get_tagged_applicants_by_company(email, company=None):
    """
    Fetch all job applicants where status = 'Tagged' and owner = given email,
    optionally filtered by company.
    """
    if not email:
        frappe.throw(_("Email is required"))

    # First, fetch Job Openings for the company filter (if provided)
    job_filters = {}
    if company:
        job_filters["company"] = company

    job_openings = frappe.get_all(
        "Job Opening",
        filters=job_filters,
        fields=["name", "company"]
    )

    # Build a map of job_name -> company
    job_map = {job.name: job.company for job in job_openings}

    # Fetch all tagged applicants for the user
    applicants = frappe.get_all(
        "Job Applicant",
        filters={
            "status": "Tagged",
            "owner": email
        },
        fields=[
            "name",
            "applicant_name",
            "email_id",
            "phone_number",
            "country",
            "job_title",  # Link to Job Opening
            "designation",
            "notes",
            "resume_attachment",
            "resume_link",
            "lower_range",
            "upper_range"
        ],
        order_by="creation desc"
    )

    result = {}

    for applicant in applicants:
        job_id = applicant.job_title  # Linked Job Opening
        company_name = job_map.get(job_id, "Unknown Company")

        # Skip if company filter is applied and does not match
        if company and company_name != company:
            continue

        if company_name not in result:
            result[company_name] = []

        result[company_name].append(applicant)

    return {"applicants_by_company": result}
