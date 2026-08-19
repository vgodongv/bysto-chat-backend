import sqlite3

def delete_user_by_phone(phone_number):
    # 1. DB 파일 연결 (파일명이 다르면 수정하세요!)
    db_path = 'bysto_farm.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 2. 삭제 SQL 실행
        # farm_info 테이블에서 해당 번호를 찾아 삭제합니다.
        sql = "DELETE FROM spray_history WHERE phone = ?"
        cursor.execute(sql, (phone_number,))

        # 3. 변경사항 저장 (중요! 이거 안 하면 안 지워져요)
        conn.commit()

        if cursor.rowcount > 0:
            print(f"✅ 삭제 성공: {phone_number} 데이터가 삭제되었습니다.")
        else:
            print(f"ℹ️ 알림: {phone_number} 번호와 일치하는 데이터가 없습니다.")

    except sqlite3.Error as e:
        print(f"❌ DB 에러 발생: {e}")
        
    finally:
        # 4. 연결 종료
        if conn:
            conn.close()

if __name__ == "__main__":
    # 삭제하고 싶은 번호 입력
    target_phone = '1076767407'
    delete_user_by_phone(target_phone)