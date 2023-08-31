import psycopg2
import pandas as pd
# 초반 DB의 테이블 내용 형성
class CreateAndInsertDataBase:
    """
    DB Table 제작 코드
    """
    def __init__(self):
        self.set_init()

    def run(self):
        self.drop_table()
        self.create_table()

    def set_init(self):
        self.conn = psycopg2.connect(host='10.10.20.97', dbname='first_ai_project_db', user='first_ai_project', password=1234, port=5432)
        # 10.10.20.97
        self.cur = self.conn.cursor()

    def drop_table(self):
        self.cur.execute("DROP TABLE IF EXISTS TB_VEHICLE CASCADE")
        self.cur.execute("DROP TABLE IF EXISTS TB_USER CASCADE")


    def create_table(self):
        self.cur.execute("CREATE TABLE TB_USER("
                         "USER_ID SERIAL PRIMARY KEY,"
                         "USER_PLATE VARCHAR(12),"
                         "USER_PW VARCHAR(20),"
                         "USER_NAME VARCHAR(12),"
                         "USER_CONTACT VARCHAR(16))")

        self.cur.execute("CREATE TABLE TB_VEHICLE("
                         
                         "VEHICLE_ID SERIAL PRIMARY KEY,"
                         
                         "VEHICLE_PLATE VARCHAR(12),"
                         "VEHICLE_USE VARCHAR(10),"
                         "VEHICLE_SEND_TIME TIMESTAMP,"
                         "GPS VARCHAR(30),"
                         "VEHICLE_FROM_USER INTEGER,"
                         
                         "CONSTRAINT TB_VEHICLE FOREIGN KEY (VEHICLE_FROM_USER)"
                         "REFERENCES TB_USER (USER_ID)"
                         "ON DELETE CASCADE ON UPDATE CASCADE)")

        self.conn.commit()
        self.conn.close()

    # def show_data(self):
    #     self.connecting()
    #
    #     # 출력
    #     self.cur.execute(f'SELECT * FROM TB_HOSPITAL', self.conn)
    #     total_data = self.cur.fetchall()
    #     for row in total_data:
    #         print(row)
    #     self.conn.close()


if __name__ == '__main__':
    database_obj = CreateAndInsertDataBase()
    database_obj.run()
    # database_obj.show_data()

