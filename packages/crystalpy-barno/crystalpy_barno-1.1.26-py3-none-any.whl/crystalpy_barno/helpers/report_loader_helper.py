import clr
import os
import json

class CrystalReportsLoader:
    # Static configuration for DLL paths
    STATIC_CONFIG = {
        "crystal_reports_engine": "CrystalDecisions.CrystalReports.Engine.dll",
        "crystal_reports_windows_forms": "CrystalDecisions.Windows.Forms.dll",
        "crystal_reports_shared": "CrystalDecisions.Shared.dll"
    }
    def __init__(self):
        """
        Initializes the CrystalReportsLoader class with the path to the configuration file.

        :param config_path: Path to the configuration JSON file.
        """
        # self.config_path = config_path
        self.crystal_reports_engine = None
        self.crystal_reports_windows_forms = None
        self.crystal_reports_shared = None

    def load_config(self):
        """
        Loads the configuration from the JSON file and sets the paths for the required DLLs.
        """
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Full path of the config file
        # full_config_path = os.path.join(script_dir, self.config_path)
        # full_config_path = self.config_path

        # Load the configuration from the JSON file
        try:
            # with open(full_config_path, 'r') as config_file:
            #     config = json.load(config_file)
            self.crystal_reports_engine = os.path.join(script_dir, 'CR', self.STATIC_CONFIG["crystal_reports_engine"])
            self.crystal_reports_windows_forms = os.path.join(script_dir, 'CR', self.STATIC_CONFIG["crystal_reports_windows_forms"])
            self.crystal_reports_shared = os.path.join(script_dir, 'CR', self.STATIC_CONFIG["crystal_reports_shared"])
        except FileNotFoundError:
            raise Exception(f"Configuration file '{self.STATIC_CONFIG}' not found. Please create the file with the correct DLL paths.")
        except json.JSONDecodeError:
            raise Exception("Error parsing the configuration file. Please check the JSON format.")

    def load_dlls(self):
        """
        Loads the DLL files dynamically using paths from the configuration file.
        """
        try:
            clr.AddReference(self.crystal_reports_engine)
            clr.AddReference(self.crystal_reports_windows_forms)
            clr.AddReference(self.crystal_reports_shared)
        except Exception as e:
            print(f"Error loading assembly: {e}")
            raise

    def import_namespaces(self):
        """
        Imports the required namespaces after loading the DLLs.
        """
        global Engine, Forms, Shared, ReportDocument, ParameterDiscreteValue, TableLogOnInfo, ExportFormatType
        import CrystalDecisions.CrystalReports.Engine as Engine
        from CrystalDecisions.Windows import Forms
        from CrystalDecisions import Shared
        from CrystalDecisions.CrystalReports.Engine import ReportDocument
        from CrystalDecisions.Shared import ParameterDiscreteValue, TableLogOnInfo, ExportFormatType

    def setup(self):
        """
        Executes the configuration loading, DLL loading, and namespace import.
        """
        self.load_config()
        self.load_dlls()
        self.import_namespaces()

