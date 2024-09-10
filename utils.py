import pandas as pd
from PIL import Image
from pdf2image import convert_from_path
import numpy as np
import cv2
import re
import pytesseract
import tkinter as tk
from tkinter import filedialog

import platform
import os

def find_poppler_and_tesseract_paths():
    base_dir = r'C:\\'
    poppler_path = None
    tesseract_path = None
    
    for root, dirs, files in os.walk(base_dir):
        # Check for Poppler directory
        for dir_name in dirs:
            if dir_name.lower().startswith('poppler'):
                potential_poppler_path = os.path.join(root, dir_name, 'Library', 'bin')
                if os.path.isdir(potential_poppler_path):
                    poppler_path = potential_poppler_path

        # Check for tesseract.exe
        for file_name in files:
            if file_name.lower() == 'tesseract.exe':
                tesseract_path = os.path.join(root, file_name)

        # Exit early if both paths are found
        if poppler_path and tesseract_path:
            break

    return poppler_path, tesseract_path

def setup_os_specific_paths():
    system = platform.system()

    if system == "Windows":
        print("Setting up paths for Windows.")
        
        poppler_path, tesseract_path = find_poppler_and_tesseract_paths()
        # Path to Tesseract executable
        
        if not os.path.exists(tesseract_path):
            raise FileNotFoundError(f"Tesseract executable not found at {tesseract_path}. Please install Tesseract.")
        print(f"Tesseract found at {tesseract_path}.")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Find and set Poppler path
        if poppler_path:
            print(f"Poppler found at {poppler_path}.")
            os.environ['PATH'] += os.pathsep + poppler_path
        else:
            raise FileNotFoundError("Poppler utilities not found. Please install Poppler.")

    elif system == "Linux":
        print("Setting up paths for Linux.")
        # No additional setup required for Poppler on Linux
        if os.system("which tesseract") != 0:
            print("Tesseract is not installed. Use 'sudo apt-get install tesseract-ocr'.")
        if os.system("which pdftoppm") != 0:
            print("Poppler is not installed. Use 'sudo apt-get install poppler-utils'.")

    else:
        raise OSError("Unsupported operating system.")

def select_csv():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    root.destroy()
    if not file_path:
        raise FileNotFoundError("No file selected.")
    return file_path

def select_pdf():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    root.destroy()
    if not file_path:
        raise FileNotFoundError("No file selected.")
    return file_path

def read_csv(csv_path, ret='dict'):
    df = pd.read_csv(csv_path)
    if ret == 'dict':
        return df.set_index(df.columns[0])[df.columns[1]].to_dict()
    elif ret == 'df':
        return df
    else:
        raise ValueError("Invalid value for ret. Choose 'df' or 'dict'.")

def pdf_to_images(pdf_path):
    pil_images = convert_from_path(pdf_path)
    cv_images = [cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR) for pil_image in pil_images]
    return cv_images

def select_crop_point(original_image):
    if original_image is None:
        raise FileNotFoundError("Original image not found or cannot be loaded.")
    original_height, original_width = original_image.shape[:2]
    resized_dimensions = (1080, 720)
    resized_image = cv2.resize(original_image, resized_dimensions)
    point = None
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            nonlocal point
            point = (x, y)
            cv2.destroyAllWindows()
    cv2.namedWindow('Select Point')
    cv2.setMouseCallback('Select Point', mouse_callback)
    cv2.imshow('Select Point', resized_image)
    cv2.waitKey(0)
    if point is None:
        raise ValueError("No point selected.")
    x_resized, y_resized = point
    x_original = int(x_resized * original_width / resized_dimensions[0])
    y_original = int(y_resized * original_height / resized_dimensions[1])
    return (x_original, y_original)

def crop_image_from_point(image, point):
    x, y = point
    height, width, _ = image.shape
    if x < width and y < height:
        return image[:, x:width, :]
    else:
        raise ValueError("Point is outside the image dimensions.")

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 11)
    return cv2.bitwise_not(thresh)

def extract_lines(data):
    words = [{'text': data['text'][i], 'top': data['top'][i], 'height': data['height'][i], 'bottom': data['top'][i] + data['height'][i], 'left': data['left'][i]} for i in range(len(data['text']))]
    words.sort(key=lambda x: x['top'])
    lines, current_line = [], []
    for word in words:
        if not current_line:
            current_line.append(word)
        else:
            last_word = current_line[-1]
            overlap = min(word['bottom'], last_word['bottom']) - max(word['top'], last_word['top'])
            overlap_percent = overlap / min(word['height'], last_word['height'])
            if overlap_percent >= 0.6:
                current_line.append(word)
            else:
                current_line.sort(key=lambda w: w['left'])
                line_text = " ".join([w['text'] for w in current_line if w['text'].strip() != ''])
                if line_text:
                    lines.append(line_text)
                current_line = [word]
    if current_line:
        current_line.sort(key=lambda w: w['left'])
        line_text = " ".join([w['text'] for w in current_line if w['text'].strip() != ''])
        if line_text:
            lines.append(line_text)
    return '\n'.join(lines)

