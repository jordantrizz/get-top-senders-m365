#!/usr/bin/python3
import requests
import json
import argparse
import configparser

# Function to set up command-line arguments
def setup_arg_parser():
    parser = argparse.ArgumentParser(description='Fetch emails from Microsoft 365 and save to files.')
    parser.add_argument('--output', type=str, default='emails_batch', help='Base name for output files')
    parser.add_argument('--batch_size', type=int, default=1000, help='Number of records per file')
    parser.add_argument('--max_records', type=int, default=18000, help='Total number of records to process')
    parser.add_argument('--debug', action='store_true', help='Enable debugging output')
    return parser.parse_args()

# Function to read configuration file
def read_config(file_name):
    config = configparser.ConfigParser()
    config.read(file_name)
    return config['DEFAULT']

# Function to get token
def get_access_token(client_id, client_secret, tenant_id, debug):
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': f'{RESOURCE}/.default'
    }
    response = requests.post(url, headers=headers, data=data)
    if debug:
        print(f"Token response: {response.text}")
    return response.json().get('access_token')

# Function to get and save emails
def get_and_save_emails(token, endpoint, file_name, debug):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(endpoint, headers=headers)
    if debug:
        print(f"Email fetch response: {response.text}")

    if response.status_code == 200:
        data = response.json()
        next_link = data.get('@odata.nextLink')
        emails = data.get('value', [])

        # Save emails to a file
        with open(f'{file_name}.json', 'w') as file:
            json.dump(emails, file)

        return next_link
    else:
        print(f"Failed to fetch emails: {response.status_code}")
        return None

# Main process
def main():
    args = setup_arg_parser()
    config = read_config('getfrom.conf')

    token = get_access_token(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID'], args.debug)
    endpoint = f"{config['RESOURCE']}/{config['API_VERSION']}/users/{config['TARGET_USER']}/mailFolders/Inbox/messages?$top={args.batch_size}&$select=sender"
    file_counter = 1
    total_records = 0

    while endpoint and total_records < args.max_records:
        print(f"Fetching batch {file_counter}...")
        next_link = get_and_save_emails(token, endpoint, f'{args.output}_{file_counter}', args.debug)
        file_counter += 1
        total_records += args.batch_size
        endpoint = next_link if next_link and total_records < args.max_records else None

# Run the main process
if __name__ == "__main__":
    main()
