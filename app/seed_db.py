import sqlite3

def init_and_seed_db():
    # This automatically creates a database file named 'workspace.db' in your project root
    conn = sqlite3.connect('workspace.db')
    cursor = conn.cursor()
    
    # 1. Create a table for Calendar Events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary TEXT,
            attendees TEXT,
            event_date TEXT
        )
    ''')
    
    # 2. Create a table for Emails
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            subject TEXT,
            body TEXT,
            received_date TEXT
        )
    ''')
    
    # Clear out any stale testing data to keep everything clean
    cursor.execute("DELETE FROM calendar_events")
    cursor.execute("DELETE FROM emails")
    
    # 3. Seed live rows directly into the tables
    cursor.execute("""
        INSERT INTO calendar_events (summary, attendees, event_date) VALUES 
        ('Project Delta UX Review', 'sarah.design@company.com, mark.pm@company.com', '2026-07-04'),
        ('Backend Architecture Alignment', 'john.eng@company.com', '2026-07-05')
    """)
    
    cursor.execute("""
        INSERT INTO emails (sender, subject, body, received_date) VALUES 
        ('sarah.design@company.com', 'Re: Project Delta UX Review', 
         'Great sync today! I will update the design mockups in Figma and share the links with you by Wednesday morning. Also, please check if my corporate card ending in 4111-2222-3333-4444 went through for the software license.', '2026-07-04'),
        ('john.eng@company.com', 'Lunch next week?', 
         'Hey, we should grab lunch sometime soon. Let me know when you are free.', '2026-07-05')
    """)
    
    conn.commit()
    conn.close()
    print("🚀 SQLite 'workspace.db' initialized and seeded successfully!")

if __name__ == '__main__':
    init_and_seed_db()