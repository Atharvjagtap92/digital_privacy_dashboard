# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from datetime import datetime

# ---------------------------------------
# 🎯 PAGE CONFIGURATION
# ---------------------------------------
st.set_page_config(
    page_title="Digital Footprints & Privacy Awareness",
    page_icon="🔒",
    layout="wide"
)

# ---------------------------------------
# 🎨 PROFESSIONAL CYBER-THEME STYLING
# ---------------------------------------
st.markdown("""
<style>
body {
    background-color: #f7f9fb;
    font-family: 'Poppins', sans-serif;
}
.banner {
    background: linear-gradient(135deg, #0d1b2a, #1b263b, #415a77);
    color: white;
    text-align: center;
    padding: 1.8rem;
    border-radius: 15px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.banner img {
    width: 120px;
    margin-bottom: 10px;
    border-radius: 10px;
}
.info-card {
    border-radius: 12px;
    background: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    padding: 1rem;
    text-align: center;
}
.tip-card {
    background: #eaf1f9;
    border-left: 5px solid #1b263b;
    padding: 0.9rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    font-size: 15px;
}
.download-section {
    background: white;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.04);
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# 🌐 HEADER WITH CYBER IMAGE (Online)
# ---------------------------------------
st.markdown("""
<div class="banner">
    <img src="https://cdn-icons-png.flaticon.com/512/3075/3075977.png" alt="cyber awareness"/>
    <h1>🔒 Digital Footprints & Privacy Awareness</h1>
    <p style="margin:0">Interactive Dashboard — Insights, Visuals & Awareness</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------
# 📊 LOAD DATA
# ---------------------------------------
DATA_FILE = "digital_privacy_data.csv"
if not os.path.exists(DATA_FILE):
    st.error(f"Data file not found: {DATA_FILE}. Put your CSV in the app folder.")
    st.stop()

data = pd.read_csv(DATA_FILE)

# Detect date column (optional)
date_col = None
for c in data.columns:
    if 'date' in c.lower():
        date_col = c
        try:
            data[date_col] = pd.to_datetime(data[date_col])
        except:
            date_col = None
        break

# ---------------------------------------
# 🧭 SIDEBAR FILTERS
# ---------------------------------------
st.sidebar.header("🔍 Filters & Options")
age_filter = st.sidebar.multiselect("Select Age Group", options=sorted(data["Age_Group"].unique()))
platform_filter = st.sidebar.multiselect("Select Platform", options=sorted(data["Platform"].unique()))

if date_col:
    min_date = data[date_col].min()
    max_date = data[date_col].max()
    date_range = st.sidebar.date_input("Select date range", value=(min_date.date(), max_date.date()))
else:
    date_range = None

filtered = data.copy()
if age_filter:
    filtered = filtered[filtered["Age_Group"].isin(age_filter)]
if platform_filter:
    filtered = filtered[filtered["Platform"].isin(platform_filter)]
if date_col and date_range:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered[date_col] >= start) & (filtered[date_col] <= end)]

# ---------------------------------------
# 🗂 TABS
# ---------------------------------------
tab_dashboard, tab_tips, tab_about = st.tabs(["📊 Dashboard", "💡 Tips", "📘 About & Feedback"])

