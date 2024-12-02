import streamlit as st
import pandas as pd
from io import BytesIO
from azure.storage.blob import BlobServiceClient, ContainerClient
from dotenv import load_dotenv
import os
from difflib import get_close_matches  # For better matching
 
load_dotenv()
 
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
 
# For the widebody
st.set_page_config(
    page_title="CapEx Analyzer",
    page_icon="✅",
    layout="wide",
)
 
# Load the CSV file
df = pd.read_csv("Quarterly_Comparison_Results_with_Company_Names.csv")

# Replace "Data not available" with "DNA"
df.replace("Data not available", "DNA", inplace=True)
 
# Get the unique company names from the CSV file
company_names = df["Company"].unique()
 
# Initialize session state to control DataFrame visibility
if 'run_clicked' not in st.session_state:
    st.session_state.run_clicked = False
 
# CSS to change the background of the Streamlit interface and center-align text
st.markdown(
    """
    <style>
    body {
        overflow: hidden !important;
    }
    .main {
        background-color: #76D7C4;
    }
 
    .dataframe {
        text-align: center;
        font-family: 'Arial', sans-serif; /* Change font */
        font-weight: bold; /* Make text bold */
        color: #1F618D; /* Change font color */
    }
    .dataframe td, .dataframe th {
        text-align: center !important;
    }
 
    .streamlit-expanderHeader {
        background-color: #1ABC9C !important;
        color: white !important;
        font-weight: bold;
        border-radius: 5px 5px 0 0;
    }
    .streamlit-expander {
        background-color: #1F618D !important;
        padding: 15px;
        border-radius: 0 0 5px 5px;
    }
 
    .small-download-button .stDownloadButton {
        font-size: small;
        padding: 3px 2px;
        width: 5cm;
        float: right;
    }
    footer {visibility: hidden;} /* Hides the "Made with Streamlit" footer */
    header {visibility: hidden;} /* Hides the "Deploy" header */
    .stApp {overflow: hidden;} /* Hides the running animation */
    .stSelectbox {
        margin-top: -60px  !important;
    }
    .run-button {
        background-color: orange;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        float: right;
        margin-right: -1100px;
    }
    .stMultiSelect {
        margin-top: -60px  !important;
    }
    .st.button{
        background-color: orange;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        float: right;
        margin-right: -1100px;
    }
    window.onscroll = function(){
        window.onscrollTo(0, 0);
    }
    </style>
    """,
    unsafe_allow_html=True
)
 
# CSS to center the title and style the headers
st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        color: #2980B9;
        font-size: 60px;
        font-weight: bold;
        margin-top: -120px;
    }
    .dataframe-header {
        font-weight: bold;
        color: #ffffff;
        background-color: #007BFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Apply the centered-title class to the title
st.markdown("<h1 class='centered-title'>CapEx Analyzer</h1>", unsafe_allow_html=True)

col_run = st.columns([4, 0.25])[1]
with col_run:
    if st.button("Run"):
        st.session_state.run_clicked = True 
st.markdown("  ")
st.text(" ")
# Creating columns for parallel layout with 80% and 20% width
col1, col2 = st.columns([4, 1])
 
# Dropdown to select companies
with col1:
    selected_companies = st.multiselect(
        "Select company names:",
        company_names,  # Use company names from the CSV
        default=None,  # Do not pre-select any companies initially
        key="company_multiselect"
    )
 
# Dropdown to select the number of companies
with col2:
    count = st.selectbox(
        "Number of companies:",
        options=list(range(0, len(company_names) + 1)),
        index=0
    )
 

   
# Initialize the DataFrame to be displayed
if st.session_state.run_clicked:
    if selected_companies:
        # Use difflib to match selected companies with CSV company names more effectively
        matched_rows = pd.DataFrame()
        for company in selected_companies:
            possible_matches = get_close_matches(company, df["Company"], n=1, cutoff=0.1)
            if possible_matches:
                match = possible_matches[0]
                matched_rows = pd.concat([matched_rows, df[df["Company"] == match]])
 
        matched_rows = matched_rows.drop_duplicates()
    else:
        matched_rows = df  # Display the entire DataFrame initially
 
    # Limit the number of companies displayed based on the "count" selection
    if count > 0:
        matched_rows = matched_rows.head(count)
 
    # Set index for matched rows if not empty
    if not matched_rows.empty:
        matched_rows.set_index("Company", inplace=True)
 
    # Apply conditional formatting
    def color_format(val):
        if isinstance(val, str):
            if val.lower() == "increase":
                return 'color: green; font-weight: bold'
            elif val.lower() == "decrease":
                return 'color: red; font-weight: bold'
            elif val.lower() == "dna":
                return 'color: blue; font-weight: bold'
            elif val.lower() == "unchanged":
                return 'color: orange; font-weight: bold'
        return ''  # Default style
 


    
    # Display the DataFrame with updated styles
    st.dataframe(matched_rows.style.map(color_format).set_table_styles(
        [
            {'selector': 'thead th', 'props': [('font-weight', 'bold'), ('color', '#ffffff'), ('background-color', '#007BFF')]},
            {'selector': 'tbody td', 'props': [('font-family', 'Arial, sans-serif'), ('font-weight', 'bold'), ('color', '#1F618D')]}  # Style for the table body
        ]
    ), height=300, width=1300)
 
    st.write("**Note:** 'DNA'-'Data not available'")
 
# def generate_csv_download(df):
#     output = BytesIO()
#     df.to_csv(output, encoding='utf-8-sig')
#     output.seek(0)
#     return output
 
# def generate_excel_download(df):
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#         df.to_excel(writer, index=True, sheet_name='Sheet1')
#     output.seek(0)
#     return output
 
# # Download options below the table with a custom background color for the expander
# col_center = st.columns([1, 0.5, 1])  # Adjust column width to reduce space for expander
# with col_center[1]:
#     with st.expander("Download Options", expanded=False):
#         # Radio button to select download format
#         download_format = st.radio("Format:", ["Excel", "CSV"], key="download_format")
 
#         # Single download button based on format selection
#         if download_format:
#             if download_format == "Excel":
#                 download_data = generate_excel_download(matched_rows)
#                 file_name = "selected_company_data.xlsx"
#                 mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             elif download_format == "CSV":
#                 download_data = generate_csv_download(matched_rows)
#                 file_name = "selected_company_data.csv"
#                 mime_type = "text/csv"
 
#             st.markdown(f"<div class='small-download-button'>", unsafe_allow_html=True)
#             st.download_button(
#                 label=f"Download {download_format}",
#                 data=download_data,
#                 file_name=file_name,
#                 mime=mime_type
#             )
#             st.markdown("</div>", unsafe_allow_html=True)
