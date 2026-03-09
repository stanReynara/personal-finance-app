import pdfplumber

# Make sure this matches your actual file name
pdf_path = "statements/jan.pdf" 

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    
    # Crop the page to remove the account info at the top and the footer
    bounding_box = (0, 230, page.width, page.height-50)
    cropped_page = page.within_bbox(bounding_box)

    # Your dialed-in coordinates
    perfect_lines = [32, 87, 298, 337, 455, 570] 
    page_start = 0
    page_end = page.width
    explicit_lines = sorted(list(set([page_start, page_end] + perfect_lines)))

    # Apply the perfectly aligned lines to your table settings
    table_settings = {
        "vertical_strategy": "explicit",
        "explicit_vertical_lines": explicit_lines, 
        "horizontal_strategy": "text", 
        "snap_tolerance": 3,
    }

    # Extract the table data using your explicit lines
    extracted_table = cropped_page.extract_table(table_settings)

    if extracted_table:
        # The first row should be your headers
        headers = extracted_table[0]
        print("HEADERS:", headers)
        print("-" * 60)
        
        # Loop through the rest of the rows and print them
        for row in extracted_table[1:]:
            # This check ensures we don't print completely blank rows
            # caused by extra whitespace in the PDF
            if any(cell and cell.strip() for cell in row):
                print(row)
    else:
        print("No table data could be extracted.")