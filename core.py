"""
BySTo Core Module
- 데이터베이스 CRUD (Soft Delete 로직 적용)
- API 라우팅
- 세션 관리
- 유틸리티
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
import requests

# ===== 로깅 =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== 세션 관리 =====
user_sessions = {}

def clean_session():
    now = datetime.now()
    expired = [uid for uid, sess in user_sessions.items() 
               if (now - sess['timestamp']).total_seconds() > 300]
    for uid in expired:
        del user_sessions[uid]

def save_session(phone, question, answer):
    if not phone: return
    user_sessions[phone] = {
        'question': question,
        'answer': answer[:200],
        'timestamp': datetime.now()
    }
    clean_session()

def get_session(phone):
    if not phone or phone not in user_sessions: return None
    session = user_sessions[phone]
    if (datetime.now() - session['timestamp']).total_seconds() > 300: return None
    return session

# ===== 유틸리티 =====
def normalize_phone(phone):
    if not phone: return ""
    digits = ''.join(filter(str.isdigit, phone))
    if digits.startswith('0'): digits = digits[1:]
    return digits

def check_vllm_connection():
    try:
        response = requests.get("http://localhost:8000/v1/models", timeout=5)
        return response.status_code == 200
    except: return False

# ===== 데이터베이스 초기화 (기본 테이블 생성용) =====
def init_database(db_path):
    conn = sqlite3.connect(db_path, timeout=10.0)
    c = conn.cursor()
    
    # 1. 농가 정보 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS farm_info (
        phone TEXT PRIMARY KEY, 
        name TEXT, crop TEXT, farm_area TEXT, region TEXT, 
        cultivation_type TEXT, planting_date TEXT, address TEXT, password TEXT,
        facility_structure TEXT, dong_count INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # 2. 방제 이력 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS spray_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        phone TEXT NOT NULL, spray_date TEXT NOT NULL, 
        pest_name TEXT, pesticide_name TEXT, amount TEXT, temperature TEXT, 
        dilution_ratio TEXT, area_sprayed TEXT, notes TEXT, crop TEXT, photo_paths TEXT,
        start_time TEXT, end_time TEXT, duration_minutes INTEGER,
        is_deleted TEXT DEFAULT 'N', 
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # 3. 건의사항 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        phone TEXT NOT NULL, name TEXT, suggestion TEXT NOT NULL, timestamp TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()
    logger.info("✅ DB 초기화 로직 수행 완료")

def get_farm_info(phone, db_path):
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        normalized_phone = normalize_phone(phone)
        c.execute('SELECT * FROM farm_info WHERE phone = ?', (normalized_phone,))
        row = c.fetchone()
        conn.close()
        
        if row:
            keys = row.keys()
            return {
                'phone': row['phone'],
                'name': row['name'] or '',
                'crop': row['crop'] or '',
                'farm_area': row['farm_area'] or '',
                'region': row['region'] or '',
                'cultivation_type': row['cultivation_type'] or '노지',
                'planting_date': row['planting_date'] or '',
                'address': row['address'] or '',
                'password': row['password'] or '',
                'facility_structure': row['facility_structure'] if 'facility_structure' in keys else '',
                'dong_count': row['dong_count'] if 'dong_count' in keys else None
            }
        return None
    except Exception as e:
        logger.error(f"❌ 농가정보 오류: {e}")
        return None

def save_farm_info(data, db_path):
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        c = conn.cursor()
        phone = normalize_phone(data.get('phone', ''))
        facility_structure = data.get('facility_structure', '')
        dong_count = data.get('dong_count')
        try: dong_count = int(dong_count) if dong_count else None
        except: dong_count = None
        now = datetime.now().isoformat()

        c.execute('SELECT phone FROM farm_info WHERE phone = ?', (phone,))
        if c.fetchone():
            update_fields = []
            update_values = []
            fields = ['name', 'crop', 'farm_area', 'region', 'cultivation_type', 
                      'planting_date', 'address', 'password', 'facility_structure', 'dong_count']
            
            for f in fields:
                if f in data:
                    update_fields.append(f"{f} = ?")
                    update_values.append(data[f])
            
            update_fields.append('updated_at = ?')
            update_values.append(now)
            
            if update_fields:
                query = f"UPDATE farm_info SET {', '.join(update_fields)} WHERE phone = ?"
                update_values.append(phone)
                c.execute(query, tuple(update_values))
        else:
            c.execute('''INSERT INTO farm_info 
                (phone, name, crop, farm_area, region, cultivation_type, planting_date, 
                 address, password, facility_structure, dong_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                phone, data.get('name', ''), data.get('crop', ''), data.get('farm_area', ''),
                data.get('region', ''), data.get('cultivation_type', ''),
                data.get('planting_date', ''), data.get('address', ''), 
                data.get('password', ''), facility_structure, dong_count, now
            ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ 저장 오류: {e}")
        return False

def get_spray_history(phone, days, db_path):
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        c = conn.cursor()
        normalized_phone = normalize_phone(phone)
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        c.execute('''SELECT spray_date, pest_name, pesticide_name, amount, temperature, 
                     dilution_ratio, area_sprayed, notes, created_at, crop, photo_paths, id,
                     start_time, end_time, duration_minutes
                     FROM spray_history 
                     WHERE phone = ? AND created_at >= ? 
                     AND (is_deleted IS NULL OR is_deleted = 'N')
                     ORDER BY created_at DESC''', (normalized_phone, cutoff_date))
        rows = c.fetchall()
        conn.close()
        
        # ✅ 시간 계산을 위해 현재 시점 가져오기
        now = datetime.now()
        
        history = []
        for row in rows:
            # ✅ 방제 시간(날짜 + 시작시간) 계산 로직 추가
            s_date = row[0]  # spray_date (YYYY-MM-DD)
            s_time = row[12] if row[12] else "00:00"  # start_time (HH:MM)
            
            hours_ago = 0.0
            try:
                # 날짜와 시간을 합쳐서 datetime 객체 생성
                dt_str = f"{s_date} {s_time}"
                last_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
                # 현재 시간과의 차이 계산
                diff = now - last_dt
                hours_ago = round(max(0, diff.total_seconds() / 3600.0), 1)
            except:
                # 파싱 실패 시 기본값 0.0
                pass

            history.append({
                'spray_date': row[0], 'pest_name': row[1], 'pesticide_name': row[2],
                'amount': row[3], 'temperature': row[4], 'dilution_ratio': row[5] or '',
                'area_sprayed': row[6] or '', 'notes': row[7] or '', 'created_at': row[8],
                'crop': row[9] or '', 'photo_paths': row[10] or '', 'id': row[11],
                'start_time': row[12] or '', 'end_time': row[13] or '', 'duration_minutes': row[14] or 0,
                'hours_ago': hours_ago  # ✅ 계산된 시간차 추가 (AI 컨설팅에서 사용)
            })
        return history
    except Exception as e:
        logger.error(f"❌ 방제이력 오류: {e}")
        return []

def save_spray_history(data, db_path):
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        c = conn.cursor()
        phone = normalize_phone(data.get('phone', ''))
        
        record_id = data.get('id')
        pest_name = data.get('target_pest') or data.get('pest_name') or ''
        pesticide_name = data.get('pesticide_name') or data.get('product_name') or ''
        amount = data.get('pesticide_amount') or data.get('amount') or ''
        crop = data.get('crop', '')
        photo_paths = data.get('photo_paths', '')
        
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        duration_minutes = data.get('duration_minutes', 0)
        
        if record_id:
            logger.info(f"🔄 수정 요청: ID={record_id}")
            if photo_paths:
                sql = '''UPDATE spray_history SET spray_date=?, crop=?, pest_name=?, 
                         pesticide_name=?, amount=?, notes=?, photo_paths=?,
                         start_time=?, end_time=?, duration_minutes=? WHERE id=?'''
                params = (data.get('spray_date', ''), crop, pest_name, pesticide_name, 
                          amount, data.get('notes', ''), photo_paths, 
                          start_time, end_time, duration_minutes, record_id)
            else:
                sql = '''UPDATE spray_history SET spray_date=?, crop=?, pest_name=?, 
                         pesticide_name=?, amount=?, notes=?,
                         start_time=?, end_time=?, duration_minutes=? WHERE id=?'''
                params = (data.get('spray_date', ''), crop, pest_name, pesticide_name, 
                          amount, data.get('notes', ''), 
                          start_time, end_time, duration_minutes, record_id)
            c.execute(sql, params)
        else:
            logger.info(f"✨ 신규 추가")
            c.execute('''INSERT INTO spray_history 
                (phone, spray_date, pest_name, pesticide_name, amount, temperature, 
                 dilution_ratio, area_sprayed, notes, crop, photo_paths, is_deleted,
                 start_time, end_time, duration_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'N', ?, ?, ?)''', (
                phone, data.get('spray_date', ''), pest_name, pesticide_name, amount, 
                data.get('temperature', ''), data.get('dilution_ratio', ''), 
                data.get('area_sprayed', ''), data.get('notes', ''), crop, photo_paths,
                start_time, end_time, duration_minutes))
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ 저장/수정 오류: {e}")
        return False

def delete_spray_log(log_id, phone, db_path):
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        c = conn.cursor()
        normalized_phone = normalize_phone(phone)
        try: target_id = int(log_id) 
        except: return False
        
        c.execute("SELECT id, is_deleted FROM spray_history WHERE id = ? AND phone = ?", (target_id, normalized_phone))
        row = c.fetchone()
        if not row:
            conn.close()
            return False
        if row[1] == 'Y':
            conn.close()
            return True

        c.execute("UPDATE spray_history SET is_deleted = 'Y' WHERE id = ?", (target_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ 삭제 로직 오류: {e}")
        return False

def delete_all_spray_history(phone, db_path):
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        c = conn.cursor()
        c.execute("UPDATE spray_history SET is_deleted = 'Y' WHERE phone = ?", (normalize_phone(phone),))
        cnt = c.rowcount
        conn.commit()
        conn.close()
        return cnt
    except: return 0

def save_suggestion(data, db_path):
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        c = conn.cursor()
        c.execute('INSERT INTO suggestions (phone, name, suggestion, timestamp) VALUES (?, ?, ?, ?)',
                  (normalize_phone(data.get('phone', '')), data.get('name', ''), 
                   data.get('suggestion', ''), data.get('timestamp', datetime.now().isoformat())))
        conn.commit()
        conn.close()
        return True
    except: return False

def load_excel_data(crop_name, excel_path):
    try:
        if not os.path.exists(excel_path): return pd.DataFrame()
        xls = pd.ExcelFile(excel_path)
        if crop_name and crop_name in xls.sheet_names: return pd.read_excel(excel_path, sheet_name=crop_name)
        return pd.read_excel(excel_path)
    except: return pd.DataFrame()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    return app

def execute_read_query(sql, params=(), db_path='bysto_farm.db'):
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return [row[0] for row in cursor.fetchall()]
    except: return []
    finally:
        if 'conn' in locals(): conn.close()

def get_region_step1(db_path):
    sql = "SELECT DISTINCT region_name FROM kma_grid_mapping WHERE region_name IS NOT NULL"
    all_regions = execute_read_query(sql, db_path=db_path)
    step1_regions = set()
    for region in all_regions:
        parts = region.split(' ')
        if parts and parts[0]: step1_regions.add(parts[0])
    return sorted(list(step1_regions))

def get_region_step2(parent_region1, db_path):
    sql = "SELECT DISTINCT region_name FROM kma_grid_mapping WHERE region_name LIKE ? || ' %'"
    all_regions = execute_read_query(sql, (parent_region1,), db_path=db_path)
    step2_regions = set()
    for region in all_regions:
        parts = region.split(' ')
        if len(parts) > 1 and parts[0] == parent_region1: step2_regions.add(parts[1])
    return sorted(list(step2_regions))

def get_region_step3(parent_regions1_2, db_path):
    sql = "SELECT DISTINCT region_name FROM kma_grid_mapping WHERE region_name LIKE ? || ' %'"
    all_regions = execute_read_query(sql, (parent_regions1_2,), db_path=db_path)
    step3_regions = set()
    prefix = parent_regions1_2 + ' '
    for region in all_regions:
        if region.startswith(prefix):
            step3 = region[len(prefix):]
            if step3: step3_regions.add(step3)
    return sorted(list(step3_regions))

def get_monthly_stats(phone, db_path):
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        c = conn.cursor()
        normalized_phone = normalize_phone(phone)
        current_month = datetime.now().strftime('%Y-%m')
        
        c.execute('''
            SELECT COUNT(*), SUM(CAST(amount AS FLOAT)), SUM(IFNULL(duration_minutes, 0))
            FROM spray_history 
            WHERE phone = ? 
              AND spray_date LIKE ? 
              AND (is_deleted IS NULL OR is_deleted = 'N')
        ''', (normalized_phone, f'{current_month}%'))
        
        result = c.fetchone()
        conn.close()
        
        count = result[0] if result else 0
        total_amount = result[1] if result and result[1] else 0.0
        total_minutes = result[2] if result and result[2] else 0
        
        return {'count': count, 'total_amount': total_amount, 'total_minutes': total_minutes}
    except Exception as e:
        logger.error(f"❌ 통계 계산 오류: {e}")
        return {'count': 0, 'total_amount': 0, 'total_minutes': 0}

# ===== 기상청 관련 (수정됨) =====
KMA_API_KEY = 'f104300aecd4febc287bd28e242f038f08ad8b4bfdb8fe8cc4f2bae368d5844d'
KMA_BASE_URL = 'https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0'

def get_grid_by_region(region_name, db_path):
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        c = conn.cursor()
        c.execute('SELECT nx, ny, region_name FROM kma_grid_mapping WHERE region_name = ?', (region_name,))
        row = c.fetchone()
        if not row:
            c.execute('SELECT nx, ny, region_name FROM kma_grid_mapping WHERE region_name LIKE ? LIMIT 1', (f'%{region_name}%',))
            row = c.fetchone()
        conn.close()
        if row: return {'nx': row[0], 'ny': row[1], 'region_name': row[2]}
        return None
    except: return None

# ✅ 시간 보정 함수 추가
def get_kma_base_datetime():
    now = datetime.now()
    if now.minute < 40: # 40분 전에는 이전 시간 데이터 요청
        now = now - timedelta(hours=1)
    return now.strftime('%Y%m%d'), now.strftime('%H00')

def get_weather_from_kma(nx, ny):
    try:
        base_date, base_time = get_kma_base_datetime()
        url = f'{KMA_BASE_URL}/getUltraSrtNcst'
        params = {'serviceKey': KMA_API_KEY, 'numOfRows': 10, 'pageNo': 1, 'dataType': 'JSON',
                  'base_date': base_date, 'base_time': base_time, 'nx': nx, 'ny': ny}
        # 🛡️ 타임아웃 5초로 단축
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200: return None
        data = response.json()
        if 'response' not in data or data['response']['header']['resultCode'] != '00': return None
        items = data['response']['body']['items']['item']
        weather_data = {'temperature': None, 'humidity': None}
        for item in items:
            if item['category'] == 'T1H': weather_data['temperature'] = float(item['obsrValue'])
            elif item['category'] == 'REH': weather_data['humidity'] = int(float(item['obsrValue']))
        return weather_data
    except Exception as e:
        logger.error(f"❌ 기상청 API 통신 에러: {e}")
        return None

def get_weather_by_phone(phone, db_path):
    try:
        farm_info = get_farm_info(phone, db_path)
        if not farm_info or not farm_info.get('region'): return None
        grid = get_grid_by_region(farm_info['region'], db_path)
        if not grid: return None
        weather = get_weather_from_kma(grid['nx'], grid['ny'])
        if weather: weather['region'] = farm_info['region']
        return weather
    except: return None


# ===== 통계 관련 =====
def get_detailed_stats(phone, db_path):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        normalized_phone = normalize_phone(phone)
        
        query_yearly = """
            SELECT strftime('%Y', spray_date) as year, 
                   COUNT(*), 
                   SUM(IFNULL(duration_minutes, 0))
            FROM spray_history
            WHERE phone = ? AND (is_deleted IS NULL OR is_deleted = 'N')
              AND spray_date >= date('now', '-5 years')
            GROUP BY year ORDER BY year ASC
        """
        c.execute(query_yearly, (normalized_phone,))
        yearly_data = [{"year": r[0], "count": r[1], "minutes": r[2]} for r in c.fetchall()]

        query_monthly = """
            SELECT strftime('%Y-%m', spray_date) as month, 
                   COUNT(*), 
                   SUM(IFNULL(duration_minutes, 0))
            FROM spray_history
            WHERE phone = ? AND (is_deleted IS NULL OR is_deleted = 'N')
              AND spray_date >= date('now', '-1 year')
            GROUP BY month ORDER BY month ASC
        """
        c.execute(query_monthly, (normalized_phone,))
        monthly_data = [{"month": r[0], "count": r[1], "minutes": r[2]} for r in c.fetchall()]

        c.execute("""
            SELECT pesticide_name, COUNT(*) as cnt 
            FROM spray_history 
            WHERE phone = ? AND is_deleted = 'N'
            GROUP BY pesticide_name ORDER BY cnt DESC LIMIT 1
        """, (normalized_phone,))
        top_pesticide = c.fetchone()

        conn.close()
        return {
            "yearly_trends": yearly_data,
            "monthly_trends": monthly_data,
            "top_pesticide": top_pesticide[0] if top_pesticide else "없음"
        }
    except Exception as e:
        print(f"Stats Error: {e}")
        return {"yearly_trends": [], "monthly_trends": [], "top_pesticide": "없음"}
    
