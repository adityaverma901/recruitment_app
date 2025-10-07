# import frappe
# from frappe import _

# @frappe.whitelist(allow_guest=False)
# def get_recruiter_dashboard_data(email=None):
#     """
#     test
#     Master function to fetch all recruiter dashboard data in a single API call.
#     Returns all applicants grouped by status with company information.
    
#     Args:
#         email: User email (defaults to current session user if not provided)
    
#     Returns:
#         Dictionary containing:
#         - companies: List of unique companies from ToDo
#         - jobs_by_company: Job titles grouped by company from ToDo
#         - applicants_by_status: Applicants grouped by each status
#         - metrics: Count of applicants by status
#         - summary: Overall statistics
#     """
#     if not email:
#         email = frappe.session.user
    
#     if not email:
#         frappe.throw(_("Email is required"))

#     # Define all statuses
#     statuses = [
#         "Tagged",
#         "Shortlisted", 
#         "Assessment Stage",
#         "Interview Stage",
#         "Offered",
#         "Rejected",
#         "Joined"
#     ]

#     # Fetch companies and jobs from ToDo
#     todos = frappe.get_all(
#         "ToDo",
#         filters={"allocated_to": email},
#         fields=["custom_company", "custom_job_title"],
#         order_by="custom_company asc"
#     )

#     # Process ToDo data
#     companies_set = set()
#     jobs_by_company = {}
    
#     for todo in todos:
#         comp = todo.custom_company or "Unknown Company"
#         job_title = todo.custom_job_title
        
#         if todo.custom_company:
#             companies_set.add(todo.custom_company)
        
#         if comp not in jobs_by_company:
#             jobs_by_company[comp] = []
#         if job_title:
#             jobs_by_company[comp].append(job_title)

#     # Fetch Job Opening map for company association
#     job_openings = frappe.get_all(
#         "Job Opening",
#         fields=["name", "company"]
#     )
#     job_map = {job.name: job.company for job in job_openings}

#     # Fetch all applicants in one query
#     all_applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"owner": email},
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
#             "upper_range",
#             "status",
#             "creation",
#             "modified"
#         ],
#         order_by="creation desc"
#     )

#     # Initialize result structures
#     metrics = {status: 0 for status in statuses}
#     applicants_by_status = {
#         "tagged_applicants": [],
#         "shortlisted_applicants": [],
#         "assessment_stage_applicants": [],
#         "interview_stage_applicants": [],
#         "offered_applicants": [],
#         "rejected_applicants": [],
#         "joined_applicants": []
#     }

#     # Status mapping to response keys
#     status_key_map = {
#         "Tagged": "tagged_applicants",
#         "Shortlisted": "shortlisted_applicants",
#         "Assessment Stage": "assessment_stage_applicants",
#         "Interview Stage": "interview_stage_applicants",
#         "Offered": "offered_applicants",
#         "Rejected": "rejected_applicants",
#         "Joined": "joined_applicants"
#     }

#     # Process all applicants
#     for applicant in all_applicants:
#         job_id = applicant.job_title
#         company_name = job_map.get(job_id, "Unknown Company")
#         status = applicant.status

#         # Count metrics
#         if status in metrics:
#             metrics[status] += 1

#         # Prepare applicant data
#         applicant_data = {
#             "name": applicant.name,
#             "applicant_name": applicant.applicant_name,
#             "email_id": applicant.email_id,
#             "phone_number": applicant.phone_number,
#             "country": applicant.country,
#             "job_title": applicant.job_title,
#             "designation": applicant.designation,
#             "notes": applicant.notes,
#             "resume_attachment": applicant.resume_attachment,
#             "resume_link": applicant.resume_link,
#             "lower_range": applicant.lower_range,
#             "upper_range": applicant.upper_range,
#             "company": company_name
#         }

#         # Add to appropriate status list
#         if status in status_key_map:
#             applicants_by_status[status_key_map[status]].append(applicant_data)

#     # Calculate summary statistics
#     total_applicants = sum(metrics.values())
#     active_pipeline = (
#         metrics.get("Tagged", 0) +
#         metrics.get("Shortlisted", 0) +
#         metrics.get("Assessment Stage", 0) +
#         metrics.get("Interview Stage", 0)
#     )
    
#     summary = {
#         "total_applicants": total_applicants,
#         "active_pipeline": active_pipeline,
#         "offered": metrics.get("Offered", 0),
#         "joined": metrics.get("Joined", 0),
#         "rejected": metrics.get("Rejected", 0),
#         "conversion_rate": round((metrics.get("Joined", 0) / total_applicants * 100), 2) if total_applicants > 0 else 0
#     }

#     return {
#         "success": True,
#         "companies": sorted(list(companies_set)),
#         "jobs_by_company": jobs_by_company,
#         "metrics": metrics,
#         "summary": summary,
#         **applicants_by_status  # Unpacks all status lists at root level
#     }


# @frappe.whitelist(allow_guest=False)
# def get_recruiter_dashboard_only_email(email=None):
#     """
#     Fetch all recruiter dashboard data in a single API call
#     """
#     if not email:
#         email = frappe.session.user
    
#     # Fetch all required data with optimized queries
#     data = {
#         'active_clients': get_companies_by_user(email),
#         'job_openings': get_job(email),
#         'tagged_applicants': get_tagged_applicants(email),
#         'shortlisted_applicants': get_shortlisted_applicants(email),
#         'assessment_stage_applicants': get_assessment_stage_applicants(email),
#         'interview_stage_applicants': get_interview_stage_applicants(email),
#         'offered_applicants': get_offered_applicants(email),
#         'rejected_applicants': get_rejected_applicants(email),
#         'joined_applicants': get_joined_applicants(email)
#     }
    
