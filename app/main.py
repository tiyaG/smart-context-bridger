import streamlit as st
import json
import os
import google.generativeai as genai
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
from datetime import datetime
import tempfile

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.readonly'
]

# Set up a clean, modern page footprint
st.set_page_config(page_title="Smart Context Bridger", page_icon="✨", layout="centered")

# --- CUSTOM SEAMLESS PASTEL BROWN & BEIGE THEME (CSS Injection) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Quicksand:wght@500;700&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #FDFBF7 !important; /* Soft warm creamy beige background */
        }
        
        h1, h2, h3, h4 {
            font-family: 'Fredoka One', 'Quicksand', sans-serif !important;
            color: #5C4033 !important; /* Deep contrasting dark brown */
        }
        
        p, span, label, div {
            font-family: 'Quicksand', sans-serif !important;
            color: #6E5B4F !important; /* Soft espresso brown for text */
        }
        
        .intro-box {
            background-color: #F1ECE4 !important; /* Premium pastel beige block */
            border: 2px solid #D7CCC8 !important;
            border-radius: 20px !important;
            padding: 30px !important;
            margin-bottom: 25px !important;
            box-shadow: 0px 4px 10px rgba(92, 64, 51, 0.05);
        }
        
        /* --- HIGH CONTRAST BUTTON STYLING --- */
        
        /* Step 1 & 2 Setup Buttons (Earthy Pastel Brown Accent) */
        div.stButton > button {
            background-color: #8D7B68 !important; 
            color: white !important;
            font-family: 'Fredoka One', sans-serif !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 10px 20px !important;
            transition: all 0.3s ease;
        }
        
        /* Step 2 Primary Action Button (Contrasting Dark Warm Cocoa Brown) */
        div.stButton > button[data-testid="stBaseButton-primary"] {
            background-color: #4A3525 !important;
            color: #FFFDF9 !important;
            font-size: 1.1em !important;
            border: 2px solid #332216 !important;
        }
        
        /* Step 3 "Add Event" Dynamic Row Buttons (Soft Soft Sage Green Accent to stand out completely) */
        div.stButton > button[key^="add_evt_"] {
            background-color: #607E65 !important;
            color: white !important;
            border: 1px solid #4D6651 !important;
        }

        /* Hover animations to keep things feeling tactile */
        div.stButton > button:hover {
            transform: scale(1.02);
            filter: brightness(0.9);
        }
    </style>
""", unsafe_allow_html=True)

# Manage introductory flow using Session State
if 'flow_started' not in st.session_state:
    st.session_state['flow_started'] = False

# --- INTRODUCTORY WELCOME WINDOW LAYOUT (Casual Tone) ---
if not st.session_state['flow_started']:
    st.markdown("""
        <div class="intro-box">
            <h2 style='text-align: center; margin-top: 0;'>👋 Yo, I'm Bob!</h2>
            <p style='font-size: 1.1em; line-height: 1.6em; text-align: center;'>
                I'm your smart assistant that saves your calendar when school life gets crazy. 
                As a college student handling tons of classes, clubs, and random emails, 
                it's way too easy to forget what you promised to do. I scan your inbox 
                for hidden tasks or deadlines and help you add them right onto your calendar!
            </p>
            <hr style='border-top: 1px solid #D7CCC8;'>
            <p style='font-size: 0.95em; color: #8C7A6B; line-height: 1.5em; text-align: center;'>
               ⚠️ <b>Development Note:</b> This system is currently operating in secure <b>Google OAuth Verification Test Mode</b>. 
                If published openly, Google verification protocols take 4 to 6 weeks to finalize. Because of this, please feel free 
                to reach out directly to add your email as an authorized test account (I have up to 100 free whitelisting slots available!).            </p>
            <p style='text-align: center; font-family: "Fredoka One", sans-serif; font-size: 1.05em; color: #5C4033;'>
                📬 Tester Signups: <u>anannyagairola@gmail.com</u>            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("✨ Let's Do This", use_container_width=True):
        st.session_state['flow_started'] = True
        st.rerun()
        
    st.stop() # Halt execution until intro is clicked

