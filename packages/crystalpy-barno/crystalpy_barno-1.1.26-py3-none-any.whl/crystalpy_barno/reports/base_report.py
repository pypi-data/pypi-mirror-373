import clr
import os
from pathlib import Path

# Get the path to the CR helper directory
package_dir = Path(__file__).parent.parent.parent
cr_dir = package_dir / "crystalpy_barno" / "helpers" / "CR"

# Add references to the local DLL files
clr.AddReference(str(cr_dir / "CrystalDecisions.CrystalReports.Engine.dll"))
clr.AddReference(str(cr_dir / "CrystalDecisions.Shared.dll"))
clr.AddReference(str(cr_dir / "CrystalDecisions.Windows.Forms.dll"))

from CrystalDecisions.CrystalReports.Engine import ReportDocument
from crystalpy_barno.config.database_config import DatabaseConfig
from crystalpy_barno.helpers.database_helper import DatabaseHelper
from crystalpy_barno.helpers.report_parameter_helper import ReportParameterHelper
from CrystalDecisions.Shared import ConnectionInfo, TableLogOnInfo
from ..config.database_config import DatabaseConfig

import logging


logging.basicConfig(filename="report_errors.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


class BaseReport:
    def __init__(self, filename, output_path, stored_procedure_name):
        self.report = ReportDocument()
        self.report.Load(filename)
        self.output_path = output_path

        # Fetch database connection details
        self.server_name, self.database_name, self.user_id, self.password = DatabaseConfig.get_connection_details()
        self.stored_procedure_name = stored_procedure_name

    def set_parameters(self, parameters):
        for name, value in parameters.items():
            ReportParameterHelper.set_parameter(self.report, name, value)

    def set_formula_fields(self, formulas):
        for name, value in formulas.items():
            ReportParameterHelper.set_formula_field(self.report, name, value)

    def apply_database_connection(self):
        """ Apply ODBC connection to the Crystal Report """
        try:
            connection_info = ConnectionInfo()
            connection_info.ServerName = self.server_name
            connection_info.DatabaseName = self.database_name
            connection_info.UserID = self.user_id
            connection_info.Password = self.password

            for table in self.report.Database.Tables:
                log_on_info = TableLogOnInfo()
                log_on_info.ConnectionInfo = connection_info
                table.ApplyLogOnInfo(log_on_info)

            logging.info(f"Database connection applied successfully in BaseReport. Server: {self.server_name}, Database: {self.database_name}")

        except Exception as e:
            logging.error(f"Error applying database connection: {e}")

    def set_stored_procedure(self, stored_procedure_name):
        """
        Set the stored procedure for the report.
        :param stored_procedure_name: The name of the stored procedure.
        """
        try:
            sp_location = f"{self.database_name}.dbo.{self.stored_procedure_name}"
            logging.info(f"Stored procedure set to: {sp_location}")

            # Apply stored procedure as table location
            self.report.Database.Tables[0].Location = sp_location

            logging.info("Stored procedure applied successfully.")
        except Exception as e:
            logging.error(f"Error setting stored procedure: {e}")
            raise

    def export(self, format_type):
        self.report.ExportToDisk(format_type, self.output_path)