#     return data


# @frappe.whitelist(allow_guest=False)
# def get_recruiter_dashboard_both(email=None,company=None):
#     """
#     Fetch all recruiter dashboard data in a single API call
#     """
#     if not email:
#         email = frappe.session.user
    
#     # Fetch all required data with optimized queries
#     data = {
#         'jobs_opening_by_company': get_jobs_by_company(email, company),
#        'tagged_applicants_by_company':get_tagged_applicants_by_company(email, company),
#         'shortlisted_applicants_by_company':get_shortlisted_applicants_by_company(email, company),
#         'assessment_stage_applicants_by_company':get_assessment_stage_applicants_by_company(email, company),
#         'interview_stage_applicants_by_company':get_interview_stage_applicants_by_company(email, company),
#         'offered_applicants_by_company':get_offered_applicants_by_company(email, company),
#         'rejected_applicants_by_company':get_rejected_applicants_by_company(email, company),
#         'joined_applicants_by_company':get_joined_applicants_by_company(email, company)
      
#     }
    
#     return data



# @frappe.whitelist(allow_guest=False)
# def get_recruiter_dashboard_data_by_company(email=None, company=None):
#     """
#     Master function to fetch all recruiter dashboard data filtered by company.
#     Returns all applicants grouped by status for a specific company.
    
#     Args:
#         email: User email (defaults to current session user if not provided)
#         company: Company name to filter by
    
#     Returns:
#         Dictionary containing:
#         - companies: List of unique companies from ToDo
#         - jobs_by_company: Job titles for the filtered company
#         - applicants_by_status: Applicants grouped by status (filtered by company)
#         - applicants_by_company: Applicants grouped by company and status
#         - metrics: Count of applicants by status
#         - summary: Overall statistics
#     """
#     if not email:
#         email = frappe.session.user
    
#     if not email:
#         frappe.throw(_("Email is required"))

#     # Define all statuses
#     statuses = [
#         "Tagged",
#         "Shortlisted", 
#         "Assessment Stage",
#         "Interview Stage",
#         "Offered",
#         "Rejected",
#         "Joined"
#     ]

#     # Fetch companies and jobs from ToDo
#     todo_filters = {"allocated_to": email}
#     if company:
#         todo_filters["custom_company"] = company

#     todos = frappe.get_all(
#         "ToDo",
#         filters=todo_filters,
#         fields=["custom_company", "custom_job_title"],
#         order_by="custom_company asc"
#     )

#     # Process ToDo data
#     companies_set = set()
#     jobs_by_company = {}
    
#     for todo in todos:
#         comp = todo.custom_company or "Unknown Company"
#         job_title = todo.custom_job_title
        
#         if todo.custom_company:
#             companies_set.add(todo.custom_company)
        
#         if comp not in jobs_by_company:
#             jobs_by_company[comp] = []
#         if job_title:
#             jobs_by_company[comp].append(job_title)

#     # Fetch Job Opening map with optional company filter
#     job_filters = {}
#     if company:
#         job_filters["company"] = company

#     job_openings = frappe.get_all(
#         "Job Opening",
#         filters=job_filters,
#         fields=["name", "company"]
#     )
#     job_map = {job.name: job.company for job in job_openings}

#     # Fetch all applicants in one query
#     all_applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"owner": email},
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
#             "upper_range",
#             "status",
#             "creation",
#             "modified"
#         ],
#         order_by="creation desc"
#     )

#     # Initialize result structures
#     metrics = {status: 0 for status in statuses}
    
#     # For backward compatibility with existing endpoints
#     applicants_by_status = {
#         "tagged_applicants_by_company": {},
#         "shortlisted_applicants_by_company": {},
#         "assessment_stage_applicants_by_company": {},
#         "interview_stage_applicants_by_company": {},
#         "offered_applicants_by_company": {},
#         "rejected_applicants_by_company": {},
#         "joined_applicants_by_company": {}
#     }

#     # Status mapping
#     status_key_map = {
#         "Tagged": "tagged_applicants_by_company",
#         "Shortlisted": "shortlisted_applicants_by_company",
#         "Assessment Stage": "assessment_stage_applicants_by_company",
#         "Interview Stage": "interview_stage_applicants_by_company",
#         "Offered": "offered_applicants_by_company",
#         "Rejected": "rejected_applicants_by_company",
#         "Joined": "joined_applicants_by_company"
#     }

#     # Process all applicants
#     for applicant in all_applicants:
#         job_id = applicant.job_title
#         company_name = job_map.get(job_id, "Unknown Company")
        
#         # Skip if company filter is applied and does not match
#         if company and company_name != company:
#             continue

#         status = applicant.status

#         # Count metrics
#         if status in metrics:
#             metrics[status] += 1

#         # Prepare applicant data
#         applicant_data = {
#             "name": applicant.name,
#             "applicant_name": applicant.applicant_name,
#             "email_id": applicant.email_id,
#             "phone_number": applicant.phone_number,
#             "country": applicant.country,
#             "job_title": applicant.job_title,
#             "designation": applicant.designation,
#             "notes": applicant.notes,
#             "resume_attachment": applicant.resume_attachment,
#             "resume_link": applicant.resume_link,
#             "lower_range": applicant.lower_range,
#             "upper_range": applicant.upper_range
#         }

#         # Add to company-grouped structure
#         if status in status_key_map:
#             status_key = status_key_map[status]
#             if company_name not in applicants_by_status[status_key]:
#                 applicants_by_status[status_key][company_name] = []
#             applicants_by_status[status_key][company_name].append(applicant_data)

