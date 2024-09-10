import utils
import cv2
from PIL import Image
import pytesseract

def main():
    # Call the setup function at the beginning of your script
    utils.setup_os_specific_paths()
    # Select CSV and PDF files.
    csv_path = utils.search_csv_files()
    if not csv_path:
        csv_path = utils.select_csv()
    pdf_path = utils.select_pdf()
    
    # Read answer key from CSV
    answerkey_dict = utils.read_csv(csv_path)
    
    # Convert PDF to images
    images = utils.pdf_to_images(pdf_path)
    
    # Select crop point from the first image
    # crop_point = utils.select_crop_point(images[0])
    crop_point = (900,0)
    
    # Initialize response dictionary
    response_dict = {}
    
    # Process each image and extract responses
    for image in images:
        # Crop the image
        cropped_img = utils.crop_image_from_point(image, crop_point)
        # Preprocess the image
        cropped_img = utils.preprocess_image(cropped_img)
        # Convert NumPy array to PIL Image
        img_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        # Perform OCR using pytesseract
        ocr_result = pytesseract.image_to_data(img_pil, output_type=pytesseract.Output.DICT)
        # Extract text lines
        extracted_text = utils.extract_lines(ocr_result)
        # Extract response blocks
        response_data = utils.extract_response_blocks(extracted_text)
        # Update the response dictionary
        response_dict.update(response_data)
    
    # Evaluate responses
    result = utils.evaluate_responses(answerkey_dict, response_dict)
    utils.save_evaluation_to_txt(result, pdf_path)
    utils.save_results_to_csv(answerkey_dict, response_dict, pdf_path)
    
    # Print summary
    print(f"Paper 1 Results:")
    print(f"  Total: {result['paper1']['overview']['total']}")
    print(f"  Correct: {result['paper1']['overview']['correct']}")
    print(f"  Incorrect: {result['paper1']['overview']['incorrect']}")
    print(f"  Unattempted: {result['paper1']['overview']['unattempted']}")
    print(f"  Score: {result['paper1']['overview']['score']}")
    print(f"  Accuracy: {result['paper1']['overview']['accuracy']:.2f}%")
    
    print(f"\nPaper 2 Results:")
    print(f"  Total: {result['paper2']['overview']['total']}")
    print(f"  Correct: {result['paper2']['overview']['correct']}")
    print(f"  Incorrect: {result['paper2']['overview']['incorrect']}")
    print(f"  Unattempted: {result['paper2']['overview']['unattempted']}")
    print(f"  Score: {result['paper2']['overview']['score']}")
    print(f"  Accuracy: {result['paper2']['overview']['accuracy']:.2f}%")
    
    print(f"\nOverall Results:")
    print(f"  Total: {result['overall']['overview']['total']}")
    print(f"  Correct: {result['overall']['overview']['correct']}")
    print(f"  Incorrect: {result['overall']['overview']['incorrect']}")
    print(f"  Score: {result['overall']['overview']['score']}")
    print(f"  Unattempted: {result['overall']['overview']['unattempted']}")
    print(f"  Accuracy: {result['overall']['overview']['accuracy']:.2f}%")

if __name__ == "__main__":
    main()
