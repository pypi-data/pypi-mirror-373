"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

from .. import ServiceRequest

class ServiceRequestApplication(ServiceRequest.ServiceRequest):
    def __init__(self, token, applicationName, applicationArguments, help):
        ServiceRequest.ServiceRequest.__init__(self)
        self.token = token
        self.applicationName = applicationName
        self.__setArguments(help, applicationArguments)

    # token
    def _get_token(self):
        return self.__token
    def _set_token(self, value):
        if not isinstance(value, str):
            raise TypeError("The token must be set to a string.")
        self.__token = value
    token = property(_get_token, _set_token)

    # applicationName
    def _get_applicationName(self):
        return self.__applicationName
    def _set_applicationName(self, value):
        if not isinstance(value, str):
            raise TypeError("The applicationName must be set to a string.")
        self.__applicationName = value
    applicationName = property(_get_applicationName, _set_applicationName)

    # applicationArguments
    def _get_applicationArguments(self):
        return self.__applicationArguments
    def _set_applicationArguments(self, value):
        if not isinstance(value, dict):
            raise TypeError("The applicationArguments must be set to a dictionary.")
        # if not all(isinstance(item, FieldQuality.FieldQuality) for item in value):
        #     raise TypeError("The quality must be set to a list of items of class 'FieldQuality.FieldQuality'.")
        self.__applicationArguments = value
    applicationArguments = property(_get_applicationArguments, _set_applicationArguments)

    # help
    def _get_help(self):
        return self.__help
    def _set_help(self, value):
        if not isinstance(value, bool):
            raise TypeError("The help must be set to a boolean.")
        self.__help = value
    help = property(_get_help, _set_help)

    def __setArguments(self, help, applicationArguments):
        self.help = help
        if self.help:
            self.applicationArguments = {}
        else:
            self.applicationArguments = applicationArguments

    def getToken(self):
        return self.token

    def getApplicationName(self):
        return self.applicationName

    def getArguments(self):
        return self.applicationArguments

    @staticmethod
    def create(applicationName, applicationArguments, help, token):
        return ServiceRequestApplication(token, applicationName, applicationArguments, help)