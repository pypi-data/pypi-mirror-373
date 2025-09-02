"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

from enum import Enum

class UsagePlan(Enum):
    UsagePlan_Client = 0
    UsagePlan_Author = 1
    UsagePlan_Administrator = 2

class Action(Enum):
    Action_Enable = 1
    Action_Disable = -1

class Difficulty(Enum):
    Difficulty_Low = -100
    Difficulty_Standard = 0
    Difficulty_Static = 10
    Difficulty_High = 100
    Difficulty_Application = 50

class WaitForCompletion(Enum):
    Wait = 1
    NotWait = 0
    StartStop = -1
    Timeout_1_Minute = 60
    Timeout_2_Minutes = 120
    Timeout_3_Minutes = 180
    Timeout_4_Minutes = 240
    Timeout_5_Minutes = 300
    Timeout_6_Minutes = 360
    Timeout_7_Minutes = 420
    Timeout_8_Minutes = 480
    Timeout_9_Minutes = 540
    Timeout_10_Minutes = 600
    Timeout_11_Minutes = 660
    Timeout_12_Minutes = 720
    Timeout_13_Minutes = 780
    Timeout_14_Minutes = 840
    Timeout_15_Minutes = 900
    Timeout_20_Minutes = 1200

    def getString(self):
        return self.name

    def getValue(self):
        return self.value

    @staticmethod
    def fromValue(value):
        return WaitForCompletion(value)

    @staticmethod
    def fromString(string):
        for waitForCompletion in WaitForCompletion:
            if string == waitForCompletion.getString():
                return waitForCompletion

    def isTimeout(self):
        if self.getString().split('_')[0] == 'Timeout':
            return True
        else:
            return False