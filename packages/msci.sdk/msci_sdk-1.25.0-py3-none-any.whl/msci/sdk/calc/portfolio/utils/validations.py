from datetime import datetime

class TypeValidation:
    def __init__(self, field_name, data_type, mandatory=False):
        """
        Fields required to perform the type validation.

        Args :
            field_name (str):Field name for which validation needs to be run.
            data_type (Object):Class reference against which type validation will be performed.

        """
        self.field_name = field_name
        self.data_type = data_type
        self.mandatory = mandatory

    def __set__(self, instance, value):
        """
            Validation logic triggered whenever a field parameter is assigned. If the validation rules are satisfied, then the field value is set else a value error is returned with appropriate message.
        """

        if self.mandatory and value is None:
            raise ValueError("The field {} is mandatory .".format(self.field_name))
            
        if isinstance(self.data_type, list):
            if (value is not None) and (not isinstance(value, tuple(self.data_type))):
                raise TypeError("The field {} should be of type {} ".format(self.field_name, tuple(self.data_type)))
        elif (self.data_type is not None and value is not None) and (not isinstance(value, self.data_type)):
            raise TypeError("The field {} should be of type {} ".format(self.field_name, self.data_type))
            
        instance.__dict__[self.field_name] = value


class StringDateFormat:
    def __init__(self, field_name, mandatory=False):
        """
        Args:
            field_name (str):The field name for which date validation needs to be run.
        """
        self.field_name = field_name
        self.mandatory = mandatory

    def __set__(self, instance, value):
        """
            Validation logic to verify that the date parameter passed as string format is in the YYYY-MM-DD format.
        """
        if self.mandatory:
            if value is None:
                raise ValueError("The field {} is mandatory .".format(self.field_name))
        elif value is None:
            return

        if not isinstance(value, str):
            raise TypeError("The field {} must be of type str ".format(self.field_name))

        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        instance.__dict__[self.field_name] = value




