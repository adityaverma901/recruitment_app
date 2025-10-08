import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_manager_dashboard_data(client=None, recruiter=None, time_period="month"):
    """
    Master function to fetch all manager dashboard data across all recruiters.
    """
    from datetime import datetime, timedelta
    
    # Calculate date filter based on time period
    date_filter = get_date_filter(time_period)
    
    # 1. Get all active recruiters
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
    
    # 2. First, get ALL job openings to build proper mapping
    all_job_filters = {"creation": [">=", date_filter]}
    all_job_openings = frappe.get_all(
        "Job Opening",
        filters=all_job_filters,
        fields=["name", "job_title", "company", "status", "creation", "owner"],
        limit=0
    )
    
    # Create comprehensive job to company mapping from ALL job openings
    job_company_map = {job.name: job.company for job in all_job_openings}
    job_details_map = {
        job.name: {
            "company": job.company,
            "job_title": job.job_title,
            "status": job.status,
            "owner": job.owner
        }
        for job in all_job_openings
    }
    
    # 3. Build filters for displayed Job Openings (with client/recruiter filters)
    job_filters = {"creation": [">=", date_filter]}
    
    if client and client != "All":
        job_filters["company"] = client
    
    if recruiter and recruiter != "all":
        job_filters["owner"] = recruiter
    
    # Fetch filtered Job Openings for display
    job_openings = frappe.get_all(
        "Job Opening",
        filters=job_filters,
        fields=["name", "job_title", "company", "location", "status", "creation", "owner"],
        limit=0,
        order_by="creation desc"
    )
    
    # 4. Build filters for Job Applicants
    applicant_filters = {"creation": [">=", date_filter]}
    
    if recruiter and recruiter != "all":
        applicant_filters["owner"] = recruiter
    
    # If client filter is applied, we need a different approach
    if client and client != "All":
        # Get ALL job openings for this client (not just filtered by date/recruiter)
        client_jobs = frappe.get_all(
            "Job Opening",
            filters={"company": client},
            fields=["name"],
            limit=0
        )
        client_job_titles = [job.name for job in client_jobs]
        
        if client_job_titles:
            # Add client filter to applicant query
            if "job_title" in applicant_filters:
                # If job_title filter already exists, combine them
                existing_titles = applicant_filters["job_title"][1] if isinstance(applicant_filters["job_title"], list) else [applicant_filters["job_title"]]
                combined_titles = list(set(existing_titles) & set(client_job_titles))
                if combined_titles:
                    applicant_filters["job_title"] = ["in", combined_titles]
                else:
                    applicant_filters["job_title"] = "___nonexistent___"
            else:
                applicant_filters["job_title"] = ["in", client_job_titles]
        else:
            applicant_filters["job_title"] = "___nonexistent___"
    
    # 5. Fetch Job Applicants with proper filters
    all_applicants = frappe.get_all(
        "Job Applicant",
        filters=applicant_filters,
        fields=[
            "name", "applicant_name", "email_id", "phone_number", 
            "job_title", "status", "creation", "modified", "owner"
        ],
        limit=0,
        order_by="creation desc"
    )
    
    # 6. Enrich applicants with company information
    enriched_applicants = []
    for applicant in all_applicants:
        # Get company from our comprehensive mapping
        company = job_company_map.get(applicant.job_title, "Unknown Company")
        
        # Only apply client filter at this stage if we didn't do it at DB level
        # This ensures we catch any edge cases
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
    
    # 7. Debug logging to see what's happening
    frappe.logger().info(f"Dashboard Debug - Client: {client}, Recruiter: {recruiter}")
    frappe.logger().info(f"Total applicants found: {len(enriched_applicants)}")
    for app in enriched_applicants[:5]:  # Log first 5 applicants
        frappe.logger().info(f"Applicant: {app['name']}, Job: {app['job_title']}, Client: {app['client']}, Status: {app['status']}")
    
    # 8. Get unique clients from ALL job openings (not just filtered ones)
    unique_companies = set([job.company for job in all_job_openings if job.company])
    clients = ["All"] + sorted(list(unique_companies))
    
    # 9. Calculate all metrics and data
    team_metrics = calculate_team_metrics(enriched_applicants, job_openings, recruiters, recruiter)
    funnel_data = calculate_funnel_data(enriched_applicants)
    job_status_data = calculate_job_status(job_openings)
    monthly_trends = calculate_monthly_trends(enriched_applicants, time_period)
    recruiter_performance = calculate_recruiter_performance(enriched_applicants, recruiters, recruiter)
    
    # 10. Format jobs for frontend
    formatted_jobs = [
        {
            "id": job.name,
            "title": job.job_title,
            "client": job.company,
            "location": job.location or "Not specified",
            "status": job.status,
            "positions": 1,
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
        "applicants": enriched_applicants[:100],
        "jobs": formatted_jobs[:50]
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
        "Total CV's Uploaded": len(applicants),
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


def get_current_quarter_info():
    """
    Get current quarter information
    Returns: (quarter_number, quarter_start_date, quarter_end_date, quarter_months)
    """
    from datetime import datetime
    import calendar
    
    now = datetime.now()
    current_month = now.month
    
    # Determine quarter (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
    quarter = (current_month - 1) // 3 + 1
    
    # Calculate quarter start month
    quarter_start_month = (quarter - 1) * 3 + 1
    
    # Create quarter start date (first day of first month)
    quarter_start = datetime(now.year, quarter_start_month, 1, 0, 0, 0, 0)
    
    # Calculate quarter end month
    quarter_end_month = quarter_start_month + 2
    
    # Get last day of quarter end month
    last_day = calendar.monthrange(now.year, quarter_end_month)[1]
    quarter_end = datetime(now.year, quarter_end_month, last_day, 23, 59, 59, 999999)
    
    # Get quarter month names
    quarter_months = []
    for i in range(3):
        month_num = quarter_start_month + i
        month_name = datetime(now.year, month_num, 1).strftime("%B")
        quarter_months.append(month_name)
    
    return quarter, quarter_start, quarter_end, quarter_months


def calculate_monthly_trends(applicants, time_period):
    """
    Calculate time-series trends for CURRENT QUARTER ONLY with 3 different views:
    
    - Weekly: Show ALL weeks from start of current quarter till today (week-by-week data)
    - Monthly: Show all 3 months of current quarter (Oct, Nov, Dec for Q4)
    - Quarterly: Show single data point for entire current quarter
    
    Example: If today is Oct 8, 2025 (Q4):
    - Quarter runs from Oct 1 to Dec 31
    - Weekly: Shows Week 1 (Oct 1-7), Week 2 (Oct 8-14 partial), ...
    - Monthly: Shows October (partial), November (0), December (0)
    - Quarterly: Shows Q4 (only Oct 1-8 data so far)
    """
    from datetime import datetime, timedelta
    import calendar
    
    now = datetime.now()
    quarter, quarter_start, quarter_end, quarter_months = get_current_quarter_info()
    
    trends = []
    
    frappe.logger().info(f"=== Calculating Trends for Current Quarter Q{quarter} ===")
    frappe.logger().info(f"Quarter Start: {quarter_start.strftime('%Y-%m-%d')}")
    frappe.logger().info(f"Quarter End: {quarter_end.strftime('%Y-%m-%d')}")
    frappe.logger().info(f"Today: {now.strftime('%Y-%m-%d')}")
    
    # Filter applicants to ONLY current quarter
    quarter_applicants = [
        a for a in applicants
        if a.get("appliedDate") and 
        quarter_start.strftime("%Y-%m-%d") <= a.get("appliedDate") <= now.strftime("%Y-%m-%d")
    ]
    
    frappe.logger().info(f"Applicants in current quarter (till today): {len(quarter_applicants)}")
    
    if time_period == "week":
        # Weekly view - show ALL weeks from quarter start till today
        # Display format: "Oct 1-7", "Oct 8-14", "Oct 15-21", etc.
        days_elapsed = (now - quarter_start).days
        num_weeks = (days_elapsed // 7) + 1  # +1 for current partial week
        
        frappe.logger().info(f"Days elapsed in quarter: {days_elapsed}, Weeks to show: {num_weeks}")
        
        for i in range(num_weeks):
            week_start = quarter_start + timedelta(days=7*i)
            week_end = week_start + timedelta(days=6)
            
            # Don't go beyond today
            if week_end > now:
                week_end = now
            
            # Week label with date range
            # Format: "Oct 1-7" or "Oct 8-14" or "Nov 1-7"
            if week_start.month == week_end.month:
                # Same month: "Oct 1-7"
                week_label = f"{week_start.strftime('%b')} {week_start.day}-{week_end.day}"
            else:
                # Different months: "Oct 29-Nov 4"
                week_label = f"{week_start.strftime('%b')} {week_start.day}-{week_end.strftime('%b')} {week_end.day}"
            
            # Filter applicants for this week
            period_applicants = [
                a for a in quarter_applicants
                if a.get("appliedDate") and 
                week_start.strftime("%Y-%m-%d") <= a.get("appliedDate") <= week_end.strftime("%Y-%m-%d")
            ]
            
            frappe.logger().info(f"{week_label}: {len(period_applicants)} applicants")
            
            trends.append({
                "month": week_label,
                "totalCVUploaded": len(period_applicants),
                "open": len([a for a in period_applicants if a.get("status") == "Open"]),
                "tagged": len([a for a in period_applicants if a.get("status") == "Tagged"]),
                "shortlisted": len([a for a in period_applicants if a.get("status") == "Shortlisted"]),
                "assessment": len([a for a in period_applicants if a.get("status") == "Assessment"]),
                "interview": len([a for a in period_applicants if a.get("status") == "Interview"]),
                "offered": len([a for a in period_applicants if a.get("status") == "Offered"]),
                "joined": len([a for a in period_applicants if a.get("status") == "Joined"])
            })
    
    elif time_period == "month":
        # Monthly view - show all 3 months of current quarter
        quarter_start_month = quarter_start.month
        
        for i in range(3):
            month_num = quarter_start_month + i
            month_year = now.year
            
            # Handle year boundary
            if month_num > 12:
                month_num -= 12
                month_year += 1
            
            month_date = datetime(month_year, month_num, 1)
            month_name = month_date.strftime("%B")
            
            # Get start and end of month
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_day = calendar.monthrange(month_year, month_num)[1]
            month_end = month_date.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
            
            # If it's current month, only go till today
            if month_year == now.year and month_num == now.month:
                month_end = now
            
            # Filter applicants for this month
            period_applicants = [
                a for a in quarter_applicants
                if a.get("appliedDate") and 
                month_start.strftime("%Y-%m-%d") <= a.get("appliedDate") <= month_end.strftime("%Y-%m-%d")
            ]
            
            frappe.logger().info(f"{month_name}: {len(period_applicants)} applicants")
            
            trends.append({
                "month": month_name,
                "totalCVUploaded": len(period_applicants),
                "open": len([a for a in period_applicants if a.get("status") == "Open"]),
                "tagged": len([a for a in period_applicants if a.get("status") == "Tagged"]),
                "shortlisted": len([a for a in period_applicants if a.get("status") == "Shortlisted"]),
                "assessment": len([a for a in period_applicants if a.get("status") == "Assessment"]),
                "interview": len([a for a in period_applicants if a.get("status") == "Interview"]),
                "offered": len([a for a in period_applicants if a.get("status") == "Offered"]),
                "joined": len([a for a in period_applicants if a.get("status") == "Joined"])
            })
    
    else:  # quarterly
        # Quarterly view - single data point for entire current quarter (till today)
        quarter_label = f"Q{quarter}"
        
        frappe.logger().info(f"{quarter_label}: {len(quarter_applicants)} applicants")
        
        trends.append({
            "month": quarter_label,
            "totalCVUploaded": len(quarter_applicants),
            "open": len([a for a in quarter_applicants if a.get("status") == "Open"]),
            "tagged": len([a for a in quarter_applicants if a.get("status") == "Tagged"]),
            "shortlisted": len([a for a in quarter_applicants if a.get("status") == "Shortlisted"]),
            "assessment": len([a for a in quarter_applicants if a.get("status") == "Assessment"]),
            "interview": len([a for a in quarter_applicants if a.get("status") == "Interview"]),
            "offered": len([a for a in quarter_applicants if a.get("status") == "Offered"]),
            "joined": len([a for a in quarter_applicants if a.get("status") == "Joined"])
        })
    
    return trends


def calculate_monthly_trends_with_debug(applicants, time_period):
    """
    Enhanced version with debug logging to verify data accuracy
    """
    from datetime import datetime, timedelta
    import calendar
    
    now = datetime.now()
    trends = []
    
    frappe.logger().info(f"=== Calculating Trends for {time_period} ===")
    frappe.logger().info(f"Current date: {now.strftime('%Y-%m-%d')}")
    frappe.logger().info(f"Total applicants to process: {len(applicants)}")
    
    if time_period == "week":
        for i in range(7):
            day_date = now - timedelta(days=6-i)
            day_name = day_date.strftime("%a %d")
            day_start = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            period_applicants = [
                a for a in applicants
                if a.get("appliedDate") and 
                day_start.strftime("%Y-%m-%d") <= a.get("appliedDate") <= day_end.strftime("%Y-%m-%d")
            ]
            
            frappe.logger().info(f"{day_name}: {len(period_applicants)} applicants")
            
            trends.append({
                "month": day_name,
                "totalCVUploaded": len(period_applicants),
                "open": len([a for a in period_applicants if a.get("status") == "Open"]),
                "tagged": len([a for a in period_applicants if a.get("status") == "Tagged"]),
                "shortlisted": len([a for a in period_applicants if a.get("status") == "Shortlisted"]),
                "assessment": len([a for a in period_applicants if a.get("status") == "Assessment"]),
                "interview": len([a for a in period_applicants if a.get("status") == "Interview"]),
                "offered": len([a for a in period_applicants if a.get("status") == "Offered"]),
                "joined": len([a for a in period_applicants if a.get("status") == "Joined"])
            })
    
    elif time_period == "month":
        for i in range(4):
            week_number = 4 - i
            week_end = now - timedelta(days=7*i)
            week_start = week_end - timedelta(days=6)
            week_label = f"Week {week_number}"
            
            period_applicants = [
                a for a in applicants
                if a.get("appliedDate") and 
                week_start.strftime("%Y-%m-%d") <= a.get("appliedDate") <= week_end.strftime("%Y-%m-%d")
            ]
            
            frappe.logger().info(f"{week_label} ({week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}): {len(period_applicants)} applicants")
            
            trends.insert(0, {
                "month": week_label,
                "totalCVUploaded": len(period_applicants),
                "open": len([a for a in period_applicants if a.get("status") == "Open"]),
                "tagged": len([a for a in period_applicants if a.get("status") == "Tagged"]),
                "shortlisted": len([a for a in period_applicants if a.get("status") == "Shortlisted"]),
                "assessment": len([a for a in period_applicants if a.get("status") == "Assessment"]),
                "interview": len([a for a in period_applicants if a.get("status") == "Interview"]),
                "offered": len([a for a in period_applicants if a.get("status") == "Offered"]),
                "joined": len([a for a in period_applicants if a.get("status") == "Joined"])
            })
    
    else:  # quarter
        for i in range(3):
            month_offset = i
            target_month = now.month + month_offset
            target_year = now.year
            
            while target_month > 12:
                target_month -= 12
                target_year += 1
            
            month_date = datetime(target_year, target_month, 1)
            month_name = month_date.strftime("%B")
            
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_day = calendar.monthrange(month_date.year, month_date.month)[1]
            month_end = month_date.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
            
            if target_year == now.year and target_month == now.month:
                month_end = now
            # For future months, month_end stays at end of month (will result in 0 applicants)
            
            period_applicants = [
                a for a in applicants
                if a.get("appliedDate") and 
                month_start.strftime("%Y-%m-%d") <= a.get("appliedDate") <= month_end.strftime("%Y-%m-%d")
            ]
            
            frappe.logger().info(f"{month_name} {target_year} ({month_start.strftime('%Y-%m-%d')} to {month_end.strftime('%Y-%m-%d')}): {len(period_applicants)} applicants")
            
            trends.append({
                "month": month_name,
                "totalCVUploaded": len(period_applicants),
                "open": len([a for a in period_applicants if a.get("status") == "Open"]),
                "tagged": len([a for a in period_applicants if a.get("status") == "Tagged"]),
                "shortlisted": len([a for a in period_applicants if a.get("status") == "Shortlisted"]),
                "assessment": len([a for a in period_applicants if a.get("status") == "Assessment"]),
                "interview": len([a for a in period_applicants if a.get("status") == "Interview"]),
                "offered": len([a for a in period_applicants if a.get("status") == "Offered"]),
                "joined": len([a for a in period_applicants if a.get("status") == "Joined"])
            })
    
    frappe.logger().info(f"=== Trend calculation complete ===")
    
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
        has_role_parents = frappe.get_all(
            "Has Role",
            filters={"role": "Recruiter", "parenttype": "User"},
            fields=["parent"],
            distinct=True
        )
        
        if has_role_parents:
            parent_list = [hr["parent"] for hr in has_role_parents]
            recruiters = frappe.get_all(
                "User",
                filters={
                    "enabled": 1,
                    "name": ["in", parent_list]
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
            fields=["name", "email", "full_name"]
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
        
        if recruiters:
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


