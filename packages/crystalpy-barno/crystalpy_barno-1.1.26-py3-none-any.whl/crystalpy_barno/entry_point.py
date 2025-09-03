from crystalpy_barno.reports.report_factory import ReportFactory
from crystalpy_barno.enums import FileTypes
from crystalpy_barno.config.database_config import DatabaseConfig

def generate_report(report_type, filename, output_path, parameters, formulas, sp_name, file_type=FileTypes.PDF, db_odbc_name=None, db_name=None, db_username=None, db_password=None):
    # Set database connection details
    DatabaseConfig.set_connection_details(db_odbc_name, db_name, db_username, db_password)
    
    report = ReportFactory.create_report(report_type, filename, output_path, parameters, formulas, sp_name)
    export_format = ReportFactory.get_export_format(file_type)
    report.export(export_format)
    print(f"Report exported to {output_path} in {file_type.upper()} format.")
