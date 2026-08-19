"""
BySTo Main Server - 통합 수정본 (점유인증 및 중복체크 포함)
"""

from flask import request, jsonify, send_from_directory
from flask_cors import CORS
from core import *
from config import *
from answer_logic import *
import logging
import os
import random  
import sys
from datetime import datetime
# ✅ [1] 맥북 경로 기강 잡기 (모든 site-packages 경로 뒤지기)
for path in [
    os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"),
    "/usr/local/lib/python3.9/site-packages",
    "/Library/Python/3.9/site-packages"
]:
    if os.path.exists(path) and path not in sys.path:
        sys.path.append(path)

# ✅ [2] 솔라피 정석 임포트 - 대리님이 찾으신 바로 그 방식!
# 실패해도 서버는 일단 켜지게 try-except 처리합니다.
solapi_ok = False
try:
    from solapi import SolapiMessageService
    from solapi.model import RequestMessage
    solapi_ok = True
    print("✅ 솔라피(solapi) 정석 모듈 로드 성공!")
except ImportError:
    print("⚠️ 경고: solapi 라이브러리를 찾을 수 없습니다. (SMS만 안 되고 서버는 켜집니다!)")

# Flask 앱 설정
app = create_app()
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ===== 로그 필터 =====
class SecurityScanFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        block_patterns = [
            'code 400', 'code 404', 'code 505',
            'Bad request', 'Invalid HTTP', '\\x16\\x03',
            'PRI * HTTP/2.0', '/favicon.ico', '/robots.txt', 'GET / HTTP',
        ]
        for pattern in block_patterns:
            if pattern in message: return False
        return True

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addFilter(SecurityScanFilter())
werkzeug_logger.setLevel(logging.WARNING)

app = create_app()
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ===== [1] SMS 인증 기능 (Solapi) =====

# [설정] 키 값
API_KEY = 'NCSZ9AC7OJ74YOJX'
API_SECRET = 'DUCEWEOIDNY1EOLZLJLSCYJSJGGKAAUB'
SENDER_PHONE = '025257774'

otp_db = {} # {폰번호: 인증번호}

# ===== [A] SMS 인증 및 계정 관련 API =====

@app.route('/api/send-otp', methods=['POST', 'OPTIONS'])
def send_otp():
    if request.method == 'OPTIONS': return jsonify({'status': 'ok'}), 200
    if not solapi_ok:
        return jsonify({'success': False, 'message': '서버에 solapi 라이브러리가 없습니다.'}), 500
    
    try:
        data = request.json
        phone = normalize_phone(data.get('phone', '')).replace('-', '')
        
        if get_farm_info(phone, DB_PATH):
            return jsonify({'success': False, 'message': '이미 가입된 번호입니다.'}), 409
            
        otp_code = str(random.randint(100000, 999999))
        otp_db[phone] = otp_code
        
        # 솔라피 정석 발송 문법
        message_service = SolapiMessageService(api_key=API_KEY, api_secret=API_SECRET)
        message = RequestMessage(
            from_=SENDER_PHONE,
            to=phone,
            text=f'[바이에스투] 인증번호 [{otp_code}]를 입력해주세요.'
        )
        message_service.send(message)
        
        print(f"✅ 문자 발송 성공: {phone} ({otp_code})")
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 2. 인증번호 확인
@app.route('/api/verify-otp', methods=['POST', 'OPTIONS'])
def verify_otp():
    if request.method == 'OPTIONS': return jsonify({'status': 'ok'}), 200
    data = request.json
    phone = normalize_phone(data.get('phone', '')).replace('-', '')
    user_code = data.get('code', '')
    
    if otp_db.get(phone) == user_code:
        del otp_db[phone]
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'message': '인증번호가 틀렸습니다.'}), 400

# 3. 번호 중복 체크 (하나만 남기고 통합)
@app.route('/api/check-phone', methods=['POST', 'OPTIONS'])
def check_phone_api():
    if request.method == 'OPTIONS': return jsonify({'status': 'ok'}), 200
    data = request.json
    phone = normalize_phone(data.get('phone', ''))
    if get_farm_info(phone, DB_PATH):
        return jsonify({'success': False, 'message': '이미 가입된 번호입니다.'}), 409
    return jsonify({'success': True, 'message': '사용 가능한 번호입니다.'}), 200
# ===== [2] 회원 가입 및 로그인 =====

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login_api():
    if request.method == 'OPTIONS': return jsonify({'status': 'ok'}), 200
    data = request.json
    phone = normalize_phone(data.get('phone', ''))
    password = data.get('password', '').strip()
    
    farm_info = get_farm_info(phone, DB_PATH)
    if not farm_info: return jsonify({'success': False, 'message': '미등록'}), 401
    if farm_info.get('password') != password: return jsonify({'success': False, 'message': '비밀번호 불일치'}), 401
    return jsonify({'success': True, 'user': farm_info})

