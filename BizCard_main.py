#Importing reuired libraries

import streamlit as st
import easyocr
from PIL import Image
import pandas as pd
from sqlalchemy import create_engine, text
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_option_menu import option_menu


# Setup Streamlit home

# Load images
image = Image.open("C:\\Users\\sansu\\OneDrive\\Pictures\\phonepe-logo-icon.jpg")
you_image = Image.open("C:\\Users\\sansu\\OneDrive\\Pictures\\Youtube.png")

#Streamlit page configuration
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_title="BizCardX",
    page_icon=image,
)

# Sidebar configuration
with st.sidebar:
    # Add a horizontal line
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)
    
    # Option menu for the main menu
    selected = option_menu("Main Menu", ["Home", 'Business Card Reader','Overview','Transactions','Users','Trend','Comparison'], 
        icons=['house-door-fill', 'cloud-upload ','bar-chart-fill','credit-card','people-fill','graph-up-arrow', 'tropical-storm'], menu_icon="cast", default_index=0,styles={
        "container": {"padding": "0!important", "background-color": "#242a44"},
        "icon": {"color": "rgb(235, 48, 84)", "font-size": "25px"}, 
        "nav-link": {"font-size": "22px", "color": "#ffffff","text-align": "left", "margin":"0px", "--hover-color": "#84706E"},
        "nav-link-selected": {"background-color": "#84706E  ","color": "white","font-size": "20px"},
    })
    
    # Add a horizontal line
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)


# Adding effects to the Streamlit button
    st.markdown(""" <style> button[data-baseweb="tab"] > di v[data-testid="stMarkdownContainer"] > p {font-size: 28px;} </style>""", unsafe_allow_html=True)
 
    

# Set the title for the main page
st.markdown("<h1 style='text-align: center; font-size: 38px; color: #5f1f9c ; font-weight: 700;font-family:PhonePeSans;'> BizCardX: Extracting Business Card Data with OCR </h1> <h2 style='text-align: right; font-size: 18px; color: #5f1f9c ; font-weight: 350;font-family:PhonePeSans;'/h2>By Santhosh Kumar", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:left; font-size: 38px; color: #5f1f9c ; font-weight: 700;font-family:PhonePeSans;'> BizCardX:</h2> ", unsafe_allow_html=True)
html_Biz = """
    <p style='text-align: left; font-size: 18px; color: #e6e2d3; font-weight: 400;font-family:PhonePeSans;text-indent: 25px;'>
            BizCardX is a business card data extraction tool powered by OCR technology. 
        It efficiently captures information from business cards, such as names, contacts, and addresses. 
        Streamlining data entry, BizCardX automates the digitization of business card content, 
        enhancing organization and accessibility for efficient business communication and networking.
    </p>
"""
st.markdown(html_Biz, unsafe_allow_html=True)

st.markdown("<h2 style='text-align:left; font-size: 38px; color: #5f1f9c ; font-weight: 700;font-family:PhonePeSans;'> About this app:</h2> ", unsafe_allow_html=True)

html_about=""" 
    <p style='text-align: left; font-size: 18px; color: #e6e2d3; font-weight: 400;font-family:PhonePeSans;text-indent: 25px;'>
The project entails developing a Streamlit application enabling users to upload business card images, extract key details using easyOCR, and display them in an intuitive GUI. Users can save the extracted information, including company name, contact details, and location, into a database. The application integrates image processing, OCR, GUI development, and database management for efficient business card information management.

</p>
"""
st.markdown(html_about, unsafe_allow_html=True)


# Add vertical space
add_vertical_space(1)