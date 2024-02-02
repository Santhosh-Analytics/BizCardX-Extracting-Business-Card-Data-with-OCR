# <div align="center"> Business Card OCR and Database Integration with Streamlit Project</div>
<div align="center"> A user-friendly application to digitize business card data using OCR and manage it in a database.</div>


## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Technical Details](#technical-details)
- [Demo/Presentation Video](#demopresentation-video)
- [Contribution](#contribution)
- [Contact](#contact)


## Overview

This project simplifies the process of extracting and managing information from business cards using optical character recognition (OCR) and a user-friendly Streamlit interface. It empowers users to:

- Upload business card images
- Extract relevant information using easyOCR
- View extracted information in a clear format
- Save information to a database (SQLite or MySQL)
- Read, update, and delete stored data through the Streamlit UI

## Problem Statement
Develop a Streamlit application that allows users to upload a business card image, extract relevant information using easyOCR, and store it in a database. The extracted details include company name, card holder name, designation, mobile number, email, website, area, city, state, and pin code. Users should be able to manage data through the Streamlit UI, including reading, updating, and deleting entries.
-Design User Interface: Use Streamlit to create an intuitive UI. Include widgets like file uploader, buttons, and text boxes for interaction.
-Implement Image Processing and OCR: Utilize easyOCR to extract information from uploaded business card images.Apply image processing techniques for quality enhancement.

## Prerequisites
Before you begin, ensure you have met the following requirements:

- Python: Version 3.11.0 or higher. [Download Python](https://www.python.org/downloads/)
- Streamlit, easyOCR: Install using pip:
- Database Management System: SQLite or MySQL. [SQLite Installation Guide](https://www.sqlite.org/download.html) | [MySQL Installation Guide](https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/)
- Git: Version control tool. [Download Git](https://git-scm.com/downloads)
- Install dependencies: `pip install -r requirements.txt`

## Testing the Application Locally
1. Clone the repository: `git clone https://github.com/yourusername/your-repo.git`
2. Navigate to the project directory: `cd your-repo`
3. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `streamlit run app.py`
6. Ensure you use your SQL credentials.

## Contact
If you have any questions or feedback, feel free to reach out at [email](mailto:santhosh90612@gmail.com).
