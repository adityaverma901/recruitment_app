# import frappe
# from frappe import _
# from datetime import datetime, timedelta
# import calendar

# @frappe.whitelist(allow_guest=False)
# def get_lead_dashboard_data(lead_owner=None, start_date=None, end_date=None):
#     """
#     Fetch lead dashboard data (WITHOUT trends)
#     Call get_lead_trends_data separately for trends
    
#     Args:
#         lead_owner: Lead Owner email (defaults to current user, "All" for all leads)
#         start_date: Custom start date (format: "YYYY-MM-DD") - optional
#         end_date: Custom end date (format: "YYYY-MM-DD") - optional
#     """
#     if not lead_owner or lead_owner == "All":
#         lead_owner = None
    
#     # Fetch all required data (WITHOUT trends)
#     data = {
#         'metrics': get_lead_metrics(lead_owner, start_date, end_date),
#         'leads_by_stage': get_leads_by_stage(lead_owner, start_date, end_date)
#     }
    
#     return data


# @frappe.whitelist(allow_guest=False)
# def get_lead_metrics(lead_owner=None, start_date=None, end_date=None):
#     """
#     Calculate summary metrics for lead dashboard
    
#     Args:
#         lead_owner: Filter by lead owner
#         start_date: Custom start date (format: "YYYY-MM-DD")
#         end_date: Custom end date (format: "YYYY-MM-DD")
    
#     Returns:
#         - total_leads: Total count of leads
#         - total_deal_value: Sum of all deal values
#         - converted_leads: Count of Onboarded + Contract leads
#         - opportunities_won: Same as converted_leads
#         - conversion_rate: Percentage of converted leads
#         - average_deal_size: Average deal value
#         - prospecting_leads: Count of Prospecting stage leads
#         - onboarded_leads: Count of Onboarded stage leads
#         - contract_leads: Count of Contract stage leads
#     """
#     # Build filters
#     filters = {}
#     if lead_owner:
#         filters["lead_owner"] = lead_owner
    
#     # Add date range filter if provided
#     if start_date and end_date:
#         filters["creation"] = ["between", [start_date, end_date]]
#     elif start_date:
#         filters["creation"] = [">=", start_date]
#     elif end_date:
#         filters["creation"] = ["<=", end_date]
    
#     # Fetch all leads with required fields
#     leads = frappe.get_all(
#         "Lead",
#         filters=filters,
#         fields=[
#             "name",
#             "lead_owner",
#             "company_name",
#             "industry",
#             "custom_stage",
#             "custom_deal_value",
#             "custom_estimated_hiring_",
#             "creation",
#             "custom_offerings"
#         ],
#         limit=0
#     )
    
#     # Calculate metrics
#     total_leads = len(leads)
#     total_deal_value = sum(float(lead.get("custom_deal_value") or 0) for lead in leads)
    
#     # Count by stage - ALL 7 STAGES
#     prospecting_leads = len([l for l in leads if l.get("custom_stage") == "Prospecting"])
#     lead_qualification_leads = len([l for l in leads if l.get("custom_stage") == "Lead Qualification"])
#     needs_analysis_leads = len([l for l in leads if l.get("custom_stage") == "Needs Analysis / Discovery"])
#     presentation_leads = len([l for l in leads if l.get("custom_stage") == "Presentation / Proposal"])
#     contract_leads = len([l for l in leads if l.get("custom_stage") == "Contract"])
#     onboarded_leads = len([l for l in leads if l.get("custom_stage") == "Onboarded"])
#     followup_leads = len([l for l in leads if l.get("custom_stage") == "Follow-Up / Relationship Management"])
    
#     # Converted leads = Contract + Onboarded (as per your original requirement)
#     converted_leads = contract_leads + onboarded_leads
#     opportunities_won = converted_leads  # Same as converted
    
#     # Conversion rate
#     conversion_rate = round((converted_leads / total_leads * 100), 2) if total_leads > 0 else 0
    
#     # Average deal size
#     average_deal_size = round(total_deal_value / total_leads, 2) if total_leads > 0 else 0
    
#     return {
#         "total_leads": total_leads,
#         "total_deal_value": total_deal_value,
#         "converted_leads": converted_leads,
#         "opportunities_won": opportunities_won,
#         "conversion_rate": conversion_rate,
#         "average_deal_size": average_deal_size,
#         "prospecting_leads": prospecting_leads,
#         "lead_qualification_leads": lead_qualification_leads,
#         "needs_analysis_leads": needs_analysis_leads,
#         "presentation_leads": presentation_leads,
#         "contract_leads": contract_leads,
#         "onboarded_leads": onboarded_leads,
#         "followup_leads": followup_leads
#     }


