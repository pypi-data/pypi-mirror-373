import csv
import os
import re
from typing import List


def split_csv(csv_file, output_dir, split_size=10):
    with open(csv_file, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    for i in range(0, len(rows), split_size):
        with open(os.path.join(output_dir, f"{i // split_size}.csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows[i : i + split_size])


# split_csv('raw/shoptalk.csv', 'raw/split')


def merge_csv(folder_path, output_files: List[str], final_file):
    with open(final_file, "w") as f:
        writer = csv.writer(f)
        for file in output_files:
            with open(os.path.join(folder_path, file), "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    writer.writerow(row)


# output_files = [f'{x}_output.csv' for x in range(0,82)]
#
# merge_csv('raw/split', output_files,
#           'raw/split/merged_output.csv')


def remove_duplicate(file_path, newfile):
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    unique_rows = []
    unique_names = []
    for row in rows:
        if row:
            company_name = row[0]
            if company_name:
                company_name = row[0].strip()
                if company_name not in unique_names:
                    unique_rows.append(row)
                    unique_names.append(company_name)

    with open(newfile, "w") as f:
        writer = csv.writer(f)
        writer.writerows(unique_rows)


def cleanup_revenue(file_path, newfile):
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    for row in rows:
        if row:
            if row[3] and row[3].strip():
                revenue = row[3].strip()
                match = re.match(r"([\d\.]+)([A-Za-z]+)", revenue)
                number, letter = match.groups() if match else (None, None)
                if letter == "B":

                    number = float(number) * 1000.0
                if revenue == "N/A":
                    row[3] = ""
                else:
                    row[3] = number

    with open(newfile, "w") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


import csv


def quote_csv(input_path, output_path):
    with open(input_path, "r", newline="", encoding="utf-8") as infile, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
        for row in reader:
            writer.writerow(row)


from openpyxl import Workbook


def csv_to_xlsx(csv_path, xlsx_path):
    wb = Workbook()
    ws = wb.active

    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            ws.append(row)

    wb.save(xlsx_path)


# csv_to_xlsx("raw/final/cleaned_revenue.csv", "raw/final/cleaned_revenue.xlsx")
# quote_csv('raw/final/cleaned_revenue.csv', 'raw/final/CleanedRevenue.csv')
# cleanup_revenue('raw/final/unique_companies.csv', 'raw/final/cleaned_revenue.csv')
# remove_duplicate('raw/split/merged_output.csv', 'raw/final/unique_companies.csv')

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_to(subject: str, content: str, recipient_email: str):
    # Email credentials
    sender_email = "baldev.bishnoi2010@gmail.com"
    sender_password = "dummy"

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg['Cc'] = "devadas.pattathil@onepint.ai, anshuman.jaiswal@onepint.ai, shivani.gupta@onepint.ai, krishna.balasubramani@onepint.ai"

    # Attach the email content
    msg.attach(MIMEText(content, 'plain'))

    try:
        # Connect to the Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return "Email sent successfully"
    except Exception as e:
        print(e)
        return f"Failed to send email: {str(e)}"

# response = send_email("test subject", "dynamic content", "baldev.bishnoi@onepint.ai")