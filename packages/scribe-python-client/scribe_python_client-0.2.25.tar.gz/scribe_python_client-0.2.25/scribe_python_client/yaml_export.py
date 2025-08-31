import yaml
import csv
import os

#Path to the YAML file that needs to be updated with column descriptions (Take the unzipped file, and copy the path of the yaml file here)
yaml_input_path = ""

#Path to the CSV file containing data we can export to YAML
# Sample: https://docs.google.com/spreadsheets/d/1MaUylXeocaeoJueLRRf6GdPAupSW88huCMPQeYjYfz8/edit?usp=sharing
csv_input_path = ""

#Path where the updated YAML file will be saved
yaml_output_path = ""

output_dir = os.path.dirname(yaml_output_path)
os.makedirs(output_dir, exist_ok=True)


column_descriptions = {}
with open(csv_input_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        table = row['table_name'].strip()
        column = row['column_name'].strip()
        desc = row['column_description'].strip()
        if desc:
            column_descriptions[(table, column)] = desc

with open(yaml_input_path, 'r', encoding='utf-8') as f:
    dataset = yaml.safe_load(f)

table_name = dataset.get('table_name')
columns = dataset.get('columns', [])

updated_count = 0
for col in columns:
    col_name = col.get('column_name')
    key = (table_name, col_name)
    if key in column_descriptions:
        col['description'] = column_descriptions[key]
        updated_count += 1

with open(yaml_output_path, 'w', encoding='utf-8') as f:
    yaml.dump(dataset, f, sort_keys=False, allow_unicode=True)

print(f"Updated descriptions for {updated_count} columns in dataset '{table_name}'.")
print(f"Saved updated YAML to: {yaml_output_path}")