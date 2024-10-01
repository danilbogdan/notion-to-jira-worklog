# Notion-Jira Sync

## Overview

This script automates the synchronization of work logs between Notion and Jira. It fetches data from a specified Notion database, processes the data, and then updates Jira issues with the respective time spent.

## Prerequisites

1. Python 3.x
2. Required Python packages (`notion_client`, `requests`, `python-dotenv`, `python-dateutil`, `pytz`)

## Installation

1. Clone the repository or download the script.
2. Install the required packages using pip:

    ```bash
    pip install notion-client requests python-dotenv python-dateutil pytz
    ```

3. Create a `.env` file in the same directory as the script with the following content:

    ```ini
    NOTION_API_KEY=your_notion_api_key
    DATABASE_ID=your_notion_database_id
    JIRA_SERVER=https://your_jira_server
    JIRA_USERNAME=your_jira_username
    JIRA_PASSWORD=your_jira_password
    ```

## Usage

Run the script:

```bash
python notion_to_jira.py
```

The script performs the following actions:

1. Fetches all pages from the specified Notion database where the `Synced` property is `False`.
2. For each page:
   - Extracts the description, URL, date, and time spent.
   - Formats the date and time spent to the format required by Jira.
   - Adds a work log entry to the corresponding Jira issue.
   - Updates the `Synced` property in Notion to `True`.

## Script Breakdown

### Setting Up Environment

The script initializes by loading environment variables from the `.env` file and setting up clients for Notion and Jira.

### Fetching Data From Notion

The `fetch_notion_pages` function queries the Notion database and returns all pages that have not been synced yet.

### Processing Each Page

For each fetched page, the script extracts necessary information, formats it appropriately, and sends a POST request to Jira to add a work log entry.

### Updating Notion Pages

After successfully adding a work log entry to Jira, the script updates the `Synced` property in the Notion database to prevent duplicate entries.

## Error Handling

The script includes basic error handling to catch and report missing properties in Notion pages and unsuccessful responses from Jira.

## Contribution

Feel free to fork the repository and make improvements. Pull requests are welcome!

## License

This project is licensed under the MIT License.

---
