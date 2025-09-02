"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import datetime
from pacifico.core.Service.ServiceRequest.ServiceRequestDataPoint import ServiceRequestDataPoint
from pacifico.core.Service.Field import FieldVersion, FieldReport
from pacifico.core.Service.Field import FieldDataType, FieldQuality, FieldTimeInterval
from pacifico.util import Variant
from pacifico.util import Enumerations


class ServiceRequestDataPointReport(ServiceRequestDataPoint.ServiceRequestDataPoint):
    def __init__(self, reports=[], timeHorizon=[], dataTypes=[], version=[], quality=[], optional={}):
        ServiceRequestDataPoint.ServiceRequest.Service.Object.__init__(self)
        ServiceRequestDataPoint.ServiceRequestDataPoint.__init__(self, reports, timeHorizon, dataTypes, version, quality, optional)

    @staticmethod
    def create(document='', item='', chapter='', section='', subsection='', paragraph='', dateStart=datetime.datetime.today().date(),
               dateEnd=datetime.datetime.today().date(), fixing=Enumerations.Fixing.EOD,
               dataType=Enumerations.FieldType.Field_Unspecified,
               versionType=Enumerations.VersionType.Version_Unspecified, author='',
               version='', quality=Enumerations.Quality.Quality_Unspecified):
        if document == '' and item == '':
            return None
            #raise Exception("The user must specify either the document or the item when requesting a report.")
        variant = Variant.Variant.getEmptyVariant()
        fieldReport = FieldReport.FieldReport(dateStart, fixing, '', '', document, item, chapter, section, subsection, paragraph, variant)
        fieldTimeInterval = FieldTimeInterval.FieldTimeInterval(dateStart, dateEnd, fixing)
        fieldDataType = FieldDataType.FieldDataType(dataType)
        fieldVersion = FieldVersion.FieldVersion(versionType, version, author)
        fieldQuality = FieldQuality.FieldQuality(quality)
        service = ServiceRequestDataPointReport([fieldReport], [fieldTimeInterval], [fieldDataType], [fieldVersion], [fieldQuality])
        return service
