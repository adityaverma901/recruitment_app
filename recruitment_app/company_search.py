import frappe

@frappe.whitelist(allow_guest=False)

def search_company(search_term=None):

    try:
        if not search_term:
            return{
                "status":"error",
                "message":"Please enter company name",
                "data":[]
            }
        
        values=[f"%{search_term}%"]
        query="""
            select
                name,
                company_name,
                email,
                website,
                country
            from `tabCompany`
            WHERE company_name LIKE %s
            ORDER BY company_name
            LIMIT 50
        """
        companies = frappe.db.sql(query,values,as_dict="True")

        return{
            "status":"Success",
            "message":f"Found {len(companies)} companies",
            "data":companies
        }
    except Exception as e:
        return{
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "data": []
        }