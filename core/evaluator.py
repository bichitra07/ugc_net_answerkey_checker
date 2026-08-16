import os
import fitz  # PyMuPDF

def evaluate_and_annotate(pdf_data, ans_dict, original_pdf_path, output_pdf_path):
    """
    Evaluates the parsed PDF data against the answer key,
    and creates a new annotated PDF with the results.
    
    Returns a dictionary of results:
    {
        'Total': int, 'Correct': int, 'Incorrect': int, 'Unattempted': int, 'Score': int,
        'Paper 1': {'Total': int, ...},
        'Paper 2': {'Total': int, ...}
    }
    """
    
    doc = fitz.open(original_pdf_path)
    
    metrics = {
        'Overall': {'Total': 0, 'Correct': 0, 'Incorrect': 0, 'Unattempted': 0},
        'Paper 1': {'Total': 0, 'Correct': 0, 'Incorrect': 0, 'Unattempted': 0},
        'Paper 2': {'Total': 0, 'Correct': 0, 'Incorrect': 0, 'Unattempted': 0}
    }
    
    for q_data in pdf_data:
        q_id = q_data['Question ID']
        chosen_opt = q_data['Chosen Option']
        options = q_data['Options']
        page_num = q_data['Page']
        
        # Determine Paper based on Question Count logic (assuming Paper 1 is first 50)
        # NTA usually puts Paper 1 first, so we use a simple counter
        # We will increment total first
        if metrics['Paper 1']['Total'] < 50:
            paper_key = 'Paper 1'
        else:
            paper_key = 'Paper 2'
            
        metrics['Overall']['Total'] += 1
        metrics[paper_key]['Total'] += 1
        
        # 1. Figure out if correct
        is_correct = False
        is_unattempted = chosen_opt is None
        correct_index = None
        
        if q_id in ans_dict:
            ans_val = str(ans_dict[q_id]).strip()
            
            # Is the answer key already an index (1, 2, 3, 4)?
            if ans_val in ['1', '2', '3', '4']:
                correct_index = ans_val
            else:
                # Answer key is an ID. We must find it in the PDF's options.
                if options and ans_val in options:
                    correct_index = str(options.index(ans_val) + 1)
                else:
                    # Fallback (maybe dropped question)
                    correct_index = ans_val
                    
            if not is_unattempted and chosen_opt == correct_index:
                is_correct = True
        
        # 2. Update metrics
        if is_unattempted:
            metrics['Overall']['Unattempted'] += 1
            metrics[paper_key]['Unattempted'] += 1
        elif is_correct:
            metrics['Overall']['Correct'] += 1
            metrics[paper_key]['Correct'] += 1
        else:
            metrics['Overall']['Incorrect'] += 1
            metrics[paper_key]['Incorrect'] += 1
            
        # 3. Annotate the PDF
        page = doc.load_page(page_num)
        
        # Search for the exact Question ID text to get its coordinates
        text_instances = page.search_for(f"Question ID : {q_id}")
        if not text_instances:
            text_instances = page.search_for(q_id)
            
        if text_instances:
            # text_instances[0] is the bounding box Rect(x0, y0, x1, y1)
            rect = text_instances[0]
            
            # Position text 30 pixels above the Question ID box 
            # (100 pixels might push it off the top edge or into other questions)
            x0 = rect.x0
            y0 = max(0, rect.y0 - 20)
            
            if is_unattempted:
                msg = f"Unattempted (Correct: {correct_index})"
                color = (0.5, 0.5, 0.5) # Gray
            elif is_correct:
                msg = f"✅ Correct (Answer: {correct_index})"
                color = (0.0, 0.7, 0.0) # Green
            else:
                msg = f"❌ Incorrect (Correct: {correct_index})"
                color = (0.9, 0.0, 0.0) # Red
                
            page.insert_text((x0, y0), msg, fontsize=10, color=color, fontname="helv")
            
    # Calculate Scores
    # Correct = +2, Incorrect = 0
    metrics['Overall']['Score'] = metrics['Overall']['Correct'] * 2
    metrics['Paper 1']['Score'] = metrics['Paper 1']['Correct'] * 2
    metrics['Paper 2']['Score'] = metrics['Paper 2']['Correct'] * 2
    
    # 4. Draw Overall Scorecard on Page 1 (Top Right)
    first_page = doc.load_page(0)
    scorecard_text = (
        f"--- RESULT SCORECARD ---\n"
        f"Paper 1: {metrics['Paper 1']['Correct']} / {metrics['Paper 1']['Total']} Correct\n"
        f"Paper 2: {metrics['Paper 2']['Correct']} / {metrics['Paper 2']['Total']} Correct\n"
        f"Total Score: {metrics['Overall']['Score']} / {metrics['Overall']['Total'] * 2}"
    )
    
    # Coordinates for top right
    page_width = first_page.rect.width
    x_score = page_width - 200
    y_score = 50
    
    # Draw a bounding box for scorecard
    rect = fitz.Rect(x_score - 10, y_score - 20, x_score + 180, y_score + 60)
    first_page.draw_rect(rect, color=(0, 0, 1), fill=(0.9, 0.9, 1.0))
    first_page.insert_text((x_score, y_score), scorecard_text, fontsize=11, color=(0,0,0.5), fontname="helv")
    
    # Save the new PDF
    doc.save(output_pdf_path)
    doc.close()
    
    return metrics
