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


class FieldQuality(Field.Field):
    def __init__(self, quality=Enumerations.Quality.Quality_Production):
        self.quality = quality

    # quality
    def _get_quality(self):
        return self.__quality
    def _set_quality(self, value):
        if not isinstance(value, Enumerations.Quality):
            raise TypeError("The quality must be set to a class 'Enumerations.Quality'.")
        self.__quality = value
    quality = property(_get_quality, _set_quality)

    # Class Methods

    def getQuality(self):
        return self.quality