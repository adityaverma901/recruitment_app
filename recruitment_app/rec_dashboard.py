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
