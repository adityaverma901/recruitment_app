import frappe
from frappe import _
from datetime import datetime, timedelta
import calendar

@frappe.whitelist(allow_guest=False)
def get_recruiter_dashboard_both(email=None, company=None, time_period="month"):
    """
    Fetch all recruiter dashboard data in a single API call
    Enhanced with trends data similar to manager dashboard
    """
    if not email:
        email = frappe.session.user
    
    # Fetch all required data with optimized queries
    data = {
        'jobs_opening_by_company': get_job_openings_with_status(email, company),
        'tagged_applicants_by_company': get_tagged_applicants_by_company(email, company),
        'shortlisted_applicants_by_company': get_shortlisted_applicants_by_company(email, company),
        'assessment_stage_applicants_by_company': get_assessment_stage_applicants_by_company(email, company),
        'interview_stage_applicants_by_company': get_interview_stage_applicants_by_company(email, company),
        'interview_reject_applicants_by_company': get_interview_reject_applicants_by_company(email, company),
        'offered_applicants_by_company': get_offered_applicants_by_company(email, company),
        'offer_drop_applicants_by_company': get_offer_drop_applicants_by_company(email, company),
        'joined_applicants_by_company': get_joined_applicants_by_company(email, company),
        # NEW: Add trends data
        'trends_data': get_recruiter_trends_data(email, company, time_period)
    }
    
    return data


