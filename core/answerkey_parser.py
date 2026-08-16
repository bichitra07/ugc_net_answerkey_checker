import os
import pandas as pd
from bs4 import BeautifulSoup
import io

def parse_html_table(html_path):
    """
    Parses the HTML Answer Key, finds the relevant table,
    and returns a DataFrame.
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    dfs = pd.read_html(io.StringIO(str(soup)))
    
    best_df = None
    q_col_idx = None
    a_col_idx = None
    
    for df in dfs:
        if df.shape[1] < 2:
            continue
            
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        cols = [str(c).lower() for c in df.columns]
        
        q_idx = -1
        a_idx = -1
        
        for i, col in enumerate(cols):
            if 'question id' in col or 'question no' in col:
                q_idx = i
            elif 'correct option' in col or 'answer' in col:
                a_idx = i
                
        if q_idx == -1 and df.shape[0] > 0:
            first_row = [str(x).lower() for x in df.iloc[0].values]
            for i, val in enumerate(first_row):
                if 'question id' in val or 'question no' in val:
                    q_idx = i
                elif 'correct option' in val or 'answer' in val:
                    a_idx = i
                    
        if q_idx != -1 and a_idx != -1:
            best_df = df
            q_col_idx = df.columns[q_idx]
            a_col_idx = df.columns[a_idx]
            break
            
    if best_df is None:
        raise ValueError("Could not find a valid Answer Key table containing Question IDs in the HTML file.")
        
    df = best_df
    
    # Filter out interleaved rows that happen when NTA nests tables
    df = df[df.iloc[:, 0].astype(str).str.len() < 5]
    
    return df, q_col_idx, a_col_idx

def read_answerkey(file_path):
    """
    Reads an Answer Key from CSV or HTML.
    If HTML, saves it as a CSV in the same directory.
    Returns a dictionary mapping: Question ID (str) -> Correct Option (str)
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.html':
        df, q_col_idx, a_col_idx = parse_html_table(file_path)
        
        # Save as CSV in the same folder
        csv_out_path = os.path.splitext(file_path)[0] + "_extracted.csv"
        df.to_csv(csv_out_path, index=False)
        print(f"Extracted HTML table saved to {csv_out_path}")
        
    elif ext == '.csv':
        df = pd.read_csv(file_path)
        if df.shape[1] < 2:
            raise ValueError("CSV must have at least 2 columns")
            
        # Try to identify columns by name, fallback to first and second columns
        cols = [str(c).lower() for c in df.columns]
        q_idx, a_idx = 0, 1
        for i, col in enumerate(cols):
            if 'question id' in col or 'question no' in col:
                q_idx = i
            elif 'correct option' in col or 'answer' in col:
                a_idx = i
                
        q_col_idx = df.columns[q_idx]
        a_col_idx = df.columns[a_idx]
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    # Convert mapping to string for safe comparison
    # We drop NAs to avoid parsing empty rows
    mapping = df.dropna(subset=[q_col_idx, a_col_idx])
    
    ans_dict = {}
    for _, row in mapping.iterrows():
        # Ensure we strip decimals if read as float (e.g. 5512.0 -> '5512')
        q_id = str(row[q_col_idx]).strip()
        if q_id.endswith('.0'):
            q_id = q_id[:-2]
            
        a_id = str(row[a_col_idx]).strip()
        if a_id.endswith('.0'):
            a_id = a_id[:-2]
            
        ans_dict[q_id] = a_id
        
    return ans_dict

def parse_final_pdf_key(pdf_path):
    """
    Parses the NTA Final Answer Key (PDF format).
    Extracts Question IDs and their Correct Option numbers using Regex.
    Returns a dictionary mapping: Question ID (str) -> Correct Option (str)
    """
    import fitz
    import re
    
    doc = fitz.open(pdf_path)
    ans_dict = {}
    
    for page in doc:
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for i in range(len(lines) - 1):
            # Check if current line is a Question ID (e.g., 8-15 digit number)
            if re.match(r'^\d{8,15}$', lines[i]):
                # The next line is the correct option index (e.g., 1, 2, 3, 4, or DROP)
                q_id = lines[i]
                ans = lines[i+1]
                
                # Basic sanity check to ensure the next line isn't another long Question ID
                if not re.match(r'^\d{8,15}$', ans):
                    ans_dict[q_id] = ans
                    
    doc.close()
    
    if not ans_dict:
        raise ValueError("Could not extract any Answer Keys from the PDF. Ensure it is a valid digital Final Answer Key.")
        
    return ans_dict