# ---------------------------------------
# 📊 DASHBOARD TAB
# ---------------------------------------
with tab_dashboard:
    st.markdown("### Quick Insights")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records", len(filtered))
    c2.metric("Avg Time (hrs/day)", round(filtered["Time_Spent (hrs/day)"].mean(), 2))
    c3.metric("Avg Data Shared (%)", round(filtered["Data_Shared (%)"].mean(), 2))
    c4.metric("Avg Awareness (0-5)", round(filtered["Awareness_Level"].mean(), 2))
    st.divider()

    # 📈 Charts
    st.subheader("📊 Data Shared by Platform")
    fig_bar = px.bar(
        filtered.groupby("Platform", as_index=False)["Data_Shared (%)"].mean(),
        x="Platform", y="Data_Shared (%)",
        title="Average Data Shared per Platform",
        color="Platform"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("📉 Awareness vs Time Spent")
    fig_scatter = px.scatter(
        filtered,
        x="Time_Spent (hrs/day)",
        y="Awareness_Level",
        color="Platform",
        size="Data_Shared (%)",
        hover_data=["Privacy_Tools_Used"],
        title="Time Spent vs Awareness Level"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("🔐 Privacy Tools Adoption")
    fig_pie = px.pie(filtered, names="Privacy_Tools_Used", title="Privacy Tools Usage Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)

    # Awareness Gauge
    st.subheader("📈 Overall Awareness Score")
    avg_awareness = round(filtered["Awareness_Level"].mean(), 2)
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_awareness if not pd.isna(avg_awareness) else 0,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Awareness (0-5)"},
        gauge={
            'axis': {'range': [0, 5]},
            'bar': {'color': "#1b263b"},
            'steps': [
                {'range': [0, 2], 'color': "#fee2e2"},
                {'range': [2, 3.5], 'color': "#fde68a"},
                {'range': [3.5, 5], 'color': "#bbf7d0"}
            ]
        }
    ))
    st.plotly_chart(gauge, use_container_width=True)

    # Leaderboard
    st.subheader("🏆 Platforms by Awareness Level")
    lb = filtered.groupby("Platform", as_index=False)["Awareness_Level"].mean().sort_values(by="Awareness_Level", ascending=False)
    lb["Awareness_Level"] = lb["Awareness_Level"].round(2)
    st.dataframe(lb.reset_index(drop=True), use_container_width=True)

    # Downloads
    st.divider()
    st.subheader("⬇️ Downloads")

    col_a, col_b = st.columns(2)
    csv_bytes = filtered.to_csv(index=False).encode('utf-8')
    with col_a:
        st.download_button(
            "💾 Download Filtered Data (CSV)",
            data=csv_bytes,
            file_name=f"filtered_privacy_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

    def generate_pdf_bytes(df: pd.DataFrame) -> BytesIO:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setTitle("Digital Privacy Summary")
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(150, 750, "Digital Privacy Summary Report")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, 720, f"Records: {len(df)}")
        pdf.drawString(50, 700, f"Avg Time Spent: {round(df['Time_Spent (hrs/day)'].mean(),2)} hrs/day")
        pdf.drawString(50, 680, f"Avg Data Shared: {round(df['Data_Shared (%)'].mean(),2)} %")
        pdf.drawString(50, 660, f"Avg Awareness: {round(df['Awareness_Level'].mean(),2)} / 5")
        pdf.line(50, 640, 550, 640)
        pdf.setFont("Helvetica", 11)
        pdf.drawString(50, 620, "Top Platforms by Awareness:")
        top = lb.head(5)
        y = 600
        for _, row in top.iterrows():
            pdf.drawString(60, y, f"{row['Platform']}: {row['Awareness_Level']}")
            y -= 16
        pdf.drawString(50, 120, "Generated by Atharv Jagtap— Digital Privacy Dashboard")
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer

    with col_b:
        pdf_buffer = generate_pdf_bytes(filtered)
        st.download_button(
            "📘 Download Summary (PDF)",
            data=pdf_buffer,
            file_name=f"privacy_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf"
        )

# ---------------------------------------
# 💡 TIPS TAB
# ---------------------------------------
with tab_tips:
    st.subheader("Practical Privacy Tips")
    st.markdown("""
    <div class="tip-card">🔑 Use strong, unique passwords for every account.</div>
    <div class="tip-card">🧱 Enable Two-Factor Authentication (2FA) wherever possible.</div>
    <div class="tip-card">📵 Avoid clicking on unknown links or attachments.</div>
    <div class="tip-card">🌐 Use VPNs on public Wi-Fi networks.</div>
    <div class="tip-card">🔍 Regularly review app permissions on your devices.</div>
    <div class="tip-card">🚫 Don't overshare personal information online.</div>
    """, unsafe_allow_html=True)

# ---------------------------------------
# 📘 ABOUT TAB
# ---------------------------------------
with tab_about:
    st.subheader("About this Project")
    st.info("""
    **Project:** Digital Footprints & Privacy Awareness Dashboard  
    **Developer:** Atharv  
    **Purpose:** Visualize digital habits and promote cyber awareness.  
    **Tech Stack:** Streamlit, Pandas, Plotly, ReportLab
    """)

    st.divider()
    st.subheader("Feedback / Notes")
    feedback = st.text_area("Share feedback or suggestions:", height=120)

    if st.button("Submit Feedback"):
        if feedback.strip() == "":
            st.warning("Please write something before submitting.")
        else:
            fb_file = "feedback.csv"
            row = {"timestamp": datetime.now().isoformat(), "feedback": feedback}
            if os.path.exists(fb_file):
                df_fb = pd.read_csv(fb_file)
                df_fb = pd.concat([df_fb, pd.DataFrame([row])], ignore_index=True)
            else:
                df_fb = pd.DataFrame([row])
            df_fb.to_csv(fb_file, index=False)
            st.success("✅ Thanks! Your feedback was saved.")
