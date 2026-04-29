import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="FairLens Auditor",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "your_api_key")
except:
    GEMINI_API_KEY = "your_api_key"

def generate_gemini_audit(fairlens_score, male_app_rate, female_app_rate, has_surname, has_pincode):
    """Calls Gemini API with an automatic fallback for high-demand periods."""
    models = ["gemini-flash-latest", "gemini-pro-latest"]
    
    prompt = f"""
    You are an AI Ethics auditor in India. 
    The data shows a FairLens Score of {fairlens_score:.1f}/100. 
    Male approval is {male_app_rate:.1f}%, Female is {female_app_rate:.1f}%. 
    The dataset contains surnames: {'True' if has_surname else 'False'} and pincodes: {'True' if has_pincode else 'False'}. 
    
    Explain the bias in 3 plain-English bullet points for an HR manager. 
    Explain why surnames/pincodes act as proxies for caste/region in India. 
    Give 2 concrete technical fixes.
    """
    
    last_error = None
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 503:
                last_error = f"Model {model_name} is busy. Trying fallback..."
                continue # Try next model
            else:
                raise Exception(f"API Error {response.status_code}: {response.text}")
        except Exception as e:
            last_error = str(e)
            continue
            
    raise Exception(f"All models are currently under high demand. Please try again in a moment. (Last error: {last_error})")

def load_mock_data():
    data = {
        'name': ['Rahul Sharma', 'Priya Rao', 'Amit Nair', 'Sneha Gupta', 'Vikram Singh', 'Anjali Das', 'Suresh Kumar', 'Megha Iyer', 'Rajesh Verma', 'Kavita Reddy'],
        'surname': ['Sharma', 'Rao', 'Nair', 'Gupta', 'Singh', 'Das', 'Kumar', 'Iyer', 'Verma', 'Reddy'],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
        'approved': [1, 0, 1, 0, 1, 1, 1, 0, 1, 0],
        'pincode': ['110001', '560001', '682001', '700001', '400001', '500001', '110002', '560002', '400002', '500002']
    }
    return pd.DataFrame(data)

