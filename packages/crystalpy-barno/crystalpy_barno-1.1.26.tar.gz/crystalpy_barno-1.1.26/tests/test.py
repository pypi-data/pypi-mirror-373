import os
import sys

from crystalpy_barno.helpers.report_loader_helper import CrystalReportsLoader

# Create an instance of the CrystalReportsLoader
loader = CrystalReportsLoader()

# Setup the loader (loads config, DLLs, and namespaces)
loader.setup()

from crystalpy_barno.config.database_config import DatabaseConfig
from crystalpy_barno.entry_point import generate_report

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ## Local
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_PASSWORD_PYODBC = os.getenv('DATABASE_PASSWORD_PYODBC')

DATABASE_DRIVER = 'ODBC+Driver+17+for+SQL+Server'
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}?driver={DATABASE_DRIVER}"

FILE_PATH_SETTINGS = './Files/'
# INV_PATH_SETTINGS = 'C:/Temp/'
INV_PATH_SETTINGS = os.getenv('PDF_FILE_PATH')
PDF_FILE_PATH = os.getenv('PDF_FILE_PATH')
RPT_PATH_SETTINGS = os.getenv('RPT_FILE_PATH')
REPORT_ODBC_NAME = os.getenv('REPORT_ODBC_NAME')


# # Set database connection details
# DatabaseConfig.set_connection_details(REPORT_ODBC_NAME, DATABASE_NAME, DATABASE_USERNAME, DATABASE_PASSWORD_PYODBC)

report_filename = os.path.join(RPT_PATH_SETTINGS, 'Sale_Memo_IncludeMaking.rpt')

# Define output path relative to the current directory
output_dir = os.path.join(os.getcwd(), "output")

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)  # Create the directory if it doesn't exist

output_path = os.path.join(output_dir, "2425SOPBAR00778.pdf")

# Generate a report
generate_report(
    report_type="sale_memo",
    filename=report_filename,
    output_path=output_path,
    parameters={
        "@pvSourcerecNo": '2425SOEBAR02135',
        "@pvVoucherNo": "2425SOPBAR00778",
        "@pvLeCode": "NJ",
        "@pvUserCode": "NIM",
        "@pvReportID": 1,
        "@pvIncludingMaking": "1",
    },
    formulas={
        "EmployeeName": "TEST",
        "ReportCaption": "Sales Report"
    },
    sp_name="spSale_Memo",
    file_type="pdf",
    db_odbc_name=REPORT_ODBC_NAME,
    db_name=DATABASE_NAME,
    db_username=DATABASE_USERNAME,
    db_password=DATABASE_PASSWORD_PYODBC
)
