import re
import fitz  # PyMuPDF

def extract_pdf_data(pdf_path):
    """
    Extracts question blocks from the PDF using PyMuPDF.
    Returns a list of dictionaries containing:
    {
        'Question ID': str,
        'Chosen Option': str (or None),
        'Options': list of str (length 4) or [],
        'Page': int
    }
    """
    doc = fitz.open(pdf_path)
    
    question_id_pattern = r'Question ID\s*(?:\s*:\s*)?(\d+)'
    status_pattern = r'Status\s*(?:\s*:\s*)*(.*)'
    chosen_option_pattern = r'Chosen Option\s*(?:\s*:\s*)?(\S+)'
    
    opt1_pattern = r'Option 1 ID\s*(?:\s*:\s*)?(\d+)'
    opt2_pattern = r'Option 2 ID\s*(?:\s*:\s*)?(\d+)'
    opt3_pattern = r'Option 3 ID\s*(?:\s*:\s*)?(\d+)'
    opt4_pattern = r'Option 4 ID\s*(?:\s*:\s*)?(\d+)'
    
    results = []
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        
        # Split text into chunks that start with "Question ID"
        blocks = re.split(r'(?=Question ID)', text)
        
        for block in blocks:
            if 'Question ID' not in block:
                continue
                
            q_id_match = re.search(question_id_pattern, block)
            if not q_id_match:
                continue
            q_id = q_id_match.group(1).strip()
            
            status_match = re.search(status_pattern, block)
            status = status_match.group(1).strip() if status_match else ''
            
            chosen_opt_match = re.search(chosen_option_pattern, block)
            chosen_opt_raw = chosen_opt_match.group(1).strip() if chosen_opt_match else ''
            
            # Clean Chosen Option (must be 1, 2, 3, or 4)
            chosen_option = None
            if 'Not Answered' not in status and chosen_opt_raw:
                digits = re.sub(r'\D', '', chosen_opt_raw)
                if len(digits) > 0 and digits[0] in {'1', '2', '3', '4'}:
                    chosen_option = digits[0]
                    
            # Try to extract the 4 Option IDs from the block (if they exist)
            options = []
            opt1_match = re.search(opt1_pattern, block)
            opt2_match = re.search(opt2_pattern, block)
            opt3_match = re.search(opt3_pattern, block)
            opt4_match = re.search(opt4_pattern, block)
            
            if opt1_match and opt2_match and opt3_match and opt4_match:
                options = [
                    opt1_match.group(1).strip(),
                    opt2_match.group(1).strip(),
                    opt3_match.group(1).strip(),
                    opt4_match.group(1).strip()
                ]
                
            results.append({
                'Question ID': q_id,
                'Chosen Option': chosen_option,
                'Options': options,
                'Page': page_num
            })
            
    doc.close()
    return results