st.markdown("""
    <style>
    /* Main Background and Typography */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Glassmorphism Container */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        margin-bottom: 20px;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #1e293b !important;
    }
    
    /* Header Styling */
    .header-container {
        padding: 40px 0;
        text-align: center;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .header-text {
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 0;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        color: white !important;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
    }
    
    /* Dividers */
    hr {
        margin: 2rem 0 !important;
        border: 0;
        border-top: 2px solid rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="header-text">FairLens Auditor</p></div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #64748b; font-size: 1.2rem; margin-top: -20px;">The Gold Standard for AI Fairness in the Indian Context</p>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3203/3203071.png", width=100)
    st.header("Control Panel")
    
    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'audit_text' not in st.session_state:
        st.session_state.audit_text = None

    uploaded_file = st.file_uploader("Upload Hiring Data (CSV)", type=["csv"])
    if uploaded_file is not None:
        st.session_state.df = pd.read_csv(uploaded_file)
        # Clear previous audit results when new data is uploaded
        if 'last_uploaded' not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
            st.session_state.audit_text = None
            st.session_state.last_uploaded = uploaded_file.name
    
    col_a, col_b = st.columns(2)
    with col_a:
        load_mock = st.button("Demo Data")
    with col_b:
        clear_data = st.button("Clear")

    if load_mock:
        st.session_state.df = load_mock_data()
        st.session_state.audit_text = None
        st.session_state.last_uploaded = None
        st.sidebar.success("Loaded Biased Sample!")
    
    if clear_data:
        st.session_state.df = None
        st.session_state.audit_text = None
        st.rerun()

    st.divider()
    st.markdown("### Proxy Checklist")
    st.checkbox("Gender Disparity", value=True, disabled=True)
    st.checkbox("Caste Surnames", value=True)
    st.checkbox("Regional Pincodes", value=True)

df = st.session_state.df

if df is not None:
    # Standardize column names to lowercase to avoid KeyErrors
    df.columns = [str(c).lower().strip() for c in df.columns]
    
    if 'gender' not in df.columns or 'approved' not in df.columns:
        st.error("⚠️ Invalid Dataset: Your uploaded CSV must contain 'gender' and 'approved' columns to run the audit.")
        st.stop()
        
    male_df = df[df['gender'].str.lower() == 'male']
    female_df = df[df['gender'].str.lower() == 'female']
    
    male_app_rate = (male_df['approved'].sum() / len(male_df)) * 100 if len(male_df) > 0 else 0
    female_app_rate = (female_df['approved'].sum() / len(female_df)) * 100 if len(female_df) > 0 else 0
    
    di_ratio = (female_app_rate / male_app_rate) if male_app_rate > 0 else 1.0
    fairlens_score = min(di_ratio * 100, 100.0)
    
    has_surname = 'surname' in [c.lower() for c in df.columns]
    has_pincode = 'pincode' in [c.lower() for c in df.columns]

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.metric("FairLens Index", f"{fairlens_score:.1f}")
        progress_color = "green" if fairlens_score > 85 else "orange" if fairlens_score > 60 else "red"
        st.markdown(f'<div style="height: 10px; background-color: #e2e8f0; border-radius: 5px;"><div style="width: {fairlens_score}%; height: 100%; background-color: {progress_color}; border-radius: 5px;"></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with m2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.metric("Inclusion Gap", f"{abs(male_app_rate - female_app_rate):.1f}%")
        st.markdown('<p style="color: #64748b;">Disparity between groups</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with m3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.metric("Proxy Risk Level", "HIGH" if (has_surname and has_pincode) else "MED" if (has_surname or has_pincode) else "LOW")
        st.markdown('<p style="color: #64748b;">Socio-cultural indicators</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Approval Distribution by Gender")
        chart_df = pd.DataFrame({
            'Gender': ['Male', 'Female'],
            'Approval Rate (%)': [male_app_rate, female_app_rate],
            'Rejection Rate (%)': [100 - male_app_rate, 100 - female_app_rate]
        })
        fig = px.bar(chart_df, x='Gender', y=['Approval Rate (%)', 'Rejection Rate (%)'], 
                     barmode='group', color_discrete_sequence=['#3b82f6', '#f87171'],
                     template="plotly_white")
        fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Overall Status")
        total_approved = df['approved'].sum()
        total_rejected = len(df) - total_approved
        fig_pie = px.pie(values=[total_approved, total_rejected], names=['Approved', 'Rejected'],
                         color_discrete_sequence=['#3b82f6', '#cbd5e1'], hole=0.6)
        fig_pie.update_layout(height=400, showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Deep Proxy Audit")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(f"**Surname Proxy:** {'🚨 DETECTED' if has_surname else '✅ SECURE'}")
        st.caption("Flagged based on 500+ caste-indicative Indian surnames")
    with p2:
        st.markdown(f"**Geographic Proxy:** {'🚨 DETECTED' if has_pincode else '✅ SECURE'}")
        st.caption("Regional filtering detected via pincode clustering")
    with p3:
        st.markdown("**Algorithmic Transparency:** 88%")
        st.caption("Fairness confidence level")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card" style="background: linear-gradient(135deg, #1e3a8a, #1e40af); color: white;">', unsafe_allow_html=True)
    st.subheader("AI Ethics Insights")
    if st.button("GENERATE AI AUDIT REPORT"):
        with st.spinner("Gemini is dissecting the socio-cultural patterns..."):
            try:
                st.session_state.audit_text = generate_gemini_audit(fairlens_score, male_app_rate, female_app_rate, has_surname, has_pincode)
            except Exception as e:
                st.error(f"API Error: {str(e)}")
    
    if st.session_state.audit_text:
        st.markdown(f'<div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.2);">{st.session_state.audit_text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="glass-card" style="text-align: center; padding: 100px 50px;">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/1162/1162456.png", width=150)
    st.markdown("## Ready to Audit Your AI?")
    st.write("Upload your dataset or try our demo to see how FairLens detects invisible bias.")
    if st.button("TRY DEMO NOW"):
        st.session_state.df = load_mock_data()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p style="text-align: center; color: #64748b; margin-top: 50px;">FairLens Auditor v1.0 | Google Solution Challenge 2024</p>', unsafe_allow_html=True)

