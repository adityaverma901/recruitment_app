# import frappe

# @frappe.whitelist(allow_guest=False)
# def search_contacts(search_term=None):
#     """
#     Common contact search by first_name, phone, or email_id from one input field.
#     Args:
#         search_term: string to search (partial match) across name, email, phone
#     Returns:
#         List of matching contacts with emails, phones, and organization
#     """
#     try:
#         if not search_term:
#             return {
#                 "status": "error",
#                 "message": "Please provide a search term",
#                 "data": []
#             }

#         values = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]        # values = ["%john%", "%john%", "%john%"]
#         query = """
#             SELECT
#                 c.name,
#                 c.first_name,
#                 c.last_name,
#                 c.designation,
#                 c.gender,
#                 c.company_name as organization
#             FROM `tabContact` c                                             #tabcontact ko c short name dera
#             WHERE (
#                 c.first_name LIKE %s                                         # c.first_name LIKE "%john%"           -- 1st %s replaced
#                 OR EXISTS (
#                     SELECT 1 FROM `tabContact Email` ce
#                     WHERE ce.parent = c.name AND ce.email_id LIKE %s          
#                 )
#                 OR EXISTS (
#                     SELECT 1 FROM `tabContact Phone` cp
#                     WHERE cp.parent = c.name AND cp.phone LIKE %s                 
#                 )
#             )
#             ORDER BY c.first_name
#             LIMIT 50
#         """

#         contacts = frappe.db.sql(query, values, as_dict=True)

#         # # Fetch emails and phones for each contact and attach
#         # for contact in contacts:
#         #     contact['email_ids'] = frappe.db.sql("""
#         #         SELECT email_id, is_primary FROM `tabContact Email`
#         #         WHERE parent = %s ORDER BY is_primary DESC
#         #     """, contact['name'], as_dict=True)

#         #     contact['phone_nos'] = frappe.db.sql("""
#         #         SELECT phone, is_primary_phone FROM `tabContact Phone`
#         #         WHERE parent = %s ORDER BY is_primary_phone DESC
#         #     """, contact['name'], as_dict=True)
#         for contact in contacts:
#             contact['email_ids'] = frappe.db.sql("""
#                 SELECT email_id, is_primary
#                 FROM `tabContact Email`
#                 WHERE parent = %s
#                 ORDER BY is_primary DESC
#             """, [contact['name']], as_dict=True)   # ✅ fixed

#             contact['phone_nos'] = frappe.db.sql("""
#                 SELECT phone, is_primary_phone
#                 FROM `tabContact Phone`
#                 WHERE parent = %s
#                 ORDER BY is_primary_phone DESC
#             """, [contact['name']], as_dict=True)   # ✅ fixed
#         return {
#             "status": "success",
#             "message": f"Found {len(contacts)} contacts",
#             "data": contacts
#         }

#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"An error occurred: {str(e)}",
#             "data": []
#         }




import frappe

@frappe.whitelist(allow_guest=False)
def search_contacts(search_term=None):
    """
    Common contact search by first_name, phone, or email_id from one input field.
    """
    try:
        if not search_term:
            return {
                "status": "error",
                "message": "Please provide a search term",
                "data": []
            }

        values = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
        query = """
            SELECT
                c.name,
                c.first_name,
                c.last_name,
                c.designation,
                c.gender,
                c.company_name as organization
            FROM `tabContact` c
            WHERE (
                c.first_name LIKE %s
                OR EXISTS (
                    SELECT 1 FROM `tabContact Email` ce
                    WHERE ce.parent = c.name AND ce.email_id LIKE %s
                )
                OR EXISTS (
                    SELECT 1 FROM `tabContact Phone` cp
                    WHERE cp.parent = c.name AND cp.phone LIKE %s
                )
            )
            ORDER BY c.first_name
            LIMIT 50
        """

        contacts = frappe.db.sql(query, values, as_dict=True)

        # Attach emails and phones
        for contact in contacts:
            contact['email_ids'] = frappe.db.sql("""
                SELECT email_id, is_primary
                FROM `tabContact Email`
                WHERE parent = %s
                ORDER BY is_primary DESC
            """, [contact['name']], as_dict=True)   # ✅ fixed

            contact['phone_nos'] = frappe.db.sql("""
                SELECT phone, is_primary_phone
                FROM `tabContact Phone`
                WHERE parent = %s
                ORDER BY is_primary_phone DESC
            """, [contact['name']], as_dict=True)   # ✅ fixed

        return {
            "status": "success",
            "message": f"Found {len(contacts)} contacts",
            "data": contacts
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"0 Contacts found with this ",
            "data": []
        }
