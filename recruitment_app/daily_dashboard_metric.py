import frappe
from frappe import _
from frappe.utils import today, getdate


@frappe.whitelist()
def get_daily_dashboard_data(date=None):
    """
    Fetch daily dashboard metrics for recruitment and staffing.
    
    Args:
        date (str, optional): Date in YYYY-MM-DD format. Defaults to today.
    
    Returns:
        dict: Dashboard metrics containing:
            - active_clients: Number of active clients with open jobs
            - total_open_roles: List of companies with their open positions
            - interviews_completed: Number of interviews cleared on the given date
            - offers_accepted: Number of job offers accepted on the given date
            - joiners: Number of unique job applicants who joined on the given date
    """
    if not date:
        date = today()
    
    try:
        target_date = getdate(date)
    except Exception:
        frappe.throw(_("Invalid date format. Please use YYYY-MM-DD format."))
    
    return {
        "date": str(target_date),
        "metrics": {
            "active_clients": get_active_clients_count(),
            "total_open_roles": get_total_open_roles(),
            "interviews_completed": get_interviews_completed(target_date),
            "offers_accepted": get_offers_accepted(target_date),
            "joiners": get_joiners_count(target_date)
        }
    }


def get_active_clients_count():
    """
    Get the number of active clients.
    
    A client is considered active if:
    - Lead stage is 'Onboarded' or 'Contract'
    - AND there are Job Openings linked to that Lead with status 'Open'
    
    Returns:
        int: Count of active clients
    """
    active_clients = frappe.db.sql("""
        SELECT COUNT(DISTINCT l.company_name) as count
        FROM `tabLead` l
        INNER JOIN `tabJob Opening` jo ON jo.company = l.company_name
        WHERE l.custom_stage IN ('Onboarded', 'Contract')
        AND jo.status = 'Open'
    """, as_dict=True)
    
    return active_clients[0].count if active_clients else 0


def get_total_open_roles():
    """
    Get total open roles grouped by company and designation.
    
    Data is fetched from Staffing Plan doctype and its child table staffing_details.
    
    Returns:
        list: List of dictionaries containing company, designation, and vacancies
    """
    open_roles = frappe.db.sql("""
        SELECT COUNT(*) as count  FROM `tabJob Opening` WHERE status !='closed'
    """, as_dict=True)
        
    return open_roles[0].count if open_roles else 0


def get_interviews_completed(date):
    """
    Get the number of interviews completed (cleared) on a specific date.
    
    Args:
        date (datetime.date): Target date
    
    Returns:
        int: Count of interviews with status 'Cleared' on the given date
    """
    interviews = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabInterview`
        WHERE status = 'Cleared'
        AND DATE(scheduled_on) = %s
    """, (date,), as_dict=True)
    
    return interviews[0].count if interviews else 0


def get_offers_accepted(date):
    """
    Get the number of job offers accepted on a specific date.
    
    Args:
        date (datetime.date): Target date
    
    Returns:
        int: Count of job offers with status 'Accepted' on the given date
    """
    offers = frappe.db.sql("""
        SELECT COUNT(DISTINCT name) as count
        FROM `tabJob Applicant`
        WHERE status = 'Offered'
        AND DATE(modified) = %s
    """, (date,), as_dict=True)
    
    return offers[0].count if offers else 0


def get_joiners_count(date):
    """
    Get the count of unique job applicants who joined on a specific date.
    
    Args:
        date (datetime.date): Target date
    
    Returns:
        int: Count of unique job applicants
    """
    # Assuming there's a 'date_of_joining' or similar field in Job Applicant
    # Adjust the field name based on your actual schema
    joiners = frappe.db.sql("""
        SELECT COUNT(DISTINCT name) as count
        FROM `tabJob Applicant`
        WHERE status = 'Joined'
        AND DATE(modified) = %s
    """, (date,), as_dict=True)
    
    return joiners[0].count if joiners else 0


@frappe.whitelist()
def get_dashboard_date_range(from_date, to_date):
    """
    Get dashboard metrics for a date range.
    
    Args:
        from_date (str): Start date in YYYY-MM-DD format
        to_date (str): End date in YYYY-MM-DD format
    
    Returns:
        dict: Dashboard metrics for each date in the range
    """
    try:
        start_date = getdate(from_date)
        end_date = getdate(to_date)
    except Exception:
        frappe.throw(_("Invalid date format. Please use YYYY-MM-DD format."))
    
    # Get interviews completed in date range
    interviews = frappe.db.sql("""
        SELECT DATE(scheduled_on) as date, COUNT(*) as count
        FROM `tabInterview`
        WHERE status = 'Cleared'
        AND DATE(scheduled_on) BETWEEN %s AND %s
        GROUP BY DATE(scheduled_on)
    """, (start_date, end_date), as_dict=True)
    
    # Get offers accepted in date range
    offers = frappe.db.sql("""
        SELECT DATE(modified) as date, COUNT(*) as count
        FROM `tabJob Offer`
        WHERE status = 'Accepted'
        AND DATE(modified) BETWEEN %s AND %s
        GROUP BY DATE(modified)
    """, (start_date, end_date), as_dict=True)
    
    # Get joiners in date range
    joiners = frappe.db.sql("""
        SELECT DATE(modified) as date, COUNT(DISTINCT name) as count
        FROM `tabJob Applicant`
        WHERE status = 'Accepted'
        AND DATE(modified) BETWEEN %s AND %s
        GROUP BY DATE(modified)
    """, (start_date, end_date), as_dict=True)
    
    return {
        "from_date": str(start_date),
        "to_date": str(end_date),
        "active_clients": get_active_clients_count(),
        "total_open_roles": get_total_open_roles(),
        "interviews_by_date": interviews,
        "offers_by_date": offers,
        "joiners_by_date": joiners
    }