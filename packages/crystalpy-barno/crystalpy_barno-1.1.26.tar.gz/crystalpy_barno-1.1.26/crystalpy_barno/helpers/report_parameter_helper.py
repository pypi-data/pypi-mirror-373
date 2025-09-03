from CrystalDecisions.Shared import ParameterDiscreteValue
from CrystalDecisions import Shared

class ReportParameterHelper:
    @staticmethod
    def set_parameter(report, param_name, value):
        """
        Set a parameter value in the report document.
        :param report: The report document object
        :param param_name: The parameter name
        :param value: The value to set
        """
        try:
            param_fields = report.DataDefinition.ParameterFields
            param_field = param_fields[param_name]
            param_value = Shared.ParameterDiscreteValue()
            
            # Ensure type compatibility
            expected_type = param_field.ParameterValueKind
            if expected_type == Shared.ParameterValueKind.NumberParameter:
                param_value.Value = float(value)  # Convert to number
            elif expected_type == Shared.ParameterValueKind.StringParameter:
                param_value.Value = str(value)  # Convert to string
            elif expected_type == Shared.ParameterValueKind.DateParameter:
                param_value.Value = value  # Ensure it's a valid date object
            else:
                param_value.Value = value  # Default fallback

            param_field.CurrentValues.Clear()
            param_field.CurrentValues.Add(param_value)
            param_field.ApplyCurrentValues(param_field.CurrentValues)
        except Exception as e:
            raise ValueError(f"Error setting parameter '{param_name}': {e}")

    @staticmethod
    def set_formula_field(report, name, value):
        report.DataDefinition.FormulaFields[name].Text = f"'{value}'"
