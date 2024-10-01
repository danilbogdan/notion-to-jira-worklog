import os
from notion_client import Client
import requests
from requests.auth import HTTPBasicAuth
import json
from dateutil import parser
import pytz
import dotenv

dotenv.load_dotenv()

# Setting up Notion client
notion_api_key = os.getenv("NOTION_API_KEY")
notion = Client(auth=notion_api_key)
database_id = os.getenv("DATABASE_ID")

# Setting up Jira access
jira_server_url = os.getenv("JIRA_SERVER")
jira_username = os.getenv("JIRA_USERNAME")
jira_password = os.getenv("JIRA_PASSWORD")
auth = HTTPBasicAuth(jira_username, jira_password)
headers = {"Content-Type": "application/json"}


# Function to fetch all pages from Notion database
def fetch_notion_pages(notion, database_id):
    pages = []
    next_cursor = None
    while True:
        response = notion.databases.query(
            database_id=database_id,
            start_cursor=next_cursor,
            filter={"property": "Synced", "checkbox": {"equals": False}},
        )
        pages.extend(response["results"])
        next_cursor = response.get("next_cursor")
        if not response.get("has_more"):
            break
    return pages


# Fetch data from Notion
pages = fetch_notion_pages(notion, database_id)

for page in pages:
    page_id = page['id']
    properties = page["properties"]

    try:
        description = properties["Name"]["title"][0]["plain_text"]
        url = properties["URL"]["url"]
        issue_key = url.split("/")[-1]
        date = properties["Date"]["date"]["start"]
        hours_spent = properties["time spent (h)"]["number"]
    except Exception as e:
        print(f"Missing property in Notion page: {e}")
        continue

    # Convert time spent to Jira format
    hours = int(hours_spent)
    minutes = int(round((hours_spent - hours) * 60))
    time_spent = ""
    if hours > 0:
        time_spent += f"{hours}h "
    if minutes > 0:
        time_spent += f"{minutes}m"
    time_spent = time_spent.strip()

    # Format date to required Jira format
    date_obj = parser.isoparse(date)
    if date_obj.tzinfo is None:
        date_obj = date_obj.replace(tzinfo=pytz.UTC)
    date_formatted = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%f%z")[:-2] + "00"

    # Prepare data for request
    data = {"comment": description, "started": date_formatted, "timeSpent": time_spent}

    # URL to add worklog in Jira
    url = f"{jira_server_url}/rest/api/2/issue/{issue_key}/worklog"

    # Send POST request to Jira
    response = requests.post(url, auth=auth, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        print(f'Successfully added time for issue {issue_key}')
        
        # Update 'Synced' property in Notion to True
        update_response = notion.pages.update(
            page_id=page_id,
            properties={
                "Synced": {
                    "checkbox": True
                }
            }
        )
        if update_response:
            print(f"Issue {issue_key} marked as synced in Notion.")
    else:
        print(f"Error adding time for issue {issue_key}: {response.status_code} {response.text