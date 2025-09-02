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
import datetime

class FieldTimeInterval(Field.Field):
    def __init__(self, dateStart=datetime.date.today(), dateEnd=datetime.date.today(), fixing=Enumerations.Fixing.EOD):
        if not dateEnd >= dateStart:
            raise ValueError('The dateEnd must be equal or superior than dateStart.')
        self.dateStart = dateStart
        self.dateEnd = dateEnd
        self.fixing = fixing

    # dateStart
    def _get_dateStart(self):
        return self.__dateStart
    def _set_dateStart(self, value):
        if not isinstance(value, datetime.date):
            raise TypeError("The dateStart must be set to a class 'datetime.date'.")
        self.__dateStart = value
    dateStart = property(_get_dateStart, _set_dateStart)

    # dateEnd
    def _get_dateEnd(self):
        return self.__dateEnd
    def _set_dateEnd(self, value):
        if not isinstance(value, datetime.date):
            raise TypeError("The dateEnd must be set to a class 'datetime.date'.")
        self.__dateEnd = value
    dateEnd = property(_get_dateEnd, _set_dateEnd)

    # fixing
    def _get_fixing(self):
        return self.__fixing
    def _set_fixing(self, value):
        if not isinstance(value, Enumerations.Fixing):
            raise TypeError("The fixing must be set to a class 'Enumerations.Fixing'.")
        self.__fixing = value
    fixing = property(_get_fixing, _set_fixing)

    # Class Methods

    def getDateStart(self):
        return self.dateStart

    def getDateEnd(self):
        return self.dateEnd

    def getFixing(self):
        return self.fixing