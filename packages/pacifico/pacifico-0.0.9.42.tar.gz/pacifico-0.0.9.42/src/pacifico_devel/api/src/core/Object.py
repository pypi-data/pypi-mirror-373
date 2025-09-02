"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

from ..util import Enumerations
import abc

class Object:
    def __init__(self):
        self.__id = None
        self.setObjectTypeValue()
        self.className = self.getClassName()

    def getClassName(self):
        return self.__class__.__name__

    def setObjectTypeValue(self):
        className = self.getClassName()
        try:
            self.objectTypeValue = Enumerations.ObjectType[className].value
        except:
            pass

    def setId(self, id):
        if isinstance(id, int):
            self.__id = id
        else:
            raise TypeError("The id must be set to a integer.")

    def getId(self):
        return self.__id

    def getObjectTypeValue(self):
        return self.objectTypeValue

    @staticmethod
    def fromJson(jsonString):
        pass

    @abc.abstractmethod
    def getJson(self):
        pass

    @abc.abstractmethod
    def saveToDB(self):
        pass