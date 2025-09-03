# crystalpy-barno

Python Integration with Crystal Report for Dynamic Output
=====================================================

## Features

* Connect Crystal Report with Python for dynamic output

## Installation

To install this project, run the following command:
```bash
pip install crystalpy-barno

```

## Usage

### Example Code
```python
import os
from datetime import datetime

from crystalpy_barno.helpers.report_loader_helper import CrystalReportsLoader
from crystalpy_barno.config.database_config import DatabaseConfig
from crystalpy_barno.entry_point import generate_report

# Set database connection details externally
DatabaseConnectionHelper.set_connection_details(
    server_name="SERVER_NAME",
    database_name="DB_NAME",
    user_id="USER",
    password="PASS"
)

voucher_no = "VOUCHER_NO"
pdf_dir = os.path.join(cwd, 'pdf')
pdf_dir_sales = os.path.join(pdf_dir, 'sales')
pdf_filepath_sale = os.path.join(pdf_dir_sales, f"{voucher_no}.pdf")

# Generate a report
generate_report(
    report_type="sale_memo",
    filename='rpt/Sale_Memo_IncludeMaking.rpt',
    output_path=pdf_filepath_sale,
    parameters={
        "@pvSourcerecNo": '2425SOEBAR02135',
        "@pvVoucherNo": "2425SOPBAR00778",
        "@pvLeCode": "NJ",
        "@pvUserCode": "NIM",
        "@pvReportID": 1,
        "@pvIncludingMaking": "1",
    },
    formulas={
        "EmployeeName": "John Doe",
        "ReportCaption": "Sales Report"
    },
    sp_name="spSale_Memo",
    file_type="pdf"
)
```

## Report Generation
This code generates a sales memo report using the SaleMemo function from the SaleSnippet module. The report is generated based on the provided parameters and saved as a PDF file in the specified output path.

## Database Connection
The database connection details are set externally using the DatabaseConnectionHelper class. You need to replace the placeholders with your actual database connection details.

## Report Templates
The report template used in this example is Sale_Memo_IncludeMaking.rpt. You can modify this template or use a different one to suit your reporting needs.

## Output Directory
The output directory for the generated report is specified using the pdf_dir variable. You can modify this to change the output directory.

## Contributing
Contributions are welcome! Please submit a pull request with your changes and a brief description of what you've added or fixed.

## License
This project is licensed under the MIT License.