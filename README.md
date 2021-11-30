## About The Project
The app is scraping the website shopee.com, collecting new negative reviews from a particular shop, and then sending it with an email.

## Details
While scraping the website app creating a review_list.json file, or if it already exists refresh it with the last available review to track changes.
If the review_list.json file is missing, scraping is limited to 20 pages.
For email sending, there is a shopeereviewnotification@gmail.com mailbox already created. It is recommended to change the password and make changes in the main review_notification.py file respectively.

## Prerequisites
pip install -r requirements.txt
Type in desirable receiver mailbox name in the main review_notification.py file.