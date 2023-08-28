import psycopg2
import random
import pandas as pd

'''
현재 존재하는 TABEL
 - TB_VEHICLE
    - VEHICLE_ID, VEHICLE_PLATE, VEHICLE_USE, VEHICLE_SEND_TIME, VEHICLE_FROM_USER
 - TB_USER
    - USER_ID, USER_PLATE, USER_PW, USER_NAME, USER_CONTACT
'''
class InteractionToDB:
    """
    DB 상호작용 코드
    """
    def __init__(self):
        self.conn = None
        self.cur = None

    def connecting(self):
        self.conn = psycopg2.connect(host='10.10.20.97', dbname='first_ai_project_db', user='first_ai_project', password=1234, port=5432)
        self.cur = self.conn.cursor()

    def insert_membership_registration(self, user_input_car_number, user_input_pw, user_input_name, user_input_phone_address): # 차량 번호, 비밀번호, 이름, 연락처
        self.connecting()
        tuple_data = (user_input_car_number, user_input_pw, user_input_name, user_input_phone_address)
        sql = '''INSERT INTO TB_USER (USER_PLATE, USER_PW, USER_NAME, USER_CONTACT) VALUES (%s, %s, %s, %s)'''
        self.cur.execute(sql, tuple_data)
        self.conn.commit()
        self.conn.close()

    def insert_detected_car_info(self, user_car_id, detected_car_plate_number, detected_car_use, detected_time): # 유저 차량 번호, 인식된 차량의 번호, 인식된 차량의 용도, 인식된 시간
        self.connecting()
        # 시간의 경우에는 "TO_TIMESTAMP('20210821 12:30', 'YYYYMMDD HH24:MI')" 이와 같이 timestamp포맷에 맞춰서 넣어줘야 한다.
        tuple_data = (user_car_id, detected_car_plate_number, detected_car_use, detected_time)
        sql = '''INSERT INTO TB_USER (VEHICLE_FROM_USER, VEHICLE_PLATE, VEHICLE_USE, VEHICLE_SEND_TIME) VALUES (%s, %s, %s, %s)'''
        self.cur.execute(sql, tuple_data)
        self.conn.commit()
        self.conn.close()

    # 특정 시간대에 있는 특정 차량 정보를 불러오도록 함.
    # sample_time > TO_TIMESTAMP('20210821 12:30', 'YYYYMMDD HH24:MI')
    # 참고 사이트 : http://www.gisdeveloper.co.kr/?p=11622
    def get_specific_car_number(self, specific_car_number, min_datetime, max_datetime):
        self.connecting()
        self.cur.execute(f"SELECT VEHICLE_ID, VEHICLE_PLATE, VEHICLE_USE, VEHICLE_SEND_TIME, VEHICLE_FROM_USER "
                         f"from TB_VEHICLE "
                         f"WHERE VEHICLE_PLATE = '{specific_car_number}' AND "
                         f"VEHICLE_SEND_TIME > TO_TIMESTAMP('{min_datetime}', 'YYYYMMDD HH24:MI') AND "
                         f"VEHICLE_SEND_TIME < TO_TIMESTAMP('{max_datetime}', 'YYYYMMDD HH24:MI')", self.conn)
        total_data = self.cur.fetchall()
        self.conn.commit()
        self.conn.close()
        return total_data

    def log_in(self, user_inpur_car_number, user_input_pw):
        '''
        등록되지 않은 차량의 경우
            return : "not_registered_this_car_number"
        비밀번호가 안맞는 경우
            return "check_pw"
        로그인 된 경우
            return "can_login"
        '''
        self.connecting()
        self.cur.execute(f"SELECT USER_PLATE, USER_PW from TB_USER WHERE USER_PLATE = '{user_inpur_car_number}'", self.conn)
        user_car_number_and_pw = self.cur.fetchone()
        if user_car_number_and_pw is None:
            return "not_registered_this_car_number"
        else:
            user_car_number = user_car_number_and_pw[0]
            user_pw = user_car_number_and_pw[1]
            if user_pw == user_input_pw:
                return "can_login"
            else:
                return "check_pw"





if __name__ == '__main__':
    interaction_to_db_obj = InteractionToDB()
    # get_data = interaction_to_db_obj.get_specific_car_number("123가 4567", "20210821 12:30", "20230821 12:30")
    # print(get_data)
    # a = get_data = interaction_to_db_obj.log_in("111가 1111", "1")
    # print(a)
    # interaction_to_db_obj.사용 함수()

