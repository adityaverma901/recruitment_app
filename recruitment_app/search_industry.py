# import frappe
# @frappe.whitelist(allow_guest=False)
# def search_industry_type(search_term=None):
#     try:
#         if not search_term:
#             return{
#                 "status":"error",
#                 "message":"Please enter the Industry name",
#                 "data":[]
#             }
#         values=[f"{search_term}"]
#         query="""
#         select 
#         industry 
#         from `tabIndustry Type`
#         WHERE industry like %s
# """
#         industries=frappe.db.sql(query,values,as_dict="True")
#         return{
#             "status":"Success",
#             "message":f"Found {len(industries)} companies",
#             "data":industries
#         }
#     except Exception as e:
#         return{
#             "status": "error",
#             "message": f"An error occurred: {str(e)}",
#             "data": []
#         }


import frappe

@frappe.whitelist(allow_guest=False)
def search_industry_type(search_term=None):
    try:
        if not search_term:
            return {
                "status": "error",
                "message": "Please enter the Industry name",
                "data": []
            }

        values = [f"%{search_term}%"]
        query = """
        select 
            industry 
        from `tabIndustry Type`
        WHERE industry like %s
        """

        industries = frappe.db.sql(query, values, as_dict=True)
        return {
            "status": "Success",
            "message": f"Found {len(industries)} companies",
            "data": industries
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "data": []
        }