# @frappe.whitelist(allow_guest=False)
# def get_leads_by_stage(lead_owner=None, start_date=None, end_date=None):
#     """
#     Get all leads grouped by stage
    
#     Args:
#         lead_owner: Filter by lead owner
#         start_date: Custom start date (format: "YYYY-MM-DD")
#         end_date: Custom end date (format: "YYYY-MM-DD")
    
#     Returns leads separated by:
#     - Prospecting
#     - Onboarded
#     - Contract
#     """
#     # Build filters
#     filters = {}
#     if lead_owner:
#         filters["lead_owner"] = lead_owner
    
#     # Add date range filter if provided
#     if start_date and end_date:
#         filters["creation"] = ["between", [start_date, end_date]]
#     elif start_date:
#         filters["creation"] = [">=", start_date]
#     elif end_date:
#         filters["creation"] = ["<=", end_date]
    
#     # Fetch all leads - only ID and stage
#     leads = frappe.get_all(
#         "Lead",
#         filters=filters,
#         fields=["name", "custom_stage"],
#         limit=0,
#         order_by="creation desc"
#     )
    
#     # Group by stage - ALL 7 STAGES
#     leads_by_stage = {
#         "Prospecting": [],
#         "Lead Qualification": [],
#         "Needs Analysis / Discovery": [],
#         "Presentation / Proposal": [],
#         "Contract": [],
#         "Onboarded": [],
#         "Follow-Up / Relationship Management": []
#     }
    
#     for lead in leads:
#         stage = lead.get("custom_stage", "Prospecting")
#         if stage in leads_by_stage:
#             leads_by_stage[stage].append(lead.name)  # Only append ID
    
#     # Calculate counts
#     stage_counts = {
#         stage: len(lead_list) 
#         for stage, lead_list in leads_by_stage.items()
#     }
    
#     return {
#         "leads_by_stage": leads_by_stage,
#         "stage_counts": stage_counts
#     }


# @frappe.whitelist(allow_guest=False)
# def get_lead_trends_data(lead_owner=None, time_period="month", start_date=None, end_date=None):
#     """
#     Calculate trends data for lead dashboard showing lead progress over time
    
#     Two modes:
#     1. If start_date and end_date provided: Use custom date range
#     2. If no dates provided: Use current quarter (default behavior)
    
#     Args:
#         lead_owner: Lead Owner email (None or "All" for all leads)
#         time_period: "week" | "month" | "quarter"
#         start_date: Custom start date (format: "YYYY-MM-DD") - optional
#         end_date: Custom end date (format: "YYYY-MM-DD") - optional
    
#     Returns:
#         Dictionary with trends data
#     """
#     now = datetime.now()
    
#     # Determine date range
#     if start_date and end_date:
#         # Custom date range mode
#         try:
#             range_start = datetime.strptime(start_date, "%Y-%m-%d")
#             range_end = datetime.strptime(end_date, "%Y-%m-%d")
            
#             # Ensure end date is not in future
#             if range_end > now:
#                 range_end = now
            
#             date_info = {
#                 "mode": "custom",
#                 "start_date": range_start.strftime("%Y-%m-%d"),
#                 "end_date": range_end.strftime("%Y-%m-%d"),
#                 "current_date": now.strftime("%Y-%m-%d")
#             }
#         except ValueError:
#             frappe.throw(_("Invalid date format. Use YYYY-MM-DD"))
#     else:
#         # Current quarter mode (default)
#         quarter, quarter_start, quarter_end, quarter_months = get_current_quarter_info()
#         range_start = quarter_start
#         range_end = now  # Only till today
        
#         date_info = {
#             "mode": "quarter",
#             "quarter": quarter,
#             "start_date": range_start.strftime("%Y-%m-%d"),
#             "end_date": quarter_end.strftime("%Y-%m-%d"),
#             "months": quarter_months,
#             "current_date": now.strftime("%Y-%m-%d")
#         }
    
#     # Build filters for leads
#     lead_filters = {
#         "creation": ["between", [range_start.strftime("%Y-%m-%d"), range_end.strftime("%Y-%m-%d")]]
#     }
    
#     # Apply lead owner filter if provided
#     if lead_owner:
#         lead_filters["lead_owner"] = lead_owner
    
#     # Fetch all leads for the date range
#     all_leads = frappe.get_all(
#         "Lead",
#         filters=lead_filters,
#         fields=[
#             "name",
#             "lead_owner",
#             "company_name",
#             "industry",
#             "custom_stage",
#             "custom_deal_value",
#             "creation"
#         ],
#         limit=0,
#         order_by="creation desc"
#     )
    
