import pdfplumber

# Make sure this matches your actual file name
pdf_path = "statements/jan.pdf" 

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
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
          # We will store our fully merged dictionary objects here
          cleaned_transactions = []
          
          # This will hold the transaction we are currently building
          current_txn = None

          # Skip the header row [0] and loop through the data
          for row in extracted_table[1:]:
              
              clean_row = [cell.strip() if cell else '' for cell in row]
              
              if not any(clean_row):
                  continue
                  
              tanggal = clean_row[0]
              keterangan = clean_row[1]
              cbg = clean_row[2]
              mutasi = clean_row[3]
              saldo = clean_row[4]

              # --- NEW STOP CONDITION ---
              # If we see "SALDO AWAL" on a row with NO date, we have hit the footer.
              # End the scan immediately.
              if tanggal == '' and 'SALDO AWAL' in keterangan.upper():
                  break 

              # If 'tanggal' has data, it is a brand new transaction
              if tanggal != '':
                  if current_txn is not None:
                      cleaned_transactions.append(current_txn)
                  
                  current_txn = {
                      'tanggal': tanggal,
                      'keterangan': keterangan,
                      'cbg': cbg,
                      'mutasi': mutasi,
                      'saldo': saldo
                  }
              
              # If 'tanggal' is empty, append to the previous transaction
              else:
                  if current_txn is not None:
                      if keterangan != '':
                          current_txn['keterangan'] += f" {keterangan}"
                      if mutasi != '':
                          current_txn['mutasi'] += f" {mutasi}"
                      if saldo != '':
                          current_txn['saldo'] += f" {saldo}"

          # Append the very last transaction (the one right before the footer)
          if current_txn is not None:
              cleaned_transactions.append(current_txn)
          # CRITICAL: After the loop finishes, append the very last transaction in the buffer
          if current_txn is not None:
              cleaned_transactions.append(current_txn)

          # --- Print the merged results ---
          for txn in cleaned_transactions:
              print(txn)

      else:
          print("No table data could be extracted.")