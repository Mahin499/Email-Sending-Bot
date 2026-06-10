import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from email_generator import EmailGenerator
from email_sender import EmailSender
from logger import OutreachLogger

# Load dotenv initially
load_dotenv()

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(
    page_title="The Closer — Cold Email Operator",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR SLEEK MODERN DARK MODE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
    
    /* Font family overrides */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Gradient Main Title */
    .main-title {
        background: linear-gradient(135deg, #a78bfa, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        letter-spacing: -0.05rem;
    }
    
    /* Subtitle styling */
    .subtitle {
        color: #9ca3af;
        font-size: 1.15rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Cards and Containers styling */
    .contact-card {
        background-color: #1e1b4b;
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 5px solid #a78bfa;
        margin-bottom: 1.5rem;
    }
    
    .contact-title {
        color: #f3f4f6;
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
    }
    
    .contact-detail {
        color: #d1d5db;
        font-size: 0.95rem;
        margin-bottom: 0.25rem;
    }

    /* Warning box */
    .warning-card {
        background-color: #7c2d12;
        border-radius: 8px;
        padding: 1rem;
        color: #ffedd5;
        border-left: 4px solid #f97316;
        margin-bottom: 1rem;
    }
    
    /* Stats cards */
    .stat-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 1rem;
        flex: 1;
        text-align: center;
    }
    
    .stat-val {
        font-size: 2rem;
        font-weight: 800;
        color: #a78bfa;
    }
    
    .stat-lbl {
        font-size: 0.85rem;
        color: #9ca3af;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: CONFIGURATION ENGINE ---
st.sidebar.markdown("### ⚙️ Operator Configuration")
st.sidebar.markdown("Configure email settings and safety values below.")

smtp_host = st.sidebar.text_input("SMTP Host", os.getenv("SMTP_HOST", "smtp.gmail.com"))
smtp_port = st.sidebar.text_input("SMTP Port", os.getenv("SMTP_PORT", "587"))
smtp_user = st.sidebar.text_input("Sender Email Address", os.getenv("SMTP_USER", ""))
smtp_pass = st.sidebar.text_input("Sender Password / App Key", os.getenv("SMTP_PASSWORD", ""), type="password")
sender_name = st.sidebar.text_input("Sender Name", os.getenv("SENDER_NAME", "Job Seeker"))

st.sidebar.markdown("---")
dry_run = st.sidebar.toggle("Safety Mode (DRY RUN)", value=True, help="When active, emails/drafts are printed to terminal/GUI without sending.")
use_llm = st.sidebar.toggle("Use Groq LLM Refinement", value=True, help="Refines the tone using Groq Llama-3.1 model.")
groq_api_key = st.sidebar.text_input("Groq API Key", os.getenv("GROQ_API_KEY", ""), type="password")

# Bundle config dictionary
config = {
    "SMTP_HOST": smtp_host,
    "SMTP_PORT": smtp_port,
    "SMTP_USER": smtp_user,
    "SMTP_PASSWORD": smtp_pass,
    "SENDER_NAME": sender_name,
    "DRY_RUN": "true" if dry_run else "false",
    "USE_LLM": "true" if use_llm else "false",
    "GROQ_API_KEY": groq_api_key
}

# --- INITIALIZE SESSION STATE ---
if "contacts" not in st.session_state:
    if os.path.exists("contacts.json"):
        with open("contacts.json", "r", encoding="utf-8") as f:
            st.session_state.contacts = json.load(f)
    else:
        st.session_state.contacts = []

if "curr_idx" not in st.session_state:
    st.session_state.curr_idx = 0

if "stats" not in st.session_state:
    st.session_state.stats = {"sent": 0, "drafted": 0, "skipped": 0, "failed": 0}

# Instantiate components
generator = EmailGenerator(use_llm=use_llm, groq_api_key=groq_api_key)
sender = EmailSender(config)
logger = OutreachLogger()

# --- MAIN APP LAYOUT ---
st.markdown('<div class="main-title">THE CLOSER</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Personalized Cold Outreach Assistant & Send Bot</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["✉️ Outreach Operator", "📥 Targets Manager", "📊 Audit Log Trail"])

# ==========================================
# TAB 1: OUTREACH OPERATOR (THE CORE FLOW)
# ==========================================
with tab1:
    if not st.session_state.contacts:
        st.info("No outreach targets loaded. Please go to the 'Targets Manager' tab to seed or load contacts.")
    elif st.session_state.curr_idx >= len(st.session_state.contacts):
        st.success("🎉 All loaded outreach targets processed!")
        
        # Render Run Summary
        st.markdown("### Outreach Session Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Sent Emails", st.session_state.stats["sent"])
        with col2:
            st.metric("Drafted Emails", st.session_state.stats["drafted"])
        with col3:
            st.metric("Skipped Targets", st.session_state.stats["skipped"])
        with col4:
            st.metric("Failed Attempts", st.session_state.stats["failed"])
            
        if st.button("Restart Session"):
            st.session_state.curr_idx = 0
            st.session_state.stats = {"sent": 0, "drafted": 0, "skipped": 0, "failed": 0}
            st.rerun()
    else:
        curr_idx = st.session_state.curr_idx
        contact = st.session_state.contacts[curr_idx]
        email = contact.get("recipient_email", "").strip()
        company = contact.get("company", "Unknown Company")
        role = contact.get("role", "Unknown Role")
        
        # Display Progress Bar
        total_contacts = len(st.session_state.contacts)
        st.progress((curr_idx) / total_contacts)
        st.markdown(f"**Target {curr_idx + 1} of {total_contacts}**: {company} — {role}")
        
        # De-duplication check warning
        already_contacted = logger.is_already_contacted(email)
        
        col_left, col_right = st.columns([1, 2])
        
        with col_left:
            st.markdown("#### Recipient Details")
            card_html = f"""
            <div class="contact-card">
                <div class="contact-title">{contact.get('recipient_name', 'Hiring Manager')}</div>
                <div class="contact-detail">📧 <b>Email:</b> {email}</div>
                <div class="contact-detail">🏢 <b>Company:</b> {company}</div>
                <div class="contact-detail">💼 <b>Role:</b> {role}</div>
                <div class="contact-detail">🔗 <b>Job URL:</b> <a href="{contact.get('job_url', '#')}" target="_blank">Link</a></div>
                <div class="contact-detail">💡 <b>Personalization:</b> {contact.get('personalization_note', 'None')}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            if already_contacted:
                st.warning("⚠️ **Deduplication Alert**: This email has already been contacted (sent or drafted) according to the audit log trail.")
                
            # Candidate context
            with st.expander("Candidate Background Context"):
                st.markdown(f"**Name:** {contact.get('candidate_name')}")
                st.markdown(f"**Background:** {contact.get('candidate_background')}")
                st.markdown(f"**Portfolio:** {contact.get('portfolio_url')}")
        
        with col_right:
            # Generate email
            with st.spinner("Writing personalized email draft..."):
                # Cache generation inside session state to prevent API calls on rerender
                state_key = f"draft_{curr_idx}"
                if state_key not in st.session_state:
                    try:
                        subj, bdy = generator.generate(contact)
                        st.session_state[state_key] = {"subject": subj, "body": bdy}
                    except Exception as e:
                        st.error(f"Generation failed: {e}")
                        st.session_state[state_key] = {"subject": f"Quick note on the {role} role", "body": ""}
            
            # Form fields for customization
            subject_input = st.text_input("Subject Line", value=st.session_state[state_key]["subject"])
            body_input = st.text_area("Email Body", value=st.session_state[state_key]["body"], height=300)
            
            # Validation warnings
            warnings = generator.validate_email(subject_input, body_input)
            if warnings:
                st.markdown("##### ⚠️ Quality Warnings")
                for w in warnings:
                    st.markdown(f"- {w}")
                st.markdown("")

            # Action confirmation buttons
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
            
            with btn_col1:
                if st.button("📤 Send Email", type="primary", width="stretch"):
                    try:
                        status = sender.send_email(email, subject_input, body_input)
                        logger.log(contact, subject_input, status)
                        st.session_state.stats["sent"] += 1
                        st.toast(f"Email sent successfully to {email}!", icon="➕")
                        st.session_state.curr_idx += 1
                        st.rerun()
                    except Exception as e:
                        logger.log(contact, subject_input, "failed", str(e))
                        st.session_state.stats["failed"] += 1
                        st.error(f"Delivery failed: {e}")
            
            with btn_col2:
                if st.button("📁 Create Draft", width="stretch"):
                    try:
                        status = sender.create_draft(email, subject_input, body_input)
                        logger.log(contact, subject_input, status)
                        st.session_state.stats["drafted"] += 1
                        st.toast(f"Draft successfully created for {email}!", icon="💾")
                        st.session_state.curr_idx += 1
                        st.rerun()
                    except Exception as e:
                        logger.log(contact, subject_input, "failed", str(e))
                        st.session_state.stats["failed"] += 1
                        st.error(f"Draft creation failed: {e}")
            
            with btn_col3:
                if st.button("⏭️ Skip Target", width="stretch"):
                    logger.log(contact, subject_input, "skipped")
                    st.session_state.stats["skipped"] += 1
                    st.session_state.curr_idx += 1
                    st.toast("Skipped outreach target.")
                    st.rerun()
            
            with btn_col4:
                if st.button("🔄 Reset Generation", width="stretch"):
                    if state_key in st.session_state:
                        del st.session_state[state_key]
                    st.rerun()

# ==========================================
# TAB 2: TARGETS MANAGER
# ==========================================
with tab2:
    st.markdown("### Manage Outreach Targets")
    
    # Upload custom CSV/JSON
    uploaded_file = st.file_uploader("Upload contacts file (JSON or CSV)", type=["json", "csv"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".json"):
                new_contacts = json.load(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
                new_contacts = df.to_dict(orient="records")
                
            if isinstance(new_contacts, list):
                st.session_state.contacts = new_contacts
                st.session_state.curr_idx = 0
                st.success(f"Successfully loaded {len(new_contacts)} targets from file!")
                st.rerun()
            else:
                st.error("Invalid file structure. Must represent an array/list of targets.")
        except Exception as e:
            st.error(f"Error parsing file: {e}")
            
    st.markdown("---")
    
    # Current targets display & Editor
    if st.session_state.contacts:
        st.markdown(f"#### Currently Loaded Target Profiles ({len(st.session_state.contacts)} targets)")
        
        # Display as dataframe
        df_display = pd.DataFrame(st.session_state.contacts)
        st.dataframe(df_display, width="stretch")
        
        if st.button("Reset Targets to Default Mock Data"):
            if os.path.exists("contacts.json"):
                with open("contacts.json", "r", encoding="utf-8") as f:
                    st.session_state.contacts = json.load(f)
                st.session_state.curr_idx = 0
                st.success("Targets reset to contacts.json seed entries.")
                st.rerun()
    else:
        st.warning("No targets loaded.")

# ==========================================
# TAB 3: AUDIT LOG TRAIL
# ==========================================
with tab3:
    st.markdown("### Audit Log History (`outreach_log.csv`)")
    st.markdown("An immutable sequence log tracking all outreach actions, skipped targets, and delivery failures.")
    
    log_file = "outreach_log.csv"
    if os.path.exists(log_file):
        try:
            df_logs = pd.read_csv(log_file)
            
            # Show summary metrics
            stat_c1, stat_c2, stat_c3, stat_c4 = st.columns(4)
            with stat_c1:
                st.metric("Total Log entries", len(df_logs))
            with stat_c2:
                sent_cnt = len(df_logs[df_logs["status"] == "sent"])
                st.metric("Delivered", sent_cnt)
            with stat_c3:
                draft_cnt = len(df_logs[df_logs["status"] == "drafted"])
                st.metric("Drafted", draft_cnt)
            with stat_c4:
                fail_cnt = len(df_logs[df_logs["status"] == "failed"])
                st.metric("Failures", fail_cnt)

            st.markdown("---")
            
            # Interactive data table
            st.dataframe(
                df_logs.sort_values(by="timestamp", ascending=False),
                width="stretch"
            )
        except Exception as e:
            st.error(f"Error reading audit log: {e}")
    else:
        st.info("No audit logs found yet. Runs will generate outreach_log.csv automatically.")
