import csv
import json


def generate_quality_report(file_path):
    """
    Generate a quality report for a CSV file.

    Args:
        file_path (str): Path to the CSV file

    Returns:
        dict: Quality report with metadata and statistics
    """

    report = {
        "row_count": 0,
        "columns": [],
        "missing_values": {},
        "invalid_values": {}
    }

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            # Extract column names
            report["columns"] = reader.fieldnames if reader.fieldnames else []

            # Initialize counters
            missing_counts = {col: 0 for col in report["columns"]}
            invalid_counts = {}

            row_count = 0

            for row in reader:
                row_count += 1

                # Check missing values
                for col in report["columns"]:
                    value = row.get(col, "")
                    if value == "" or value is None:
                        missing_counts[col] += 1

                # Check invalid amount values
                if "amount" in row:
                    try:
                        amount = float(row["amount"])
                        if amount <= 0:
                            invalid_counts["amount"] = invalid_counts.get("amount", 0) + 1
                    except (ValueError, TypeError):
                        pass

            # Update report
            report["row_count"] = row_count
            report["missing_values"] = {
                k: v for k, v in missing_counts.items() if v > 0
            }
            report["invalid_values"] = invalid_counts

            return report

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


if __name__ == "__main__":
    csv_file = "../data/transactions.csv"
    report = generate_quality_report(csv_file)

    if report:
        output_file = "../output/csv_quality_report.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"Quality report generated successfully: {output_file}")
