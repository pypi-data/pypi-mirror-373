import logging
from crystalpy_barno.config.database_config import DatabaseConfig

logging.basicConfig(filename="report_errors.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

class DatabaseHelper:
    @staticmethod
    def apply_connection(crpt):
        try:
            server, database, user, password = DatabaseConfig.get_connection_details()

            if not all([server, database, user, password]):
                logging.error(f"Incomplete database credentials")

            logging.info(f"Applying database connection to report. Server: {server}, Database: {database}")
            
            for table in crpt.Database.Tables:
                logon_info = table.LogOnInfo
                logon_info.ConnectionInfo.ServerName = server
                logon_info.ConnectionInfo.DatabaseName = database
                logon_info.ConnectionInfo.UserID = user
                logon_info.ConnectionInfo.Password = password
                table.ApplyLogOnInfo(logon_info)

            logging.info("Database connection applied successfully in crystalpy_barno.")

        except Exception as e:
            logging.error(f"Database connection error in DatabaseHelper: {e}")
            raise