def extract_response_blocks(text, ret='dict'):

    def clean_chosen_option(option):
        # Remove non-digit characters
        digits = re.sub(r'\D', '', option)
        if len(digits) == 0:
            return None
        elif len(digits) == 1:
            # Single digit
            if digits in {'1', '2', '3', '4'}:
                return digits
            else:
                return None
        elif len(digits) == 2:
            # Two digits
            first_digit = digits[0]
            second_digit = digits[1]
            if first_digit in {'1', '2', '3', '4'}:
                return int(first_digit)
            elif second_digit in {'1', '2', '3', '4'}:
                return int(second_digit)
            else:
                return None
        return None
    # Regular expressions
    question_id_pattern = r'Question ID\s*(?:\s*:\s*)?(\d+)'
    status_pattern = r'Status\s*(?:\s*:\s*)?(Answered|Not Answered)'
    chosen_option_pattern = r'Chosen Option\s*(?:\s*:\s*)?(\S+)'

    # Find all matches
    question_ids = re.findall(question_id_pattern, text)
    statuses = re.findall(status_pattern, text)
    chosen_options = re.findall(chosen_option_pattern, text)

    # Process matches
    df_data = []
    for question_id, status, chosen_option in zip(question_ids, statuses, chosen_options):

        question_id_int = int(question_id)
        chosen_option_int = clean_chosen_option(chosen_option) if status == 'Answered' else None
        
        df_data.append({
            'Question ID': question_id_int,
            'Response': int(chosen_option_int) if chosen_option_int is not None else None,
        })
    
    # Check if all lengths match up; otherwise raise an error for mismatched data
    if not (len(question_ids) == len(statuses) == len(chosen_options)):
        raise ValueError("Mismatch in the number of Question IDs, Statuses, and Chosen Options.")
        
    # Create DataFrame from df_data
    df = pd.DataFrame(df_data)    
    # Return based on the 'ret' parameter
    if ret == 'df':
        return df
    elif ret == 'dict':
        return df.set_index(df.columns[0])[df.columns[1]].to_dict()
    else:
        raise ValueError("Invalid value for 'ret'. Choose 'df' or 'dict'.")

def evaluate_responses(answerkey_dict, response_dict):
    split_index = 50
    paper1_responses = {k: response_dict[k] for k in list(response_dict)[:split_index]}
    paper2_responses = {k: response_dict[k] for k in list(response_dict)[split_index:]}

    def evaluate_paper(answerkey_dict, responses):
        correct_answers = []
        incorrect_answers = []
        unattempted_answers = []
        not_found_answers = []

        for key, val in responses.items():
            if key not in answerkey_dict:
                not_found_answers.append({key: val})
                continue
            if val is None:
                unattempted_answers.append({key: val})
            elif answerkey_dict[key] == val:
                correct_answers.append({key: val})
            else:
                incorrect_answers.append({key: val})
        
        # Calculate score
        score = len(correct_answers) * 2
        total_questions = len(responses)
        
        return {
            'overview': {
                'total': total_questions,
                'correct': len(correct_answers),
                'incorrect': len(incorrect_answers),
                'unattempted': len(unattempted_answers),
                'score': f'{score}/{total_questions * 2}',
                'accuracy': (len(correct_answers) / (len(correct_answers) + len(incorrect_answers) + len(unattempted_answers))) * 100 if (len(correct_answers) + len(incorrect_answers) + len(unattempted_answers)) > 0 else 0
            },
            'detailed': {
                'correct_answers': correct_answers,
                'incorrect_answers': incorrect_answers,
                'unattempted_answers': unattempted_answers,
            }
        }

    result_paper1 = evaluate_paper(answerkey_dict, paper1_responses)
    result_paper2 = evaluate_paper(answerkey_dict, paper2_responses)

    paper1_score_numerator = int(result_paper1['overview']['score'].split('/')[0])
    paper2_score_numerator = int(result_paper2['overview']['score'].split('/')[0])
    total_score = paper1_score_numerator + paper2_score_numerator

    total_questions = result_paper1['overview']['total'] + result_paper2['overview']['total']
    max_score = total_questions * 2

    score = f"{total_score}/{max_score}"
    
    overall_result = {
        'overview': {
            'total': result_paper1['overview']['total'] + result_paper2['overview']['total'],
            'correct': result_paper1['overview']['correct'] + result_paper2['overview']['correct'],
            'incorrect': result_paper1['overview']['incorrect'] + result_paper2['overview']['incorrect'],
            'unattempted': result_paper1['overview']['unattempted'] + result_paper2['overview']['unattempted'],
            'score': f'{total_score}/{max_score}',
            'accuracy': (result_paper1['overview']['correct'] + result_paper2['overview']['correct']) / (result_paper1['overview']['total'] + result_paper2['overview']['total']) * 100 if (result_paper1['overview']['total'] + result_paper2['overview']['total']) > 0 else 0
        },
        'detailed': {
            'correct_answers': result_paper1['detailed']['correct_answers'] + result_paper2['detailed']['correct_answers'],
            'incorrect_answers': result_paper1['detailed']['incorrect_answers'] + result_paper2['detailed']['incorrect_answers'],
            'unattempted_answers': result_paper1['detailed']['unattempted_answers'] + result_paper2['detailed']['unattempted_answers']
        }
    }

    return {
        'paper1': result_paper1,
        'paper2': result_paper2,
        'overall': overall_result
    }