@frappe.whitelist(allow_guest=False)
def get_recruiter_trends_data(email=None, company=None, time_period="month"):
    """
    Calculate trends data for recruiter dashboard showing applicant progress over time
    Shows data for CURRENT QUARTER ONLY with 3 different views
    
    Args:
        email: Recruiter email (defaults to current user)
        company: Optional company filter
        time_period: "week" | "month" | "quarter"
    
    Returns:
        Dictionary with trends data for current quarter
    """
    if not email:
        email = frappe.session.user
    
    # Get date filter for current quarter
    quarter, quarter_start, quarter_end, quarter_months = get_current_quarter_info()
    now = datetime.now()
    
    # Build filters for applicants - only till today (not future dates)
    applicant_filters = {
        "owner": email,
        "creation": ["between", [quarter_start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")]]
    }
    
    # Apply company filter if provided
    if company:
        # Get all job openings for this company
        job_openings = frappe.get_all(
            "Job Opening",
            filters={"company": company},
            fields=["name"],
            limit=0
        )
        company_job_titles = [job.name for job in job_openings]
        
        if company_job_titles:
            applicant_filters["job_title"] = ["in", company_job_titles]
        else:
            # No jobs for this company, return empty trends
            return {
                "trends": [],
                "metrics": create_empty_metrics(),
                "quarter_info": {
                    "quarter": quarter,
                    "start_date": quarter_start.strftime("%Y-%m-%d"),
                    "end_date": quarter_end.strftime("%Y-%m-%d"),
                    "months": quarter_months,
                    "current_date": now.strftime("%Y-%m-%d")
                }
            }
    
    # Fetch all applicants for current quarter till today
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
    
    # Convert to format similar to manager dashboard
    formatted_applicants = []
    for applicant in all_applicants:
        formatted_applicants.append({
            "id": applicant.name,
            "name": applicant.applicant_name,
            "email": applicant.email_id,
            "phone": applicant.phone_number,
            "job_title": applicant.job_title,
            "status": applicant.status,
            "appliedDate": applicant.creation.strftime("%Y-%m-%d") if applicant.creation else None,
            "lastUpdated": applicant.modified.strftime("%Y-%m-%d") if applicant.modified else None,
            "recruiter": applicant.owner
        })
    
    # Calculate trends based on time period
    trends = calculate_recruiter_trends(formatted_applicants, time_period, quarter_start, quarter_end, now)
    
    # Calculate summary metrics
    metrics = calculate_recruiter_metrics(formatted_applicants)
    
    return {
        "trends": trends,
        "metrics": metrics,
        "quarter_info": {
            "quarter": quarter,
            "start_date": quarter_start.strftime("%Y-%m-%d"),
            "end_date": quarter_end.strftime("%Y-%m-%d"),
            "months": quarter_months,
            "current_date": now.strftime("%Y-%m-%d")
        }
    }


def get_current_quarter_info():
    """
    Get current quarter information
    Returns: (quarter_number, quarter_start_date, quarter_end_date, quarter_months)
    """
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


def calculate_recruiter_trends(applicants, time_period, quarter_start, quarter_end, now):
    """
    Calculate time-series trends for recruiter dashboard
    Shows data for CURRENT QUARTER ONLY with 3 different views
    All data is calculated ONLY till current date (not future dates)
    """
    trends = []
    
    frappe.logger().info(f"=== Calculating Recruiter Trends for {time_period} ===")
    frappe.logger().info(f"Quarter Start: {quarter_start.strftime('%Y-%m-%d')}")
    frappe.logger().info(f"Today: {now.strftime('%Y-%m-%d')}")
    frappe.logger().info(f"Total applicants in quarter till today: {len(applicants)}")
    
    if time_period == "week":
        # Weekly view - show ALL weeks from quarter start till today
        trends = calculate_weekly_trends(applicants, quarter_start, now)
    
    elif time_period == "month":
        # Monthly view - show all 3 months of current quarter (till today for current month)
        trends = calculate_monthly_trends(applicants, quarter_start, now)
    
    else:  # quarterly
        # Quarterly view - single data point for entire current quarter (till today)
        trends = calculate_quarterly_trends(applicants, quarter_start, now)
    
    frappe.logger().info(f"Generated {len(trends)} trend data points")
    
    return trends


def calculate_weekly_trends(applicants, quarter_start, now):
    """Calculate weekly trends from quarter start till today"""
    trends = []
    
    # Calculate total weeks from quarter start till today
    days_elapsed = (now - quarter_start).days
    num_weeks = (days_elapsed // 7) + 1  # +1 for current partial week
    
    for week_num in range(num_weeks):
        week_start = quarter_start + timedelta(days=7 * week_num)
        week_end = week_start + timedelta(days=6)
        
        # For the current week, end date should be today
        if week_end > now:
            week_end = now
        
        # Week label with date range
        if week_start.month == week_end.month:
            week_label = f"{week_start.strftime('%b')} {week_start.day}-{week_end.day}"
        else:
            week_label = f"{week_start.strftime('%b')} {week_start.day}-{week_end.strftime('%b')} {week_end.day}"
        
        # Filter applicants for this week
        period_applicants = get_applicants_for_period(applicants, week_start, week_end)
        
        trends.append(create_trend_data_point(week_label, period_applicants))
    
    return trends


def calculate_monthly_trends(applicants, quarter_start, now):
    """Calculate monthly trends for current quarter months till today"""
    trends = []
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
        
        # Only include months that have started (not future months)
        if month_start <= now:
            # Filter applicants for this month
            period_applicants = get_applicants_for_period(applicants, month_start, month_end)
            
            trends.append(create_trend_data_point(month_name, period_applicants))
    
    return trends


def calculate_quarterly_trends(applicants, quarter_start, now):
    """Calculate quarterly trends - single data point for current quarter till today"""
    trends = []
    
    quarter_num = (quarter_start.month - 1) // 3 + 1
    quarter_label = f"Q{quarter_num}"
    
    # All applicants are already filtered to current quarter till today
    trends.append(create_trend_data_point(quarter_label, applicants))
    
    return trends


def get_applicants_for_period(applicants, period_start, period_end):
    """Filter applicants for a specific time period"""
    period_applicants = []
    
    for applicant in applicants:
        applied_date = applicant.get("appliedDate")
        if applied_date:
            try:
                # Convert string date to datetime for comparison
                if isinstance(applied_date, str):
                    applied_date_dt = datetime.strptime(applied_date, "%Y-%m-%d")
                else:
                    applied_date_dt = applied_date
                
                # Check if applied date falls within the period
                if period_start.date() <= applied_date_dt.date() <= period_end.date():
                    period_applicants.append(applicant)
            except Exception as e:
                frappe.logger().error(f"Error parsing date {applied_date}: {str(e)}")
                continue
    
    return period_applicants


def create_trend_data_point(label, period_applicants):
    """
    Create a single trend data point with all status counts
    """
    return {
        "period": label,
        "totalCVUploaded": len(period_applicants),
        "open": len([a for a in period_applicants if a.get("status") == "Open"]),
        "tagged": len([a for a in period_applicants if a.get("status") == "Tagged"]),
        "shortlisted": len([a for a in period_applicants if a.get("status") == "Shortlisted"]),
        "assessment": len([a for a in period_applicants if a.get("status") == "Assessment"]),
        "interview": len([a for a in period_applicants if a.get("status") == "Interview"]),
        "interviewReject": len([a for a in period_applicants if a.get("status") == "Interview Reject"]),
        "offered": len([a for a in period_applicants if a.get("status") == "Offered"]),
        "offerDrop": len([a for a in period_applicants if a.get("status") == "Offer Drop"]),
        "joined": len([a for a in period_applicants if a.get("status") == "Joined"])
    }


def calculate_recruiter_metrics(applicants):
    """
    Calculate summary metrics for recruiter dashboard
    """
    return {
        "totalApplicants": len(applicants),
        "open": len([a for a in applicants if a.get("status") == "Open"]),
        "tagged": len([a for a in applicants if a.get("status") == "Tagged"]),
        "shortlisted": len([a for a in applicants if a.get("status") == "Shortlisted"]),
        "assessment": len([a for a in applicants if a.get("status") == "Assessment"]),
        "interview": len([a for a in applicants if a.get("status") == "Interview"]),
        "interviewReject": len([a for a in applicants if a.get("status") == "Interview Reject"]),
        "offered": len([a for a in applicants if a.get("status") == "Offered"]),
        "offerDrop": len([a for a in applicants if a.get("status") == "Offer Drop"]),
        "joined": len([a for a in applicants if a.get("status") == "Joined"])
    }


def create_empty_metrics():
    """Create empty metrics when no data is available"""
    return {
        "totalApplicants": 0,
        "open": 0,
        "tagged": 0,
        "shortlisted": 0,
        "assessment": 0,
        "interview": 0,
        "interviewReject": 0,
        "offered": 0,
        "offerDrop": 0,
        "joined": 0
    }


# ============================================================================
# EXISTING FUNCTIONS - UNCHANGED
# ============================================================================

@frappe.whitelist(allow_guest=False)
def get_job_openings_with_status(email, company=None):
    """
    Fetch count of open todos for the given user.
    
    Args:
        email: Created by email (required)
        company: Filter by reference_type (optional)
    
    Returns:
        dict: Open todo count
    """
    if not email:
        frappe.throw(_("Email is required"))
    
    # Build filters - only get Open status todos
    filters = {
        "owner": email,
        "status": "Open"
    }
    
    # If company is provided, use it as reference_type filter
    if company:
        filters["reference_type"] = company
    
    # Get count of open todos
    open_todo_count = frappe.db.count("ToDo", filters=filters)
    
    return {
        "open_todo_count": open_todo_count
    }

@frappe.whitelist(allow_guest=False)
def get_tagged_applicants_by_company(email, company=None):
    """
    Fetch all job applicants where status = 'Tagged' and owner = given email,
    optionally filtered by company.
    """
    if not email:
        frappe.throw(_("Email is required"))

    job_filters = {}
    if company:
        job_filters["company"] = company

    job_openings = frappe.get_all(
        "Job Opening",
        filters=job_filters,
        fields=["name", "company"],
        limit=0
    )

    job_map = {job.name: job.company for job in job_openings}

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
            "job_title",
            "designation",
            "notes",
            "resume_attachment",
            "resume_link",
            "lower_range",
            "upper_range"
        ],
        limit=0,
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
        limit=0
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
        limit=0,
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
        limit=0
    )
    job_map = {job.name: job.company for job in job_openings}

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Assessment", "owner": email},
        fields=[
            "name","applicant_name","email_id","phone_number","country",
            "job_title","designation","notes","resume_attachment","resume_link",
            "lower_range","upper_range"
        ],
        limit=0,
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
        limit=0
    )
    job_map = {job.name: job.company for job in job_openings}

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Interview", "owner": email},
        fields=[
            "name","applicant_name","email_id","phone_number","country",
            "job_title","designation","notes","resume_attachment","resume_link",
            "lower_range","upper_range"
        ],
        limit=0,
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
def get_interview_reject_applicants_by_company(email, company=None):
    if not email:
        frappe.throw(_("Email is required"))

    job_filters = {}
    if company:
        job_filters["company"] = company

    job_openings = frappe.get_all(
        "Job Opening", 
        filters=job_filters, 
        fields=["name", "company"],
        limit=0
    )
    job_map = {job.name: job.company for job in job_openings}

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Interview Reject", "owner": email},
        fields=[
            "name","applicant_name","email_id","phone_number","country",
            "job_title","designation","notes","resume_attachment","resume_link",
            "lower_range","upper_range"
        ],
        limit=0,
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
        limit=0
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
        limit=0,
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
def get_offer_drop_applicants_by_company(email, company=None):
    """
    Fetch applicants with status 'Offer Drop' filtered by company
    """
    if not email:
        frappe.throw(_("Email is required"))

    job_filters = {}
    if company:
        job_filters["company"] = company

    job_openings = frappe.get_all(
        "Job Opening", 
        filters=job_filters, 
        fields=["name", "company"],
        limit=0
    )
    job_map = {job.name: job.company for job in job_openings}

    applicants = frappe.get_all(
        "Job Applicant",
        filters={"status": "Offer Drop", "owner": email},
        fields=[
            "name","applicant_name","email_id","phone_number","country",
            "job_title","designation","notes","resume_attachment","resume_link",
            "lower_range","upper_range"
        ],
        limit=0,
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
        limit=0
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
        limit=0,
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


# Remove or fix the duplicate get_rejected_applicants_by_company function
# Since you have "Interview Reject" and "Offer Drop" as separate statuses,
# you might not need a general "Rejected" status

@frappe.whitelist(allow_guest=False)
def get_recruiter_dashboard_data(email=None):
    """
    Master function to fetch all recruiter dashboard data in a single API call.
    Returns all applicants grouped by status with company information.
    """
    if not email:
        email = frappe.session.user
    
    if not email:
        frappe.throw(_("Email is required"))

    # Define all statuses according to your requirements
    statuses = [
        "Tagged",
        "Shortlisted", 
        "Assessment",
        "Interview",
        "Interview Reject",  # ADDED: This status was missing
        "Offered",
        "Offer Drop",  # ADDED: This status was missing
        "Joined"
    ]

    # Fetch companies and jobs from ToDo
    todos = frappe.get_all(
        "ToDo",
        filters={"allocated_to": email},
        fields=["custom_company", "custom_job_title"],
        limit=0,
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
        limit=0
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
        limit=0,
        order_by="creation desc"
    )

    # Initialize result structures
    metrics = {status: 0 for status in statuses}
    applicants_by_status = {
        "tagged_applicants": [],
        "shortlisted_applicants": [],
        "assessment_stage_applicants": [],
        "interview_stage_applicants": [],
        "interview_reject_applicants": [],  # ADDED: This was missing
        "offered_applicants": [],
        "offer_drop_applicants": [],  # ADDED: This was missing
        "joined_applicants": []
    }

    # Status mapping to response keys - UPDATED with new statuses
    status_key_map = {
        "Tagged": "tagged_applicants",
        "Shortlisted": "shortlisted_applicants",
        "Assessment": "assessment_stage_applicants",
        "Interview": "interview_stage_applicants",
        "Interview Reject": "interview_reject_applicants",  # ADDED
        "Offered": "offered_applicants",
        "Offer Drop": "offer_drop_applicants",  # ADDED
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
        metrics.get("Assessment", 0) +
        metrics.get("Interview", 0)
    )
    
    summary = {
        "total_applicants": total_applicants,
        "active_pipeline": active_pipeline,
        "offered": metrics.get("Offered", 0),
        "joined": metrics.get("Joined", 0),
        "interview_reject": metrics.get("Interview Reject", 0),  # ADDED
        "offer_drop": metrics.get("Offer Drop", 0),  # ADDED
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

# Also update the get_recruiter_dashboard_data_by_company function similarly
@frappe.whitelist(allow_guest=False)
def get_recruiter_dashboard_data_by_company(email=None, company=None):
    """
    Master function to fetch all recruiter dashboard data filtered by company.
    """
    if not email:
        email = frappe.session.user
    
    if not email:
        frappe.throw(_("Email is required"))

    # Define all statuses
    statuses = [
        "Tagged",
        "Shortlisted", 
        "Assessment",
        "Interview",
        "Interview Reject",  # ADDED
        "Offered",
        "Offer Drop",  # ADDED
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
        limit=0,
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
        limit=0
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
        limit=0,
        order_by="creation desc"
    )

    # Initialize result structures
    metrics = {status: 0 for status in statuses}
    
    # Updated status mapping
    applicants_by_status = {
        "tagged_applicants_by_company": {},
        "shortlisted_applicants_by_company": {},
        "assessment_stage_applicants_by_company": {},
        "interview_stage_applicants_by_company": {},
        "interview_reject_applicants_by_company": {},  # ADDED
        "offered_applicants_by_company": {},
        "offer_drop_applicants_by_company": {},  # ADDED
        "joined_applicants_by_company": {}
    }

    # Status mapping - UPDATED
    status_key_map = {
        "Tagged": "tagged_applicants_by_company",
        "Shortlisted": "shortlisted_applicants_by_company",
        "Assessment": "assessment_stage_applicants_by_company",
        "Interview": "interview_stage_applicants_by_company",
        "Interview Reject": "interview_reject_applicants_by_company",  # ADDED
        "Offered": "offered_applicants_by_company",
        "Offer Drop": "offer_drop_applicants_by_company",  # ADDED
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
        metrics.get("Assessment", 0) +
        metrics.get("Interview", 0)
    )
    
    summary = {
        "total_applicants": total_applicants,
        "active_pipeline": active_pipeline,
        "offered": metrics.get("Offered", 0),
        "joined": metrics.get("Joined", 0),
        "interview_reject": metrics.get("Interview Reject", 0),  # ADDED
        "offer_drop": metrics.get("Offer Drop", 0),  # ADDED
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