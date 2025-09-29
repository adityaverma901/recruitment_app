# in job_applicant.py (custom app)
import frappe
from frappe import _

def validate_job_applicant(doc, method):
    if doc.email_id and doc.job_title:
        existing = frappe.get_list(
            "Job Applicant",
            filters={
                "email_id": doc.email_id,
                "job_title": doc.job_title,
                "name": ["!=", doc.name]
            },
            fields=["name", "applicant_name"]
        )
        if existing:
            frappe.throw(_("This email has already applied for this job opening. Existing applicant: {0}").format(existing[0].applicant_name))