#     # Calculate summary statistics
#     total_applicants = sum(metrics.values())
#     active_pipeline = (
#         metrics.get("Tagged", 0) +
#         metrics.get("Shortlisted", 0) +
#         metrics.get("Assessment Stage", 0) +
#         metrics.get("Interview Stage", 0)
#     )
    
#     summary = {
#         "total_applicants": total_applicants,
#         "active_pipeline": active_pipeline,
#         "offered": metrics.get("Offered", 0),
#         "joined": metrics.get("Joined", 0),
#         "rejected": metrics.get("Rejected", 0),
#         "conversion_rate": round((metrics.get("Joined", 0) / total_applicants * 100), 2) if total_applicants > 0 else 0
#     }

#     # Format output to match original API structure
#     result = {
#         "success": True,
#         "companies": sorted(list(companies_set)),
#         "jobs_by_company": jobs_by_company,
#         "metrics": metrics,
#         "summary": summary,
#         "company_filter": company
#     }

#     # Add each status's applicants_by_company at root level
#     for status_key in applicants_by_status:
#         result[status_key] = {"applicants_by_company": applicants_by_status[status_key]}

#     return result


# @frappe.whitelist(allow_guest=False)
# def get_companies_by_user(email):
#     """
#     Fetch all unique company names from ToDo where allocated_to = given email.
#     """
#     if not email:
#         frappe.throw(_("Email is required"))

#     companies = frappe.get_all(
#         "ToDo",
#         filters={"allocated_to": email},
#         fields=["distinct custom_company as company"],
#         order_by="custom_company asc"
#     )

#     # Remove empty or null companies
#     companies = [c.company for c in companies if c.company]

#     return {"companies": companies}


# @frappe.whitelist(allow_guest=False)
# def get_job(email):
#     """
#     Fetch all job titles from ToDo where allocated_to = given email.
#     Includes duplicates.
#     """
#     if not email:
#         frappe.throw(_("Email is required"))

#     jobs = frappe.get_all(
#         "ToDo",
#         filters={"allocated_to": email},
#         fields=["custom_job_title"],
#         order_by="custom_job_title asc"
#     )

#     # Extract the job titles and remove empty/null ones
#     jobs = [j.custom_job_title for j in jobs if j.custom_job_title]

#     return {"job_titles": jobs}


# @frappe.whitelist(allow_guest=False)
# def get_jobs_by_company(email, company=None):
#     """
#     Fetch all job titles from ToDo where allocated_to = given email, optionally filtered by company.
#     """
#     if not email:
#         frappe.throw(_("Email is required"))

#     filters = {"allocated_to": email}
#     if company:
#         filters["custom_company"] = company

#     todos = frappe.get_all(
#         "ToDo",
#         filters=filters,
#         fields=["custom_company", "custom_job_title"],
#         order_by="custom_company asc"
#     )

#     result = {}
#     for todo in todos:
#         comp = todo.custom_company or "Unknown Company"
#         job_title = todo.custom_job_title or "No Job Title"

#         if comp not in result:
#             result[comp] = []
#         result[comp].append(job_title)

#     return {"jobs_by_company": result}