#     # Format leads data
#     formatted_leads = []
#     for lead in all_leads:
#         formatted_leads.append({
#             "id": lead.name,
#             "lead_owner": lead.lead_owner,
#             "company_name": lead.company_name,
#             "industry": lead.industry,
#             "stage": lead.custom_stage,
#             "deal_value": float(lead.custom_deal_value or 0),
#             "creation_date": lead.creation.strftime("%Y-%m-%d") if lead.creation else None
#         })
    
#     # Calculate trends based on time period
#     trends = calculate_lead_trends(formatted_leads, time_period, range_start, range_end, now)
    
#     # Calculate summary metrics
#     metrics = calculate_trend_metrics(formatted_leads)
    
#     return {
#         "trends": trends,
#         "metrics": metrics,
#         "date_info": date_info
#     }


# def get_current_quarter_info():
#     """
#     Get current quarter information
#     Returns: (quarter_number, quarter_start_date, quarter_end_date, quarter_months)
#     """
#     now = datetime.now()
#     current_month = now.month
    
#     # Determine quarter (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
#     quarter = (current_month - 1) // 3 + 1
    
#     # Calculate quarter start month
#     quarter_start_month = (quarter - 1) * 3 + 1
    
#     # Create quarter start date (first day of first month)
#     quarter_start = datetime(now.year, quarter_start_month, 1, 0, 0, 0, 0)
    
#     # Calculate quarter end month
#     quarter_end_month = quarter_start_month + 2
    
#     # Get last day of quarter end month
#     last_day = calendar.monthrange(now.year, quarter_end_month)[1]
#     quarter_end = datetime(now.year, quarter_end_month, last_day, 23, 59, 59, 999999)
    
#     # Get quarter month names
#     quarter_months = []
#     for i in range(3):
#         month_num = quarter_start_month + i
#         month_name = datetime(now.year, month_num, 1).strftime("%B")
#         quarter_months.append(month_name)
    
#     return quarter, quarter_start, quarter_end, quarter_months


# def calculate_lead_trends(leads, time_period, quarter_start, quarter_end, now):
#     """
#     Calculate time-series trends for lead dashboard
#     Shows data for CURRENT QUARTER ONLY with 3 different views
#     All data is calculated ONLY till current date (not future dates)
#     """
#     trends = []
    
#     frappe.logger().info(f"=== Calculating Lead Trends for {time_period} ===")
#     frappe.logger().info(f"Quarter Start: {quarter_start.strftime('%Y-%m-%d')}")
#     frappe.logger().info(f"Today: {now.strftime('%Y-%m-%d')}")
#     frappe.logger().info(f"Total leads in quarter till today: {len(leads)}")
    
#     if time_period == "week":
#         # Weekly view - show ALL weeks from quarter start till today
#         trends = calculate_weekly_trends(leads, quarter_start, now)
    
#     elif time_period == "month":
#         # Monthly view - show all 3 months of current quarter (till today for current month)
#         trends = calculate_monthly_trends(leads, quarter_start, now)
    
#     else:  # quarterly
#         # Quarterly view - single data point for entire current quarter (till today)
#         trends = calculate_quarterly_trends(leads, quarter_start, now)
    
#     frappe.logger().info(f"Generated {len(trends)} trend data points")
    
#     return trends


# def calculate_weekly_trends(leads, quarter_start, now):
#     """Calculate weekly trends from quarter start till today"""
#     trends = []
    
#     # Calculate total weeks from quarter start till today
#     days_elapsed = (now - quarter_start).days
#     num_weeks = (days_elapsed // 7) + 1  # +1 for current partial week
    
#     for week_num in range(num_weeks):
#         week_start = quarter_start + timedelta(days=7 * week_num)
#         week_end = week_start + timedelta(days=6)
        
#         # For the current week, end date should be today
#         if week_end > now:
#             week_end = now
        
#         # Week label with date range
#         if week_start.month == week_end.month:
#             week_label = f"{week_start.strftime('%b')} {week_start.day}-{week_end.day}"
#         else:
#             week_label = f"{week_start.strftime('%b')} {week_start.day}-{week_end.strftime('%b')} {week_end.day}"
        
#         # Filter leads for this week
#         period_leads = get_leads_for_period(leads, week_start, week_end)
        
#         trends.append(create_trend_data_point(week_label, period_leads))
    
#     return trends


# def calculate_monthly_trends(leads, quarter_start, now):
#     """Calculate monthly trends for current quarter months till today"""
#     trends = []
#     quarter_start_month = quarter_start.month
    
#     for i in range(3):
#         month_num = quarter_start_month + i
#         month_year = now.year
        
#         # Handle year boundary
#         if month_num > 12:
#             month_num -= 12
#             month_year += 1
        
#         month_date = datetime(month_year, month_num, 1)
#         month_name = month_date.strftime("%B")
        
