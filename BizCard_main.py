#Importing reuired libraries

import streamlit as st
from easyocr import Reader
from streamlit_option_menu import option_menu
import os
import tempfile
import cv2
from PIL import Image
import mysql.connector 
from SQL_root_config import PASSWORD
from mysql.connector import Error
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

# Adding effects to the Streamlit button using CSS
st.markdown("""
<style>
.stButton button {
    background-color: #3498db !important;
    color: #ffffff;
    font:verdana !important;
    font-size: 20px;
    height: 2.5em;
    width: 15em;
    border-radius: 10px;
    transition: background-color 0.3s ease;
}
.stButton button:hover {
    background-color: #3498db !important;
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
    background-color: #0066cc !important;
    border-color: #ffffff !important;
    box-shadow: none !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)



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
        "container": {"padding": "0!important", "background-color": "#f7786b"},
        "icon": {"color": "rgb(235, 48, 84)", "font-size": "25px"}, 
        "nav-link": {"font-size": "22px", "color": "#ffffff","text-align": "left", "margin":"0px", "--hover-color": "#84706E"},
        "nav-link-selected": {"background-color": "#84706E  ","color": "white","font-size": "20px"},
    })
    
# Defining functions


# function to create table and database if not exists 
def create_db_table():
  try:
    mydb = mysql.connector.connect(
      host='localhost',
      user='root',
      password=PASSWORD,
      database='bizcardx'
      )
    mycur = mydb.cursor()
    mycur.execute("CREATE DATABASE IF NOT EXISTS bizcardx")
    mycur.execute("use bizcardx")

    mycur.execute('''CREATE TABLE IF NOT EXISTS card_data      
              (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                company_name TEXT ,
                card_holder TEXT ,
                designation TEXT,
                mobile_number VARCHAR(50),
                email  VARCHAR(255) UNIQUE,  
                website TEXT,
                area TEXT,
                city TEXT,
                state TEXT,
                pin_code VARCHAR(10),
                image LONGBLOB
                )''')
    mydb.commit()
    return mydb
  except Error as e:
    st.error(f"The error '{e}' occurred")
    return None

# function to upload processed data to SQL database
def query_db(mydb,query,data):

  data_to_insert = tuple(data.iloc[0])
  try:
    with mydb.cursor( ) as cur:
      cur.execute(query,data_to_insert)
      mydb.commit()
    
  except Error as e:
    st.error(f"The error '{e}' occurred")
  finally:
    mydb.close()
  
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
    with  mysql.connector.connect(
      host='localhost',
      user='root',
      password=PASSWORD,
      database='bizcardx'
      ) as mydb:
      mycur = mydb.cursor()
      mycur.execute("select * from card_data")
      sql_data=mycur.fetchall()
      if sql_data:
        columns = ["ID",  "Company Name", "Card Holder", "Designation", "Mobile Number", "Email", "Website", "Address", "City", "State", "ZipCode","Image"]
        df=pd.DataFrame(sql_data,columns=columns)
        
        return df
      else:
        st.write("No data found in the 'card_data' table.")

  except Error as e:
     st.write(e)

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
  mydb=  mysql.connector.connect(host='localhost',user='root',password=PASSWORD,database='bizcardx') 
  mycur = mydb.cursor()
  mycur.execute("select Card_Holder,id  from card_data")
  resu=mycur.fetchall()
  return resu,mycur,mydb



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
  
  st.markdown("<h5 style='text-align:left; font-size: 28px; color: #ffffff ; font-weight: 200;font-family:verdana;'> Choose a business card image:</h5> ", unsafe_allow_html=True)

  uploaded_card = st.file_uploader(label="",label_visibility="visible",type=["png","jpeg","jpg"])
  st.markdown("<hr style='border: 2px solid #ffffff;'>", unsafe_allow_html=True)

  if uploaded_card:
    read_col, view_col=st.columns([1,1])
    read_col.markdown(f""" <div style='text-align:left; font-size: 18px; color: #ffffff ;padding: 5px;font-weight: 100;font-family:verdana;'>You have uploaded {uploaded_card.name}.  You can verify the image down here 👇</div>""",unsafe_allow_html=True)
    read_col.write(" ")
    st.markdown("<hr style='border: 2px solid #ffffff;'>", unsafe_allow_html=True)


    read_col.image(uploaded_card,caption='Uploaded Image')

    with view_col:
       with st.spinner('Wait for loading  your image...'):
        st.set_option('deprecation.showPyplotGlobalUse', False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_file.write(uploaded_card.read())
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

    


    # plt.rcParams['figure.figsize'] = (5,5)
    # plt.axis('off')
    # plt.imshow(threshl)
    # st.pyplot()
    ret,threshr=    cv2.threshold(grayr, 300, 120, cv2.THRESH_TOZERO_INV)
    # plt.rcParams['figure.figsize'] = (5,5)
    # plt.axis('off')
    # plt.imshow(threshr)
    # st.pyplot()

    resl=reader.readtext(threshl,detail=0,paragraph=False)
    resr=reader.readtext(threshr,detail=0,paragraph=False)
    data_list=[    resl,resr ]
    
    long=[]
    short=[]

    for i in data_list:
        if len(i)<=2:
            short.append(i)


            short[0]=" ".join(short[0])
        else:
            long.append(i)



    data = ocr_to_dict(long[0],short)

    st.markdown(f""" <div style='text-align:left; font-size: 18px; color: #ffffff ; height: 90px; padding: 5px;font-weight: 100;font-family:verdana;'>You can see the extracted text from image below 👇</div>""",unsafe_allow_html=True)


    df=pd.DataFrame( data)
    

    df_display = df.rename(columns={'company_name': 'Company_Name'})
    df = df.reset_index(drop=True)

    with st.container():
      st.dataframe(df,height=90,hide_index=True)

    


    temp_file.close()
    os.remove(temp_file.name)

    dd=st.button('Push to MySQL database')

    if dd:
        try:
          query="""INSERT  INTO card_data(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,image)
                              VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
               company_name=VALUES(company_name), card_holder=VALUES(card_holder),
               designation=VALUES(designation), mobile_number=VALUES(mobile_number),
               website=VALUES(website), area=VALUES(area),
               city=VALUES(city), state=VALUES(state), pin_code=VALUES(pin_code), image=VALUES(image)"""  
          query_db(create_db_table(),query,df)
        except Error as e:
           st.error(f'correct the error {e}')
        finally:
           st.success('Data sent to MySQL')
           




if selected == "Data Hub":


  st.markdown("<h2 style='text-align:center; font-size: 38px; color: #BCFD4C ; font-weight: 500;font-family:Arial;'> Interactive Data Management Hub:</h2> ", unsafe_allow_html=True)
  st.write(' ')
  st.write(' ')
  st.write(' ')

  word,button=st.columns([5,2])
  button.button('Reload Data',key=None,on_click=get_data_sql)

  df = get_data_sql()
  
  
  if df is None:
     st.markdown(f""" <div style='text-align:left; font-size: 22px; color: #ffffff ;background-color: #3498db; height: 40px; padding: 5px;font-weight: 100;font-family:verdana;'>No records in the database.</div>""",unsafe_allow_html=True) 
  else:
    create_data = {"Company Name": "text", 'Card Holder': 'multiselect'}
    all_wid = sp.create_widgets(df, create_data, ignore_columns=["ZipCode", "State", "City", "Address", "Designation", "Mobile Number", "Email", "Website"])
    res = sp.filter_df(df, all_wid)
    
    word.markdown("<h4 style='text-align:left; font-size: 38px; color: #BCFD4C ; font-weight: 500;font-family:Arial;'>Explore Cardx DataFrame:</h4> ", unsafe_allow_html=True)
    word.write('  ')
    st.dataframe(res,hide_index=True)

    a,b=st.columns([4,7])
    st.markdown("<h4 style='text-align:left; font-size: 38px; color: #BCFD4C ; font-weight: 500;font-family:Arial;'>Edit, and Modify MySQL Database Records:</h4> ", unsafe_allow_html=True)

    resu,mycur,mydb=sql_df()
    card_name={row[1]:row[0] for row in resu}
     
    select_name=a.selectbox("Select Card Holder name to view data", list(card_name.values()), key=list(card_name.keys()))
    mycur.execute(f"select * from card_data where card_holder = '{select_name}'  ")
    resu1=mycur.fetchone()
    column_names = [desc[0] for desc in mycur.description]
    col1, col2,col3 = st.columns(3)
    input_values = []
    n=1
    for i in column_names[1:4]:
      input_values.append(col1.text_input(i,resu1[n],key=n))
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
    save_button=col1.button('Commit changes',use_container_width=True,key='save_button', help="save_button",on_click=sql_df)
    col2.write(' ')
    
    del_button=col2.button(f"Delete {select_name}'s record",use_container_width=True,on_click=sql_df)
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
            card_holder=%s
    """
    
    
    if save_button:
      try:
         mycur.execute(update_query,tuple(input_values +[select_name]))
         mydb.commit()
      except Error as e:
         st.warning(e)
      finally:
         b.write(' ')
         b.success(f"Changes committed to {select_name}'s record  successfully!")
    if del_button:
      try:
         mycur.execute(f""" Delete from card_data where card_holder ='{select_name}' """)
         mydb.commit()
         mycur.fetchall()
      except Error as e:
         st.warning(e)
      finally:
         b.write(' ')
         b.success(f"{select_name}'s record has been removed from the database.")




      