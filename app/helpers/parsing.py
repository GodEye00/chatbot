import os
import csv 
import re  # Import the regular expression module

docs_path_dir = "../utils/extracted_pages"
output_csv_dir = "../docs/output.csv"

passages = []

for docs_path in os.listdir(docs_path_dir):
    if docs_path.endswith(".txt"):
        extracted_docs_path = os.path.join(docs_path_dir, docs_path)
        
        with open(extracted_docs_path, 'r', encoding='utf-8') as input_file:
            extracted_data = input_file.read()
            
            # Use regular expression to replace consecutive newlines with a single space
            extracted_data = re.sub(r'\n+', ' ', extracted_data)
            
            extracted_data_stripped = extracted_data.strip()
            
            chunk_size = 200
            for i in range(0, len(extracted_data_stripped), chunk_size):
                chunk = extracted_data_stripped[i:i+chunk_size]
                passages.append({"Passage": chunk})
print(len(passages))
with open(output_csv_dir, 'a', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['Passage']
    writer = csv.DictWriter(csv_file, fieldnames)
    writer.writeheader()
    for passage in passages:
        writer.writerow(passage)