#         # Get start and end of month
#         month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         last_day = calendar.monthrange(month_year, month_num)[1]
#         month_end = month_date.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
        
#         # If it's current month, only go till today
#         if month_year == now.year and month_num == now.month:
#             month_end = now
        
#         # Only include months that have started (not future months)
#         if month_start <= now:
#             # Filter leads for this month
#             period_leads = get_leads_for_period(leads, month_start, month_end)
            
#             trends.append(create_trend_data_point(month_name, period_leads))
    
#     return trends


# def calculate_quarterly_trends(leads, quarter_start, now):
#     """Calculate quarterly trends - single data point for current quarter till today"""
#     trends = []
    
#     quarter_num = (quarter_start.month - 1) // 3 + 1
#     quarter_label = f"Q{quarter_num}"
    
#     # All leads are already filtered to current quarter till today
#     trends.append(create_trend_data_point(quarter_label, leads))
    
#     return trends


# def get_leads_for_period(leads, period_start, period_end):
#     """Filter leads for a specific time period"""
#     period_leads = []
    
#     for lead in leads:
#         creation_date = lead.get("creation_date")
#         if creation_date:
#             try:
#                 # Convert string date to datetime for comparison
#                 if isinstance(creation_date, str):
#                     creation_date_dt = datetime.strptime(creation_date, "%Y-%m-%d")
#                 else:
#                     creation_date_dt = creation_date
                
#                 # Check if creation date falls within the period
#                 if period_start.date() <= creation_date_dt.date() <= period_end.date():
#                     period_leads.append(lead)
#             except Exception as e:
#                 frappe.logger().error(f"Error parsing date {creation_date}: {str(e)}")
#                 continue
    
#     return period_leads


# def create_trend_data_point(label, period_leads):
#     """
#     Create a single trend data point with all metrics for ALL 7 STAGES
#     """
#     total_deal_value = sum(lead.get("deal_value", 0) for lead in period_leads)
    
#     # Count all 7 stages
#     prospecting = len([l for l in period_leads if l.get("stage") == "Prospecting"])
#     lead_qualification = len([l for l in period_leads if l.get("stage") == "Lead Qualification"])
#     needs_analysis = len([l for l in period_leads if l.get("stage") == "Needs Analysis / Discovery"])
#     presentation = len([l for l in period_leads if l.get("stage") == "Presentation / Proposal"])
#     contract = len([l for l in period_leads if l.get("stage") == "Contract"])
#     onboarded = len([l for l in period_leads if l.get("stage") == "Onboarded"])
#     followup = len([l for l in period_leads if l.get("stage") == "Follow-Up / Relationship Management"])
    
#     converted = contract + onboarded
    
#     return {
#         "period": label,
#         "total_leads": len(period_leads),
#         "total_deal_value": round(total_deal_value, 2),
#         "converted_leads": converted,
#         "prospecting": prospecting,
#         "lead_qualification": lead_qualification,
#         "needs_analysis": needs_analysis,
#         "presentation": presentation,
#         "contract": contract,
#         "onboarded": onboarded,
#         "followup": followup
#     }


# def calculate_trend_metrics(leads):
#     """
#     Calculate summary metrics for trends - ALL 7 STAGES
#     """
#     total_deal_value = sum(lead.get("deal_value", 0) for lead in leads)
    
#     # Count all 7 stages
#     prospecting = len([l for l in leads if l.get("stage") == "Prospecting"])
#     lead_qualification = len([l for l in leads if l.get("stage") == "Lead Qualification"])
#     needs_analysis = len([l for l in leads if l.get("stage") == "Needs Analysis / Discovery"])
#     presentation = len([l for l in leads if l.get("stage") == "Presentation / Proposal"])
#     contract = len([l for l in leads if l.get("stage") == "Contract"])
#     onboarded = len([l for l in leads if l.get("stage") == "Onboarded"])
#     followup = len([l for l in leads if l.get("stage") == "Follow-Up / Relationship Management"])
    
#     converted = contract + onboarded
#     conversion_rate = round((converted / len(leads) * 100), 2) if len(leads) > 0 else 0
    
#     return {
#         "total_leads": len(leads),
#         "total_deal_value": round(total_deal_value, 2),
#         "converted_leads": converted,
#         "conversion_rate": conversion_rate,
#         "prospecting": prospecting,
#         "lead_qualification": lead_qualification,
#         "needs_analysis": needs_analysis,
#         "presentation": presentation,
#         "contract": contract,
#         "onboarded": onboarded,
#         "followup": followup
#     }


# @frappe.whitelist(allow_guest=False)
# def get_all_lead_owners():
#     """
#     Get list of all unique lead owners for filter dropdown
#     """
#     lead_owners = frappe.get_all(
#         "Lead",
#         fields=["lead_owner"],
#         distinct=True,
#         order_by="lead_owner asc"
#     )
    
