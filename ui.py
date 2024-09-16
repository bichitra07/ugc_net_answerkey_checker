import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import cv2
import os
import pytesseract
import utils

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from PyPDF2 import PdfReader, PdfWriter

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

        # Apply a theme
        style = ttk.Style()
        style.theme_use("clam")

        # Create custom styles for frames
        style.configure("Sunken.TFrame", background="#d4e157", relief="sunken", borderwidth=3)
        style.configure("Raised.TFrame", background="#ffeb3b", relief="raised", borderwidth=3)
        style.configure("Groove.TFrame", background="#aed581", relief="groove", borderwidth=3)

        # Configure styles for buttons and frames
        style.configure("TButton", font=("Arial", 12), padding=6)
        style.configure("TLabel", font=("Arial", 12))

        # Create UI elements
        self.create_widgets()
        
        # Add an exit protocol for X button exit case.
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        
        # Update button text with file name
        if self.answerkey_path:
            # Update button text to file name without extension
            file_name = os.path.splitext(os.path.basename(self.answerkey_path))[0]
            self.btn_select_answerkey_csv.config(text=file_name)
    
    def create_widgets(self):    
        # Button frame at the top (custom style applied)
        button_frame = ttk.Frame(self.root, style="Sunken.TFrame", padding=10)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Buttons with padding and alignment
        self.btn_select_answerkey_csv = ttk.Button(button_frame, text="Select Answer Key CSV", command=self.select_answerkey_csv)
        self.btn_select_answerkey_csv.pack(side=tk.LEFT, padx=10)

        self.btn_select_response_pdf = ttk.Button(button_frame, text="Select Response PDF", command=self.select_response_pdf)
        self.btn_select_response_pdf.pack(side=tk.LEFT, padx=10)

        self.btn_evaluate = ttk.Button(button_frame, text="Evaluate", command=self.evaluate)
        self.btn_evaluate.pack(side=tk.LEFT, padx=10)

        # Paper1 and Paper2 frames with light colors
        paper_frame = ttk.Frame(self.root, style="Raised.TFrame", padding=10)
        paper_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Use the same light color for both Paper 1 and Paper 2
        light_color = "#e0f7fa"  # Light cyan color
        self.create_paper_frame(paper_frame, "Paper 1", light_color)  
        self.create_paper_frame(paper_frame, "Paper 2", light_color)

        # Overall frame
        overall_frame = ttk.Frame(self.root, style="Groove.TFrame", padding=10)
        overall_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.create_overall_frame(overall_frame)

        # Frame for Save Result button and file path textbox
        save_frame = ttk.Frame(self.root, style="Sunken.TFrame", padding=10)
        save_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Save Result Button on the left
        self.btn_save_result = ttk.Button(save_frame, text="Save Result", command=self.save_result)
        self.btn_save_result.pack(side=tk.LEFT, padx=10, pady=10)

        # Disabled textbox for displaying save path
        self.save_path_entry = tk.Entry(save_frame, state='readonly', width=60)
        self.save_path_entry.pack(side=tk.LEFT, padx=10)

        # Exit Button at the bottom
        self.btn_exit = ttk.Button(self.root, text="Exit", command=self.exit_app)
        self.btn_exit.pack(side=tk.BOTTOM, padx=10, pady=10)

    def create_paper_frame(self, parent_frame, paper_name, bg_color):
        paper_frame = tk.LabelFrame(parent_frame, text=paper_name, bg=bg_color, padx=5, pady=5)
        paper_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        labels = ['Total Questions', 'Correct Answers', 'Incorrect Answers', 'Unattempted', 'Score', 'Percentages']
        for i, label in enumerate(labels):
            tk.Label(paper_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = tk.Entry(paper_frame)
            entry.grid(row=i, column=1, padx=5, pady=2)
            key = f'{paper_name.lower().replace(" ", "_")}_{label.lower().replace(" ", "_")}'
            setattr(self, key, entry)  # Use setattr to dynamically create attributes
    
    def create_overall_frame(self, parent_frame):
        overall_frame = tk.LabelFrame(parent_frame, text="Overall", padx=5, pady=5, bg="#e0f7fa")
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
            # Ask the user where to save the result CSV
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                # Save CSV and TXT results using utils
                utils.save_results_to_csv(self.answerkey_dict, self.response_dict, file_path)
                utils.save_evaluation_to_txt(self.result, file_path)

                # Update the save path textbox
                self.save_path_entry.config(state=tk.NORMAL)
                self.save_path_entry.delete(0, tk.END)
                self.save_path_entry.insert(0, file_path)
                self.save_path_entry.config(state='readonly')

                # Use the PDF file selected via select_response_pdf
                if hasattr(self, 'response_pdf_path') and self.response_pdf_path:
                    self.append_results_to_pdf(self.response_pdf_path, file_path)
                else:
                    messagebox.showerror("Error", "Please select a PDF file to append the results to.")

                messagebox.showinfo("Success", "Results saved successfully!")
        else:
            messagebox.showerror("Error", "Please evaluate the responses first.")

    def append_results_to_pdf(self, pdf_path, file_path):
        # Prepare the data for the table
        table_data = [['Question ID', 'Answer', 'Response', 'Status']]
        for question_id, response in self.response_dict.items():
            correct_answer = self.answerkey_dict.get(question_id, None)
            status = 'Unattempted' if response is None else 'Correct' if correct_answer == response else 'Incorrect'
            table_data.append([question_id, correct_answer, response, status])

        # Create a PDF with reportlab
        packet = BytesIO()
        doc = SimpleDocTemplate(packet, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        elements = []
        styles = getSampleStyleSheet()

        # Add a title
        title = Paragraph("UGC-NET Answer Key Evaluation Results", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))  # Add space between title and table

        # Create the table with a margin
        table = Table(table_data, colWidths=[doc.pagesize[0] / 4 - 14] * 4)  # Adjust column widths to fit within margins

        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),   # Header row background color
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Add the table to the elements
        elements.append(table)
        
        # Build the PDF to the BytesIO buffer
        doc.build(elements)
        packet.seek(0)  # Ensure the buffer is at the beginning for reading

        # Read the original PDF
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        # Append all original pages to the writer
        for page_num in range(len(reader.pages)):
            writer.add_page(reader.pages[page_num])

        # Add the new pages with the results
        new_pdf_reader = PdfReader(packet)
        for page_num in range(len(new_pdf_reader.pages)):
            writer.add_page(new_pdf_reader.pages[page_num])

        # Save the new PDF with appended results
        output_pdf_path = os.path.splitext(pdf_path)[0] + "_with_results.pdf"
        with open(output_pdf_path, "wb") as output_pdf_file:
            writer.write(output_pdf_file)

        print(f"Results appended to {output_pdf_path}")
        
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
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.root.quit()

if __name__ == "__main__":
    # Call the setup function at the beginning of your script
    utils.setup_os_specific_paths()
    root = tk.Tk()
    app = AnswerKeyCheckerUI(root)
    root.mainloop()
