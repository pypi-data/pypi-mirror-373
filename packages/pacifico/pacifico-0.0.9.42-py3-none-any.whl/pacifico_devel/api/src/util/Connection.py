try:
    import psycopg2
except Exception as e:
    print(f'Error importing psycopg2 ({str(e)})')

class Connection:

    @staticmethod
    def connect(user="pacifico", password="PACIFICO", host="pacifico.cx4dwi9ydr2o.us-west-2.rds.amazonaws.com", port="5432", database="pacifico"):
        connection = psycopg2.connect(user=user,
                                      password=password,
                                      host=host,
                                      port=port,
                                      database=database)
        return connection