#     owners = [owner.lead_owner for owner in lead_owners if owner.lead_owner]
    
#     return {
#         "success": True,
#         "lead_owners": owners
#     }



import frappe
from frappe import _
from datetime import datetime, timedelta
import calendar

@frappe.whitelist(allow_guest=False)
def get_lead_dashboard_data(lead_owner=None, start_date=None, end_date=None):
    """
    Fetch lead dashboard data (WITHOUT trends)
    Call get_lead_trends_data separately for trends
    
    Args:
        lead_owner: Lead Owner email (defaults to current user, "All" for all leads)
        start_date: Custom start date (format: "YYYY-MM-DD") - optional
        end_date: Custom end date (format: "YYYY-MM-DD") - optional
    """
    if not lead_owner or lead_owner == "All":
        lead_owner = None
    
    # Fetch all required data (WITHOUT trends)
    data = {
        'metrics': get_lead_metrics(lead_owner, start_date, end_date),
        'leads_by_stage': get_leads_by_stage(lead_owner, start_date, end_date)
    }
    
    return data


@frappe.whitelist(allow_guest=False)
def get_lead_metrics(lead_owner=None, start_date=None, end_date=None):
    """
    Calculate summary metrics for lead dashboard
    
    Args:
        lead_owner: Filter by lead owner
        start_date: Custom start date (format: "YYYY-MM-DD")
        end_date: Custom end date (format: "YYYY-MM-DD")
    
    Returns:
        - total_leads: Total count of leads
        - total_deal_value: Sum of all deal values
        - converted_leads: Count of Onboarded + Contract leads
        - opportunities_won: Same as converted_leads
        - conversion_rate: Percentage of converted leads
        - average_deal_size: Average deal value
        - prospecting_leads: Count of Prospecting stage leads
        - onboarded_leads: Count of Onboarded stage leads
        - contract_leads: Count of Contract stage leads
    """
    # Build filters
    filters = {}
    if lead_owner:
        filters["lead_owner"] = lead_owner
    
    # Add date range filter if provided
    if start_date and end_date:
        filters["creation"] = ["between", [start_date, end_date]]
    elif start_date:
        filters["creation"] = [">=", start_date]
    elif end_date:
        filters["creation"] = ["<=", end_date]
    
    # Fetch all leads with required fields
    leads = frappe.get_all(
        "Lead",
        filters=filters,
        fields=[
            "name",
            "lead_owner",
            "company_name",
            "industry",
            "custom_stage",
            "custom_deal_value",
            "custom_estimated_hiring_",
            "creation",
            "custom_offerings"
        ],
        limit=0
    )
    
    # Calculate metrics
    total_leads = len(leads)
    total_deal_value = sum(float(lead.get("custom_deal_value") or 0) for lead in leads)
    
    # Count by stage - ALL 7 STAGES
    prospecting_leads = len([l for l in leads if l.get("custom_stage") == "Prospecting"])
    lead_qualification_leads = len([l for l in leads if l.get("custom_stage") == "Lead Qualification"])
    needs_analysis_leads = len([l for l in leads if l.get("custom_stage") == "Needs Analysis / Discovery"])
    presentation_leads = len([l for l in leads if l.get("custom_stage") == "Presentation / Proposal"])
    contract_leads = len([l for l in leads if l.get("custom_stage") == "Contract"])
    onboarded_leads = len([l for l in leads if l.get("custom_stage") == "Onboarded"])
    followup_leads = len([l for l in leads if l.get("custom_stage") == "Follow-Up / Relationship Management"])
    
    # Converted leads = Contract + Onboarded (as per your original requirement)
    converted_leads = contract_leads + onboarded_leads
    opportunities_won = converted_leads  # Same as converted
    
    # Conversion rate
    conversion_rate = round((converted_leads / total_leads * 100), 2) if total_leads > 0 else 0
    
    # Average deal size
    average_deal_size = round(total_deal_value / total_leads, 2) if total_leads > 0 else 0
    
    return {
        "total_leads": total_leads,
        "total_deal_value": total_deal_value,
        "converted_leads": converted_leads,
        "opportunities_won": opportunities_won,
        "conversion_rate": conversion_rate,
        "average_deal_size": average_deal_size,
        "prospecting_leads": prospecting_leads,
        "lead_qualification_leads": lead_qualification_leads,
        "needs_analysis_leads": needs_analysis_leads,
        "presentation_leads": presentation_leads,
        "contract_leads": contract_leads,
        "onboarded_leads": onboarded_leads,
        "followup_leads": followup_leads
    }


