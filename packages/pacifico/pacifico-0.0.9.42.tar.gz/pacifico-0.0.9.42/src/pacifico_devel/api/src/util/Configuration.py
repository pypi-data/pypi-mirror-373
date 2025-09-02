"""Copyright © 2020 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

try:
    import psycopg2
except Exception as e:
    print(f'Error importing psycopg2 ({str(e)})')

class Configuration():

    @staticmethod
    def get(key, connection):
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM public."Configuration" WHERE key=%s;', (key,))
            value = cursor.fetchone()[1]
        except (Exception, psycopg2.Error) as error:
            print(error)
        finally:
            if (connection):
                cursor.close()
        return value

if __name__=='__main__':
    import Connection
    connection = Connection.Connection.connect()
    x = Configuration.get("expiry_meters", connection)
    print(x, type(x))
