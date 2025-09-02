"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import json
import datetime
from pacifico.util import Variant
from pacifico.util import Enumerations, Dates
from pacifico.core.Service.Field import Field


class FieldReport(Field.Field):
    def __init__(self, datePublication, fixing, dateEffective, dateTenor, document, item, chapter, section, subsection, paragraph, variant, other=''):
        self.datePublication = datePublication
        self.fixing = fixing
        self.setDateEffective(dateEffective)
        self.setDateTenor(dateTenor)
        documentIsEmpty = document == ''
        itemIsEmpty = item == ''
        if documentIsEmpty and itemIsEmpty:
            if documentIsEmpty:
                raise TypeError("The document must not be an empty string.")
            elif itemIsEmpty:
                raise TypeError("The item must not be an empty string.")
        if chapter == '':
            section = ''
        if section == '':
            subsection = ''
        if subsection == '':
            paragraph = ''
        self.document = document
        self.chapter = chapter
        self.section = section
        self.subsection = subsection
        self.paragraph = paragraph
        self.item = item
        self.variant = variant
        self.other = other

    # fixing
    def _get_fixing(self):
        return self.__fixing
    def _set_fixing(self, value):
        if not isinstance(value, Enumerations.Fixing):
            raise TypeError("The fixing must be set to a class 'Enumerations.Fixing'.")
        self.__fixing = value
    fixing = property(_get_fixing, _set_fixing)

    # document
    def _get_document(self):
        return self.__document
    def _set_document(self, value):
        if not isinstance(value, str):
            raise TypeError("The document must be set to a string.")
        self.__document = value
    document = property(_get_document, _set_document)

    # item
    def _get_item(self):
        return self.__item
    def _set_item(self, value):
        if not isinstance(value, str):
            raise TypeError("The item must be set to a string.")
        self.__item = value
    item = property(_get_item, _set_item)

    # chapter
    def _get_chapter(self):
        return self.__chapter
    def _set_chapter(self, value):
        if not isinstance(value, str):
            raise TypeError("The chapter must be set to a string.")
        self.__chapter = value
    chapter = property(_get_chapter, _set_chapter)

    # section
    def _get_section(self):
        return self.__section
    def _set_section(self, value):
        if not isinstance(value, str):
            raise TypeError("The section must be set to a string.")
        self.__section = value
    section = property(_get_section, _set_section)

    # subsection
    def _get_subsection(self):
        return self.__subsection
    def _set_subsection(self, value):
        if not isinstance(value, str):
            raise TypeError("The subsection must be set to a string.")
        self.__subsection = value
    subsection = property(_get_subsection, _set_subsection)

    # paragraph
    def _get_paragraph(self):
        return self.__paragraph
    def _set_paragraph(self, value):
        if not isinstance(value, str):
            raise TypeError("The paragraph must be set to a string.")
        self.__paragraph = value
    paragraph = property(_get_paragraph, _set_paragraph)

    # variant
    def _get_variant(self):
        return self.__variant
    def _set_variant(self, value):
        if not isinstance(value, Variant.Variant):
            raise TypeError("The variant must be set to a class 'Variant.Variant'.")
        self.__variant = value
    variant = property(_get_variant, _set_variant)

    # other
    def _get_other(self):
        return self.__other
    def _set_other(self, value):
        if not isinstance(value, str):
            raise TypeError("The other must be set to a string.")
        self.__other = value
    other = property(_get_other, _set_other)

    def getDatePublication(self):
        return self.datePublication

    def getFixing(self):
        return self.fixing

    def getDateEffective(self):
        return self.dateEffective

    def getDateTenor(self):
        return self.dateTenor

    def getDocument(self):
        return self.document

    def getItem(self):
        return self.item

    def getChapter(self):
        return self.chapter

    def getSection(self):
        return self.section

    def getSubsection(self):
        return self.subsection

    def getParagraph(self):
        return self.paragraph

    def getVariant(self):
        return self.variant

    def getOther(self):
        return self.other

    def setDateEffective(self, dateEffective):
        if isinstance(dateEffective, (datetime.datetime, datetime.date)):
            self.dateEffective = dateEffective
        else:
            if dateEffective != '':
                self.dateEffective = Dates.dateTimeFromString(dateEffective)
            else:
                if isinstance(self.getDatePublication(), str):
                    if Dates.isDateTimeFromDateTimeOrDateString(self.getDatePublication()):
                        self.dateEffective = Dates.dateTimeFromString(self.getDatePublication())
                    else:
                        datePublication = Dates.dateFromString(self.getDatePublication())
                        hour, minute, second = Enumerations.Fixing.getTime(self.getFixing())
                        self.dateEffective = Dates.createDateTimeFromValues(datePublication.year, datePublication.month, datePublication.day, hour, minute, second)
                else:
                    hour, minute, second = Enumerations.Fixing.getTime(self.getFixing())
                    self.dateEffective = Dates.createDateTimeFromValues(self.getDatePublication().year, self.getDatePublication().month, self.getDatePublication().day, hour, minute, second)

    def setDateTenor(self, dateTenor):
        if isinstance(dateTenor, (datetime.datetime, datetime.date)):
            self.dateTenor = dateTenor
        else:
            if dateTenor != '':
                self.dateTenor = Dates.dateTimeFromString(dateTenor)
            else:
                self.dateTenor = self.getDateEffective()

    def getBase(self):
        for base in self.__class__.__bases__:
            return base.__name__

    @staticmethod
    def __serializeAndClean(dictionary):
        delete = []
        for key, value in zip(dictionary.keys(), dictionary.values()):
            #if key in ['fixing', 'datePublication']:
            #    delete.append(key)
            if value in [[], {}, None]:
                delete.append(key)
            elif isinstance(value, list):
                dictionary[key] = [item.getJson(True) for item in value]
            elif isinstance(value, Enumerations.Enum):
                dictionary[key] = value.value
            elif isinstance(value, (datetime.date, datetime.datetime)):
                dictionary[key] = Dates.getDateOrDateTimeString(value)
            elif isinstance(value, Variant.Variant):
                dictionary[key] = value.getJson()
            else:
                dictionary[key] = value
        for key in delete:
            del dictionary[key]
        return dictionary

    def getJson(self):
        # Get all attributes as a dictionary
        data = self.__dict__.copy()
        # Delete object private prefix from attribute names
        oldKeys = list(data.keys())
        for key in oldKeys:
            newKey = key.replace('_' + self.__class__.__name__ + '__', '')
            newKey = newKey.replace('_' + self.getBase() + '__', '')
            data[newKey] = data.pop(key)
        # Serialize object within the attribute and delete empty attributes
        data = self.__serializeAndClean(data)
        # jsonize data
        dataJson = json.dumps(data)
        return dataJson

