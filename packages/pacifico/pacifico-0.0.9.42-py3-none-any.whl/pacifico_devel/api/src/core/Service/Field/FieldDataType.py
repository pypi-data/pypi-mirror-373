"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

from . import Field
from ....util import Enumerations


class FieldDataType(Field.Field):
    def __init__(self, dataType=Enumerations.FieldType.Field_Unspecified):
        self.dataType = dataType

    # dataType
    def _get_dataType(self):
        return self.__dataType
    def _set_dataType(self, value):
        if not isinstance(value, Enumerations.FieldType):
            raise TypeError("The dataType must be set to a class 'Enumerations.FieldType'.")
        self.__dataType = value
    dataType = property(_get_dataType, _set_dataType)

    # Class Methods
    def getDataType(self):
        return self.dataType