# @frappe.whitelist(allow_guest=False)
# def get_tagged_applicants(email):
#     """
#     Fetch all job applicants where status = 'Tagged' and owner = given email.
#     """
#     if not email:
#         frappe.throw(_("Email is required"))

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={
#             "status": "Tagged",
#             "owner": email  # Use 'allocated_to' if your workflow assigns differently
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

#     return {"tagged_applicants": applicants}


# @frappe.whitelist(allow_guest=False)
# def get_shortlisted_applicants(email):
#     if not email:
#         frappe.throw(_("Email is required"))

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Shortlisted", "owner": email},
#         fields=[
#             "name", "applicant_name", "email_id", "phone_number", "country",
#             "job_title", "designation", "notes", "resume_attachment",
#             "resume_link", "lower_range", "upper_range"
#         ],
#         order_by="creation desc"
#     )
#     return {"shortlisted_applicants": applicants}


# @frappe.whitelist(allow_guest=False)
# def get_assessment_stage_applicants(email):
#     if not email:
#         frappe.throw(_("Email is required"))

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Assessment Stage", "owner": email},
#         fields=[
#             "name", "applicant_name", "email_id", "phone_number", "country",
#             "job_title", "designation", "notes", "resume_attachment",
#             "resume_link", "lower_range", "upper_range"
#         ],
#         order_by="creation desc"
#     )
#     return {"assessment_stage_applicants": applicants}


# @frappe.whitelist(allow_guest=False)
# def get_interview_stage_applicants(email):
#     if not email:
#         frappe.throw(_("Email is required"))

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Interview Stage", "owner": email},
#         fields=[
#             "name", "applicant_name", "email_id", "phone_number", "country",
#             "job_title", "designation", "notes", "resume_attachment",
#             "resume_link", "lower_range", "upper_range"
#         ],
#         order_by="creation desc"
#     )
#     return {"interview_stage_applicants": applicants}


# @frappe.whitelist(allow_guest=False)
# def get_offered_applicants(email):
#     if not email:
#         frappe.throw(_("Email is required"))

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Offered", "owner": email},
#         fields=[
#             "name", "applicant_name", "email_id", "phone_number", "country",
#             "job_title", "designation", "notes", "resume_attachment",
#             "resume_link", "lower_range", "upper_range"
#         ],
#         order_by="creation desc"
#     )
#     return {"offered_applicants": applicants}


# @frappe.whitelist(allow_guest=False)
# def get_rejected_applicants(email):
#     if not email:
#         frappe.throw(_("Email is required"))

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Rejected", "owner": email},
#         fields=[
#             "name", "applicant_name", "email_id", "phone_number", "country",
#             "job_title", "designation", "notes", "resume_attachment",
#             "resume_link", "lower_range", "upper_range"
#         ],
#         order_by="creation desc"
#     )
#     return {"rejected_applicants": applicants}


# @frappe.whitelist(allow_guest=False)
# def get_joined_applicants(email):
#     if not email:
#         frappe.throw(_("Email is required"))

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Joined", "owner": email},
#         fields=[
#             "name", "applicant_name", "email_id", "phone_number", "country",
#             "job_title", "designation", "notes", "resume_attachment",
#             "resume_link", "lower_range", "upper_range"
#         ],
#         order_by="creation desc"
#     )
#     return {"joined_applicants": applicants}


# @frappe.whitelist(allow_guest=False)
# def get_tagged_applicants_by_company(email, company=None):
#     """
#     Fetch all job applicants where status = 'Tagged' and owner = given email,
#     optionally filtered by company.
#     """
#     if not email:
#         frappe.throw(_("Email is required"))

#     # First, fetch Job Openings for the company filter (if provided)
#     job_filters = {}
#     if company:
#         job_filters["company"] = company

#     job_openings = frappe.get_all(
#         "Job Opening",
#         filters=job_filters,
#         fields=["name", "company"]
#     )

#     # Build a map of job_name -> company
#     job_map = {job.name: job.company for job in job_openings}

#     # Fetch all tagged applicants for the user
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
#             "job_title",  # Link to Job Opening
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
#         job_id = applicant.job_title  # Linked Job Opening
#         company_name = job_map.get(job_id, "Unknown Company")

#         # Skip if company filter is applied and does not match
#         if company and company_name != company:
#             continue

#         if company_name not in result:
#             result[company_name] = []

#         result[company_name].append(applicant)

#     return {"applicants_by_company": result}


# @frappe.whitelist(allow_guest=False)
# def get_shortlisted_applicants_by_company(email, company=None):
#     if not email:
#         frappe.throw(_("Email is required"))

#     job_filters = {}
#     if company:
#         job_filters["company"] = company

#     job_openings = frappe.get_all("Job Opening", filters=job_filters, fields=["name", "company"])
#     job_map = {job.name: job.company for job in job_openings}

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Shortlisted", "owner": email},
#         fields=[
#             "name","applicant_name","email_id","phone_number","country",
#             "job_title","designation","notes","resume_attachment","resume_link",
#             "lower_range","upper_range"
#         ],
#         order_by="creation desc"
#     )

#     result = {}
#     for applicant in applicants:
#         job_id = applicant.job_title
#         company_name = job_map.get(job_id, "Unknown Company")
#         if company and company_name != company:
#             continue
#         if company_name not in result:
#             result[company_name] = []
#         result[company_name].append(applicant)

#     return {"applicants_by_company": result}


# @frappe.whitelist(allow_guest=False)
# def get_assessment_stage_applicants_by_company(email, company=None):
#     if not email:
#         frappe.throw(_("Email is required"))

#     job_filters = {}
#     if company:
#         job_filters["company"] = company

#     job_openings = frappe.get_all("Job Opening", filters=job_filters, fields=["name", "company"])
#     job_map = {job.name: job.company for job in job_openings}

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Assessment Stage", "owner": email},
#         fields=[
#             "name","applicant_name","email_id","phone_number","country",
#             "job_title","designation","notes","resume_attachment","resume_link",
#             "lower_range","upper_range"
#         ],
#         order_by="creation desc"
#     )

#     result = {}
#     for applicant in applicants:
#         job_id = applicant.job_title
#         company_name = job_map.get(job_id, "Unknown Company")
#         if company and company_name != company:
#             continue
#         if company_name not in result:
#             result[company_name] = []
#         result[company_name].append(applicant)

#     return {"applicants_by_company": result}


# @frappe.whitelist(allow_guest=False)
# def get_interview_stage_applicants_by_company(email, company=None):
#     if not email:
#         frappe.throw(_("Email is required"))

#     job_filters = {}
#     if company:
#         job_filters["company"] = company

#     job_openings = frappe.get_all("Job Opening", filters=job_filters, fields=["name", "company"])
#     job_map = {job.name: job.company for job in job_openings}

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Interview Stage", "owner": email},
#         fields=[
#             "name","applicant_name","email_id","phone_number","country",
#             "job_title","designation","notes","resume_attachment","resume_link",
#             "lower_range","upper_range"
#         ],
#         order_by="creation desc"
#     )

#     result = {}
#     for applicant in applicants:
#         job_id = applicant.job_title
#         company_name = job_map.get(job_id, "Unknown Company")
#         if company and company_name != company:
#             continue
#         if company_name not in result:
#             result[company_name] = []
#         result[company_name].append(applicant)

#     return {"applicants_by_company": result}


# @frappe.whitelist(allow_guest=False)
# def get_offered_applicants_by_company(email, company=None):
#     if not email:
#         frappe.throw(_("Email is required"))

#     job_filters = {}
#     if company:
#         job_filters["company"] = company

#     job_openings = frappe.get_all("Job Opening", filters=job_filters, fields=["name", "company"])
#     job_map = {job.name: job.company for job in job_openings}

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Offered", "owner": email},
#         fields=[
#             "name","applicant_name","email_id","phone_number","country",
#             "job_title","designation","notes","resume_attachment","resume_link",
#             "lower_range","upper_range"
#         ],
#         order_by="creation desc"
#     )

#     result = {}
#     for applicant in applicants:
#         job_id = applicant.job_title
#         company_name = job_map.get(job_id, "Unknown Company")
#         if company and company_name != company:
#             continue
#         if company_name not in result:
#             result[company_name] = []
#         result[company_name].append(applicant)

#     return {"applicants_by_company": result}


# @frappe.whitelist(allow_guest=False)
# def get_rejected_applicants_by_company(email, company=None):
#     if not email:
#         frappe.throw(_("Email is required"))

#     job_filters = {}
#     if company:
#         job_filters["company"] = company

#     job_openings = frappe.get_all("Job Opening", filters=job_filters, fields=["name", "company"])
#     job_map = {job.name: job.company for job in job_openings}

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Rejected", "owner": email},
#         fields=[
#             "name","applicant_name","email_id","phone_number","country",
#             "job_title","designation","notes","resume_attachment","resume_link",
#             "lower_range","upper_range"
#         ],
#         order_by="creation desc"
#     )

#     result = {}
#     for applicant in applicants:
#         job_id = applicant.job_title
#         company_name = job_map.get(job_id, "Unknown Company")
#         if company and company_name != company:
#             continue
#         if company_name not in result:
#             result[company_name] = []
#         result[company_name].append(applicant)

#     return {"applicants_by_company": result}


# @frappe.whitelist(allow_guest=False)
# def get_joined_applicants_by_company(email, company=None):
#     if not email:
#         frappe.throw(_("Email is required"))

#     job_filters = {}
#     if company:
#         job_filters["company"] = company

#     job_openings = frappe.get_all("Job Opening", filters=job_filters, fields=["name", "company"])
#     job_map = {job.name: job.company for job in job_openings}

#     applicants = frappe.get_all(
#         "Job Applicant",
#         filters={"status": "Joined", "owner": email},
#         fields=[
#             "name","applicant_name","email_id","phone_number","country",
#             "job_title","designation","notes","resume_attachment","resume_link",
#             "lower_range","upper_range"
#         ],
#         order_by="creation desc"
#     )

#     result = {}
#     for applicant in applicants:
#         job_id = applicant.job_title
#         company_name = job_map.get(job_id, "Unknown Company")
#         if company and company_name != company:
#             continue
#         if company_name not in result:
#             result[company_name] = []
#         result[company_name].append(applicant)

#     return {"applicants_by_company": result}





import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_recruiter_dashboard_data(email=None):
    """
    Master function to fetch all recruiter dashboard data in a single API call.
    Returns all applicants grouped by status with company information.
    
    Args:
        email: User email (defaults to current session user if not provided)
    
    Returns:
        Dictionary containing:
        - companies: List of unique companies from ToDo
        - jobs_by_company: Job titles grouped by company from ToDo
        - applicants_by_status: Applicants grouped by each status
        - metrics: Count of applicants by status
        - summary: Overall statistics
    """
    if not email:
        email = frappe.session.user
    
    if not email:
        frappe.throw(_("Email is required"))

    # Define all statuses
    statuses = [
        "Tagged",
        "Shortlisted", 
        "Assessment Stage",
        "Interview Stage",
        "Offered",
        "Rejected",
        "Joined"
    ]

    # Fetch companies and jobs from ToDo
    todos = frappe.get_all(
        "ToDo",
        filters={"allocated_to": email},
        fields=["custom_company", "custom_job_title"],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="custom_company asc"
    )

    # Process ToDo data
    companies_set = set()
    jobs_by_company = {}
    
    for todo in todos:
        comp = todo.custom_company or "Unknown Company"
        job_title = todo.custom_job_title
        
        if todo.custom_company:
            companies_set.add(todo.custom_company)
        
        if comp not in jobs_by_company:
            jobs_by_company[comp] = []
        if job_title:
            jobs_by_company[comp].append(job_title)

    # Fetch Job Opening map for company association
    job_openings = frappe.get_all(
        "Job Opening",
        fields=["name", "company"],
        limit=0  # CHANGED: Added limit=0 to remove default 20 record limit
    )
    job_map = {job.name: job.company for job in job_openings}

    # Fetch all applicants in one query
    all_applicants = frappe.get_all(
        "Job Applicant",
        filters={"owner": email},
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
            "upper_range",
            "status",
            "creation",
            "modified"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )

    # Initialize result structures
    metrics = {status: 0 for status in statuses}
    applicants_by_status = {
        "tagged_applicants": [],
        "shortlisted_applicants": [],
        "assessment_stage_applicants": [],
        "interview_stage_applicants": [],
        "offered_applicants": [],
        "rejected_applicants": [],
        "joined_applicants": []
    }

    # Status mapping to response keys
    status_key_map = {
        "Tagged": "tagged_applicants",
        "Shortlisted": "shortlisted_applicants",
        "Assessment Stage": "assessment_stage_applicants",
        "Interview Stage": "interview_stage_applicants",
        "Offered": "offered_applicants",
        "Rejected": "rejected_applicants",
        "Joined": "joined_applicants"
    }

    # Process all applicants
    for applicant in all_applicants:
        job_id = applicant.job_title
        company_name = job_map.get(job_id, "Unknown Company")
        status = applicant.status

        # Count metrics
        if status in metrics:
            metrics[status] += 1

        # Prepare applicant data
        applicant_data = {
            "name": applicant.name,
            "applicant_name": applicant.applicant_name,
            "email_id": applicant.email_id,
            "phone_number": applicant.phone_number,
            "country": applicant.country,
            "job_title": applicant.job_title,
            "designation": applicant.designation,
            "notes": applicant.notes,
            "resume_attachment": applicant.resume_attachment,
            "resume_link": applicant.resume_link,
            "lower_range": applicant.lower_range,
            "upper_range": applicant.upper_range,
            "company": company_name
        }

        # Add to appropriate status list
        if status in status_key_map:
            applicants_by_status[status_key_map[status]].append(applicant_data)

    # Calculate summary statistics
    total_applicants = sum(metrics.values())
    active_pipeline = (
        metrics.get("Tagged", 0) +
        metrics.get("Shortlisted", 0) +
        metrics.get("Assessment Stage", 0) +
        metrics.get("Interview Stage", 0)
    )
    
    summary = {
        "total_applicants": total_applicants,
        "active_pipeline": active_pipeline,
        "offered": metrics.get("Offered", 0),
        "joined": metrics.get("Joined", 0),
        "rejected": metrics.get("Rejected", 0),
        "conversion_rate": round((metrics.get("Joined", 0) / total_applicants * 100), 2) if total_applicants > 0 else 0
    }

    return {
        "success": True,
        "companies": sorted(list(companies_set)),
        "jobs_by_company": jobs_by_company,
        "metrics": metrics,
        "summary": summary,
        **applicants_by_status  # Unpacks all status lists at root level
    }


@frappe.whitelist(allow_guest=False)
def get_recruiter_dashboard_only_email(email=None):
    """
    Fetch all recruiter dashboard data in a single API call
    """
    if not email:
        email = frappe.session.user
    
    # Fetch all required data with optimized queries
    data = {
        'active_clients': get_companies_by_user(email),
        'job_openings': get_job(email),
        'tagged_applicants': get_tagged_applicants(email),
        'shortlisted_applicants': get_shortlisted_applicants(email),
        'assessment_stage_applicants': get_assessment_stage_applicants(email),
        'interview_stage_applicants': get_interview_stage_applicants(email),
        'offered_applicants': get_offered_applicants(email),
        'rejected_applicants': get_rejected_applicants(email),
        'joined_applicants': get_joined_applicants(email)
    }
    
    return data


@frappe.whitelist(allow_guest=False)
def get_recruiter_dashboard_both(email=None,company=None):
    """
    Fetch all recruiter dashboard data in a single API call
    """
    if not email:
        email = frappe.session.user
    
    # Fetch all required data with optimized queries
    data = {
        'jobs_opening_by_company': get_jobs_by_company(email, company),
       'tagged_applicants_by_company':get_tagged_applicants_by_company(email, company),
        'shortlisted_applicants_by_company':get_shortlisted_applicants_by_company(email, company),
        'assessment_stage_applicants_by_company':get_assessment_stage_applicants_by_company(email, company),
        'interview_stage_applicants_by_company':get_interview_stage_applicants_by_company(email, company),
        'offered_applicants_by_company':get_offered_applicants_by_company(email, company),
        'rejected_applicants_by_company':get_rejected_applicants_by_company(email, company),
        'joined_applicants_by_company':get_joined_applicants_by_company(email, company)
      
    }
    
    return data



@frappe.whitelist(allow_guest=False)
def get_recruiter_dashboard_data_by_company(email=None, company=None):
    """
    Master function to fetch all recruiter dashboard data filtered by company.
    Returns all applicants grouped by status for a specific company.
    
    Args:
        email: User email (defaults to current session user if not provided)
        company: Company name to filter by
    
    Returns:
        Dictionary containing:
        - companies: List of unique companies from ToDo
        - jobs_by_company: Job titles for the filtered company
        - applicants_by_status: Applicants grouped by status (filtered by company)
        - applicants_by_company: Applicants grouped by company and status
        - metrics: Count of applicants by status
        - summary: Overall statistics
    """
    if not email:
        email = frappe.session.user
    
    if not email:
        frappe.throw(_("Email is required"))

    # Define all statuses
    statuses = [
        "Tagged",
        "Shortlisted", 
        "Assessment Stage",
        "Interview Stage",
        "Offered",
        "Rejected",
        "Joined"
    ]

    # Fetch companies and jobs from ToDo
    todo_filters = {"allocated_to": email}
    if company:
        todo_filters["custom_company"] = company

    todos = frappe.get_all(
        "ToDo",
        filters=todo_filters,
        fields=["custom_company", "custom_job_title"],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="custom_company asc"
    )

    # Process ToDo data
    companies_set = set()
    jobs_by_company = {}
    
    for todo in todos:
        comp = todo.custom_company or "Unknown Company"
        job_title = todo.custom_job_title
        
        if todo.custom_company:
            companies_set.add(todo.custom_company)
        
        if comp not in jobs_by_company:
            jobs_by_company[comp] = []
        if job_title:
            jobs_by_company[comp].append(job_title)

    # Fetch Job Opening map with optional company filter
    job_filters = {}
    if company:
        job_filters["company"] = company

    job_openings = frappe.get_all(
        "Job Opening",
        filters=job_filters,
        fields=["name", "company"],
        limit=0  # CHANGED: Added limit=0 to remove default 20 record limit
    )
    job_map = {job.name: job.company for job in job_openings}

    # Fetch all applicants in one query
    all_applicants = frappe.get_all(
        "Job Applicant",
        filters={"owner": email},
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
            "upper_range",
            "status",
            "creation",
            "modified"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )

    # Initialize result structures
    metrics = {status: 0 for status in statuses}
    
    # For backward compatibility with existing endpoints
    applicants_by_status = {
        "tagged_applicants_by_company": {},
        "shortlisted_applicants_by_company": {},
        "assessment_stage_applicants_by_company": {},
        "interview_stage_applicants_by_company": {},
        "offered_applicants_by_company": {},
        "rejected_applicants_by_company": {},
        "joined_applicants_by_company": {}
    }

    # Status mapping
    status_key_map = {
        "Tagged": "tagged_applicants_by_company",
        "Shortlisted": "shortlisted_applicants_by_company",
        "Assessment Stage": "assessment_stage_applicants_by_company",
        "Interview Stage": "interview_stage_applicants_by_company",
        "Offered": "offered_applicants_by_company",
        "Rejected": "rejected_applicants_by_company",
        "Joined": "joined_applicants_by_company"
    }

    # Process all applicants
    for applicant in all_applicants:
        job_id = applicant.job_title
        company_name = job_map.get(job_id, "Unknown Company")
        
        # Skip if company filter is applied and does not match
        if company and company_name != company:
            continue

        status = applicant.status

        # Count metrics
        if status in metrics:
            metrics[status] += 1

        # Prepare applicant data
        applicant_data = {
            "name": applicant.name,
            "applicant_name": applicant.applicant_name,
            "email_id": applicant.email_id,
            "phone_number": applicant.phone_number,
            "country": applicant.country,
            "job_title": applicant.job_title,
            "designation": applicant.designation,
            "notes": applicant.notes,
            "resume_attachment": applicant.resume_attachment,
            "resume_link": applicant.resume_link,
            "lower_range": applicant.lower_range,
            "upper_range": applicant.upper_range
        }

        # Add to company-grouped structure
        if status in status_key_map:
            status_key = status_key_map[status]
            if company_name not in applicants_by_status[status_key]:
                applicants_by_status[status_key][company_name] = []
            applicants_by_status[status_key][company_name].append(applicant_data)

    # Calculate summary statistics
    total_applicants = sum(metrics.values())
    active_pipeline = (
        metrics.get("Tagged", 0) +
        metrics.get("Shortlisted", 0) +
        metrics.get("Assessment Stage", 0) +
        metrics.get("Interview Stage", 0)
    )
    
    summary = {
        "total_applicants": total_applicants,
        "active_pipeline": active_pipeline,
        "offered": metrics.get("Offered", 0),
        "joined": metrics.get("Joined", 0),
        "rejected": metrics.get("Rejected", 0),
        "conversion_rate": round((metrics.get("Joined", 0) / total_applicants * 100), 2) if total_applicants > 0 else 0
    }

    # Format output to match original API structure
    result = {
        "success": True,
        "companies": sorted(list(companies_set)),
        "jobs_by_company": jobs_by_company,
        "metrics": metrics,
        "summary": summary,
        "company_filter": company
    }

    # Add each status's applicants_by_company at root level
    for status_key in applicants_by_status:
        result[status_key] = {"applicants_by_company": applicants_by_status[status_key]}

    return result


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
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
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
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
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
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
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
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )

    return {"tagged_applicants": applicants}


