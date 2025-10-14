# File: your_app/your_app/tasks.py

import frappe
import requests
from frappe.utils import now_datetime, getdate, get_first_day, formatdate
import json

def daily_api_data_sync():
    """
    Fetch data from custom API and save to Daily Dashboard Logs DocType
    This function will be called by the scheduled job at 11:59 PM daily
    """
    try:
        # Your API endpoint
        api_url = "https://recruiter.gennextit.com/api/method/recruitment_app.daily_dashboard_metric.get_daily_dashboard_data"
        
        # Make API request
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        # Parse response data
        api_response = response.json()
        api_data = api_response.get("message", {})
        
        # Extract date and metrics
        date = api_data.get("date")
        metrics = api_data.get("metrics", {})
        
        if not date or not metrics:
            frappe.log_error(
                title="Daily API Sync - Invalid Data",
                message=f"Missing date or metrics in API response: {json.dumps(api_data, indent=2)}"
            )
            return
        
        # Save to DocType
        save_daily_dashboard_log(date, metrics)
        
        # Log success
        frappe.logger().info(f"Daily Dashboard Log synced successfully for {date}")
        
    except requests.exceptions.RequestException as e:
        # Log API request errors
        frappe.log_error(
            title="Daily API Sync - Request Failed",
            message=f"Error fetching data from API: {str(e)}"
        )
    except Exception as e:
        # Log any other errors
        frappe.log_error(
            title="Daily API Sync - Error",
            message=f"Error during sync: {str(e)}\n{frappe.get_traceback()}"
        )

def save_daily_dashboard_log(date, metrics):
    """
    Save daily metrics to Daily Dashboard Logs DocType
    Creates a new monthly record if doesn't exist, or updates existing one
    """
    try:
        # Convert date string to date object
        log_date = getdate(date)
        
        # Get month name and year (e.g., "January 2025")
        month_name = log_date.strftime("%B")  # Full month name
        year = log_date.year
        month_doc_name = f"{month_name} {year}"  # e.g., "October 2025"
        
        # Check if monthly record exists
        if frappe.db.exists("Daily dashboard log", month_doc_name):
            # Get existing document
            doc = frappe.get_doc("Daily dashboard log", month_doc_name)
            
            # Check if entry for this date already exists in child table
            existing_log = None
            for log in doc.logs:
                if getdate(log.date) == log_date:
                    existing_log = log
                    break
            
            if existing_log:
                # Update existing log
                existing_log.active_clients_counts = str(metrics.get("active_clients", 0))
                existing_log.total_open_roles = str(metrics.get("total_open_roles", 0))
                existing_log.interviews_completed_count = str(metrics.get("interviews_completed", 0))
                existing_log.offers_accepted_count = str(metrics.get("offers_accepted", 0))
                existing_log.joiners_count = str(metrics.get("joiners", 0))
            else:
                # Add new log entry
                doc.append("logs", {
                    "date": date,
                    "active_clients_counts": str(metrics.get("active_clients", 0)),
                    "total_open_roles": str(metrics.get("total_open_roles", 0)),
                    "interviews_completed_count": str(metrics.get("interviews_completed", 0)),
                    "offers_accepted_count": str(metrics.get("offers_accepted", 0)),
                    "joiners_count": str(metrics.get("joiners", 0))
                })
            
            # Save the document
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            
            frappe.logger().info(f"Updated existing monthly log: {month_doc_name} for date: {date}")
            
        else:
            # Create new monthly document
            doc = frappe.get_doc({
                "doctype": "Daily dashboard log",
                "month": month_doc_name,
                "logs": [{
                    "date": date,
                    "active_clients_counts": str(metrics.get("active_clients", 0)),
                    "total_open_roles": str(metrics.get("total_open_roles", 0)),
                    "interviews_completed_count": str(metrics.get("interviews_completed", 0)),
                    "offers_accepted_count": str(metrics.get("offers_accepted", 0)),
                    "joiners_count": str(metrics.get("joiners", 0))
                }]
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
            frappe.logger().info(f"Created new monthly log: {month_doc_name} for date: {date}")
        
    except Exception as e:
        frappe.log_error(
            title="Error saving to Daily Dashboard Logs",
            message=f"Error: {str(e)}\nDate: {date}\nMetrics: {json.dumps(metrics, indent=2)}\n{frappe.get_traceback()}"
        )
        raise