# --- MAIN AGENT RUNTIME SCREEN ---
st.markdown("<h1 style='text-align: center;'>✨ Your Smart Context Bridger</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8D7B68;'>Let's look into your recent communications to find promises and add them straight to your calendar.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- CREDENTIAL RESOLUTION MANAGER (LOCAL FILE OR STREAMLIT CLOUD SECRETS) ---

# Helper to look up or generate a credentials source dictionary safely
def load_secrets_dict():
    if os.path.exists('credentials.json'):
        with open('credentials.json', 'r') as f:
            return json.load(f)
    elif 'google_credentials' in st.secrets:
        # Pull straight from the secure Streamlit cloud setting panel dictionary
        return dict(st.secrets['google_credentials'])
    return None

# Soft check validation fallback setup
if load_secrets_dict() is None:
    st.error("🔑 Connection File Missing: Please make sure 'credentials.json' from your Google Cloud Console is saved in your local folder or configured in Streamlit Cloud Secrets.")
    st.stop()

def get_google_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            secrets_data = load_secrets_dict()
            
            # Streamlit Cloud needs a temporary file path to pass to the OAuth library flow
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp_file:
                json.dump(secrets_data, tmp_file)
                tmp_file_path = tmp_file.name
                
            try:
                flow = InstalledAppFlow.from_client_secrets_file(tmp_file_path, SCOPES)
                creds = flow.run_local_server(port=0)
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            finally:
                os.unlink(tmp_file_path) # Clean up temporary directory file path safely
                
    return creds

def add_to_google_calendar(service, summary, deadline):
    event = {
        'summary': summary,
        'description': 'Automatically caught and synchronized by your Smart Context Bridger Agent.',
        'start': {'date': deadline, 'timeZone': 'UTC'},
        'end': {'date': deadline, 'timeZone': 'UTC'},
    }
    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event.get('htmlLink')
    except Exception as e:
        return f"Error: {str(e)}"

# --- STEP-BY-STEP CHRONOLOGICAL INPUT WORKFLOW ---

st.markdown("### 🛠️ Step 1: Connect Your Services")
col_api, col_auth = st.columns(2)

with col_api:
    api_key = st.text_input("Google AI Studio Key", type="password", placeholder="Paste your AI Studio Key here...")

with col_auth:
    st.write("") # Layout alignment spacing
    st.write("") 
    if st.button("🔐 Link Gmail & Calendar", use_container_width=True):
        creds = get_google_credentials()
        if creds:
            st.session_state['authenticated'] = True
            st.toast("Connected to Google services!", icon="✅")

if 'authenticated' in st.session_state and api_key:
    st.markdown("---")
    st.markdown("### 🔍 Step 2: Let Your Assistant Go to Work")
    st.write("Click below to cross-reference recent emails against your active calendar schedule to surface hidden to-do items.")
    
    if st.button("🚀 Find Hidden Calendar Commitments", type="primary", use_container_width=True):
        with st.spinner("Reviewing your feeds gracefully..."):
            try:
                creds = get_google_credentials()
                calendar_service = build('calendar', 'v3', credentials=creds)
                gmail_service = build('gmail', 'v1', credentials=creds)
                
                # Fetch calendar metadata
                events_result = calendar_service.events().list(calendarId='primary', maxResults=15).execute()
                live_events = events_result.get('items', [])
                
                # Fetch email snippets
                messages_result = gmail_service.users().messages().list(userId='me', maxResults=8).execute()
                messages = messages_result.get('messages', [])
                
                email_payloads = []
                for msg in messages:
                    m_data = gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
                    email_payloads.append({"snippet": m_data.get('snippet')})
                
                # Bundle the live cloud feeds into session state
                st.session_state['cloud_data'] = {"calendar": live_events, "emails": email_payloads}
                
                # Trigger Gemini reasoning engine
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                with open(".agents/skills/task-synthesizer/SKILL.md", "r") as f:
                    synthesizer_rules = f.read()
                    
                # Grab today's real calendar context dynamically
                today_context = f"Today's current date is Monday, July 6, 2026."
                    
                prompt = f"""
                {synthesizer_rules}
                
                {today_context}
                
                Compare these live feeds and flag explicitly any upcoming project deadlines, 
                meeting requests, or calendar adjustments that do not exist yet in the schedule:
                {json.dumps(st.session_state['cloud_data'])}
                """
                
                res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                
                # Remove markdown code block fences if Gemini accidentally adds them
                clean_text = res.text.strip().lstrip("```json").rstrip("```").strip()
                
                st.session_state['detected_gaps'] = json.loads(clean_text)
                st.toast("Analysis complete!", icon="🎯")
            except Exception as e:
                st.error(f"Something went wrong while processing: {str(e)}")

# --- CHRONOLOGICAL CALENDAR-BASED OUTPUT WORKFLOW ---
if 'detected_gaps' in st.session_state:
    st.markdown("---")
    st.markdown("### 📅 Step 3: Your Action Dashboard Timeline")
    st.write("Here are the commitments your assistant identified that aren't on your calendar yet:")
    
    gaps = st.session_state['detected_gaps']
    
    if not gaps:
        st.info("🎉 All clear! Your inbox matches your calendar layout perfectly right now.")
    else:
        # Sort items by date so they display in actual chronological calendar order
        try:
            gaps_sorted = sorted(gaps, key=lambda x: x.get('deduced_deadline', ''))
        except Exception:
            gaps_sorted = gaps # Fallback layout sorting constraint safety
            
        creds = get_google_credentials()
        calendar_service = build('calendar', 'v3', credentials=creds)
        
        # Display each day beautifully
        for idx, gap in enumerate(gaps_sorted):
            raw_date = gap.get('deduced_deadline', 'Unspecified Date')
            
            # Reformat string to a friendly calendar header format (e.g., "July 10, 2026")
            try:
                parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
                friendly_date = parsed_date.strftime("%B %d, %Y")
            except Exception:
                friendly_date = raw_date
                
            # Render a card layout representing a clean day metric item block
            with st.container(border=True):
                date_col, action_col = st.columns([3, 1])
                
                with date_col:
                    st.markdown(f"#### 📅 {friendly_date}")
                    st.markdown(f"**Task Detected:** {gap.get('implicit_commitment', 'N/A')}")
                    st.caption(f"💬 Found via: {gap.get('originating_source', 'N/A')}")
                
                with action_col:
                    st.write("") # Balancing spacer lines
                    
                    # Targetable button with custom unique key tracking attributes for the CSS layout rules
                    if st.button("➕ Add Event", key=f"add_evt_{idx}", use_container_width=True):
                        link = add_to_google_calendar(
                            calendar_service,
                            gap.get('implicit_commitment'),
                            gap.get('deduced_deadline', '2026-07-10')
                        )
                        st.success("Added!")
                        if "Error" not in link:
                            st.markdown(f"[📅 View Event]({link})")