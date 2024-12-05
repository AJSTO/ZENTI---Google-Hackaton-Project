# 📊 ZENTI - Sentiment Analysis - Google Hackathon 2024
This project includes a Google Cloud Function that interacts with Google BigQuery to analyze sentiment and reasons from product reviews. The results are stored in a BigQuery table.

# Looker Visualization
## [ZENTI Looker Dashboard](https://lookerstudio.google.com/u/0/reporting/e0c51a92-f61f-4223-9c37-717941877d10/page/p_xo1b0urjnd/appview)

![Dashboard](ZENTI_Looker_Dashboard.gif)

# 🔍 Overview
### The project consists of a Google Cloud Function:
* `hello_http`: Executes a BigQuery SQL query to analyze sentiment from product reviews and stores the results in a specified BigQuery table.
### Prerequisites
* *Google Cloud Project*: Ensure you have a Google Cloud Project with billing enabled.
* *BigQuery Dataset*: Your project should have the following BigQuery datasets and tables:
  * `reviews` - which is external table of Google Sheet;
  * `Reviews - Wyniki` - table where results are saved;
* *Google Cloud SDK*: Ensure you have the Google Cloud SDK installed and configured.
* *Service Account*: Create a service account in Google Cloud and download the JSON key file.
* *Enable APIs*: Make sure the following APIs are enabled in your Google Cloud project:
  * BigQuery API
  * Cloud Functions API
  * Cloud Build API
# 🔑 Setup 

## Clone repository:
```sh
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```
