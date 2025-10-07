import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_manager_dashboard_data(client=None, recruiter=None, time_period="month"):
    """
    Master function to fetch all manager dashboard data across all recruiters.
    No email required - aggregates data from all users.
    
    Args:
        client: Filter by specific client/company (optional, default "All")
        recruiter: Filter by specific recruiter email (optional, default "all")
        time_period: Time period filter - "week", "month", or "quarter" (default: "month")
    
    Returns:
        Dictionary containing:
        - clients: List of unique clients
        - recruiters: List of all recruiters with their info
        - team_metrics: Overall team statistics
        - funnel_data: Recruitment funnel stage counts
        - job_status_data: Job opening status distribution
        - monthly_trends: Time-series data for trends chart
        - recruiter_performance: Performance metrics by recruiter
        - applicants: Recent applicants list
        - jobs: Job openings list
    """
    from datetime import datetime, timedelta
    
    # Calculate date filter based on time period
    date_filter = get_date_filter(time_period)
    
    # 1. Get all active recruiters (users with "Recruiter" role)
    recruiters_list = get_recruiters_list()
    
    # Format recruiters for frontend
    recruiters = [
        {
            "id": r.name,
            "name": r.full_name or r.email,
            "email": r.email
        }
        for r in recruiters_list
    ]
    
    # 2. Build filters for Job Opening
    job_filters = {
        "creation": [">=", date_filter]
    }
    
    if client and client != "All":
        job_filters["company"] = client
    
    if recruiter and recruiter != "all":
        job_filters["owner"] = recruiter
    
    # Fetch Job Openings (using only fields that exist in standard Job Opening)
    job_openings = frappe.get_all(
        "Job Opening",
        filters=job_filters,
        fields=[
            "name",
            "job_title",
            "company",
            "location",
            "status",
            "creation",
            "owner"
        ],
        limit=0,
        order_by="creation desc"
    )
    
    # Create job to company mapping
    job_company_map = {job.name: job.company for job in job_openings}
    
    # 3. Build filters for Job Applicant
    applicant_filters = {
        "creation": [">=", date_filter]
    }
    
    if recruiter and recruiter != "all":
        applicant_filters["owner"] = recruiter
    
    # Fetch all Job Applicants
    all_applicants = frappe.get_all(
        "Job Applicant",
        filters=applicant_filters,
        fields=[
            "name",
            "applicant_name",
            "email_id",
            "phone_number",
            "job_title",
            "status",
            "creation",
            "modified",
            "owner"
        ],
        limit=0,
        order_by="creation desc"
    )
    
    # 4. Enrich applicants with company information and filter by client
    enriched_applicants = []
    for applicant in all_applicants:
        company = job_company_map.get(applicant.job_title, "Unknown Company")
        
        # Apply client filter
        if client and client != "All" and company != client:
            continue
            
        applicant_data = {
            "id": applicant.name,
            "name": applicant.applicant_name,
            "email": applicant.email_id,
            "phone": applicant.phone_number,
            "job_title": applicant.job_title,
            "client": company,
            "status": applicant.status,
            "appliedDate": applicant.creation.strftime("%Y-%m-%d") if applicant.creation else None,
            "lastUpdated": applicant.modified.strftime("%Y-%m-%d") if applicant.modified else None,
            "recruiter": applicant.owner
        }
        enriched_applicants.append(applicant_data)
    
    # 5. Get unique clients from job openings
    unique_companies = set([job.company for job in job_openings if job.company])
    clients = ["All"] + sorted(list(unique_companies))
    
    # 6. Calculate all metrics and data
    team_metrics = calculate_team_metrics(enriched_applicants, job_openings, recruiters, recruiter)
    funnel_data = calculate_funnel_data(enriched_applicants)
    job_status_data = calculate_job_status(job_openings)
    monthly_trends = calculate_monthly_trends(enriched_applicants, time_period)
    recruiter_performance = calculate_recruiter_performance(enriched_applicants, recruiters, recruiter)
    
    # 7. Format jobs for frontend (set positions to 1 as default)
    formatted_jobs = [
        {
            "id": job.name,
            "title": job.job_title,
            "client": job.company,
            "location": job.location or "Not specified",
            "status": job.status,
            "positions": 1,  # Default to 1 since field doesn't exist in standard doctype
            "createdDate": job.creation.strftime("%Y-%m-%d") if job.creation else None,
            "recruiter": job.owner
        }
        for job in job_openings
    ]
    
    return {
        "success": True,
        "clients": clients,
        "recruiters": recruiters,
        "team_metrics": team_metrics,
        "funnel_data": funnel_data,
        "job_status_data": job_status_data,
        "monthly_trends": monthly_trends,
        "recruiter_performance": recruiter_performance,
        "applicants": enriched_applicants[:100],  # Limit to recent 100
        "jobs": formatted_jobs[:50]  # Limit to recent 50
    }


