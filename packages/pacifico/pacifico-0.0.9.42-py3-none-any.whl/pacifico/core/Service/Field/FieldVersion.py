"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

from pacifico.core.Service.Field import Field
from pacifico.util import Enumerations


class FieldVersion(Field.Field):
    def __init__(self, type=Enumerations.VersionType.Version_Unspecified, version='', author=''):
        if type == Enumerations.VersionType.Version_Unspecified:
            if version == '':
                type = Enumerations.VersionType.Version_Pricing
            else:
                type = Enumerations.VersionType.Version_Prediction
        self.type = type
        self.author = author
        self.version = version

    # type
    def _get_type(self):
        return self.__type
    def _set_type(self, value):
        if not isinstance(value, Enumerations.VersionType):
            raise TypeError("The type must be set to a class 'Enumerations.VersionType'.")
        self.__type = value
    type = property(_get_type, _set_type)

    # author
    def _get_author(self):
        return self.__author
    def _set_author(self, value):
        if not isinstance(value, str):
            raise TypeError("The author must be set to a string.")
        self.__author = value
    author = property(_get_author, _set_author)

    # version
    def _get_version(self):
        return self.__version
    def _set_version(self, value):
        if not isinstance(value, str):
            raise TypeError("The version must be set to a string.")
        self.__version = value
    version = property(_get_version, _set_version)

    # Class Methods

    def getType(self):
        return self.type

    def getAuthor(self):
        return self.author

    def getVersion(self):
        return self.version