#!/usr/bin/python3
import json
import os
import argparse
from collections import Counter

# Function to set up command-line arguments
def setup_arg_parser():
    parser = argparse.ArgumentParser(description='Generate a report on the top email senders.')
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing the email JSON files')
    parser.add_argument('--top_n', type=int, default=10, help='Number of top senders to display')
    return parser.parse_args()

# Function to read and process email files
def process_email_files(input_dir, top_n):
    sender_count = Counter()
    total_records = 0

    # Process each file in the directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.json'):
            with open(os.path.join(input_dir, file_name), 'r') as file:
                emails = json.load(file)
                total_records += len(emails)
                for email in emails:
                    sender = email.get('sender', {}).get('emailAddress', {}).get('address', '')
                    if sender:
                        sender_count[sender] += 1

    # Display top N senders and their total email counts
    print(f"Top {top_n} Email Senders:")
    top_senders_total = 0
    for sender, count in sender_count.most_common(top_n):
        print(f"{sender}: {count} emails")
        top_senders_total += count

    # Display total emails by top senders
    print(f"\nTotal Emails by Top {top_n} Senders: {top_senders_total}")

    # Display total number of records processed
    print(f"Total Email Records Processed: {total_records}")

# Main process
def main():
    args = setup_arg_parser()
    process_email_files(args.input_dir, args.top_n)

# Run the main process
if __name__ == "__main__":
    main()