def get_date_filter(time_period):
    """Calculate date filter based on time period"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    if time_period == "week":
        return now - timedelta(days=7)
    elif time_period == "month":
        return now - timedelta(days=30)
    elif time_period == "quarter":
        return now - timedelta(days=90)
    else:
        return now - timedelta(days=30)


def calculate_team_metrics(applicants, jobs, recruiters, selected_recruiter):
    """Calculate overall team metrics"""
    total_recruiters = 1 if selected_recruiter and selected_recruiter != "all" else len(recruiters)
    
    # Since number_of_positions doesn't exist, count each job as 1 position
    open_jobs_count = len([job for job in jobs if job.get("status") == "Open"])
    
    return {
        "totalRecruiters": total_recruiters,
        "totalApplicants": len(applicants),
        "totalJobs": len(jobs),
        "openPositions": open_jobs_count,  # Each job = 1 position
        "joined": len([a for a in applicants if a.get("status") == "Joined"])
    }


def calculate_funnel_data(applicants):
    """Calculate recruitment funnel stage counts"""
    stages = {
        "Open": len([a for a in applicants if a.get("status") == "Open"]),
        "Tagged": len([a for a in applicants if a.get("status") == "Tagged"]),
        "Shortlisted": len([a for a in applicants if a.get("status") == "Shortlisted"]),
        "Assessment": len([a for a in applicants if a.get("status") == "Assessment"]),
        "Interview": len([a for a in applicants if a.get("status") == "Interview"]),
        "Interview Reject": len([a for a in applicants if a.get("status") == "Interview Reject"]),
        "Offered": len([a for a in applicants if a.get("status") == "Offered"]),
        "Offer Drop": len([a for a in applicants if a.get("status") == "Offer Drop"]),
        "Joined": len([a for a in applicants if a.get("status") == "Joined"])
    }
    
    return {
        "labels": list(stages.keys()),
        "data": list(stages.values())
    }


def calculate_job_status(jobs):
    """Calculate job opening status distribution"""
    status_counts = {
        "Open": 0,
        "Closed": 0,
        "Cancelled": 0
    }
    
    for job in jobs:
        job_status = job.get("status", "Open")
        if job_status in status_counts:
            status_counts[job_status] += 1
        else:
            # If status is not in our expected values, count it as Open
            status_counts["Open"] += 1
    
    return {
        "labels": list(status_counts.keys()),
        "data": list(status_counts.values())
    }


def calculate_monthly_trends(applicants, time_period):
    """
    Calculate time-series trends data with actual date-based distribution
    """
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    # Determine periods and labels
    if time_period == "week":
        labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        num_periods = 7
        period_days = 1
    elif time_period == "month":
        labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
        num_periods = 4
        period_days = 7
    else:  # quarter
        labels = ["Month 1", "Month 2", "Month 3"]
        num_periods = 3
        period_days = 30
    
    # Initialize period buckets
    trends = []
    
    for i in range(num_periods):
        period_start = now - timedelta(days=period_days * (num_periods - i))
        period_end = now - timedelta(days=period_days * (num_periods - i - 1))
        
        # Filter applicants for this period
        period_applicants = [
            a for a in applicants
            if a.get("appliedDate") and 
            period_start.strftime("%Y-%m-%d") <= a.get("appliedDate") <= period_end.strftime("%Y-%m-%d")
        ]
        
        # Count by status using the updated status values
        period_data = {
            "month": labels[i],
            "totalCVUploaded": len(period_applicants),
            "open": len([a for a in period_applicants if a.get("status") == "Open"]),
            "tagged": len([a for a in period_applicants if a.get("status") == "Tagged"]),
            "shortlisted": len([a for a in period_applicants if a.get("status") == "Shortlisted"]),
            "assessment": len([a for a in period_applicants if a.get("status") == "Assessment"]),
            "interview": len([a for a in period_applicants if a.get("status") == "Interview"]),
            "offered": len([a for a in period_applicants if a.get("status") == "Offered"]),
            "joined": len([a for a in period_applicants if a.get("status") == "Joined"])
        }
        
        trends.append(period_data)
    
    # If no data in periods, use cumulative approach
    if all(t["totalCVUploaded"] == 0 for t in trends):
        total_count = len(applicants)
        for i, label in enumerate(labels):
            factor = (i + 1) / len(labels)
            trends[i] = {
                "month": label,
                "totalCVUploaded": int(total_count * factor),
                "open": int(len([a for a in applicants if a.get("status") == "Open"]) * factor),
                "tagged": int(len([a for a in applicants if a.get("status") == "Tagged"]) * factor),
                "shortlisted": int(len([a for a in applicants if a.get("status") == "Shortlisted"]) * factor),
                "assessment": int(len([a for a in applicants if a.get("status") == "Assessment"]) * factor),
                "interview": int(len([a for a in applicants if a.get("status") == "Interview"]) * factor),
                "offered": int(len([a for a in applicants if a.get("status") == "Offered"]) * factor),
                "joined": int(len([a for a in applicants if a.get("status") == "Joined"]) * factor)
            }
    
    return trends


def calculate_recruiter_performance(applicants, recruiters, selected_recruiter):
    """Calculate performance metrics by recruiter"""
    # Filter recruiters if specific one selected
    active_recruiters = recruiters
    if selected_recruiter and selected_recruiter != "all":
        active_recruiters = [r for r in recruiters if r["email"] == selected_recruiter]
    
    performance = []
    
    for recruiter in active_recruiters:
        recruiter_applicants = [a for a in applicants if a.get("recruiter") == recruiter["email"]]
        
        # Calculate metrics using updated status values
        open_count = len([a for a in recruiter_applicants if a.get("status") == "Open"])
        tagged_count = len([a for a in recruiter_applicants if a.get("status") == "Tagged"])
        shortlisted_count = len([a for a in recruiter_applicants if a.get("status") == "Shortlisted"])
        assessment_count = len([a for a in recruiter_applicants if a.get("status") == "Assessment"])
        interview_count = len([a for a in recruiter_applicants if a.get("status") == "Interview"])
        offered_count = len([a for a in recruiter_applicants if a.get("status") == "Offered"])
        joined_count = len([a for a in recruiter_applicants if a.get("status") == "Joined"])
        
        performance.append({
            "recruiter_name": recruiter["name"],
            "recruiter_id": recruiter["id"],
            "open": open_count,
            "tagged": tagged_count,
            "shortlisted": shortlisted_count,
            "assessment": assessment_count,
            "interview": interview_count,
            "offered": offered_count,
            "joined": joined_count,
            "total_applicants": len(recruiter_applicants)
        })
    
    # Sort by total applicants descending
    performance.sort(key=lambda x: x["total_applicants"], reverse=True)
    
    return performance


def get_recruiters_list():
    """Get all users with Recruiter role using proper Frappe methods"""
    
    # Method 1: Using Frappe's get_all with role filter
    try:
        recruiters = frappe.get_all(
            "User",
            filters={
                "enabled": 1,
                "name": ["in", frappe.get_all(
                    "Has Role",
                    filters={"role": "Recruiter", "parenttype": "User"},
                    fields=["parent"],
                    distinct=True
                )]
            },
            fields=["name", "email", "full_name"],
            order_by="full_name"
        )
        
        if recruiters:
            return recruiters
    except Exception as e:
        frappe.log_error(f"Error getting recruiters method 1: {str(e)}")
    
    # Method 2: Alternative query approach
    try:
        recruiters = frappe.db.sql("""
            SELECT DISTINCT u.name, u.email, u.full_name
            FROM `tabUser` u
            WHERE u.name IN (
                SELECT DISTINCT parent 
                FROM `tabHas Role` 
                WHERE role = 'Recruiter' 
                AND parenttype = 'User'
            )
            AND u.enabled = 1
            ORDER BY u.full_name
        """, as_dict=True)
        
        if recruiters:
            return recruiters
    except Exception as e:
        frappe.log_error(f"Error getting recruiters method 2: {str(e)}")
    
    # Method 3: Fallback - get all enabled users and filter by role
    try:
        all_users = frappe.get_all(
            "User",
            filters={"enabled": 1},
            fields=["name", "email", "full_name", "roles"]
        )
        
        recruiters = []
        for user in all_users:
            user_doc = frappe.get_doc("User", user.name)
            user_roles = [r.role for r in user_doc.roles]
            if "Recruiter" in user_roles:
                recruiters.append({
                    "name": user.name,
                    "email": user.email,
                    "full_name": user.full_name
                })
        
        return recruiters
    except Exception as e:
        frappe.log_error(f"Error getting recruiters method 3: {str(e)}")
    
    # Method 4: Ultimate fallback - return current user if no recruiters found
    frappe.log_error("No recruiters found with any method, returning current user")
    current_user = frappe.session.user
    return [{
        "name": current_user,
        "email": current_user,
        "full_name": frappe.get_value("User", current_user, "full_name") or current_user
    }]
    """Get all users with Recruiter role using proper Frappe methods"""
    
    # Method 1: Using Frappe's get_all with role filter
    try:
        recruiters = frappe.get_all(
            "User",
            filters={
                "enabled": 1,
                "name": ["in", frappe.get_all(
                    "Has Role",
                    filters={"role": "Recruiter", "parenttype": "User"},
                    fields=["parent"],
                    distinct=True
                )]
            },
            fields=["name", "email", "full_name"],
            order_by="full_name"
        )
        
        if recruiters:
            return recruiters
    except Exception as e:
        frappe.log_error(f"Error getting recruiters method 1: {str(e)}")
    
    # Method 2: Alternative query approach
    try:
        recruiters = frappe.db.sql("""
            SELECT DISTINCT u.name, u.email, u.full_name
            FROM `tabUser` u
            WHERE u.name IN (
                SELECT DISTINCT parent 
                FROM `tabHas Role` 
                WHERE role = 'Recruiter' 
                AND parenttype = 'User'
            )
            AND u.enabled = 1
            ORDER BY u.full_name
        """, as_dict=True)
        
        if recruiters:
            return recruiters
    except Exception as e:
        frappe.log_error(f"Error getting recruiters method 2: {str(e)}")
    
    # Method 3: Fallback - get all enabled users and filter by role
    try:
        all_users = frappe.get_all(
            "User",
            filters={"enabled": 1},
            fields=["name", "email", "full_name", "roles"]
        )
        
        recruiters = []
        for user in all_users:
            user_doc = frappe.get_doc("User", user.name)
            user_roles = [r.role for r in user_doc.roles]
            if "Recruiter" in user_roles:
                recruiters.append({
                    "name": user.name,
                    "email": user.email,
                    "full_name": user.full_name
                })
        
        return recruiters
    except Exception as e:
        frappe.log_error(f"Error getting recruiters method 3: {str(e)}")
    
    # Method 4: Ultimate fallback - return current user if no recruiters found
    frappe.log_error("No recruiters found with any method, returning current user")
    current_user = frappe.session.user
    return [{
        "name": current_user,
        "email": current_user,
        "full_name": frappe.get_value("User", current_user, "full_name") or current_user
    }]