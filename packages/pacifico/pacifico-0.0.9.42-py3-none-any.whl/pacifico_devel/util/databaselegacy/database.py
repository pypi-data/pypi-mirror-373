import pandas as pd
import psycopg2 as pcg
import typing as typ

import pacifico_devel.util.cfg.Configuration as cfg
import pacifico_devel.util.reportTemplate.src.util.dataSource.dataSource as ds
import pacifico_devel.util.databaselegacy.CONFIG as CFG
import pacifico_devel.util.databaselegacy.Enumerations as enm


class PacificoDb(ds.DataSource):
    _host = CFG.HOST
    _port = CFG.PORT
    _user = CFG.USER
    _password = CFG.PASSWORD

    @classmethod
    def makeQuery(cls,
                  sqlQuery: str,
                  database: typ.Union[enm.DataBase, str] = enm.DataBase.Tasas,
                  toDateTime: bool = True) -> pd.DataFrame:
        """
        Returns data from database in dataFrame form.

        Returns (pd.DataFrame): data from database.
        """

        if any(s.lower() in CFG.SQL_MODIFICATION_WORDS for s in sqlQuery.split(" ")):
            raise ValueError("Can only make requests to server.")

        if isinstance(database, str):
            database = enm.DataBase[database]
        database = str(database)
        conn = pcg.connect(user=cls._user,
                           password=cls._password,
                           host=cls._host,
                           port=cls._port,
                           database=database)

        print(f"Loading from database {database}...")
        cursor = conn.cursor()
        cursor.execute(sqlQuery)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        conn.close()
        print(f"Loading from database {database}... DONE!")

        df = pd.DataFrame(data, columns=columns)

        if toDateTime:
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df.date)
        return df

    @classmethod
    def mostRecentEntryInDb(cls,
                            ticker: str):
        """

        Returns: most recent dates asociated to a given ticker, if they exist on any table of the database.

        """
        query = "SELECT * FROM information_schema.tables"
        dfTables = cls.makeQuery(sqlQuery=query)
        return dfTables


if __name__ == '__main__':
    print(cfg.get("Token_Pacifico"))
    sqlQuery = 'Select * from trackrecord_bkp'
    PacificoDb().makeQuery(sqlQuery).to_excel('trackRecord1.xlsx')
