import argparse
import sys
import os

from core.answerkey_parser import read_answerkey
from core.pdf_parser import extract_pdf_data
from core.evaluator import evaluate_and_annotate

def main():
    parser = argparse.ArgumentParser(description="UGC NET Answer Key Checker CLI")
    parser.add_argument("answerkey", help="Path to the Answer Key (CSV or HTML)")
    parser.add_argument("pdf", help="Path to the candidate's Response Sheet PDF")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.answerkey):
        print(f"Error: Answer key file not found: {args.answerkey}")
        sys.exit(1)
        
    if not os.path.exists(args.pdf):
        print(f"Error: PDF file not found: {args.pdf}")
        sys.exit(1)
        
    try:
        print("1. Parsing Answer Key...")
        ans_dict = read_answerkey(args.answerkey)
        
        print("2. Parsing Response PDF using PyMuPDF...")
        pdf_data = extract_pdf_data(args.pdf)
        
        print("3. Evaluating and Annotating...")
        output_pdf_path = os.path.splitext(args.pdf)[0] + "_evaluated.pdf"
        metrics = evaluate_and_annotate(pdf_data, ans_dict, args.pdf, output_pdf_path)
        
        print("\n=== EVALUATION RESULTS ===")
        print(f"Total Questions: {metrics['Overall']['Total']}")
        print(f"Correct: {metrics['Overall']['Correct']}")
        print(f"Incorrect: {metrics['Overall']['Incorrect']}")
        print(f"Unattempted: {metrics['Overall']['Unattempted']}")
        print(f"Total Score: {metrics['Overall']['Score']}")
        
        print(f"\nAnnotated PDF saved to: {output_pdf_path}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Fatal error during execution: {e}")

if __name__ == "__main__":
    main()