@frappe.whitelist(allow_guest=False)
def get_leads_by_stage(lead_owner=None, start_date=None, end_date=None):
    """
    Get all leads grouped by stage
    
    Args:
        lead_owner: Filter by lead owner
        start_date: Custom start date (format: "YYYY-MM-DD")
        end_date: Custom end date (format: "YYYY-MM-DD")
    
    Returns leads separated by:
    - Prospecting
    - Onboarded
    - Contract
    """
    # Build filters
    filters = {}
    if lead_owner:
        filters["lead_owner"] = lead_owner
    
    # Add date range filter if provided
    if start_date and end_date:
        filters["creation"] = ["between", [start_date, end_date]]
    elif start_date:
        filters["creation"] = [">=", start_date]
    elif end_date:
        filters["creation"] = ["<=", end_date]
    
    # Fetch all leads - only ID and stage
    leads = frappe.get_all(
        "Lead",
        filters=filters,
        fields=["name", "custom_stage"],
        limit=0,
        order_by="creation desc"
    )
    
    # Group by stage - ALL 7 STAGES
    leads_by_stage = {
        "Prospecting": [],
        "Lead Qualification": [],
        "Needs Analysis / Discovery": [],
        "Presentation / Proposal": [],
        "Contract": [],
        "Onboarded": [],
        "Follow-Up / Relationship Management": []
    }
    
    for lead in leads:
        stage = lead.get("custom_stage", "Prospecting")
        if stage in leads_by_stage:
            leads_by_stage[stage].append(lead.name)  # Only append ID
    
    # Calculate counts
    stage_counts = {
        stage: len(lead_list) 
        for stage, lead_list in leads_by_stage.items()
    }
    
    return {
        "leads_by_stage": leads_by_stage,
        "stage_counts": stage_counts
    }


