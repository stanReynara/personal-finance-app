import pdfplumber

pdf_path = "statements/jan.pdf" 

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
    
      # --- 1. FIND THE FOOTER SPLIT LINE ---
      words = page.extract_words()
      footer_y0 = page.height - 50 # Default to near the bottom margin
      
      # Scan the page to find where "SALDO AWAL" appears
      saldo_awal_tops = []
      for i in range(len(words)-1):
          if words[i]['text'].upper() == 'SALDO' and words[i+1]['text'].upper() == 'AWAL':
              saldo_awal_tops.append(words[i]['top'])
              
      if saldo_awal_tops:
          # We only care about the very last occurrence on the page
          last_y = saldo_awal_tops[-1]
          
          # Verify it's in the bottom half of the page so we don't accidentally 
          # cut off the first transaction of the month
          if last_y > page.height / 2:
              footer_y0 = last_y - 5 # Subtract 5 points to give the crop a clean padding line
              
      # --- 2. CROP THE PAGE INTO TWO PIECES ---
      # Crop 1: The Table (stops right before the footer begins)
      table_bbox = (0, 230, page.width, footer_y0)
      table_page = page.within_bbox(table_bbox)
      
      # Crop 2: The Footer (starts where the table ends)
      footer_bbox = (0, footer_y0, page.width, page.height - 10)
      footer_page = page.within_bbox(footer_bbox)

      # --- 3. EXTRACT TABLE (Top Half) ---
      perfect_lines = [32, 87, 298, 337, 455, 570] 
      explicit_lines = sorted(list(set([0, page.width] + perfect_lines)))

      table_settings = {
          "vertical_strategy": "explicit",
          "explicit_vertical_lines": explicit_lines, 
          "horizontal_strategy": "text", 
          "snap_tolerance": 3,
      }

      extracted_table = table_page.extract_table(table_settings)
      cleaned_transactions = []
      
      if extracted_table:
          current_txn = None
          for row in extracted_table[1:]:
              clean_row = [cell.strip() if cell else '' for cell in row]
              if not any(clean_row):
                  continue
                  
              tanggal, keterangan, cbg, mutasi, saldo = clean_row[:5]

              # Buffer logic to handle multi-line descriptions
              if tanggal != '':
                  if current_txn is not None: 
                      cleaned_transactions.append(current_txn)
                  current_txn = {'tanggal': tanggal, 'keterangan': keterangan, 'cbg': cbg, 'mutasi': mutasi, 'saldo': saldo}
              else:
                  if current_txn is not None:
                      if keterangan: current_txn['keterangan'] += f" {keterangan}"
                      if mutasi: current_txn['mutasi'] += f" {mutasi}"
                      if saldo: current_txn['saldo'] += f" {saldo}"

          # Append the final transaction (which is now guaranteed to not contain footer garbage)
          if current_txn is not None: 
              cleaned_transactions.append(current_txn)

      # --- 4. EXTRACT FOOTER TEXT (Bottom Half) ---
      footer_text = footer_page.extract_text()
      footer_summary = {}
      
      if footer_text:
          # Since we are using pure text extraction, we can just split by the colon
          for line in footer_text.split('\n'):
              line = line.strip().upper()
              if ':' in line:
                  parts = line.split(':', 1)
                  key = parts[0].strip()
                  val = parts[1].strip()
                  
                  if 'SALDO AWAL' in key:
                    footer_summary['Saldo Awal'] = val
                  elif 'MUTASI CR' in key:
                    footer_summary['Mutasi CR'] = val.split()[0]
                    footer_summary['Mutasi CR Amount'] = val.split()[1]
                  elif 'MUTASI DB' in key:
                    footer_summary['Mutasi DB'] = val.split()[0]
                    footer_summary['Mutasi DB Amount'] = val.split()[1]
                  elif 'SALDO AKHIR' in key:
                    footer_summary['Saldo Akhir'] = val

      # --- PRINT RESULTS ---
      for txn in cleaned_transactions:
          print(txn)
        
      if len(footer_summary) > 0: 
        print(footer_summary)
      # for key, value in footer_summary.items():
      #     print(f"{key}: {value}")