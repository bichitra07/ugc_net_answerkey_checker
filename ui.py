import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import cv2
import os
import pytesseract
import utils

class AnswerKeyCheckerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UGC-NET AnswerKey Checker")
        
        # Initialize variables for file paths
        self.answerkey_path = utils.search_csv_files()        
        self.response_pdf_path = None
        
        self.answerkey_dict = None
        self.response_dict = None
        self.result = None
        # Create UI elements
        self.create_widgets()

        # Update button text with file name
        if self.answerkey_path:
            # Update button text to file name without extension
            file_name = os.path.splitext(os.path.basename(self.answerkey_path))[0]
            self.btn_select_answerkey_csv.config(text=file_name)
    
    def create_widgets(self):
        # Button frame at the top
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Buttons
        self.btn_select_answerkey_csv = tk.Button(button_frame, text="Select Answer Key CSV", command=self.select_answerkey_csv)
        self.btn_select_answerkey_csv.pack(side=tk.LEFT, padx=5)
        
        self.btn_select_response_pdf = tk.Button(button_frame, text="Select Response PDF", command=self.select_response_pdf)
        self.btn_select_response_pdf.pack(side=tk.LEFT, padx=5)
        
        self.btn_evaluate = tk.Button(button_frame, text="Evaluate", command=self.evaluate)
        self.btn_evaluate.pack(side=tk.LEFT, padx=5)
        
        
        # Paper1 and Paper2 frames
        paper_frame = tk.Frame(self.root)
        paper_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.create_paper_frame(paper_frame, "Paper 1")
        self.create_paper_frame(paper_frame, "Paper 2")
        
        # Overall frame
        overall_frame = tk.Frame(self.root)
        overall_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.create_overall_frame(overall_frame)

        self.btn_save_result = tk.Button(overall_frame, text="save result", command=self.save_result)
        self.btn_save_result.pack(padx=5)
          
        self.btn_exit = tk.Button(self.root, text="Exit", command=self.exit_app)
        self.btn_exit.pack( side=tk.BOTTOM,padx=5)
    
    def create_paper_frame(self, parent_frame, paper_name):
        paper_frame = tk.LabelFrame(parent_frame, text=paper_name, padx=5, pady=5)
        paper_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        labels = ['Total Questions', 'Correct Answers', 'Incorrect Answers', 'Unattempted', 'Score', 'Percentages']
        for i, label in enumerate(labels):
            tk.Label(paper_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = tk.Entry(paper_frame)
            entry.grid(row=i, column=1, padx=5, pady=2)
            key = f'{paper_name.lower().replace(" ", "_")}_{label.lower().replace(" ", "_")}'
            setattr(self, key, entry)  # Use setattr to dynamically create attributes
    
    def create_overall_frame(self, parent_frame):
        overall_frame = tk.LabelFrame(parent_frame, text="Overall", padx=5, pady=5)
        overall_frame.pack(fill=tk.X, padx=5, pady=5)
        
        labels = ['Total', 'Correct', 'Incorrect', 'Unattempted', 'Score', 'Percentages']
        for i, label in enumerate(labels):
            tk.Label(overall_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = tk.Entry(overall_frame)
            entry.grid(row=i, column=1, padx=5, pady=2)
            setattr(self, label.lower(), entry)  # Use setattr to dynamically create attributes
    
    def select_answerkey_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            messagebox.showerror("Error", "No CSV file selected")
        else:
            # Update button text to file name without extension
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            self.btn_select_answerkey_csv.config(text=file_name)
            self.answerkey_path = file_path  # Assuming you are storing the path
    
    def select_response_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            messagebox.showerror("Error", "No PDF file selected")
        else:
             # Update button text to file name without extension
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            self.btn_select_response_pdf.config(text=file_name)
            self.response_pdf_path = file_path  # Assuming you are storing the path
    
    def evaluate(self):
        if not self.answerkey_path or not self.response_pdf_path:
            messagebox.showerror("Error", "Please select both the answer key CSV and response PDF")
            return
        
        self.answerkey_dict = utils.read_csv(self.answerkey_path)
        images = utils.pdf_to_images(self.response_pdf_path)
        # crop_point = utils.select_crop_point(images[0])
        crop_point = (900,0)
        self.response_dict = {}
        
        for image in images:
            cropped_img = utils.crop_image_from_point(image, crop_point)
            cropped_img = utils.preprocess_image(cropped_img)
            img_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            ocr_result = pytesseract.image_to_data(img_pil, output_type=pytesseract.Output.DICT)
            extracted_text = utils.extract_lines(ocr_result)
            response_data = utils.extract_response_blocks(extracted_text)
            self.response_dict.update(response_data)
        
        self.result = utils.evaluate_responses(self.answerkey_dict, self.response_dict)
        
        # Update UI with results
        self.update_ui()

    def save_result(self):
        if self.answerkey_dict and self.response_dict and self.result:
            utils.save_results_to_csv(self.answerkey_dict, self.response_dict, self.response_pdf_path)
            utils.save_evaluation_to_txt(self.result, self.response_pdf_path)
            messagebox.showinfo("Success", "Results saved successfully!")
        else:
            messagebox.showerror("Error", "Please evaluate the responses first.")
    
    def update_ui(self):
        # Paper1 results
        paper1 = self.result['paper1']['overview']
        self.paper_1_total_questions.delete(0, tk.END)
        self.paper_1_total_questions.insert(0, paper1['total'])
        self.paper_1_correct_answers.delete(0, tk.END)
        self.paper_1_correct_answers.insert(0, paper1['correct'])
        self.paper_1_incorrect_answers.delete(0, tk.END)
        self.paper_1_incorrect_answers.insert(0, paper1['incorrect'])
        self.paper_1_unattempted.delete(0, tk.END)
        self.paper_1_unattempted.insert(0, paper1['unattempted'])
        self.paper_1_score.delete(0, tk.END)
        self.paper_1_score.insert(0, paper1['score'])
        self.paper_1_percentages.delete(0, tk.END)
        self.paper_1_percentages.insert(0, f"{paper1['accuracy']:.2f}%")
        
        # Paper2 results
        paper2 = self.result['paper2']['overview']
        self.paper_2_total_questions.delete(0, tk.END)
        self.paper_2_total_questions.insert(0, paper2['total'])
        self.paper_2_correct_answers.delete(0, tk.END)
        self.paper_2_correct_answers.insert(0, paper2['correct'])
        self.paper_2_incorrect_answers.delete(0, tk.END)
        self.paper_2_incorrect_answers.insert(0, paper2['incorrect'])
        self.paper_2_unattempted.delete(0, tk.END)
        self.paper_2_unattempted.insert(0, paper2['unattempted'])
        self.paper_2_score.delete(0, tk.END)
        self.paper_2_score.insert(0, paper2['score'])
        self.paper_2_percentages.delete(0, tk.END)
        self.paper_2_percentages.insert(0, f"{paper2['accuracy']:.2f}%")
        
        # Overall results
        overall = self.result['overall']['overview']
        self.total.delete(0, tk.END)
        self.total.insert(0, overall['total'])
        self.correct.delete(0, tk.END)
        self.correct.insert(0, overall['correct'])
        self.incorrect.delete(0, tk.END)
        self.incorrect.insert(0, overall['incorrect'])
        self.unattempted.delete(0, tk.END)
        self.unattempted.insert(0, overall['unattempted'])
        self.score.delete(0, tk.END)
        self.score.insert(0, overall['score'])
        self.percentages.delete(0, tk.END)
        self.percentages.insert(0, f"{overall['accuracy']:.2f}%")
    

    def exit_app(self):
        self.root.quit()

if __name__ == "__main__":
    # Call the setup function at the beginning of your script
    utils.setup_os_specific_paths()
    root = tk.Tk()
    app = AnswerKeyCheckerUI(root)
    root.mainloop()
