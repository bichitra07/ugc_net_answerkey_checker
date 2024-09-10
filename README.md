# UGC-NET AnswerKey Checker

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Build Status](https://img.shields.io/github/actions/workflow/status/yourusername/ugc_net_answerkey_checker/ci.yml?branch=main)
![Coverage](https://img.shields.io/codecov/c/github/bichitr07/ugc_net_answerkey_checker)


## Prerequisites

- Python 3.10 or above

### Install Poppler Utilities

#### For Linux (Ubuntu)
```bash
sudo apt-get install poppler-utils
```

#### For Windows
1. Download Poppler utilities from [here](https://github.com/oschwartz10612/poppler-windows/releases/).
2. Extract the contents inside the `C://` directory.

### Install Tesseract-OCR

#### For Linux
```bash
sudo apt-get install tesseract-ocr
```

#### For Windows
1. Download the Tesseract-OCR setup file from [here](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install it.

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
5. Run `main.py` for the command-line interface (CLI) or `ui.py` for the graphical user interface (GUI).

## Process Instructions

1. **Select AnswerKey CSV File**: You will be prompted to input a CSV file containing the answer key. The CSV should have two columns: `Question ID` and `Answer`.
2. **Select Response PDF**: Select the response PDF. By default, it will evaluate the Computer Science answer key. You can change the subject by selecting a different CSV or PDF.
3. **Evaluate**: In the GUI, click the "Evaluate" button to start the evaluation process. In the CLI, it will evaluate automatically once the files are selected.
4. **Save Results**: After evaluation, you can save the results to a CSV file and the detailed analysis report to a text file. Results will be saved in the `results` folder with the same name as the response PDF.

## How to Make the Answer Key CSV

1. Copy the table contents of the answer key from [UGC-NET Official Site](https://ugcnet.nta.ac.in/) after logging in.
2. Paste the content into a Google Sheet and download it as a CSV.  
   *Note: The answer key for Computer Science and Applications is used by default.*

## Download Response Sheet PDF

Download your response sheet PDF from the [NTA website](https://ugcnet.nta.ac.in/).  
*Note: Login required. [Currently, Login is closed.]*

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
```
