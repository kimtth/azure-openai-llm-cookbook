import os
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from openai import AzureOpenAI


AZURE_OPENAI_API_KEY = "your-api-key"  # Replace with your OpenAI API key
AZURE_OPENAI_MODEL_NAME = "your-model-name"  # Vision model for image analysis
AZURE_OPENAI_API_VERSION = "your-api-version"  # API version for OpenAI
AZURE_OPENAI_ENDPOINT = "your-endpoint"  # Azure endpoint for OpenAI

AZURE_DEVOPS_PAT = "your-pat"  # Azure DevOps Personal Access Token
AZURE_DEVOPS_ORG_URL = "your-org-url"  # Azure DevOps organization URL
AZURE_DEVOPS_PROJECT = "DemoProject"  # Azure DevOps project name


def create_user_stories():
    """
    Creates sample user stories in an Azure DevOps project
    """
    # Setup authentication
    personal_access_token = os.getenv("AZURE_DEVOPS_PAT", AZURE_DEVOPS_PAT)
    organization_url = os.getenv("AZURE_DEVOPS_ORG_URL", AZURE_DEVOPS_ORG_URL)

    if not personal_access_token or not organization_url:
        print(
            "Error: Azure DevOps PAT and organization URL must be set as environment variables."
        )
        return []

    credentials = BasicAuthentication("", personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)

    # Get work item tracking client
    work_client = connection.clients.get_work_item_tracking_client()

    # Use existing project
    project_name = os.getenv("AZURE_DEVOPS_PROJECT", AZURE_DEVOPS_PROJECT)
    print(f"Using project: {project_name}")
    # Check if project exists and if it has user stories
    try:
        # Check if user stories already exist in the project
        wiql_query = """
            SELECT [System.Id]
            FROM workitems
            WHERE [System.TeamProject] = '{}'
            AND [System.WorkItemType] = 'User Story'
        """.format(
            project_name
        )

        wiql_results = work_client.query_by_wiql(wiql_query)

        if wiql_results.work_items:
            print(
                f"User stories already exist in project '{project_name}'. Skipping creation."
            )
            work_item_ids = [int(item.id) for item in wiql_results.work_items]
            existing_work_items = work_client.get_work_items(work_item_ids)
            return existing_work_items

    except Exception as e:
        print(f"Error checking for existing user stories: {str(e)}")
        return []

    # Create sample user stories
    user_stories = [
        {
            "title": "User can login to the system",
            "description": "As a user, I want to login to the system so that I can access my account",
            "priority": 1,
            "state": "New",
        },
        {
            "title": "User can view dashboard",
            "description": "As a user, I want to view a dashboard so that I can see an overview of my data",
            "priority": 2,
            "state": "Active",
        },
        {
            "title": "User can reset password",
            "description": "As a user, I want to reset my password so that I can regain access if I forget it",
            "priority": 3,
            "state": "New",
        },
        {
            "title": "Admin can manage users",
            "description": "As an admin, I want to manage user accounts so that I can help users with account issues",
            "priority": 1,
            "state": "Resolved",
        },
        {
            "title": "User can update profile",
            "description": "As a user, I want to update my profile information so that my details are current",
            "priority": 2,
            "state": "Closed",
        },
    ]

    created_work_items = []
    for story in user_stories:
        document = [
            {"op": "add", "path": "/fields/System.Title", "value": story["title"]},
            {
                "op": "add",
                "path": "/fields/System.Description",
                "value": story["description"],
            },
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Common.Priority",
                "value": story["priority"],
            },
            {"op": "add", "path": "/fields/System.State", "value": story["state"]},
        ]

        try:
            # Create the work item
            work_item = work_client.create_work_item(
                document=document, project=project_name, type="User Story"
            )

            created_work_items.append(work_item)
            print(f"Created User Story: {story['title']}")
        except Exception as e:
            print(f"Failed to create user story '{story['title']}': {str(e)}")

    print(f"Created {len(created_work_items)} user stories successfully.")
    return created_work_items


def fetch_and_summarize_progress():
    """
    Fetches user stories from Azure DevOps and summarizes project progress using Azure OpenAI
    """
    # Setup authentication for Azure DevOps
    personal_access_token = os.getenv("AZURE_DEVOPS_PAT", AZURE_DEVOPS_PAT)
    organization_url = os.getenv("AZURE_DEVOPS_ORG_URL", AZURE_DEVOPS_ORG_URL)

    credentials = BasicAuthentication("", personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)

    # Get work item tracking client
    work_client = connection.clients.get_work_item_tracking_client()

    # Use existing project
    project_name = os.getenv("AZURE_DEVOPS_PROJECT", AZURE_DEVOPS_PROJECT)

    # Query for all user stories in the project
    wiql_query = """
        SELECT [System.Id], [System.Title], [System.State], [System.Tags]
        FROM workitems
        WHERE [System.TeamProject] = '{}'
        AND [System.WorkItemType] = 'User Story'
        ORDER BY [System.Id]
    """.format(
        project_name
    )

    wiql_results = work_client.query_by_wiql(wiql_query)

    # If we have user stories
    if wiql_results.work_items:
        work_item_ids = [int(item.id) for item in wiql_results.work_items]
        work_items = work_client.get_work_items(work_item_ids)

        # Prepare data for the OpenAI model
        user_stories_data = []
        for work_item in work_items:
            user_stories_data.append(
                {
                    "id": work_item.id,
                    "title": work_item.fields["System.Title"],
                    "state": work_item.fields["System.State"],
                    "tags": work_item.fields.get("System.Tags", ""),
                }
            )

        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY", AZURE_OPENAI_API_KEY),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", AZURE_OPENAI_API_VERSION),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", AZURE_OPENAI_ENDPOINT),
        )

        # Create messages for the OpenAI model
        messages = [
            {
                "role": "system",
                "content": "You are a project management assistant. Analyze the provided user stories and summarize the project progress.",
            },
            {
                "role": "user",
                "content": f"Analyze these user stories and provide a summary of project progress: {user_stories_data}. Include overall status, completion percentage, key areas, and next steps.",
            },
        ]

        # Call Azure OpenAI for summary
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_MODEL_NAME", AZURE_OPENAI_MODEL_NAME),
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )

        # Print the summary
        print("\nProject Progress Summary:")
        print(response.choices[0].message.content)
    else:
        print("No user stories found in the project.")


def main():
    print("Azure DevOps Project Management Tool")
    print("-" * 40)

    # Part 1: Create user stories
    print("\nPart 1: Creating sample user stories...")
    create_user_stories()

    # Part 2: Fetch and summarize progress
    print("\nPart 2: Fetching and summarizing project progress...")
    fetch_and_summarize_progress()


if __name__ == "__main__":
    main()
