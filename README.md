```markdown
# UGC-NET AnswerKey Checker

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

3. After cloning, change into the newly created directory:
```bash
cd ugc_net_answerkey_checker
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Run `main.py` for CLI or `ui.py` for GUI.

## Process Instructions

1. **Select AnswerKey CSV File**: It will ask you to input a CSV file of the answer key. The CSV should have two columns: `Question ID` and `Answer`.

2. **Select Response PDF**: You will be prompted to select the answer key CSV and response PDF. By default, it will read the Computer Science answer key. You can change it by clicking the button.

3. **Evaluate**: Click the "Evaluate" button to start the evaluation process (for GUI). For CLI, it  will automatically evaluate the response.

4. **Save Results**: After evaluation, you can save the results to a CSV file and complete analysis report to txt file (for GUI). For CLI, it will automatically save the results. Results will be saved in the `results` folder where the script ruuns with same name as the response PDF.

## How to Make Answer Key CSV

1. Copy the table content of the answer key from [https://ugcnet.nta.ac.in/](https://ugcnet.nta.ac.in/) by logging in with your details.
2. Paste it into a Google Sheet and download it as a CSV. Note: Currently, the answer key for Computer Science and Applications is provided. [Note: Login closed]

## Download Response Sheet PDF

Download your response sheet PDF from the NTA website. [Note: Login closed]


## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
```
