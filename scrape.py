import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime

def scrape_lots_project():
    url = 'https://lots-project.com/'  # Replace with the actual data URL if different
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; LOTS-Scraper/1.0; +https://github.com/your-username/lots-scraper)'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the table within 'extensions-table-container'
    table_container = soup.select_one('body > div > div.extensions-table-container')
    if not table_container:
        print("Could not find the extensions table container on the page.")
        return

    table = table_container.find('table')
    if not table:
        print("Could not find the table within the extensions table container.")
        return

    # Extract table headers
    headers = []
    header_row = table.find('thead')
    if header_row:
        headers = [th.text.strip() for th in header_row.find_all('th')]
    else:
        # If there's no thead, assume the first row contains headers
        first_row = table.find('tr')
        if first_row:
            headers = [th.text.strip() for th in first_row.find_all(['th', 'td'])]
        else:
            print("No headers found in the table.")
            return

    # Add new columns
    headers.append('Date Scraped')
    headers.append('Status')

    # Extract table rows
    data = []
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
    else:
        rows = table.find_all('tr')[1:]  # Skip the header row if tbody is not present

    for row in rows:
        cols = row.find_all(['td', 'th'])
        cols_text = [col.get_text(strip=True) for col in cols]
        if cols_text:  # Avoid empty rows
            data.append(cols_text)

    if not data:
        print("No data found in the table.")
        return

    # Define CSV file path
    csv_file = 'data.csv'
    file_exists = os.path.isfile(csv_file)

    # Prepare new data with additional columns
    date_scraped = datetime.utcnow().strftime('%Y-%m-%d')  # UTC date
    new_data = []
    for row in data:
        row_with_date = row + [date_scraped, "To be reviewed"]
        new_data.append(row_with_date)

    # Read existing data to avoid duplicates
    existing_entries = set()
    if file_exists:
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                existing_headers = next(reader, None)
                # Assuming the first N columns uniquely identify a row
                # Adjust the range as per your data structure
                unique_id_indices = range(len(headers) - 2)  # Exclude Date and Status
                for row in reader:
                    unique_id = tuple(row[i] for i in unique_id_indices)
                    existing_entries.add(unique_id)
        except IOError as e:
            print(f"Error reading {csv_file}: {e}")
            return

    # Filter out duplicates
    filtered_new_data = []
    for row in new_data:
        unique_id = tuple(row[i] for i in range(len(headers) - 2))  # Exclude Date and Status
        if unique_id not in existing_entries:
            filtered_new_data.append(row)

    if not filtered_new_data:
        print("No new data to append.")
        return

    # Write data to CSV
    try:
        with open(csv_file, 'a' if file_exists else 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)  # Write header row if file doesn't exist
            writer.writerows(filtered_new_data)  # Write new data rows
        print(f"Data successfully {'appended to' if file_exists else 'written to'} {csv_file}")
    except IOError as e:
        print(f"Error writing to {csv_file}: {e}")

if __name__ == "__main__":
    scrape_lots_project()
