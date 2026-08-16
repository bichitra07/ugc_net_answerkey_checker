import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

from core.answerkey_parser import read_answerkey, parse_final_pdf_key
from core.pdf_parser import extract_pdf_data
from core.evaluator import evaluate_and_annotate

class EvaluationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UGC NET Answer Key Checker")
        self.root.geometry("800x650")
        
        # Variables
        self.answerkey_path = None
        self.response_pdf_path = None
        
        self.create_widgets()
        
    def create_widgets(self):    
        # Button frame at the top (custom style applied)
        button_frame = ttk.Frame(self.root, style="Sunken.TFrame", padding=10)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Buttons with padding and alignment
        self.btn_select_answerkey = ttk.Button(button_frame, text="Select Answer Key (CSV/HTML)", command=self.select_answerkey)
        self.btn_select_answerkey.pack(side=tk.LEFT, padx=10)

        self.btn_select_response_pdf = ttk.Button(button_frame, text="Select Response PDF", command=self.select_response_pdf)
        self.btn_select_response_pdf.pack(side=tk.LEFT, padx=10)

        self.btn_evaluate = ttk.Button(button_frame, text="Evaluate", command=self.evaluate)
        self.btn_evaluate.pack(side=tk.LEFT, padx=10)

        # Paper1 and Paper2 frames with light colors
        paper_frame = ttk.Frame(self.root, style="Raised.TFrame", padding=10)
        paper_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

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

        self.btn_save_result = ttk.Button(save_frame, text="Save Result", command=self.save_result)
        self.btn_save_result.pack(side=tk.LEFT, padx=10, pady=10)

        self.save_path_entry = tk.Entry(save_frame, state='readonly', width=60)
        self.save_path_entry.pack(side=tk.LEFT, padx=10)

        self.btn_exit = ttk.Button(self.root, text="Exit", command=self.exit_app)
        self.btn_exit.pack(side=tk.BOTTOM, padx=10, pady=10)

    def create_paper_frame(self, parent_frame, paper_name, bg_color):
        paper_frame = tk.LabelFrame(parent_frame, text=paper_name, bg=bg_color, padx=5, pady=5)
        paper_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        labels = ['Total Questions', 'Correct Answers', 'Incorrect Answers', 'Unattempted', 'Dropped', 'Score', 'Percentages']
        for i, label in enumerate(labels):
            tk.Label(paper_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = tk.Entry(paper_frame)
            entry.grid(row=i, column=1, padx=5, pady=2)
            key = f'{paper_name.lower().replace(" ", "_")}_{label.lower().replace(" ", "_")}'
            setattr(self, key, entry)
    
    def create_overall_frame(self, parent_frame):
        overall_frame = tk.LabelFrame(parent_frame, text="Overall", padx=5, pady=5, bg="#e0f7fa")
        overall_frame.pack(fill=tk.X, padx=5, pady=5)
        
        labels = ['Total', 'Correct', 'Incorrect', 'Unattempted', 'Dropped', 'Score', 'Percentages']
        for i, label in enumerate(labels):
            tk.Label(overall_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = tk.Entry(overall_frame)
            entry.grid(row=i, column=1, padx=5, pady=2)
            setattr(self, label.lower(), entry)
    
    def select_answerkey(self):
        file_path = filedialog.askopenfilename(filetypes=[("Answer Key Files", "*.csv *.html *.pdf"), ("CSV files", "*.csv"), ("HTML files", "*.html"), ("PDF files", "*.pdf")])
        if not file_path:
            messagebox.showerror("Error", "No file selected")
        else:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            self.btn_select_answerkey.config(text=file_name)
            self.answerkey_path = file_path
    
    def select_response_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            messagebox.showerror("Error", "No PDF file selected")
        else:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            self.btn_select_response_pdf.config(text=file_name)
            self.response_pdf_path = file_path
    
    def evaluate(self):
        if not self.answerkey_path or not self.response_pdf_path:
            messagebox.showerror("Error", "Please select both the answer key (CSV/HTML) and response PDF")
            return
        
        try:
            # 1. Parse Answer Key
            if self.answerkey_path.lower().endswith('.pdf'):
                ans_dict = parse_final_pdf_key(self.answerkey_path)
                eval_type = "FINAL"
            else:
                ans_dict = read_answerkey(self.answerkey_path)
                eval_type = "PROVISIONAL"
            
            # 2. Parse PDF Text
            pdf_data = extract_pdf_data(self.response_pdf_path)
            
            # 3. Evaluate and Annotate new PDF
            output_pdf_path = os.path.splitext(self.response_pdf_path)[0] + "_evaluated.pdf"
            metrics = evaluate_and_annotate(pdf_data, ans_dict, self.response_pdf_path, output_pdf_path, evaluation_type=eval_type)
            
            self.update_ui(metrics)
            
            # Show output path
            self.save_path_entry.config(state='normal')
            self.save_path_entry.delete(0, tk.END)
            self.save_path_entry.insert(0, output_pdf_path)
            self.save_path_entry.config(state='readonly')
            
            messagebox.showinfo("Success", f"Evaluation complete! Annotated PDF saved to:\n{output_pdf_path}")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"An error occurred during evaluation:\n{e}")

    def update_ui(self, metrics):
        def set_entry(entry, value):
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

        for paper in ['Paper 1', 'Paper 2']:
            prefix = paper.lower().replace(" ", "_")
            m = metrics[paper]
            total = m['Total']
            
            set_entry(getattr(self, f'{prefix}_total_questions'), total)
            set_entry(getattr(self, f'{prefix}_correct_answers'), m['Correct'])
            set_entry(getattr(self, f'{prefix}_incorrect_answers'), m['Incorrect'])
            set_entry(getattr(self, f'{prefix}_unattempted'), m['Unattempted'])
            set_entry(getattr(self, f'{prefix}_dropped'), m.get('Dropped', 0))
            set_entry(getattr(self, f'{prefix}_score'), m['Score'])
            
            pct = round((m['Correct'] / total * 100), 2) if total > 0 else 0
            set_entry(getattr(self, f'{prefix}_percentages'), f"{pct}%")
            
        # Overall
        mo = metrics['Overall']
        ototal = mo['Total']
        set_entry(self.total, ototal)
        set_entry(self.correct, mo['Correct'])
        set_entry(self.incorrect, mo['Incorrect'])
        set_entry(self.unattempted, mo['Unattempted'])
        set_entry(self.dropped, mo.get('Dropped', 0))
        set_entry(self.score, mo['Score'])
        
        opct = round((mo['Correct'] / ototal * 100), 2) if ototal > 0 else 0
        set_entry(self.percentages, f"{opct}%")

    def save_result(self):
        # Result is already saved by evaluate(). We can just remind the user.
        path = self.save_path_entry.get()
        if path:
            messagebox.showinfo("Saved", f"Results have already been saved to:\n{path}")
        else:
            messagebox.showwarning("Warning", "Please evaluate a PDF first.")

    def exit_app(self):
        self.root.destroy()
