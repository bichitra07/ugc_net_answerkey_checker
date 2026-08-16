import streamlit as st
import os
import tempfile

from core.answerkey_parser import read_answerkey
from core.pdf_parser import extract_pdf_data
from core.evaluator import evaluate_and_annotate

st.set_page_config(page_title="UGC NET Evaluator", layout="centered", page_icon="📝")

st.title("📝 UGC NET Answer Key Checker")
st.markdown("Instantly evaluate your UGC NET Response Sheet against the official NTA Answer Key.")

# File uploaders
st.sidebar.header("1. Upload Files")
answerkey_file = st.sidebar.file_uploader("Upload Answer Key (HTML or CSV)", type=['html', 'csv'])
response_pdf = st.sidebar.file_uploader("Upload Response Sheet (PDF)", type=['pdf'])

if st.sidebar.button("Evaluate Now", type="primary"):
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
                    ans_dict = read_answerkey(ak_path)
                    
                    # 2. Extract PDF Data
                    pdf_data = extract_pdf_data(pdf_path)
                    
                    # 3. Evaluate and Annotate
                    metrics = evaluate_and_annotate(pdf_data, ans_dict, pdf_path, out_pdf_path)
                    
                    st.success("Evaluation Complete!")
                    
                    # Display Metrics
                    st.header("📊 Evaluation Results")
                    col1, col2, col3, col4 = st.columns(4)
                    mo = metrics['Overall']
                    col1.metric("Total Questions", mo['Total'])
                    col2.metric("Correct", mo['Correct'])
                    col3.metric("Incorrect", mo['Incorrect'])
                    col4.metric("Total Score", f"{mo['Score']} / {mo['Total']*2}")
                    
                    # Provide Download Button for the new PDF
                    with open(out_pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                        
                    st.download_button(
                        label="📄 Download Annotated Response Sheet",
                        data=pdf_bytes,
                        file_name="Evaluated_" + response_pdf.name,
                        mime="application/pdf"
                    )
                    
            except Exception as e:
                st.error(f"An error occurred during evaluation: {str(e)}")
else:
    st.info("👈 Upload your files in the sidebar and click 'Evaluate Now' to get started.")
