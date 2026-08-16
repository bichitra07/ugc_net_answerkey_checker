import streamlit as st
import os
import tempfile

from core.answerkey_parser import read_answerkey, parse_final_pdf_key
from core.pdf_parser import extract_pdf_data
from core.evaluator import evaluate_and_annotate

st.set_page_config(page_title="UGC NET Evaluator", layout="wide", page_icon="📝")

# Inject custom CSS to reduce the huge top padding in the sidebar and main page
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("📝 UGC NET Answer Key Checker")
st.markdown("Instantly evaluate your UGC NET Response Sheet against the official NTA Answer Key.")

st.markdown("""
<div style='color: gray; font-size: 0.9em; margin-bottom: 20px;'>
👨‍💻 Created by <b>Bichitra Panda</b> | 
<a href='https://github.com/bichitra07/ugc_net_answerkey_checker' style='text-decoration: none;'>🔗 GitHub</a> | 
<a href='https://in.linkedin.com/in/bichitra-panda-484124148' style='text-decoration: none;'>🔗 LinkedIn</a>
</div>
""", unsafe_allow_html=True)

# File uploaders
ak_type = st.sidebar.radio("Answer Key Format:", ["Provisional (HTML/CSV)", "Final (PDF)"], horizontal=True)

if ak_type == "Provisional (HTML/CSV)":
    answerkey_file = st.sidebar.file_uploader("Upload Answer Key (HTML or CSV)", type=['html', 'csv'])
else:
    answerkey_file = st.sidebar.file_uploader("Upload Final Answer Key (PDF)", type=['pdf'])

response_pdf = st.sidebar.file_uploader("Upload Response Sheet (PDF)", type=['pdf'])

@st.dialog("ℹ️ How to download the Provisional Answer Key", width="large")
def show_instructions():
    st.markdown("""
    ### Option 1: Save as HTML (Recommended)
    **Step 1:** Log into your NTA UGC NET account.  
    **Step 2:** Navigate to **"Challenge Answer Key"** to open the page containing the table of correct answers.  
    **Step 3:** Save the file:
    - 💻 **On PC/Mac:** Press `Ctrl + S` (or `Cmd + S`) and choose "Save as type: Webpage, HTML Only".
    - 📱 **On Mobile (Android/Chrome):** Tap the 3-dot Menu icon in the top right corner and tap the **Download ⬇️** icon. This saves the page as an HTML file.
    - 🍏 **On Mobile (iOS/Safari):** Tap the Share icon, select Options, choose 'Web Archive', and save to Files.
    
    ---
    
    ### Option 2: The CSV Method
    If downloading the HTML page does not work, you can create a CSV file manually:
    1. Highlight and copy the entire Answer Key table from the NTA website.
    2. Open **Google Sheets**, **MS Excel**, or **LibreOffice Calc**.
    3. Paste the table into a new spreadsheet.
    4. Go to `File -> Download / Save As` and choose **CSV (Comma Separated Values)**.
    """)
    if st.button("Got it!", use_container_width=True):
        st.rerun()

col1, col2 = st.sidebar.columns(2)
if col1.button("ℹ️ Download Provisional Answer Key", use_container_width=True):
    show_instructions()

submit = col2.button("Evaluate Now", type="primary", use_container_width=True)


if submit:
    if not answerkey_file or not response_pdf:
        st.sidebar.error("Please upload both files first!")
    else:
        with st.spinner("Evaluating your responses..."):
            try:
                # Create temporary directory to store files for processing
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save uploaded files temporarily
                    ak_path = os.path.join(temp_dir, answerkey_file.name)
                    pdf_path = os.path.join(temp_dir, response_pdf.name)
                    
                    with open(ak_path, "wb") as f:
                        f.write(answerkey_file.getbuffer())
                    with open(pdf_path, "wb") as f:
                        f.write(response_pdf.getbuffer())
                        
                    # Output path for annotated PDF
                    out_pdf_path = os.path.join(temp_dir, "Evaluated_" + response_pdf.name)
                    
                    # 1. Parse Answer Key
                    if ak_type == "Final (PDF)":
                        ans_dict = parse_final_pdf_key(ak_path)
                    else:
                        ans_dict = read_answerkey(ak_path)
                    
                    # 2. Extract PDF Data
                    pdf_data = extract_pdf_data(pdf_path)
                    
                    # 3. Evaluate and Annotate
                    metrics = evaluate_and_annotate(pdf_data, ans_dict, pdf_path, out_pdf_path)
                    
                    st.success("🎉 Evaluation Complete! Scroll down to download your annotated PDF.")
                    
                    # Display Metrics
                    st.header("📊 Detailed Analysis")
                    
                    tab1, tab2, tab3 = st.tabs(["🏆 Overall Performance", "📄 Paper 1", "📄 Paper 2"])
                    
                    def render_metrics(container, data):
                        total = data['Total']
                        if total == 0:
                            container.info("No questions found for this section.")
                            return
                            
                        correct = data['Correct']
                        incorrect = data['Incorrect']
                        unattempted = data['Unattempted']
                        score = data['Score']
                        percentage = (correct / total) * 100
                        
                        col1, col2, col3, col4 = container.columns(4)
                        col1.metric("🎯 Score", f"{score} / {total*2}", f"{percentage:.2f}%")
                        col2.metric("✅ Correct", correct)
                        col3.metric("❌ Incorrect", incorrect)
                        col4.metric("➖ Unattempted", unattempted)
                        
                        container.progress(percentage / 100)
                        
                    with tab1:
                        render_metrics(st, metrics['Overall'])
                    with tab2:
                        render_metrics(st, metrics['Paper 1'])
                    with tab3:
                        render_metrics(st, metrics['Paper 2'])
                    
                    st.divider()
                    
                    # Provide Download Button for the new PDF
                    with open(out_pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                        
                    st.download_button(
                        label="⬇️ Download Annotated Response Sheet (PDF)",
                        data=pdf_bytes,
                        file_name="Evaluated_" + response_pdf.name,
                        mime="application/pdf",
                        type="primary"
                    )
                    
            except Exception as e:
                import traceback
                st.error(f"An error occurred during evaluation: {str(e)}")
else:
    st.info("👈 Upload your files in the sidebar and click 'Evaluate Now' to get started.")
