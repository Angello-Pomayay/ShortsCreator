import fitz  # PyMuPDF

def process_text(text):
    print(text+"\n--------------------------------------------------------------------------------------------\n\n")
    pass

def read_pdf_until_special_combination(pdf_path, special_combination, start_index=0, num_parts=1):
    doc = fitz.open(pdf_path)
    remaining_text = ""

    parts_processed = 0  # Counter for the number of parts processed

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = remaining_text + page.get_text()

        while True:
            # Find the index of the special combination in the text
            special_comb_index = text.find(special_combination)

            if special_comb_index == -1:
                break  # Special combination not found on this page

            # Extract text before the special combination
            truncated_text = text[:special_comb_index].strip()

            # Check if this part of text should be processed
            if parts_processed >= start_index and parts_processed < start_index + num_parts:
                # Process the text if within the specified range
                process_text(truncated_text)

            parts_processed += 1  # Increment the parts counter

            # Update text to continue searching after the special combination
            text = text[special_comb_index + len(special_combination):].strip()

            # Exit loop if reached the specified number of parts
            if parts_processed >= start_index + num_parts:
                return

        # Store the remaining text for the next iteration
        remaining_text = text

    # Print any remaining text after the last page
    if remaining_text and parts_processed >= start_index and parts_processed < start_index + num_parts:
        process_text(remaining_text)


pdf_path = '../PDF_folder/jokes.pdf'

special_combination = '****'

start_index = 0
num_parts = 3
read_pdf_until_special_combination(pdf_path, special_combination, start_index, num_parts)
