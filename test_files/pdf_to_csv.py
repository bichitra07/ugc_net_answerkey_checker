import sys
import os
import csv
import fitz
import re

def pdf_to_csv(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        return

    print(f"Parsing Final Answer Key PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    ans_dict = {}
    
    for page in doc:
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for i in range(len(lines) - 1):
            if re.match(r'^\d{8,15}$', lines[i]):
                q_id = lines[i]
                ans = lines[i+1]
                if not re.match(r'^\d{8,15}$', ans):
                    ans_dict[q_id] = ans
                    
    doc.close()
    
    if not ans_dict:
        print("Error: Could not extract any Answer Keys from the PDF.")
        return
        
    csv_path = os.path.splitext(pdf_path)[0] + ".csv"
    
    print(f"Extracted {len(ans_dict)} questions. Writing to CSV...")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Question ID", "Correct Option"])
        for q_id, ans in ans_dict.items():
            writer.writerow([q_id, ans])
            
    print(f"Success! CSV saved to: {csv_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_csv.py <path_to_final_answerkey_pdf>")
        sys.exit(1)
        
    pdf_to_csv(sys.argv[1])
