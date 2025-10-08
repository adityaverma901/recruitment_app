import frappe
from frappe import _
from datetime import datetime, timedelta
import calendar


@frappe.whitelist(allow_guest=False)
def get_recruiter_trends_granular(email=None, company=None, time_period="month"):
    """
    Get granular trends data for recruiter dashboard
    
    Time period breakdown:
    - "week": Returns 7 days of data (Mon-Sun for current week)
    - "month": Returns 4-5 weeks of data for current month
    - "quarter": Returns 3 months of data for current quarter
    
    Args:
        email: Recruiter email (defaults to current user)
        company: Optional company filter
        time_period: "week" | "month" | "quarter"
    
    Returns:
        Dictionary with granular trends data and metrics
    """
    if not email:
        email = frappe.session.user
    
    now = datetime.now()
    
    # Get the appropriate date range based on time period
    if time_period == "week":
        period_start, period_end = get_current_week_range(now)
    elif time_period == "month":
        period_start, period_end = get_current_month_range(now)
    else:  # quarter
        period_start, period_end = get_current_quarter_range(now)
    
    # Build filters for applicants
    applicant_filters = {
        "owner": email,
        "creation": ["between", [period_start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")]]
    }
    
    # Apply company filter if provided
    if company:
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
                "period_info": {
                    "type": time_period,
                    "start_date": period_start.strftime("%Y-%m-%d"),
                    "end_date": period_end.strftime("%Y-%m-%d"),
                    "current_date": now.strftime("%Y-%m-%d")
                }
            }
    
    # Fetch all applicants for the period
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
    
    # Format applicants
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
    
    # Calculate granular trends
    if time_period == "week":
        trends = calculate_daily_trends(formatted_applicants, period_start, now)
    elif time_period == "month":
        trends = calculate_weekly_trends_in_month(formatted_applicants, period_start, now)
    else:  # quarter
        trends = calculate_monthly_trends_in_quarter(formatted_applicants, period_start, now)
    
    # Calculate summary metrics
    metrics = calculate_recruiter_metrics(formatted_applicants)
    
    return {
        "trends": trends,
        "metrics": metrics,
        "period_info": {
            "type": time_period,
            "start_date": period_start.strftime("%Y-%m-%d"),
            "end_date": period_end.strftime("%Y-%m-%d"),
            "current_date": now.strftime("%Y-%m-%d")
        }
    }


def get_current_week_range(now):
    """
    Get current week range (Monday to Sunday)
    Returns: (week_start, week_end)
    """
    # Get Monday of current week
    weekday = now.weekday()  # 0 = Monday, 6 = Sunday
    week_start = (now - timedelta(days=weekday)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Sunday of current week
    week_end = (week_start + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Don't go beyond today
    if week_end > now:
        week_end = now
    
    return week_start, week_end


def get_current_month_range(now):
    """
    Get current month range (1st to last day)
    Returns: (month_start, month_end)
    """
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Last day of month
    last_day = calendar.monthrange(now.year, now.month)[1]
    month_end = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    
    # Don't go beyond today
    if month_end > now:
        month_end = now
    
    return month_start, month_end


def get_current_quarter_range(now):
    """
    Get current quarter range
    Returns: (quarter_start, quarter_end)
    """
    current_month = now.month
    quarter = (current_month - 1) // 3 + 1
    quarter_start_month = (quarter - 1) * 3 + 1
    
    quarter_start = datetime(now.year, quarter_start_month, 1, 0, 0, 0, 0)
    
    quarter_end_month = quarter_start_month + 2
    last_day = calendar.monthrange(now.year, quarter_end_month)[1]
    quarter_end = datetime(now.year, quarter_end_month, last_day, 23, 59, 59, 999999)
    
    # Don't go beyond today
    if quarter_end > now:
        quarter_end = now
    
    return quarter_start, quarter_end


def calculate_daily_trends(applicants, week_start, now):
    """
    Calculate daily trends for current week (7 days: Mon-Sun)
    Shows data for each day from Monday to today
    """
    trends = []
    
    # Day names
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for day_offset in range(7):
        day_date = week_start + timedelta(days=day_offset)
        
        # Only show days up to today
        if day_date.date() > now.date():
            break
        
        day_start = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # If it's today, end at current time
        if day_date.date() == now.date():
            day_end = now
        
        # Day label: "Mon 7" or "Tue 8"
        day_label = f"{day_names[day_offset][:3]} {day_date.day}"
        
        # Filter applicants for this day
        day_applicants = get_applicants_for_period(applicants, day_start, day_end)
        
        trends.append(create_trend_data_point(day_label, day_applicants))
    
    return trends


def calculate_weekly_trends_in_month(applicants, month_start, now):
    """
    Calculate weekly trends for current month (4-5 weeks)
    Shows data for each complete or partial week in the month
    """
    trends = []
    
    current_date = month_start
    week_num = 1
    
    while current_date <= now:
        # Start of week (or start of month for first week)
        week_start = current_date
        
        # End of week (6 days later) or end of month
        week_end = current_date + timedelta(days=6)
        week_end = week_end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Don't exceed current time
        if week_end > now:
            week_end = now
        
        # Week label with date range
        if week_start.month == week_end.month:
            week_label = f"Week {week_num} ({week_start.day}-{week_end.day})"
        else:
            # Week spans multiple months
            week_label = f"Week {week_num} ({week_start.strftime('%b %d')}-{week_end.strftime('%b %d')})"
        
        # Filter applicants for this week
        week_applicants = get_applicants_for_period(applicants, week_start, week_end)
        
        trends.append(create_trend_data_point(week_label, week_applicants))
        
        # Move to next week
        current_date = week_end + timedelta(days=1)
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        week_num += 1
        
        # Stop if we've passed today
        if current_date > now:
            break
    
    return trends


def calculate_monthly_trends_in_quarter(applicants, quarter_start, now):
    """
    Calculate monthly trends for current quarter (3 months)
    Shows data for each month in the quarter
    """
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
        
        # Only include months that have started
        if month_start <= now:
            # Filter applicants for this month
            month_applicants = get_applicants_for_period(applicants, month_start, month_end)
            
            trends.append(create_trend_data_point(month_name, month_applicants))
    
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