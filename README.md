# UGC-NET AnswerKey Checker

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)

A professional, extremely fast, and robust tool for students to automatically evaluate their UGC NET response sheets against the official NTA Answer Keys.

## Highlights
- **Lightning Fast Evaluation**: Processes a standard 100-page response sheet in less than 1 second.
- **No OCR Required**: Natively extracts text and Option IDs from the digital PDF using PyMuPDF. No heavy image processing or Tesseract installations required.
- **Native PDF Annotations**: Automatically outputs an evaluated copy of your PDF (`_evaluated.pdf`) with ✅ Correct and ❌ Incorrect annotations directly on the questions, along with a top-level scorecard.
- **Smart Answer Key Parser**: Supports uploading both HTML (saved directly from the portal) or CSV answer keys. The system natively uses the PDF Option IDs, requiring zero manual key normalization.

## Prerequisites

- Python 3.10 or above

## Instructions

1. Open your terminal or command prompt.
2. Clone the repository:
   ```bash
   git clone https://github.com/bichitra07/ugc_net_answerkey_checker.git
   ```
3. Change into the newly created directory:
   ```bash
   cd ugc_net_answerkey_checker
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the graphical user interface (GUI) or the command-line interface (CLI):
   ```bash
   python run_gui.py
   # OR
   python main.py <answer_key_path> <response_pdf_path>
   ```

## Process Instructions

1. **Select AnswerKey File**: Select either the downloaded HTML file from the NTA portal or a generated CSV. 
2. **Select Response PDF**: Select your downloaded NTA response sheet PDF.
3. **Evaluate**: Click the "Evaluate" button. 
4. **View Results**: The tool will instantly evaluate your performance and save a brand new PDF (e.g. `ResponseSheet_evaluated.pdf`) in the same folder as your original PDF. Open it to see your scorecard and question-by-question annotations!

## How to get the Answer Key

1. Log into the [UGC-NET Official Site](https://ugcnet.nta.ac.in/).
2. Navigate to the Answer Key challenge page.
3. Simply press `Ctrl + S` (or right-click -> Save As) to save the webpage as an `.html` file. You can directly upload this HTML file into the tool!
*(Alternatively, you can copy the table to a Google Sheet and save as CSV).*

## Download Response Sheet PDF

Download your response sheet PDF from the [NTA website](https://ugcnet.nta.ac.in/).
Ensure you are using the "Save as PDF" option from your browser print menu, ensuring the text is selectable.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
