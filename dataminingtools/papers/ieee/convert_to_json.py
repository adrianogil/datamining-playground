# convert_to_json.py: Converts the CSV files containing the papers data to a JSON file.
import csv
import json


def convert_paper_row_to_dict(row):
    # Assuming authors are separated by a semicolon in the "Authors" column.
    authors = row['Authors'].split(';') if row['Authors'] else []
    return {
        "title": row['Document Title'],
        "link": row['PDF Link'],
        "authors": authors,
        "pages": f"{row['Start Page']}-{row['End Page']}" if row['Start Page'] and row['End Page'] else "",
        "pdf_link": row['PDF Link']
    }

def convert_papers_csv_to_json(current_issue_title, csv_list, json_path):
    papers = []
    for csv_path in csv_list:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            papers.extend([convert_paper_row_to_dict(row) for row in reader])

    papers_data = {
        "current_issue_title": current_issue_title,
        "papers": papers
    }

    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(papers_data, jsonfile, indent=4)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Usage: python convert_to_json.py <current_issue_title> <csv_file1> <csv_file2> ...")
        sys.exit(1)

    current_issue_title = sys.argv[1]
    csv_list = sys.argv[2:]
    json_path = "ieee_papers.json"
    convert_papers_csv_to_json(current_issue_title, csv_list, json_path)
