#Importing reuired libraries

import streamlit as st
from easyocr import Reader
from streamlit_option_menu import option_menu
import os
import tempfile
import cv2
from dotenv import load_dotenv
from PIL import Image
import pymysql
from pymysql import Error
import re
import pandas as pd
import streamlit_pandas as sp
from io import BytesIO
import io
import filetype  




# Setup Streamlit home

# Load images
image = Image.open("ssss.png")

#Streamlit page configuration
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_title="BizCardX",
    page_icon=image,
)

page_bg_img = '''
<style>
    .stApp {
        background-image:url("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwallpaperset.com%2Fw%2Ffull%2Fc%2F4%2F2%2F2932.jpg&f=1&nofb=1&ipt=167b8ede7fb9039711212e5ae543004922bc451239b539ed9d447699ccab439d&ipo=images")
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
</style> 
'''

def number_widget_int(df, column, ss_name):
    """Create a number widget with integer values."""
    min_value = df[column].min()
    max_value = df[column].max()

    # Check if the min and max values are equal
    if min_value == max_value:
        # If they are equal, display a fixed value using st.sidebar.number_input
        temp_input = st.sidebar.number_input(
            f"{column.title()}",
            min_value=min_value,
            max_value=max_value,
            value=min_value,
            key=ss_name
        )
    else:
        # Create a slider for a range of values
        temp_input = st.sidebar.slider(
            f"{column.title()}",
            min_value=min_value,
            max_value=max_value,
            value=(min_value, max_value),
            key=ss_name
        )

    return temp_input

users = {
    "San": "san12",
    "Admin": "admin12"
}

def authenticate(username, password):
    """Authenticate user credentials."""
    return username in users and users[username] == password

