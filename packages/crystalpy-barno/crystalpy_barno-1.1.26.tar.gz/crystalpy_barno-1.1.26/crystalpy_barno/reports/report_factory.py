from crystalpy_barno.reports.base_report import BaseReport
from CrystalDecisions.Shared import ExportFormatType

class ReportFactory:
    @staticmethod
    def create_report(report_type, filename, output_path, parameters, formulas, sp_name):
        report = BaseReport(filename, output_path, sp_name)
        report.set_parameters(parameters)
        report.set_formula_fields(formulas)
        report.apply_database_connection()
        report.set_stored_procedure(sp_name)
        return report

    @staticmethod
    def get_export_format(file_type):
        formats = {
            "pdf": ExportFormatType.PortableDocFormat,
            "html": ExportFormatType.HTML40,
            "excel": ExportFormatType.Excel
        }
        return formats.get(file_type.lower(), ExportFormatType.PortableDocFormat)
