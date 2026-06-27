"""
AI Guardian OS - Main Application
Unified workflow for responsible AI assessment
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime
import json
import time
from workflow_pipeline import WorkflowPipeline

# Configure Streamlit
st.set_page_config(
    page_title="AI Guardian OS - Workflow",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Session State Initialization ====================
if 'pipeline_executed' not in st.session_state:
    st.session_state.pipeline_executed = False
if 'pipeline_results' not in st.session_state:
    st.session_state.pipeline_results = None
if 'uploaded_df' not in st.session_state:
    st.session_state.uploaded_df = None

# ==================== Custom CSS ====================
st.markdown("""
<style>
    .stage-container {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid;
    }
    .stage-passed {
        background-color: #d4edda;
        border-left-color: #28a745;
    }
    .stage-warning {
        background-color: #fff3cd;
        border-left-color: #ffc107;
    }
    .stage-failed {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }
    .score-excellent {
        color: #28a745;
        font-weight: bold;
        font-size: 24px;
    }
    .score-good {
        color: #17a2b8;
        font-weight: bold;
        font-size: 24px;
    }
    .score-fair {
        color: #ffc107;
        font-weight: bold;
        font-size: 24px;
    }
    .score-poor {
        color: #dc3545;
        font-weight: bold;
        font-size: 24px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== Header ====================
st.markdown("""
<div style="font-size: 2.5em; font-weight: bold; color: #2c3e50; margin-bottom: 10px;">🛡️ AI Guardian OS - Unified Workflow Pipeline</div>
<p style="font-size: 1.1em; color: #555;">End-to-End Responsible AI Assessment Platform</p>
""", unsafe_allow_html=True)

st.divider()

# ==================== Sidebar ====================
with st.sidebar:
    st.title("🛡️ Pipeline Control")
    st.markdown("### Workflow Status")
    
    if st.session_state.pipeline_executed:
        st.success("✅ Pipeline Executed")
        if st.session_state.pipeline_results:
            st.metric("AI Trust Score", f"{st.session_state.pipeline_results.total_score:.1f}/100")
            st.metric("Can Deploy", "Yes ✅" if st.session_state.pipeline_results.can_deploy else "No ❌")
    else:
        st.info("⏳ Awaiting dataset upload")

# ==================== Main Content ====================
# Workflow Diagram
with st.expander("📊 Workflow Pipeline Diagram", expanded=False):
    st.markdown("""
    ```
    1️⃣  Upload Dataset (max 1GB)
            ↓
    2️⃣  Data Quality Analysis
            ↓
    3️⃣  Fairness Audit
            ↓
    4️⃣  Privacy Scan
            ↓
    5️⃣  Explainability Analysis
            ↓
    6️⃣  Risk Assessment
            ↓
    7️⃣  Compliance Check
            ↓
    8️⃣  AI Trust Score Calculation
            ↓
    9️⃣  Deployment Decision
    ```
    """)

# ==================== Stage 1: Upload Dataset ====================
st.markdown("## 1️⃣ Upload Dataset")
st.markdown("*Upload files up to 1GB in CSV, Parquet, Excel, or JSON format*")

col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'parquet', 'xlsx', 'json'],
        help="Supported formats: CSV, Parquet, Excel, JSON (Max 1GB)"
    )

with col2:
    file_info = st.empty()