def login():
    """Login page logic."""
    st.title("Login Page")

    # Initialize session state for login status if it doesn't exist
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # If the user is already logged in, display the success message and redirect
    elif st.session_state.logged_in:
        st.success("You are already logged in!")
        st.write("Welcome to the application!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()  # Refresh to show the login page again

    else:
        # Display the login input fields
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.success("Login successful!")
                st.session_state.logged_in = True
                if "username" not in st.session_state:
                    st.session_state.username = username
                st.rerun()  # Refresh to show the Home page
            else:
                st.error("Invalid username or password")

# Adding effects to the Streamlit button using CSS
st.markdown("""
<style>
.stButton button {
    background-color: #3498db !important;
    color: #ffffff !important;
    font:verdana !important;
    font-size: 20px !important;
    height: 2.5em !important;
    width: 10em !important;
    border-radius: 15px !important;
    transition: background-color 0.3s ease !important;
}
.stButton button:hover {
    background-color: darkgreen !important;
    font:verdana !important;
    color: #ffffff !important;
}

.stButton button:focus:not(:active) {
    border-color: #ffffff !important;
    box-shadow: none !important;
    color: #ffffff !important;
    background-color: #0066cc !important;
}

.stButton button:focus:active {
    background-color: darkgreen !important;
    border-color: #ffffff !important;
    box-shadow: none !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)


def main_menu():
    
    username = st.session_state.get("username", "Guest")
    
    st.markdown(
        f"""
        <div style='text-align: right; color:#BCFD4C; font-size:20px;'>
            Welcome to the Bizcardx app, {username}!
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
        


    # Heading for all pages
    st.markdown("<h1 style='text-align: center; font-size: 38px; color: #BCFD4C ; font-weight: 700;font-family:Arial;'> BizCardX: Extracting Business Card Data with OCR </h1> ", unsafe_allow_html=True)
        
    # Add a horizontal line
    st.markdown("<hr style='border: 2px solid #ffffff;'>", unsafe_allow_html=True)



    # Sidebar configuration
    with st.sidebar:
        
        # Add a horizontal line
        st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)
        
        # Option menu for the main menu
        selected = option_menu("Main Menu", ["Home", 'Card Reader','Data Hub',], 
            icons=['house-door-fill', 'cloud-upload ','pencil-square'], menu_icon="cast", default_index=0,styles={
            "container": {"padding": "12!important", "background-color": "Teal"},
            "icon": {"color": "rgb(235, 48, 84)", "font-size": "25px","font-family": "JetBrainsMono Nerd Font",}, 
            "nav-link": {"font-size": "22px", "color": "#ffffff","text-align": "left", "margin":"0px", "--hover-color": "#84706E"},
            "nav-link-selected": {"background-color": "darkgreen","color": "white","font-size": "20px"},
        })
        
        st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)
        
    # Defining functions

    load_dotenv()

    db_user = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = 'bizcardx'


    # function to create table and database if not exists 
    def create_db_table():
        try:
            mydb = pymysql.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            
            with mydb.cursor() as mycur:
                # Create the database if it doesn't exist
                create_db_sql = f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                mycur.execute(create_db_sql)
                
                use_db_sql = f"USE {db_name}"
                mycur.execute(use_db_sql)
                
                # Create the table
                create_table_sql = '''CREATE TABLE IF NOT EXISTS card_data (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    company_name TEXT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email VARCHAR(255),
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code VARCHAR(10),
                    image LONGBLOB
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'''
                mycur.execute(create_table_sql)
                
            mydb.commit()
            return mydb
        except Error as e:
            st.error(f"The error '{e}' occurred")
            print(f"Full error details: {str(e)}")
            return None

    def compare_records(existing_record, new_record):
        """Compare two records and return True if they are different"""
        fields_to_compare = [
            'company_name', 'card_holder', 'designation', 'mobile_number',
            'website', 'area', 'city', 'state', 'pin_code'
        ]
        
        for field in fields_to_compare:
            if str(existing_record.get(field)) != str(new_record.get(field)):
                return True
        return False

    def process_record(db, row):
        """Process a single record - check if it exists and handle accordingly"""
        try:
            with db.cursor() as cur:
                # First, check if a record with this email exists
                check_query = """SELECT * FROM card_data WHERE email = %s"""
                cur.execute(check_query, (row['email'],))
                existing_record = cur.fetchone()
                
                if existing_record:
                    # Convert row to dict for comparison
                    new_record = {
                        'company_name': row['company_name'],
                        'card_holder': row['card_holder'],
                        'designation': row['designation'],
                        'mobile_number': row['mobile_number'],
                        'website': row['website'],
                        'area': row['area'],
                        'city': row['city'],
                        'state': row['state'],
                        'pin_code': row['pin_code']
                    }
                    
                    # Check if any fields are different
                    if compare_records(existing_record, new_record):
                        # Update the existing record
                        update_query = """UPDATE card_data 
                            SET company_name=%s, card_holder=%s, designation=%s, 
                                mobile_number=%s, website=%s, area=%s, city=%s, 
                                state=%s, pin_code=%s, image=%s
                            WHERE email=%s"""
                        update_data = (
                            row['company_name'], row['card_holder'], row['designation'],
                            row['mobile_number'], row['website'], row['area'],
                            row['city'], row['state'], row['pin_code'], row['image'],
                            row['email']
                        )
                        cur.execute(update_query, update_data)
                        db.commit()
                        return "updated"
                    else:
                        return "unchanged"
                else:
                    # Insert new record
                    insert_query = """INSERT INTO card_data(
                        company_name, card_holder, designation, mobile_number, 
                        email, website, area, city, state, pin_code, image
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    insert_data = (
                        row['company_name'], row['card_holder'], row['designation'],
                        row['mobile_number'], row['email'], row['website'],
                        row['area'], row['city'], row['state'], row['pin_code'],
                        row['image']
                    )
                    cur.execute(insert_query, insert_data)
                    db.commit()
                    return "inserted"
        except Error as e:
            st.error(f"Error processing record: {e}")
            return "error"

   



    # function to upload processed data to SQL database
    def query_db(mydb, query, data):
        if mydb is None:
            st.error("Database connection was not established.")
            return False  # Return a status indicating failure

        try:
            with mydb.cursor() as cur:
                # Check if the input data is a DataFrame
                if isinstance(data, pd.DataFrame):
                    # Loop through the DataFrame rows
                    for i in range(data.shape[0]):
                        data_to_insert = tuple(data.iloc[i])
                        cur.execute(query, data_to_insert)
                elif isinstance(data, list):
                    # If data is a list, loop through each record
                    for record in data:
                        data_to_insert = tuple(record)
                        cur.execute(query, data_to_insert)
                else:
                    st.error("Unsupported data format. Please provide a DataFrame or list.")
                    return False  # Return a status indicating failure

            # Commit all the changes once
            mydb.commit()
            return True  # Return a status indicating success
        except Error as e:
            st.error(f"An error occurred while inserting data: {e}")
            return False  # Return a status indicating failure
        
                    
    #function to convert image to binary file
    def img_to_bin(file):
        with open(file,'rb') as file:
            return file.read()
        
    # Creating empty list to append the data
    data = {"company_name" : [],
    "card_holder" : [],
    "designation" : [],
    "mobile_number" :[],
    "email" : [],
    "website" : [],
    "area" : [],
    "city" : [],
    "state" : [],
    "pin_code" : [],
    "image" : None
    }


    # Appending the extracted data dictionary
    def ocr_to_dict(long, short):
        data = {"company_name" : [],
        "card_holder" : [],
        "designation" : [],
        "mobile_number" :[],
        "email" : [],
        "website" : [],
        "area" : [],
        "city" : [],
        "state" : [],
        "pin_code" : [],
        "image" : None
        }

        pattern1 = r'\b(St|st)\b'
        pattern2 = r'\d{3}\s+[a-zA-Z]{3,}\b'
        pattern = re.compile(r'\b\d{3}\s+[a-zA-Z]+\s+st\b|\bst\s+\d{3}\s+[a-zA-Z]+\b')

        data['company_name'] = short[0].title()
        data['card_holder'] = long[0].title()
        data["designation"] = long[1].title()
        data["mobile_number"] = [i for i in long if '-' in i]
        if len(data["mobile_number"]) > 1:
            data["mobile_number"] = ', '.join(data["mobile_number"])
        data["email"] = [i.lower() for i in long if '@' in i]
        data["website"] = [i.lower().replace('www ', 'www.').replace(' ', '') for i in long if 'www' in i.lower() and 'com' in i.lower()]
        state_pattern = re.compile(r'tamilnadu', re.IGNORECASE)
        data["state"] = [match.group() for item in long for match in [state_pattern.search(item)] if match]
        pin_pattern = re.compile(r'\b\d{6,7}\b')
        data["pin_code"] = [match.group() for i in long for match in [pin_pattern.search(i)] if match]
        data["image"] = img_to_bin(uploaded_card_path)

        for i in long:
            match1 = re.findall('.+St,, ([a-zA-Z]+).+', i)
            match2 = re.search(r'\b([A-Z][a-z]{4,}),\s*$', i)
            match4 = re.findall(r',\s(.*?);', i)
            if match1:
                data["city"].extend(word.title()for word in match1)
            
            elif match2:
                data["city"].append(match2.group(1).title())
            
            elif match4:
                data["city"].extend(word.title()for word in match4)


            if re.search(pattern1, i) and not any(re.search(pattern1, item) for item in data['area']):
                data['area'].append(i.lower())

            if re.search(pattern2, i) and not any(re.search(pattern2, item) for item in data['area']):
                data['area'].append(i)

        data['area'] = " ".join(data['area']).strip().replace(',', '')

        match = pattern.search(data["area"])
        if match:
            data["area"] = match.group()

        if not data['website']:
            for ind, val in enumerate(long):
                if 'www' in val.lower() and '.com' in long[ind+1]:
                    data['website'] = [f'www.{long[ind+1]}']
        if data['website'] and 'com' in data['website'][0] and '.com' not in data['website'][0]:
            data['website'][0] = data['website'][0].replace('com', '.com', 1)
        elif data['website'] and 'com' not in data['website'][0]:
            data['website'][0] = '.'.join(data['website'][0].split('.')[:-1]) + '.com'

        return data


    # Display Image with Detected Text and Bounding Boxes
    def image_preview(image,res): 
        for (bbox, text, prob) in res: 
    # unpack the bounding box
            (tl, tr, br, bl) = bbox
            tl = (int(tl[0]), int(tl[1]))
            tr = (int(tr[0]), int(tr[1]))
            br = (int(br[0]), int(br[1]))
            bl = (int(bl[0]), int(bl[1]))
            cv2.threshold(image, 120, 300, cv2.THRESH_BINARY)
            cv2.rectangle(image, tl, br, (0, 255, 0), 2)
            cv2.putText(image, text, (tl[0], tl[1] - 10), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        st.image(image, caption='Processed Image', use_column_width=True)

    # Pulling data from MySQL DB
    def get_data_sql():
        try:
            with  pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
            ) as mydb:
                mycur = mydb.cursor()
                mycur.execute("select * from card_data")
                sql_data=mycur.fetchall()
            if sql_data:
                columns = ["ID",  "Company Name", "Card Holder", "Designation", "Mobile Number", "Email", "Website", "Address", "City", "State", "ZipCode","Image"]
                df=pd.DataFrame(sql_data,columns=columns)
                
                return df
            else:
                pass
                # st.write("No data found in the 'card_data' table.")

        except Error as e:
            st.write(e,'get')

    # def get_data_sql():
    #   try:
    #     with  mysql.connector.connect(
    #       host='localhost',
    #       user='root',
    #       password=PASSWORD,
    #       database='bizcardx'
    #       ) as mydb:
    #       mycur = mydb.cursor()
    #       mycur.execute("select * from card_data")
    #       sql_data=mycur.fetchall()
    #       if sql_data:
    #         columns = ["ID",  "Company Name", "Card Holder", "Designation", "Mobile Number", "Email", "Website", "Address", "City", "State", "ZipCode","Image"]
    #         df=pd.DataFrame(sql_data,columns=columns)
            
    #         return df
    #       else:
    #         st.write("No data found in the 'card_data' table.")

    #   except Error as e:
    #      st.write(e)

    # getting selected record data from SQL
    def sql_df():
        mydb = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        mycur = mydb.cursor()
        mycur.execute("SELECT Card_Holder, id FROM card_data")
        resu = mycur.fetchall()
        return resu, mycur, mydb


    if selected == "Home":

        # Set the title for the main page
        st.markdown("<h2 style='text-align:left; font-size: 38px; color: #BCFD4C ; font-weight: 500;font-family:Arial;'> BizCardX:</h2> ", unsafe_allow_html=True)

        # about business card
        html_Biz = """
            <p style='text-align: left; font-size: 18px; color: #ffffff; font-weight: 400;font-family:verdana;text-indent: 25px;'>
                    BizCardX is a business card data extraction tool powered by OCR technology. 
                It efficiently captures information from business cards, such as names, contacts, and addresses. 
                Streamlining data entry, BizCardX automates the digitization of business card content, 
                enhancing organization and accessibility for efficient business communication and networking.
            </p>
        """
        st.markdown(html_Biz, unsafe_allow_html=True)


        #sub heading
        st.markdown("<h2 style='text-align:left; font-size: 38px; color: #BCFD4C ; font-weight: 500;font-family:Arial;'> About this app:</h2> ", unsafe_allow_html=True)

        html_about=""" 
            <p style='text-align: left; font-size: 18px; color: #ffffff; font-weight: 400;font-family:verdana;text-indent: 25px;'>
        The project entails developing a Streamlit application enabling users to upload business card images, extract key details using easyOCR, and display them in an intuitive GUI. Users can save the extracted information, including company name, contact details, and location, into a database. The application integrates image processing, OCR, GUI development, and database management for efficient business card information management.

        </p>
        """
        st.markdown(html_about, unsafe_allow_html=True)


    #Creating object for easy ocr
    
    reader = Reader(['en'],gpu=True)
    if selected == "Card Reader":
        
        all_data = []
        
    
        st.markdown("<h5 style='text-align:left; font-size: 28px; color: #ffffff ; font-weight: 200;font-family:verdana;'> Choose a business card image:</h5>", unsafe_allow_html=True)
        uploaded_cards = st.file_uploader(label="Choose an image file with an extension png, jpeg, jpg:",label_visibility="visible",type=["png","jpeg","jpg"], accept_multiple_files=True)
        st.markdown("<hr style='border: 2px solid #ffffff;'>", unsafe_allow_html=True)

        if uploaded_cards:
            
            for card in uploaded_cards:
                read_col, view_col=st.columns([1,1])
                read_col.markdown(f""" <div style='text-align:left; font-size: 18px; color: #ffffff ;padding: 5px;font-weight: 100;font-family:verdana;'>You have uploaded {card.name}.  You can verify the image down here 👇</div>""",unsafe_allow_html=True)
                read_col.write(" ")
                st.markdown("<hr style='border: 2px solid #ffffff;'>", unsafe_allow_html=True)
                read_col.image(card,caption='Uploaded Image')

                with view_col:
                    with st.spinner('Wait for loading  your image...'):
                        # st.set_option('deprecation.showPyplotGlobalUse', False)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                            temp_file.write(card.read())
                            uploaded_card_path = temp_file.name


                        image = cv2.imread(uploaded_card_path)
                        result = reader.readtext(uploaded_card_path,decoder='greedy')
                        
                        
                        view_col.markdown(f""" <div style='text-align:left; font-size: 18px; color: #ffffff ;padding: 5px;font-weight: 100;font-family:verdana;'>You can see the processed version of your image  down here 👇</div>""",unsafe_allow_html=True)
                        view_col.write(" ")
                        image_preview(image,result)
                    
                        st.write()

                        crop_img=cv2.imread(uploaded_card_path)
                        crop_l=crop_img[:,:450  ]
                        crop_r=crop_img[:,451:]
                        grayl = cv2.cvtColor(crop_l, cv2.COLOR_BGR2GRAY)
                        grayr = cv2.cvtColor(crop_r, cv2.COLOR_BGR2GRAY)

                        ret,threshl =   cv2.threshold(grayl, 255,120, cv2.THRESH_TOZERO_INV)
                        ret,threshr=    cv2.threshold(grayr, 300, 120, cv2.THRESH_TOZERO_INV)
                        resl=reader.readtext(threshl,detail=0,paragraph=False)
                        resr=reader.readtext(threshr,detail=0,paragraph=False)

                


                        # plt.rcParams['figure.figsize'] = (5,5)
                        # plt.axis('off')
                        # plt.imshow(threshl)
                        # st.pyplot()
                        
                        # plt.rcParams['figure.figsize'] = (5,5)
                        # plt.axis('off')
                        # plt.imshow(threshr)
                        # st.pyplot()

                        
                        data_list=[resl,resr]
                        # st.write(data_list)
                        long=[]
                        short=[]

                        for i in data_list:
                            # st.write(i)
                            # st.write(len(i))
                            if len(i)<=2:
                                if i:
                                    short.append(i)
                                    if len(short) > 0 and len(short[0]) > 0:
                                        short[0] = " ".join(short[0])
                            else:
                                long.append(i)
                                
                        # st.write("Short : - ",short)
                        # st.write("long : - ",long)

                        data = {}
                        if long and short:
                            # st.write("Short : - ",short)
                            # st.write("long : - ",long)
                            
                            data = ocr_to_dict(long[0], short)
                        elif long:
                            data = ocr_to_dict(long[0], [])
                        elif short:
                            data = ocr_to_dict([], short)
                            
                        
                        data = ocr_to_dict(long[0],short)
                        all_data.append(data)
                    
                

            st.markdown(f""" <div style='text-align:left; font-size: 18px; color: #ffffff ; height: 90px; padding: 5px;font-weight: 100;font-family:verdana;'>You can see the extracted text from image below 👇</div>""",unsafe_allow_html=True)


            df=pd.DataFrame(all_data)
                

            # df_display = df.rename(columns={'company_name': 'Company_Name'})
            df_display = df.reset_index(drop=True)

            with st.container():
                st.dataframe(df_display,height=df_display.shape[0] * 55,hide_index=True,use_container_width = True)

                


            temp_file.close()
            os.remove(temp_file.name)
            
            df_display['mobile_number'] = df_display['mobile_number'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
          

            dd=st.button('Push to MySQL database')
            
            if dd:
                try:
                    db = create_db_table()
                    
                    if db is not None:
                        for _, row in df_display.iterrows():
                            result = process_record(db, row)
                            if result == "inserted":
                                st.success('New record added to database')
                            elif result == "updated":
                                st.success('Existing record updated with new information')
                            elif result == "unchanged":
                                st.info('Record already exists and no changes detected')
                            else:
                                st.error('Error processing record')
                                
                except Error as e:
                    st.error(f'Error: {str(e)}')

            # if dd:
            #     try:
            #         check_query = """SELECT * FROM card_data WHERE email=%s"""

                         
            #         insert_query = """INSERT INTO card_data(company_name, card_holder, designation, mobile_number, email, website, 
            #                area, city, state, pin_code, image) 
            #                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            #                ON DUPLICATE KEY UPDATE 
            #                company_name=VALUES(company_name), card_holder=VALUES(card_holder),
            #                designation=VALUES(designation), mobile_number=VALUES(mobile_number),
            #                website=VALUES(website), area=VALUES(area),
            #                city=VALUES(city), state=VALUES(state), pin_code=VALUES(pin_code), image=VALUES(image)"""


            #         db = create_db_table()
                    
            #         if db is not None:
            #             for _, row in df_display.iterrows():
            #                 record_exists = query_db(db, check_query, [row['email']])
        
                    
            #                 if not record_exists:
            #                     query_db(db, insert_query, row)
            #                     st.success('Data sent to MySQL')
            #                 else:
            #                     st.info('Record already exists, no changes made.')
                            
            #     except Error as e:
            #         st.error(f'correct the error {str(e), e}')
                
            

    def run_functions():
        # Reload the data from the database
        df_display = get_data_sql()
        # Update the displayed dataframe with the latest data
        st.dataframe(df_display, hide_index=True)
        
    # df = None
    if selected == "Data Hub":


        st.markdown("<h2 style='text-align:center; font-size: 38px; color: #BCFD4C ; font-weight: 500;font-family:Arial;'> Interactive Data Management Hub:</h2> ", unsafe_allow_html=True) 
        st.write(' ')
        st.write(' ')
        st.write(' ')

        word,button=st.columns([5,2])
        button.button('Reload Data',key=None,on_click=get_data_sql)

        df_display = get_data_sql()
        res = df_display.copy() if df_display is not None else st.write('')
        
        if df_display is None:
            st.markdown(f""" <div style='text-align:left; font-size: 22px; color: #ffffff ;background-color: transparent; height: 40px; padding: 5px;font-weight: 100;font-family:verdana;'>No records in the database.</div>""",unsafe_allow_html=True) 
        elif df_display.shape[0] > 1 :
            word.markdown("<h4 style='text-align:left; font-size: 38px; color: #BCFD4C ; font-weight: 500;font-family:Arial;'>Explore Cardx DataFrame:</h4> ", unsafe_allow_html=True)
            word.write('  ')
            create_data = {"Company Name": "text", 'Card Holder': 'multiselect'}
            all_wid = sp.create_widgets(df_display, create_data, ignore_columns=["ZipCode", "State", "City", "Address", "Designation", "Mobile Number", "Email", "Website"])
            res = sp.filter_df(df_display, all_wid)
        
        
            
        
        if isinstance(res, pd.DataFrame):
            st.dataframe(res, hide_index=True)
        else:
            st.write("")
        # st.dataframe(res,hide_index=True) if df_display is not None else st.write('')

        a,b=st.columns([4,7])
        

        resu,mycur,mydb=sql_df()
        card_id={row[1]:row[1] for row in resu} if resu is not None else st.write(' ')
        
        
        if resu is not None and df_display is not None:
            st.markdown("<h4 style='text-align:left; font-size: 38px; color: #BCFD4C ; font-weight: 500;font-family:Arial;'>Edit, and Modify MySQL Database Records:</h4> ", unsafe_allow_html=True)
            select_name=a.selectbox("Select id number to manage the data", list(card_id.keys()), key=list(card_id.values())) 
            mycur.execute(f"select * from card_data where ID = '{select_name}'  ")
            resu1=mycur.fetchone()
            column_names = [desc[0] for desc in mycur.description]
            col1, col2,col3 = st.columns(3)
            input_values = []
            n=1
            for i in column_names[1:4]:
                input_values.append(col1.text_input(i,resu1[n],key=str(n)+'22'))
                n+=1
            
            n=4
            for i in column_names[4:7]:
                input_values.append(col2.text_input(i,resu1[n],key=n))
                n+=1
            n=7
            for i in column_names[7:11]:
                input_values.append(col3.text_input(i,resu1[n],key=n))
                n+=1

            col1.write(' ')
            save_button=col1.button('Commit changes',use_container_width=True,key='save_button', help="save_button",on_click=run_functions)
            col2.write(' ')
            
            del_button=col2.button(f"Delete {select_name}'s record",use_container_width=True,on_click=run_functions)
            image_data=resu1[11]
            
            st.write('Image')
            kind = filetype.guess(image_data)
            format = kind.mime.split('/')[1]
            st.image(image_data, caption=f'Business card of {resu1[1]}', use_column_width=True)
            update_query = """
                UPDATE card_data
                SET
                    company_name=%s,
                    card_holder=%s,
                    designation=%s,
                    mobile_number=%s,
                    email=%s,
                    website=%s,
                    area=%s,
                    city=%s,
                    state=%s,
                    pin_code=%s
                WHERE
                    ID=%s
            """
      
        
            if save_button:
                try:
                    mycur.execute(update_query,tuple(input_values +[select_name]))
                    mydb.commit()
                    run_functions()
                    st.rerun()
                except Error as e:
                    st.warning(e)
                finally:
                    b.write(' ')
                    b.success(f"Changes committed to {select_name}'s record  successfully!")
                    run_functions()
            if del_button:
                try:
                    mycur.execute(f""" Delete from card_data where ID ='{select_name}' """)
                    mydb.commit()
                    mycur.fetchall()
                    run_functions()
                    st.rerun()
                except Error as e:
                    st.warning(e)
                finally:
                    b.write(' ')
                    b.success(f"{select_name}'s record has been removed from the database.")
                    run_functions()
        else:
            st.write('')

if __name__ == "__main__":
    if st.session_state.get("logged_in"):
        # If user is logged in, show the main menu
        main_menu()
    else:
        # If user is not logged in, show the login page
        login()
        