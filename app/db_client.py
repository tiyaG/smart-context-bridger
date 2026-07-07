import sqlite3

def fetch_workspace_records():
    """
    Connects to our physical SQLite database file, queries the rows,
    and returns a structured data collection for our processing pipeline.
    """
    conn = sqlite3.connect('workspace.db')
    cursor = conn.cursor()
    
    # Fetch calendar items
    cursor.execute("SELECT summary, attendees, event_date FROM calendar_events")
    calendar_rows = cursor.fetchall()
    calendar_list = [{"summary": row[0], "attendees": row[1], "date": row[2]} for row in calendar_rows]
    
    # Fetch email items
    cursor.execute("SELECT sender, subject, body, received_date FROM emails")
    email_rows = cursor.fetchall()
    email_list = [{"from": row[0], "subject": row[1], "body": row[2], "date": row[3]} for row in email_rows]
    
    conn.close()
    return {"calendar": calendar_list, "emails": email_list}
