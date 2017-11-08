#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
from bs4 import BeautifulSoup
import csv
import re

# Read the config file
config = configparser.ConfigParser()
config.read('config.ini')

BASE_DIR = config.get('sympa', 'base_dir')
SERVER_NAME = config.get('sympa', 'server_name')
BASE_URL = config.get('sympa', 'base_url')
OUTPUT_FILE = config.get('sympa', 'output_file')
MAILING_LISTS = config.get('sympa', 'mailing_lists').split(',')
all_files = []

mail_pattern = re.compile("^msg\d{5}$")

for ml in MAILING_LISTS:
    print("Parsing emails from {}@{} mailing list".format(ml, SERVER_NAME))
    ml_dir = BASE_DIR + '/' + ml + '@' + SERVER_NAME

    months = os.listdir(ml_dir)

    for m in months:
        monthly_dir = ml_dir + '/' + m
        for entry in os.listdir(monthly_dir):

            """
            If there a mail has an attachment, there will will be both
            a msgXXXXX dir along the msgXXXXX.html file, so for each
            msgXXXXX dir, we parse the matching html file.
            """
            if mail_pattern.match(entry):
                mail_file = entry + '.html'
                email_file = monthly_dir + '/' + mail_file

                with open(email_file, 'r') as f:
                    webpage = f.read()
                    soup = BeautifulSoup(webpage, 'html.parser')

                    current_mail = {}
                    current_mail['URL'] = BASE_URL + m + '/' + mail_file

                    for i in soup.find_all('li'):
                        if hasattr(i, 'strong') and hasattr(i.strong, 'text'):
                            fieldname = i.strong.text

                            if fieldname in ['Date', 'To', 'From', 'Subject']:
                                start = len(fieldname) + 2
                                current_mail[fieldname] = i.text[start:]

                    for i in soup.find_all('p'):
                        if 'Attachment:' in i.text:
                            current_file = current_mail.copy()
                            current_file['Attachment'] = i.a.text

                    all_files.append(current_file)

with open(OUTPUT_FILE, 'w') as csvfile:
    fieldnames = [
        'Date',
        'Subject',
        'From',
        'To',
        'Attachment',
        'URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for f in all_files:
        writer.writerow(f)