@frappe.whitelist(allow_guest=False)
def get_shortlisted_applicants(email):
    if not email:
        frappe.throw(_("Email is required"))

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Shortlisted", "owner": email},
        fields=[
            "name", "applicant_name", "email_id", "phone_number", "country",
            "job_title", "designation", "notes", "resume_attachment",
            "resume_link", "lower_range", "upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )
    return {"shortlisted_applicants": applicants}


@frappe.whitelist(allow_guest=False)
def get_assessment_stage_applicants(email):
    if not email:
        frappe.throw(_("Email is required"))

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Assessment Stage", "owner": email},
        fields=[
            "name", "applicant_name", "email_id", "phone_number", "country",
            "job_title", "designation", "notes", "resume_attachment",
            "resume_link", "lower_range", "upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )
    return {"assessment_stage_applicants": applicants}


@frappe.whitelist(allow_guest=False)
def get_interview_stage_applicants(email):
    if not email:
        frappe.throw(_("Email is required"))

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Interview Stage", "owner": email},
        fields=[
            "name", "applicant_name", "email_id", "phone_number", "country",
            "job_title", "designation", "notes", "resume_attachment",
            "resume_link", "lower_range", "upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )
    return {"interview_stage_applicants": applicants}


@frappe.whitelist(allow_guest=False)
def get_offered_applicants(email):
    if not email:
        frappe.throw(_("Email is required"))

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Offered", "owner": email},
        fields=[
            "name", "applicant_name", "email_id", "phone_number", "country",
            "job_title", "designation", "notes", "resume_attachment",
            "resume_link", "lower_range", "upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )
    return {"offered_applicants": applicants}


@frappe.whitelist(allow_guest=False)
def get_rejected_applicants(email):
    if not email:
        frappe.throw(_("Email is required"))

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Rejected", "owner": email},
        fields=[
            "name", "applicant_name", "email_id", "phone_number", "country",
            "job_title", "designation", "notes", "resume_attachment",
            "resume_link", "lower_range", "upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )
    return {"rejected_applicants": applicants}


@frappe.whitelist(allow_guest=False)
def get_joined_applicants(email):
    if not email:
        frappe.throw(_("Email is required"))

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Joined", "owner": email},
        fields=[
            "name", "applicant_name", "email_id", "phone_number", "country",
            "job_title", "designation", "notes", "resume_attachment",
            "resume_link", "lower_range", "upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )
    return {"joined_applicants": applicants}


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
        fields=["name", "company"],
        limit=0  # CHANGED: Added limit=0 to remove default 20 record limit
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
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
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


@frappe.whitelist(allow_guest=False)
def get_shortlisted_applicants_by_company(email, company=None):
    if not email:
        frappe.throw(_("Email is required"))

    job_filters = {}
    if company:
        job_filters["company"] = company

    job_openings = frappe.get_all(
        "Job Opening", 
        filters=job_filters, 
        fields=["name", "company"],
        limit=0  # CHANGED: Added limit=0 to remove default 20 record limit
    )
    job_map = {job.name: job.company for job in job_openings}

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Shortlisted", "owner": email},
        fields=[
            "name","applicant_name","email_id","phone_number","country",
            "job_title","designation","notes","resume_attachment","resume_link",
            "lower_range","upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )

    result = {}
    for applicant in applicants:
        job_id = applicant.job_title
        company_name = job_map.get(job_id, "Unknown Company")
        if company and company_name != company:
            continue
        if company_name not in result:
            result[company_name] = []
        result[company_name].append(applicant)

    return {"applicants_by_company": result}


@frappe.whitelist(allow_guest=False)
def get_assessment_stage_applicants_by_company(email, company=None):
    if not email:
        frappe.throw(_("Email is required"))

    job_filters = {}
    if company:
        job_filters["company"] = company

    job_openings = frappe.get_all(
        "Job Opening", 
        filters=job_filters, 
        fields=["name", "company"],
        limit=0  # CHANGED: Added limit=0 to remove default 20 record limit
    )
    job_map = {job.name: job.company for job in job_openings}

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Assessment Stage", "owner": email},
        fields=[
            "name","applicant_name","email_id","phone_number","country",
            "job_title","designation","notes","resume_attachment","resume_link",
            "lower_range","upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )

    result = {}
    for applicant in applicants:
        job_id = applicant.job_title
        company_name = job_map.get(job_id, "Unknown Company")
        if company and company_name != company:
            continue
        if company_name not in result:
            result[company_name] = []
        result[company_name].append(applicant)

    return {"applicants_by_company": result}


@frappe.whitelist(allow_guest=False)
def get_interview_stage_applicants_by_company(email, company=None):
    if not email:
        frappe.throw(_("Email is required"))

    job_filters = {}
    if company:
        job_filters["company"] = company

    job_openings = frappe.get_all(
        "Job Opening", 
        filters=job_filters, 
        fields=["name", "company"],
        limit=0  # CHANGED: Added limit=0 to remove default 20 record limit
    )
    job_map = {job.name: job.company for job in job_openings}

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Interview Stage", "owner": email},
        fields=[
            "name","applicant_name","email_id","phone_number","country",
            "job_title","designation","notes","resume_attachment","resume_link",
            "lower_range","upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )

    result = {}
    for applicant in applicants:
        job_id = applicant.job_title
        company_name = job_map.get(job_id, "Unknown Company")
        if company and company_name != company:
            continue
        if company_name not in result:
            result[company_name] = []
        result[company_name].append(applicant)

    return {"applicants_by_company": result}


@frappe.whitelist(allow_guest=False)
def get_offered_applicants_by_company(email, company=None):
    if not email:
        frappe.throw(_("Email is required"))

    job_filters = {}
    if company:
        job_filters["company"] = company

    job_openings = frappe.get_all(
        "Job Opening", 
        filters=job_filters, 
        fields=["name", "company"],
        limit=0  # CHANGED: Added limit=0 to remove default 20 record limit
    )
    job_map = {job.name: job.company for job in job_openings}

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Offered", "owner": email},
        fields=[
            "name","applicant_name","email_id","phone_number","country",
            "job_title","designation","notes","resume_attachment","resume_link",
            "lower_range","upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )

    result = {}
    for applicant in applicants:
        job_id = applicant.job_title
        company_name = job_map.get(job_id, "Unknown Company")
        if company and company_name != company:
            continue
        if company_name not in result:
            result[company_name] = []
        result[company_name].append(applicant)

    return {"applicants_by_company": result}


@frappe.whitelist(allow_guest=False)
def get_rejected_applicants_by_company(email, company=None):
    if not email:
        frappe.throw(_("Email is required"))

    job_filters = {}
    if company:
        job_filters["company"] = company

    job_openings = frappe.get_all(
        "Job Opening", 
        filters=job_filters, 
        fields=["name", "company"],
        limit=0  # CHANGED: Added limit=0 to remove default 20 record limit
    )
    job_map = {job.name: job.company for job in job_openings}

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Rejected", "owner": email},
        fields=[
            "name","applicant_name","email_id","phone_number","country",
            "job_title","designation","notes","resume_attachment","resume_link",
            "lower_range","upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )

    result = {}
    for applicant in applicants:
        job_id = applicant.job_title
        company_name = job_map.get(job_id, "Unknown Company")
        if company and company_name != company:
            continue
        if company_name not in result:
            result[company_name] = []
        result[company_name].append(applicant)

    return {"applicants_by_company": result}


@frappe.whitelist(allow_guest=False)
def get_joined_applicants_by_company(email, company=None):
    if not email:
        frappe.throw(_("Email is required"))

    job_filters = {}
    if company:
        job_filters["company"] = company

    job_openings = frappe.get_all(
        "Job Opening", 
        filters=job_filters, 
        fields=["name", "company"],
        limit=0  # CHANGED: Added limit=0 to remove default 20 record limit
    )
    job_map = {job.name: job.company for job in job_openings}

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Joined", "owner": email},
        fields=[
            "name","applicant_name","email_id","phone_number","country",
            "job_title","designation","notes","resume_attachment","resume_link",
            "lower_range","upper_range"
        ],
        limit=0,  # CHANGED: Added limit=0 to remove default 20 record limit
        order_by="creation desc"
    )

    result = {}
    for applicant in applicants:
        job_id = applicant.job_title
        company_name = job_map.get(job_id, "Unknown Company")
        if company and company_name != company:
            continue
        if company_name not in result:
            result[company_name] = []
        result[company_name].append(applicant)

    return {"applicants_by_company": result}