@frappe.whitelist(allow_guest=False)
def get_lead_trends_data(lead_owner=None, time_period="month", start_date=None, end_date=None):
    """
    Calculate trends data for lead dashboard showing lead progress over time
    
    Two modes:
    1. If start_date and end_date provided: Use custom date range
    2. If no dates provided: Use current quarter (default behavior)
    
    Args:
        lead_owner: Lead Owner email (None or "All" for all leads)
        time_period: "week" | "month" | "quarter"
        start_date: Custom start date (format: "YYYY-MM-DD") - optional
        end_date: Custom end date (format: "YYYY-MM-DD") - optional
    
    Returns:
        Dictionary with trends data
    """
    now = datetime.now()
    
    # Determine date range
    if start_date and end_date:
        # Custom date range mode
        try:
            range_start = datetime.strptime(start_date, "%Y-%m-%d")
            range_end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Ensure end date is not in future
            if range_end > now:
                range_end = now
            
            date_info = {
                "mode": "custom",
                "start_date": range_start.strftime("%Y-%m-%d"),
                "end_date": range_end.strftime("%Y-%m-%d"),
                "current_date": now.strftime("%Y-%m-%d")
            }
        except ValueError:
            frappe.throw(_("Invalid date format. Use YYYY-MM-DD"))
    else:
        # Current quarter mode (default)
        quarter, quarter_start, quarter_end, quarter_months = get_current_quarter_info()
        range_start = quarter_start
        range_end = now  # Only till today
        
        date_info = {
            "mode": "quarter",
            "quarter": quarter,
            "start_date": range_start.strftime("%Y-%m-%d"),
            "end_date": quarter_end.strftime("%Y-%m-%d"),
            "months": quarter_months,
            "current_date": now.strftime("%Y-%m-%d")
        }
    
    # Build filters for leads
    lead_filters = {
        "creation": ["between", [range_start.strftime("%Y-%m-%d"), range_end.strftime("%Y-%m-%d")]]
    }
    
    # Apply lead owner filter if provided
    if lead_owner:
        lead_filters["lead_owner"] = lead_owner
    
    # Fetch all leads for the date range
    all_leads = frappe.get_all(
        "Lead",
        filters=lead_filters,
        fields=[
            "name",
            "lead_owner",
            "company_name",
            "industry",
            "custom_stage",
            "custom_deal_value",
            "creation"
        ],
        limit=0,
        order_by="creation desc"
    )
    
    # Format leads data
    formatted_leads = []
    for lead in all_leads:
        formatted_leads.append({
            "id": lead.name,
            "lead_owner": lead.lead_owner,
            "company_name": lead.company_name,
            "industry": lead.industry,
            "stage": lead.custom_stage,
            "deal_value": float(lead.custom_deal_value or 0),
            "creation_date": lead.creation.strftime("%Y-%m-%d") if lead.creation else None
        })
    
    # Calculate trends based on time period
    trends = calculate_lead_trends(formatted_leads, time_period, range_start, range_end, now)
    
    # Calculate summary metrics
    metrics = calculate_trend_metrics(formatted_leads)
    
    return {
        "trends": trends,
        "metrics": metrics,
        "date_info": date_info
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


def calculate_lead_trends(leads, time_period, quarter_start, quarter_end, now):
    """
    Calculate time-series trends for lead dashboard
    Shows data for CURRENT QUARTER ONLY with 3 different views
    All data is calculated ONLY till current date (not future dates)
    """
    trends = []
    
    frappe.logger().info(f"=== Calculating Lead Trends for {time_period} ===")
    frappe.logger().info(f"Quarter Start: {quarter_start.strftime('%Y-%m-%d')}")
    frappe.logger().info(f"Today: {now.strftime('%Y-%m-%d')}")
    frappe.logger().info(f"Total leads in quarter till today: {len(leads)}")
    
    if time_period == "week":
        # Weekly view - show ALL weeks from quarter start till today
        trends = calculate_weekly_trends(leads, quarter_start, now)
    
    elif time_period == "month":
        # Monthly view - show all 3 months of current quarter (till today for current month)
        trends = calculate_monthly_trends(leads, quarter_start, now)
    
    else:  # quarterly
        # Quarterly view - single data point for entire current quarter (till today)
        trends = calculate_quarterly_trends(leads, quarter_start, now)
    
    frappe.logger().info(f"Generated {len(trends)} trend data points")
    
    return trends


def calculate_daily_trends_current_week(leads, now):
    """
    Calculate daily trends for CURRENT WEEK ONLY (Mon-Sun)
    Shows 7 days: Monday to Sunday of current week
    """
    trends = []
    
    # Get current week's Monday
    current_weekday = now.weekday()  # 0=Monday, 6=Sunday
    week_start = now - timedelta(days=current_weekday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Generate 7 days (Mon-Sun)
    for day_num in range(7):
        day_date = week_start + timedelta(days=day_num)
        day_end = day_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # If day is in future, skip it
        if day_date.date() > now.date():
            continue
        
        # If it's today, only go till now
        if day_date.date() == now.date():
            day_end = now
        
        # Day label (e.g., "Mon 14", "Tue 15")
        day_label = day_date.strftime("%a %d")
        
        # Filter leads for this day
        period_leads = get_leads_for_period(leads, day_date, day_end)
        
        trends.append(create_trend_data_point(day_label, period_leads))
    
    return trends


def calculate_weekly_trends_current_month(leads, now):
    """
    Calculate weekly trends for CURRENT MONTH ONLY
    Shows weeks of current month (Week 1, Week 2, etc.)
    """
    trends = []
    
    # Get current month start and end
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = calendar.monthrange(now.year, now.month)[1]
    month_end = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    
    # Calculate weeks in current month
    current_date = month_start
    week_num = 1
    
    while current_date <= now:
        # Week runs from current_date to next Sunday (or month end)
        week_start = current_date
        
        # Find next Sunday or month end
        days_until_sunday = (6 - current_date.weekday()) % 7
        if days_until_sunday == 0 and current_date.weekday() != 6:  # If not Sunday
            days_until_sunday = 7
        
        week_end = current_date + timedelta(days=days_until_sunday)
        week_end = week_end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Don't go beyond month end
        if week_end > month_end:
            week_end = month_end
        
        # Don't go beyond today
        if week_end > now:
            week_end = now
        
        # Week label
        if week_start.month == week_end.month:
            week_label = f"Week {week_num} ({week_start.day}-{week_end.day})"
        else:
            week_label = f"Week {week_num}"
        
        # Filter leads for this week
        period_leads = get_leads_for_period(leads, week_start, week_end)
        
        trends.append(create_trend_data_point(week_label, period_leads))
        
        # Move to next week
        current_date = week_end + timedelta(days=1)
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        week_num += 1
        
        # Stop if we've gone beyond current month or today
        if current_date.month != now.month or current_date > now:
            break
    
    return trends


def calculate_three_months_trends(leads, now):
    """
    Calculate monthly trends for 3 MONTHS:
    - Previous month
    - Current month
    - Next month (if exists, otherwise skip)
    """
    trends = []
    
    current_year = now.year
    current_month = now.month
    
    # Define 3 months: Previous, Current, Next
    months_to_show = []
    
    # Previous month
    if current_month == 1:
        prev_month = 12
        prev_year = current_year - 1
    else:
        prev_month = current_month - 1
        prev_year = current_year
    months_to_show.append((prev_year, prev_month, "Previous"))
    
    # Current month
    months_to_show.append((current_year, current_month, "Current"))
    
    # Next month
    if current_month == 12:
        next_month = 1
        next_year = current_year + 1
    else:
        next_month = current_month + 1
        next_year = current_year
    months_to_show.append((next_year, next_month, "Next"))
    
    # Process each month
    for year, month, label_type in months_to_show:
        month_date = datetime(year, month, 1)
        month_name = month_date.strftime("%B %Y")
        
        # Get start and end of month
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = calendar.monthrange(year, month)[1]
        month_end = month_date.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
        
        # For current month, only go till today
        if year == now.year and month == now.month:
            month_end = now
        
        # Skip future months beyond next month
        if month_start > now and label_type == "Next":
            # For next month, show it but data will be 0
            pass
        
        # Month label
        month_label = f"{month_name} ({label_type})"
        
        # Filter leads for this month
        period_leads = get_leads_for_period(leads, month_start, month_end)
        
        trends.append(create_trend_data_point(month_label, period_leads))
    
    return trends


def get_leads_for_period(leads, period_start, period_end):
    """Filter leads for a specific time period"""
    period_leads = []
    
    for lead in leads:
        creation_date = lead.get("creation_date")
        if creation_date:
            try:
                # Convert string date to datetime for comparison
                if isinstance(creation_date, str):
                    creation_date_dt = datetime.strptime(creation_date, "%Y-%m-%d")
                else:
                    creation_date_dt = creation_date
                
                # Check if creation date falls within the period
                if period_start.date() <= creation_date_dt.date() <= period_end.date():
                    period_leads.append(lead)
            except Exception as e:
                frappe.logger().error(f"Error parsing date {creation_date}: {str(e)}")
                continue
    
    return period_leads


def create_trend_data_point(label, period_leads):
    """
    Create a single trend data point with all metrics for ALL 7 STAGES
    """
    total_deal_value = sum(lead.get("deal_value", 0) for lead in period_leads)
    
    # Count all 7 stages
    prospecting = len([l for l in period_leads if l.get("stage") == "Prospecting"])
    lead_qualification = len([l for l in period_leads if l.get("stage") == "Lead Qualification"])
    needs_analysis = len([l for l in period_leads if l.get("stage") == "Needs Analysis / Discovery"])
    presentation = len([l for l in period_leads if l.get("stage") == "Presentation / Proposal"])
    contract = len([l for l in period_leads if l.get("stage") == "Contract"])
    onboarded = len([l for l in period_leads if l.get("stage") == "Onboarded"])
    followup = len([l for l in period_leads if l.get("stage") == "Follow-Up / Relationship Management"])
    
    converted = contract + onboarded
    
    return {
        "period": label,
        "total_leads": len(period_leads),
        "total_deal_value": round(total_deal_value, 2),
        "converted_leads": converted,
        "prospecting": prospecting,
        "lead_qualification": lead_qualification,
        "needs_analysis": needs_analysis,
        "presentation": presentation,
        "contract": contract,
        "onboarded": onboarded,
        "followup": followup
    }


def calculate_trend_metrics(leads):
    """
    Calculate summary metrics for trends - ALL 7 STAGES
    """
    total_deal_value = sum(lead.get("deal_value", 0) for lead in leads)
    
    # Count all 7 stages
    prospecting = len([l for l in leads if l.get("stage") == "Prospecting"])
    lead_qualification = len([l for l in leads if l.get("stage") == "Lead Qualification"])
    needs_analysis = len([l for l in leads if l.get("stage") == "Needs Analysis / Discovery"])
    presentation = len([l for l in leads if l.get("stage") == "Presentation / Proposal"])
    contract = len([l for l in leads if l.get("stage") == "Contract"])
    onboarded = len([l for l in leads if l.get("stage") == "Onboarded"])
    followup = len([l for l in leads if l.get("stage") == "Follow-Up / Relationship Management"])
    
    converted = contract + onboarded
    conversion_rate = round((converted / len(leads) * 100), 2) if len(leads) > 0 else 0
    
    return {
        "total_leads": len(leads),
        "total_deal_value": round(total_deal_value, 2),
        "converted_leads": converted,
        "conversion_rate": conversion_rate,
        "prospecting": prospecting,
        "lead_qualification": lead_qualification,
        "needs_analysis": needs_analysis,
        "presentation": presentation,
        "contract": contract,
        "onboarded": onboarded,
        "followup": followup
    }


@frappe.whitelist(allow_guest=False)
def get_all_lead_owners():
    """
    Get list of all unique lead owners for filter dropdown
    """
    lead_owners = frappe.get_all(
        "Lead",
        fields=["lead_owner"],
        distinct=True,
        order_by="lead_owner asc"
    )
    
    owners = [owner.lead_owner for owner in lead_owners if owner.lead_owner]
    
    return {
        "success": True,
        "lead_owners": owners
    }