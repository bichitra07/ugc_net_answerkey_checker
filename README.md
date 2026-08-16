# UGC-NET AnswerKey Checker

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)

A professional, extremely fast, and robust tool for students to automatically evaluate their UGC NET response sheets against the official NTA Answer Keys.

## Highlights
- **Lightning Fast Evaluation**: Processes a standard 100-page response sheet in less than 1 second.
- **No OCR Required**: Natively extracts text and Option IDs from the digital PDF using PyMuPDF. No heavy image processing required.
- **Native PDF Annotations**: Automatically outputs an evaluated copy of your PDF (`_evaluated.pdf`) with ✅ Correct and ❌ Incorrect annotations directly on the questions, along with a top-level scorecard.
- **Smart Answer Key Parser**: Supports uploading both HTML (saved directly from the portal) or CSV answer keys. The system natively uses the PDF Option IDs, requiring zero manual key normalization.
- **Web App & Docker**: Includes a sleek Streamlit Web Application and Docker Compose configuration for easy hosting locally or on the internet via Ngrok.

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

### Option 1: Save as HTML (Recommended)
1. Log into your NTA UGC NET account.
2. Navigate to **"Challenge Answer Key"** to open the page containing the table of correct answers.
3. Save the file:
   - 💻 **On PC/Mac:** Press `Ctrl + S` (or `Cmd + S`) and choose "Save as type: Webpage, HTML Only".
   - 📱 **On Mobile (Android/Chrome):** Tap the 3-dot Menu icon in the top right corner and tap the **Download ⬇️** icon. This saves the page as an HTML file.
   - 🍏 **On Mobile (iOS/Safari):** Tap the Share icon, select Options, choose 'Web Archive', and save to Files.

### Option 2: The CSV Method
If downloading the HTML page does not work, you can create a CSV file manually:
1. Highlight and copy the entire Answer Key table from the NTA website.
2. Open **Google Sheets**, **MS Excel**, or **LibreOffice Calc**.
3. Paste the table into a new spreadsheet.
4. Go to `File -> Download / Save As` and choose **CSV (Comma Separated Values)**.

## Download Response Sheet PDF

Download your response sheet PDF from the [NTA website](https://ugcnet.nta.ac.in/).
Ensure you are using the "Save as PDF" option from your browser print menu, ensuring the text is selectable.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
