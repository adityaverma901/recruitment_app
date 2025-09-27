import frappe

@frappe.whitelist(allow_guest=False)
def search_designation(search_term=None):
    try:
        # Check if search_term is provided
        if not search_term:
            return {
                "status": "error",
                "message": "Please enter the Designation name",
                "data": []
            }

        # Prepare the search parameter
        search_param = f"%{search_term}%"
        
        # Updated query - make sure table name and field name are correct
        query = """
            SELECT 
                name,
                designation_name,
                description
            FROM `tabDesignation`
            WHERE designation_name LIKE %s
            ORDER BY designation_name
            LIMIT 20
        """

        # Execute the query
        designations = frappe.db.sql(query, (search_param,), as_dict=True)
        
        return {
            "status": "success",
            "message": f"Found {len(designations)} designations",
            "data": designations
        }

    except Exception as e:
        frappe.log_error(f"Error in search_designation API: {str(e)}")
        return {
            "status": "error", 
            "message": f"An error occurred: {str(e)}",
            "data": []
        }