@app.route('/api/signup', methods=['POST', 'OPTIONS'])
def signup_api():
    if request.method == 'OPTIONS': return jsonify({'status': 'ok'}), 200
    try:
        data = request.json
        phone = normalize_phone(data.get('phone', ''))
        # 최종 가입 시에도 한 번 더 체크 (보안용)
        if get_farm_info(phone, DB_PATH): return jsonify({'success': False, 'message': '이미 가입'}), 409
        if save_farm_info(data, DB_PATH): return jsonify({'success': True}), 200
        return jsonify({'success': False}), 500
    except Exception as e:
        return jsonify({'success': False}), 500
    
# ✅ [복구] 홈 화면용 농장 정보 API
@app.route('/api/farm_info', methods=['GET', 'OPTIONS'])
def get_farm_info_api():
    if request.method == 'OPTIONS': return jsonify({'status': 'ok'}), 200
    try:
        phone = normalize_phone(request.args.get('phone', ''))
        # DB에서 정보를 가져옵니다 (이미 core.py에 로직은 살아있을 거예요)
        info = get_farm_info(phone, DB_PATH)
        
        if info:
            # 💡 Flutter 코드에서 요구하는 'farm_info' 키값으로 응답합니다.
            return jsonify({'success': True, 'farm_info': info}), 200
        else:
            return jsonify({'success': False, 'message': '정보 없음'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ✅ [복구] 이번달 방제 현황(횟수, 시간, 양) 통계를 가져오는 API
@app.route('/api/stats', methods=['GET', 'OPTIONS'])
def get_monthly_stats_api():
    if request.method == 'OPTIONS': 
        return jsonify({'status': 'ok'}), 200
    try:
        phone = normalize_phone(request.args.get('phone', ''))
        
        # 💡 core.py에 정의된 통계 계산 함수를 호출합니다.
        # 이 함수는 이번 달의 count, total_amount, total_minutes를 반환해야 합니다.
        stats = get_monthly_stats(phone, DB_PATH)
        
        if stats:
            return jsonify({'success': True, 'data': stats}), 200
        else:
            # 데이터가 아직 없는 경우 기본값 응답
            return jsonify({
                'success': True, 
                'data': {'count': 0, 'total_amount': 0, 'total_minutes': 0}
            }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# @app.route('/api/check-phone', methods=['POST', 'OPTIONS'])
# def check_phone_api():
#     if request.method == 'OPTIONS': return jsonify({'status': 'ok'}), 200
#     data = request.json
#     phone = normalize_phone(data.get('phone', ''))
#     if get_farm_info(phone, DB_PATH):
#         return jsonify({'success': False, 'message': '이미 가입된 전화번호입니다.'}), 409
#     return jsonify({'success': True, 'message': '사용 가능한 번호입니다.'}), 200

# ===== [3] AI 질문 답변 기능 =====

# @app.route('/ask', methods=['POST', 'OPTIONS'])
# def ask_question():
#     if request.method == 'OPTIONS': return jsonify({'status': 'ok'}), 200
#     try:
#         data = request.json
#         question = data.get('question', '').strip()
#         phone = normalize_phone(data.get('phone', ''))
#         if not question: return jsonify({'error': '질문 필요'}), 400
        
#         logger.info(f"📞 {phone} | {question}")
#         question_type = classify_question_type(question, phone)
#         context = get_all_context(phone, question, question_type)
#         answer = build_answer(question_type, context)
#         save_session(phone, question, answer)
        
#         return jsonify({'answer': answer, 'sources': [DATA_INFO['source']], 'type': question_type})
#     except Exception as e:
#         logger.error(f"❌ 오류: {e}")
#         return jsonify({'error': str(e)}), 500

# ================================================================
# 【복붙 위치】 main.py 의 "[3] AI 질문 답변 기능" 섹션, 기존 @app.route('/ask') 아래에 추가
# ----------------------------------------------------------------
# 기존 /ask 는 그대로 두고, 새 RAG 파이프라인을 /ask2 로 띄워 A/B 비교.
# (answer_question_rag 는 from answer_logic import * 로 이미 들어와 있음)
#
# 테스트:
#   curl -X POST http://localhost:8888/ask2 \
#        -H "Content-Type: application/json" \
#        -d '{"question":"고추 탄저병 발생 시 즉시 조치 방법","phone":"01076767407"}'
#
# 만족스러우면 → 기존 ask_question() 의 본문 3줄을
#   answer = answer_question_rag(question, phone)  로 바꿔치기하면 /ask 가 RAG로 전환됨.
# ================================================================

@app.route('/ask', methods=['POST', 'OPTIONS'])
def ask_question_rag_api():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    try:
        data = request.json
        question = data.get('question', '').strip()
        phone = normalize_phone(data.get('phone', ''))
        if not question:
            return jsonify({'error': '질문 필요'}), 400

        logger.info(f"📞[RAG] {phone} | {question}")
        answer = answer_question_rag(question, phone)     # ★ 새 파이프라인
        save_session(phone, question, answer)

        return jsonify({'answer': answer, 'sources': [DATA_INFO['source']], 'type': 'rag'})
    except Exception as e:
        logger.error(f"❌[RAG] 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
# ===== [4] 방제 일지 및 사진 관리 =====

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/spray_history', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
def spray_history_api():
    if request.method == 'OPTIONS': return jsonify({'status': 'ok'}), 200
    
    if request.method == 'GET':
        phone = normalize_phone(request.args.get('phone', ''))
        days = int(request.args.get('days', 30))
        history = get_spray_history(phone, days, DB_PATH)
        return jsonify({'success': True, 'data': history})
    
    elif request.method == 'POST':
        if request.content_type and 'multipart/form-data' in request.content_type:
            try:
                data = request.form.to_dict()
                data['start_time'] = request.form.get('start_time', '')
                data['end_time'] = request.form.get('end_time', '')
                data['duration_minutes'] = request.form.get('duration_minutes', 0)
                
                photo_path = ""
                if 'photo' in request.files:
                    file = request.files['photo']
                    if file and file.filename != '':
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                        saved_filename = timestamp + filename
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], saved_filename))
                        photo_path = f"/uploads/{saved_filename}"
                
                if photo_path: data['photo_paths'] = photo_path
                
                if save_spray_history(data, DB_PATH): return jsonify({'success': True, 'message': '저장 완료'})
                return jsonify({'success': False, 'message': 'DB 저장 실패'}), 500
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500
        else:
            data = request.json
            if save_spray_history(data, DB_PATH): return jsonify({'success': True, 'message': '저장 완료'})
            return jsonify({'success': False, 'message': '저장 실패'}), 500
    
    elif request.method == 'DELETE':
        phone = normalize_phone(request.args.get('phone', ''))
        log_id = request.args.get('id')
        if log_id:
            if delete_spray_log(log_id, phone, DB_PATH): return jsonify({'success': True})
            return jsonify({'success': False}), 500
        return jsonify({'success': False, 'message': 'ID 누락'}), 400

# ===== [5] 부가 기능 (날씨, 지역, 통계) =====

@app.route('/api/weather', methods=['GET', 'OPTIONS'])
def weather_api():
    if request.method == 'OPTIONS': return jsonify({'status': 'ok'}), 200
    phone = normalize_phone(request.args.get('phone', ''))
    weather = get_weather_by_phone(phone, DB_PATH)
    if weather: return jsonify({'success': True, 'data': weather})
    return jsonify({'success': False}), 404

@app.route('/api/regions/step1', methods=['GET'])
def get_regions_step1_api(): return jsonify(get_region_step1(DB_PATH)), 200

@app.route('/api/regions/step2', methods=['GET'])
def get_regions_step2_api(): return jsonify(get_region_step2(request.args.get('parent'), DB_PATH)), 200

@app.route('/api/regions/step3', methods=['GET'])
def get_regions_step3_api(): return jsonify(get_region_step3(request.args.get('parent'), DB_PATH)), 200

@app.route('/api/stats/detail', methods=['GET'])
def stats_detail_api():
    phone = normalize_phone(request.args.get('phone', ''))
    result = get_detailed_stats(phone, DB_PATH)
    return jsonify({'success': True, 'data': result})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'version': 'v4.3'})

# ✅ [추가] 농장 정보 수정 API
@app.route('/api/update_farm_info', methods=['POST', 'OPTIONS'])
def update_farm_info_api():
    if request.method == 'OPTIONS': return jsonify({'status': 'ok'}), 200
    try:
        data = request.json
        # core.py의 save_farm_info를 호출합니다. (이미 UPDATE 로직이 포함되어 있습니다)
        if save_farm_info(data, DB_PATH):
            return jsonify({'success': True, 'message': '정보가 수정되었습니다.'}), 200
        return jsonify({'success': False, 'message': '데이터베이스 저장 실패'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== 서버 시작 =====
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 BySTo 서버 v4.3 (SMS 중복체크 통합본)")
    print("=" * 60)
    init_database(DB_PATH)
    
    if check_vllm_connection(): print("✅ vLLM 연결 성공")
    if test_ai_connection(): print("✅ AI 연결 성공")
    
    app.run(host='0.0.0.0', port=8888, debug=True, threaded=True, use_reloader=False)