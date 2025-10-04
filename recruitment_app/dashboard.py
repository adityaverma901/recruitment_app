# In your Frappe app: recruitment_app/recruitment_app/api/dashboard.py

import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_recruiter_dashboard_data(email=None):
    """
    Fetch all recruiter dashboard data in a single API call
    """
    if not email:
        email = frappe.session.user
    
    # Fetch all required data with optimized queries
    data = {
        'applicants': get_applicants_summary(email),
        'job_openings': get_job_openings_summary(email),
        'monthly_metrics': get_monthly_metrics(email),
        'active_clients': get_active_clients(email)
    }
    
    return data

def get_applicants_summary(email):
    """Get applicant statistics grouped by status and client"""
    applicants = frappe.get_all(
        'Job Applicant',
        filters={'owner': email},
        fields=[
            'name', 'applicant_name', 'email_id', 'job_title',
            'status', 'creation', 'modified'
        ],
        order_by='creation desc',
        limit_page_length=0
    )
    
    # Enrich with job opening details (client info)
    for applicant in applicants:
        if applicant.get('job_title'):
            job = frappe.get_cached_value(
                'Job Opening',
                applicant['job_title'],
                ['company', 'job_title', 'location'],
                as_dict=True
            )
            if job:
                applicant['client'] = job.get('company')
                applicant['job_title_name'] = job.get('job_title')
                applicant['location'] = job.get('location')
    
    return applicants

def get_job_openings_summary(email):
    """Get job openings with position counts"""
    jobs = frappe.get_all(
        'Job Opening',
        filters={'owner': email},
        fields=[
            'name', 'job_title', 'company', 'location',
            'status', 'planned_vacancies', 'creation'
        ],
        order_by='creation desc',
        limit_page_length=0
    )
    
    return jobs

def get_monthly_metrics(email):
    """Calculate monthly recruitment metrics"""
    # Get data for last 4 months
    from dateutil.relativedelta import relativedelta
    from datetime import datetime
    
    months_data = []
    today = datetime.now()
    
    for i in range(4):
        month_start = (today - relativedelta(months=i)).replace(day=1)
        month_end = (month_start + relativedelta(months=1))
        
        metrics = frappe.db.sql("""
            SELECT 
                COUNT(CASE WHEN status = 'Tagged' THEN 1 END) as tagged,
                COUNT(CASE WHEN status = 'Interview' THEN 1 END) as interviews,
                COUNT(CASE WHEN status = 'Offered' THEN 1 END) as offers,
                COUNT(CASE WHEN status = 'Hired' THEN 1 END) as joined
            FROM `tabJob Applicant`
            WHERE owner = %s
            AND creation BETWEEN %s AND %s
        """, (email, month_start, month_end), as_dict=True)
        
        months_data.insert(0, {
            'month': month_start.strftime('%b'),
            **metrics[0]
        })
    
    return months_data



@frappe.whitelist(allow_guest=False)
def get_active_clients(email):
    """Get count of active clients with open positions from ToDo"""
    clients = frappe.db.sql("""
        SELECT DISTINCT custom_company  
        FROM `tabToDo`
        WHERE allocated_to = %s
        AND status = 'Open'
        AND custom_company IS NOT NULL
        AND custom_company != ''
    """, email, as_dict=True)
    
    return clients
