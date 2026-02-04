import csv

def clean_csv(input_file, output_file):

    try:
        with open(input_file, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            columns = reader.fieldnames

            cleaned_rows = []

            for row in reader:

                # Skip rows with missing name
                if not row.get('name') or row['name'].strip() == "":
                    continue

                # Validate age
                age = row.get('age', '').strip()
                try:
                    age_value = int(age)
                    row['age'] = str(age_value) if age_value >= 0 else 'UNKNOWN'
                except (ValueError, TypeError):
                    row['age'] = 'UNKNOWN'

                # Convert email to lowercase
                if row.get('email'):
                    row['email'] = row['email'].strip().lower()

                cleaned_rows.append(row)

    except FileNotFoundError:
        print("File not found")
        return

    with open(output_file, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=columns)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    print(f"Cleaned {len(cleaned_rows)} rows. Output saved to {output_file}")


if __name__ == "__main__":
    input_file = "../data/raw_users.csv"
    output_file = "../output/clean_users.csv"
    clean_csv(input_file, output_file)