def search_csv_files():
    # Get the current directory where the code is executed
    current_directory = os.getcwd()
    
    # Search for all CSV files in the directory
    csv_files = [f for f in os.listdir(current_directory) if f.endswith('.csv')]

    # If only one CSV file is found, return that file
    if len(csv_files) == 1:
        return csv_files[0]
    return None

def save_results_to_csv(answerkey_dict, response_dict, pdf_filename):
    # Create results directory if it doesn't exist
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir,exist_ok=True)
    
    # Extract the base name of the PDF (without extension)
    base_filename = os.path.splitext(os.path.basename(pdf_filename))[0]
    
    # Prepare the data for the DataFrame
    data = []
    for question_id, response in response_dict.items():
        correct_answer = answerkey_dict.get(question_id, None)
        if response is None:
            status = 'Unattempted'
        elif correct_answer is None:
            status = 'Not Found'
        elif correct_answer == response:
            status = 'Correct'
        else:
            status = 'Incorrect'
        
        data.append({
            'Question ID': question_id,
            'Answer': correct_answer,
            'Response': response,
            'Status': status
        })
    
    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    
    # Save to CSV in the results folder
    output_path = os.path.join(results_dir, f"{base_filename}.csv")
    df.to_csv(output_path, index=False)
    
    print(f"Results saved to {output_path}")

def save_evaluation_to_txt(evaluation_result, filename):
    # Create results directory if it doesn't exist
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir, exist_ok=True)
    
    # Prepare the file path
    base_filename = os.path.splitext(os.path.basename(filename))[0]
    output_path = os.path.join(results_dir, f"{base_filename}_evaluation.txt")

    with open(output_path, 'w') as f:
        # Paper 1 Overview
        f.write("Paper 1 Overview:\n")
        f.write(f"Total Questions: {evaluation_result['paper1']['overview']['total']}\n")
        f.write(f"Correct: {evaluation_result['paper1']['overview']['correct']}\n")
        f.write(f"Incorrect: {evaluation_result['paper1']['overview']['incorrect']}\n")
        f.write(f"Unattempted: {evaluation_result['paper1']['overview']['unattempted']}\n")
        f.write(f"Score: {evaluation_result['paper1']['overview']['score']}\n")
        f.write(f"Accuracy: {evaluation_result['paper1']['overview']['accuracy']:.2f}%\n\n")
        
        # Paper 2 Overview
        f.write("Paper 2 Overview:\n")
        f.write(f"Total Questions: {evaluation_result['paper2']['overview']['total']}\n")
        f.write(f"Correct: {evaluation_result['paper2']['overview']['correct']}\n")
        f.write(f"Incorrect: {evaluation_result['paper2']['overview']['incorrect']}\n")
        f.write(f"Unattempted: {evaluation_result['paper2']['overview']['unattempted']}\n")
        f.write(f"Score: {evaluation_result['paper2']['overview']['score']}\n")
        f.write(f"Accuracy: {evaluation_result['paper2']['overview']['accuracy']:.2f}%\n\n")
        
        # Overall Overview
        f.write("Overall Overview:\n")
        f.write(f"Total Questions: {evaluation_result['overall']['overview']['total']}\n")
        f.write(f"Correct: {evaluation_result['overall']['overview']['correct']}\n")
        f.write(f"Incorrect: {evaluation_result['overall']['overview']['incorrect']}\n")
        f.write(f"Unattempted: {evaluation_result['overall']['overview']['unattempted']}\n")
        f.write(f"Score: {evaluation_result['overall']['overview']['score']}\n")
        f.write(f"Accuracy: {evaluation_result['overall']['overview']['accuracy']:.2f}%\n\n")
        
        # Detailed Results for Paper 1 and Paper 2
        f.write("Detailed Correct Answers (Paper 1 & 2):\n")
        for answer in evaluation_result['overall']['detailed']['correct_answers']:
            f.write(f"{list(answer.keys())[0]}: {list(answer.values())[0]} (Correct)\n")
        
        f.write("\nDetailed Incorrect Answers (Paper 1 & 2):\n")
        for answer in evaluation_result['overall']['detailed']['incorrect_answers']:
            f.write(f"{list(answer.keys())[0]}: {list(answer.values())[0]} (Incorrect)\n")
        
        f.write("\nDetailed Unattempted Answers (Paper 1 & 2):\n")
        for answer in evaluation_result['overall']['detailed']['unattempted_answers']:
            f.write(f"{list(answer.keys())[0]}: {list(answer.values())[0]} (Unattempted)\n")
    
    print(f"Evaluation results saved to {output_path}")