if uploaded_file is not None:
    try:
        # Validate file size
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        if file_size_mb > 1024:
            st.error(f"❌ File too large: {file_size_mb:.2f}MB (Max: 1024MB)")
        else:
            # Load data
            file_ext = Path(uploaded_file.name).suffix.lower()
            
            try:
                if file_ext == '.csv':
                    df = pd.read_csv(uploaded_file)
                elif file_ext == '.parquet':
                    df = pd.read_parquet(uploaded_file)
                elif file_ext == '.xlsx':
                    df = pd.read_excel(uploaded_file)
                elif file_ext == '.json':
                    df = pd.read_json(uploaded_file)
                
                st.session_state.uploaded_df = df
                file_info.metric("File Size", f"{file_size_mb:.2f} MB")
                
                st.success(f"✅ File loaded successfully: {uploaded_file.name}")
                
                # Display data preview
                with st.expander("📋 Data Preview", expanded=False):
                    col_prev1, col_prev2 = st.columns(2)
                    with col_prev1:
                        st.write(f"**Rows:** {df.shape[0]}")
                        st.write(f"**Columns:** {df.shape[1]}")
                    with col_prev2:
                        st.write(f"**Memory Usage:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                    
                    st.dataframe(df.head(10), use_container_width=True)
                
                st.divider()
                
                # ==================== Execute Pipeline ====================
                if st.button("▶️ Execute Full Pipeline", key="execute_pipeline", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_placeholder = st.empty()
                    results_container = st.container()
                    
                    pipeline = WorkflowPipeline()
                    stages = [
                        ("Data Quality Analysis", 1/9),
                        ("Fairness Audit", 2/9),
                        ("Privacy Scan", 3/9),
                        ("Explainability", 4/9),
                        ("Risk Assessment", 5/9),
                        ("Compliance Check", 6/9),
                        ("AI Trust Score", 7/9),
                        ("Deployment Decision", 8/9),
                    ]
                    
                    with results_container:
                        st.markdown("### 🔄 Pipeline Execution Progress")
                        
                        for idx, (stage_name, progress_val) in enumerate(stages):
                            status_placeholder.info(f"🔄 Processing: {stage_name}...")
                            progress_bar.progress(progress_val)
                            time.sleep(0.3)
                        
                        # Execute pipeline
                        report = pipeline.execute(df)
                        st.session_state.pipeline_results = report
                        st.session_state.pipeline_executed = True
                        
                        progress_bar.progress(1.0)
                        status_placeholder.success("✅ Pipeline Execution Complete!")
                    
                    st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ==================== Results Section ====================
if st.session_state.pipeline_executed and st.session_state.pipeline_results:
    st.divider()
    st.markdown("## 📊 Pipeline Results")
    
    report = st.session_state.pipeline_results
    
    # Overall Score Display
    col1, col2, col3, col4 = st.columns(4)
    
    trust_score = report.total_score
    with col1:
        if trust_score >= 90:
            score_class = "score-excellent"
            emoji = "🟢"
        elif trust_score >= 80:
            score_class = "score-good"
            emoji = "🟡"
        elif trust_score >= 70:
            score_class = "score-fair"
            emoji = "🟠"
        else:
            score_class = "score-poor"
            emoji = "🔴"
        
        st.markdown(f"<div class='{score_class}'>AI Trust Score<br>{emoji} {trust_score:.1f}/100</div>", unsafe_allow_html=True)
    
    with col2:
        deployment_status = "✅ APPROVED" if report.can_deploy else "❌ NOT APPROVED"
        st.metric("Deployment Status", deployment_status)
    
    with col3:
        stages_passed = sum(1 for r in report.stages if r.status.value.startswith("✅"))
        st.metric("Stages Passed", f"{stages_passed}/{len(report.stages)}")
    
    with col4:
        total_duration = sum(r.duration_seconds for r in report.stages)
        st.metric("Total Duration", f"{total_duration:.2f}s")
    
    st.divider()
    
    # Detailed Results by Stage
    st.markdown("### 📋 Stage-by-Stage Results")
    
    tabs = st.tabs([f"{i+1}. {r.stage.value.split()[0]}" for i, r in enumerate(report.stages)])
    
    for tab_idx, (tab, result) in enumerate(zip(tabs, report.stages)):
        with tab:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### {result.stage.value}")
                st.markdown(f"**Status:** {result.status.value}")
            
            with col2:
                st.metric("Score", f"{result.score:.1f}/100")
            
            with col3:
                st.metric("Duration", f"{result.duration_seconds:.2f}s")
            
            st.divider()
            
            # Stage Details
            if result.details:
                st.markdown("**Details:**")
                
                for key, value in result.details.items():
                    if isinstance(value, (list, dict)):
                        st.json(value)
                    else:
                        st.write(f"- **{key}:** {value}")
    
    st.divider()
    
    # Final Recommendation
    st.markdown("### 🎯 Final Recommendation")
    
    if report.can_deploy:
        st.success(f"### {report.recommendation}")
        st.markdown("""
        ✅ This AI system is **approved for deployment**
        
        **Next Steps:**
        1. Conduct final manual review
        2. Set up monitoring dashboards
        3. Establish feedback loops
        4. Document model lineage
        """)
    else:
        st.error(f"### {report.recommendation}")
        st.markdown("""
        ❌ This AI system is **NOT recommended for deployment**
        
        **Remediation Steps:**
        1. Address failing compliance areas
        2. Improve data quality
        3. Mitigate identified risks
        4. Re-run assessment after fixes
        """)
    
    st.divider()
    
    # Download Results
    st.markdown("### 📥 Export Results")
    
    # Generate JSON report
    report_json = {
        "timestamp": report.timestamp.isoformat(),
        "total_score": report.total_score,
        "can_deploy": report.can_deploy,
        "recommendation": report.recommendation,
        "stages": [
            {
                "stage": r.stage.value,
                "status": r.status.value,
                "score": r.score,
                "details": r.details,
                "duration_seconds": r.duration_seconds,
            }
            for r in report.stages
        ]
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📄 Download JSON Report",
            data=json.dumps(report_json, indent=2),
            file_name=f"ai_guardian_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        if st.session_state.uploaded_df is not None:
            csv = st.session_state.uploaded_df.to_csv(index=False)
            st.download_button(
                label="📊 Download Analyzed Dataset",
                data=csv,
                file_name=f"analyzed_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# ==================== Footer ====================
st.divider()
st.markdown("""
---
**AI Guardian OS** | Responsible AI Assessment Platform
- Built with ❤️ for Responsible AI
- Privacy-First | Compliance-Focused | Transparent
""")
