"""
BySTo Answer Logic
- 35개 질문 유형 분류
- 35개 답변 템플릿
- Excel 검색 및 필터링
- 템플릿 조립
- AI 호출

🔥 이 파일을 주로 수정합니다.
"""

# import re
# import requests
# from datetime import datetime
# from config import *
# from answer_logic_data import *
# from core import logger, load_excel_data

# # ===== 질문 정규화 함수 =====
# def normalize_agricultural_terms(question):
#     """
#     농업 용어의 띄어쓰기 자동 제거
    
#     예시:
#         "점박이 응애" → "점박이응애"
#         "차 응애" → "차응애"
#         "흰 가루 병" → "흰가루병"
#         "잿빛 곰팡이 병" → "잿빛곰팡이병"
    
#     작동 원리:
#         병해충 접미사(응애, 진딧물, 병 등) 앞의 띄어쓰기를 제거하여
#         "점박이 응애"처럼 띄어쓰기된 입력을 정규화
#     """
    
#     # 병해충 접미사 목록 (자주 사용되는 것들)
#     pest_suffixes = [
#         # 해충 접미사
#         '응애', '진딧물', '나방', '벌레', '벌', '충', '선충', 
#         '파리', '깍지벌레', '매미충', '노린재', '바구미', '가루이',
#         '총채벌레', '풍뎅이', '굼벵이', '방아벌레', '잎벌레',
#         '하늘소', '메뚜기', '여치', '달팽이', '무당벌레',
        
#         # 병 접미사
#         '병', '곰팡이', '무늬병', '썩음병', '마름병', '더뎅이병',
#         '잘록병', '역병', '탄저병', '흰가루병', '노균병', '시들음병',
#         '균핵병', '비단병', '녹병', '잎마름병', '흑병', '떡병'
#     ]
    
#     result = question
    
#     for suffix in pest_suffixes:
#         # 패턴: "한글2글자이상 + 공백 + 접미사"를 "한글+접미사"로 변경
#         # 예: "점박이 응애" → "점박이응애"
#         pattern = r'([가-힣]{2,})\s+(' + re.escape(suffix) + r')'
#         result = re.sub(pattern, r'\1\2', result)
    
#     return result

# def get_josa(word, josa_type):
#     """
#     한국어 조사 자동 처리
    
#     Args:
#         word: 명사 (예: "응애", "잿빛곰팡이")
#         josa_type: 조사 종류 ("이/가", "을/를", "은/는")
    
#     Returns:
#         적절한 조사 (예: "가", "를", "는")
#     """
#     if not word:
#         return josa_type.split('/')[0]  # 기본값
    
#     # 마지막 글자의 유니코드 값
#     last_char = word[-1]
    
#     # 한글이 아니면 기본값
#     if not ('가' <= last_char <= '힣'):
#         return josa_type.split('/')[0]
    
#     # 받침 확인: (글자코드 - 0xAC00) % 28
#     # 0이면 받침 없음, 1~27이면 받침 있음
#     code = ord(last_char) - 0xAC00
#     has_jongsung = (code % 28) != 0
    
#     # 조사 선택
#     if josa_type == "이/가":
#         return "이" if has_jongsung else "가"
#     elif josa_type == "을/를":
#         return "을" if has_jongsung else "를"
#     elif josa_type == "은/는":
#         return "은" if has_jongsung else "는"
#     elif josa_type == "과/와":
#         return "과" if has_jongsung else "와"
#     else:
#         return josa_type.split('/')[0]

# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# # 질문 분류 함수
# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# def classify_question_type(question, phone=None):
#     """질문을 36개 유형 중 하나로 분류"""
    
#     # 🔥 질문 정규화 (띄어쓰기 문제 해결)
#     question = normalize_agricultural_terms(question)
    
#     q_lower = question.lower().replace(' ', '')
    
#     # 위험군 (1~6)
#     # 1단계: 명시적 약해 (질문에 방제 언급)
#     if _is_damage_question(question):
#         return 1
    
#     # 2단계: 암묵적 약해 (최근 방제 + 약해 증상)
#     if phone and _check_recent_spray_damage(question, phone):
#         return 1
    
#     if any(kw in q_lower for kw in ['섞어', '혼용', '같이써도', '함께', '같이뿌려']):
#         return 2
    
#     if any(kw in q_lower for kw in ['희석', '배수', '물양', '몇배', '물몇리터', '희석배수']):
#         return 3
    
#     if any(kw in q_lower for kw in ['언제쳐', '언제뿌려', '언제사용', '사용시기', '적기']):
#         return 4
    
#     if any(kw in q_lower for kw in ['날씨', '비올때', '비오면', '비온후', '비예보']):
#         return 5
    
#     if any(kw in q_lower for kw in ['안전사용', '수확전', '사용횟수', '최대횟수', '안전기준']):
#         return 6
    
#     # 증상 진단군 (7~13)
#     has_symptom = any(kw in q_lower for kw in [
#         # 원인/이유 질문
#         '왜', '무슨', '증상', '이유', '원인', '어째서',
#         # 발생/출현
#         '생겼', '생김', '나왔', '났어', '나타났', '발생', '왔어', '왔음', '옴',
#         # 상태 관찰
#         '있어', '있음', '보여', '보임', '발견',
#         # 확산/진행
#         '퍼졌', '번졌', '확대', '커졌', '늘었', '심해졌',
#         # 변화
#         '변했', '바뀌었', '됐어', '되었'
#     ])
#     has_pest = _extract_pest_from_question(question) is not None
    
#     # 병해충명이 없고, 증상 키워드가 있으면 유형 7~13
#     # 단, 약제 요청 키워드가 있으면 증상 진단 건너뜀 (약제 추천군으로)
#     # 약제 키워드는 아래에서 정의되므로 여기서는 직접 체크
#     temp_has_pesticide = any(kw in q_lower for kw in ['약', '추천', '뿌려', '방제', '농약', '살포', '치료', '써', '쳐', '살균제', '살충제', '약제', '약추천'])
    
#     if not has_pest and not temp_has_pesticide:
#         # 구체적 증상 키워드가 있으면 해당 유형으로 직접 분류
#         if any(kw in q_lower for kw in ['노랗', '빨갛', '갈색', '색이', '변색', '누렇', '황색', '적색']):
#             return 8
        
#         if any(kw in q_lower for kw in ['시들', '시듦', '축축', '늘어', '쳐짐', '말라', '시들시들', '축늘']):
#             return 9
        
#         if any(kw in q_lower for kw in ['반점', '점', '무늬', '얼룩', '점무늬', '검은점', '갈색점', '흰점', '흑점']):
#             return 10
        
#         if any(kw in q_lower for kw in [
#             '벌레', '벌레가', '작은벌레', '벌레있', '벌레보여',
#             '날아다녀', '날아다님', '기어다녀', '움직여', '달라붙'
#         ]):
#             return 11
        
#         if any(kw in q_lower for kw in ['끈적', '분비', '진득', '이슬', '끈끈', '감로', '끈적끈적']):
#             return 12
        
#         if any(kw in q_lower for kw in ['곰팡이', '가루', '곰팡', '흰가루', '회색', '솜털', '곰팡이병']):
#             return 13
        
#         # 증상 키워드는 있지만 구체적이지 않으면 유형 7
#         if has_symptom:
#             return 7
    
#     # 작물 정보군 (36) - 약제 추천보다 우선
#     # 취약 병해충 질문 (작물명 없이도 키워드만으로 판단)
#     if any(kw in q_lower for kw in ['취약', '잘걸리는', '잘생기는', '주의할병', '조심할병', '많은병', '흔한병', '흔한해충', '자주나는', '자주생기는', '주의해야할']):
#         crop = _extract_crop_from_question(question)
#         # 작물명이 있거나, DB에서 가져올 수 있으면 유형 36
#         if crop or phone:  # phone이 있으면 DB에서 작물명 가져올 수 있음
#             return 36


#     # 새로운 유형 감지 (37~45)
    
#     # 변수 미리 정의
#     pests = _extract_all_pests(question)
#     has_pesticide_keyword = any(kw in q_lower for kw in ['약', '추천', '뿌려', '방제', '농약', '살포', '치료', '써', '쳐', '살균제', '살충제', '약제', '약추천'])
    
#     # 37번: 교차 확인
#     if len(pests) >= 2 and any(kw in q_lower for kw in ['도', '둘다', '같이', '함께', '도되나', '도잡나', '도죽', '함께잡', '동시']):
#         return 37
    
#     # 38번: 예방
#     if any(kw in q_lower for kw in ['예방', '미리', '생기기전', '방지', '예방약', '예방차원', '예방용']):
#         return 38
    
    
#     # 46번: 생육단계별 방제 (모든 작물)
#     # 작물별 생육단계 키워드 감지
#     detected_crop = None
#     detected_stage = None
    
#     for crop, keywords in CROP_GROWTH_KEYWORDS.items():
#         for keyword in keywords:
#             if keyword in q_lower:
#                 detected_stage = keyword
#                 detected_crop = crop
#                 break
#         if detected_stage:
#             break
    
#     if detected_stage:
#         # 생육단계 키워드가 감지되면
#         # 1순위: DB에서 작물명 확인
#         if phone and not detected_crop:
#             try:
#                 from core import get_farm_info
#                 farm_info = get_farm_info(phone, DB_PATH)
#                 crop_name = farm_info.get('crop_name', '') if farm_info else ''
#                 # DB 작물명으로 키워드 재확인
#                 for crop, keywords in CROP_GROWTH_KEYWORDS.items():
#                     if crop in crop_name:
#                         detected_crop = crop
#                         break
#             except:
#                 pass
        
#         # 2순위: 질문에서 작물명 추출
#         if not detected_crop:
#             extracted_crop = _extract_crop_from_question(question)
#             if extracted_crop:
#                 for crop in CROP_GROWTH_KEYWORDS.keys():
#                     if crop in extracted_crop:
#                         detected_crop = crop
#                         break
        
#         # 방제 관련 키워드가 있으면 46번
#         if has_pesticide_keyword or any(kw in q_lower for kw in ['방제', '약', '추천', '어떻게', '관리']):
#             return 46
    
#     # 39번: 생육주기
#     growth_stage_keywords = [
#         '개화', '개화기', '꽃필때', '꽃피', '꽃피는', '개화중',
#         '착과', '착과기', '열매맺', '열매맺을때', '결실',
#         '정식', '정식후', '정식전', '심은후', '이식',
#         '육묘', '육묘기', '육묘중', '모종',
#         '수확기', '수확전', '수확후', '수확', '수확며칠전',
#         '생육기', '생육초기', '생육중기', '생육후기',
#         '어릴때', '어린', '초기', '성장기',
#         '화방', '1화방', '2화방', '3화방', '4화방', '5화방',
#         '엽기', '본엽', '떡잎',
#     ]
#     if any(kw in q_lower for kw in growth_stage_keywords) and has_pesticide_keyword:
#         return 39
    
#     # 40번: 계통 변경
#     if any(kw in q_lower for kw in ['계통', '성분바꿔', '성분변경', '다른성분', '순환']):
#         return 40
    
#     # 41번: 복합 병해충
#     if len(pests) >= 2 and any(kw in q_lower for kw in ['둘다잡', '한번에', '동시', '하나로', '같이잡']):
#         return 41
    
#     # 42번: 약제 비교
#     if any(kw in q_lower for kw in ['비교', '차이', '뭐가나아', '어떤게나아', '어떤게좋', '중뭐가']):
#         return 42
    
#     # 43번: 약효 지속
#     if any(kw in q_lower for kw in ['얼마나가나', '며칠가나', '효과며칠', '지속', '언제또', '얼마나오래']):
#         return 43
    
#     # 45번: 복잡 상황 (조건 3개 이상)
#     conditions = 0
#     if len(pests) >= 2: conditions += 1
#     if any(kw in q_lower for kw in growth_stage_keywords): conditions += 1
#     if any(kw in q_lower for kw in ['날씨', '비', '바람', '더워', '추워', '습도']): conditions += 1
#     if phone:
#         from core import get_spray_history
#         history = get_spray_history(phone, 3, DB_PATH)
#         if history: conditions += 1
#     if any(kw in q_lower for kw in ['심각', '너무', '어떡하', '어떻게', '걱정', '큰일']): conditions += 1
    
#     if conditions >= 3:
#         return 45

    
#     # 약제 추천군 (14~19)
#     has_pesticide_keyword = any(kw in q_lower for kw in ['약', '추천', '뿌려', '방제', '농약', '살포', '치료', '써', '쳐'])
    
#     if has_pest or has_pesticide_keyword:
#         is_ineffective = any(kw in q_lower for kw in ['효과없', '효과가없', '안죽', '안듣', '그대로', '여전', '계속'])
        
#         if is_ineffective:
#             return 15
        
#         if any(kw in q_lower for kw in ['예방', '미리', '생기기전', '방지', '예방약', '예방차원']):
#             return 18
        
#         if any(kw in q_lower for kw in ['또', '다시', '재발', '또생', '또나왔', '또발생']):
#             return 19
        
#         return 14
    
#     # 비병해충군 (20~24)
#     if any(kw in q_lower for kw in ['영양', '결핍', '비료', '질소', '칼슘', '끝이썩', '칼륨', '마그네슘']):
#         return 20
    
#     if any(kw in q_lower for kw in ['일소', '냉해', '동해', '수분', '스트레스', '생리']):
#         return 21
    
#     if any(kw in q_lower for kw in ['익충', '무당벌레', '좋은벌레', '해충아닌', '꿀벌']):
#         return 22
    
#     if '잡초' in q_lower or ('풀' in q_lower and '제거' in q_lower):
#         return 23
    
#     if any(kw in q_lower for kw in ['생육', '자람', '크기', '성장', '자라']):
#         return 24
    
#     # 기록·정보군 (25~28)
#     if any(kw in q_lower for kw in ['이력', '기록', '언제쳤', '뭐뿌렸', '기록보여', '사용내역']):
#         return 25
    
#     if any(kw in q_lower for kw in ['다음', '다음방제', '언제가능', '시기언제']):
#         return 26
    
#     if any(kw in q_lower for kw in ['정보', '성분', '어떤약', '약제정보', '알려줘']):
#         if _contains_pesticide_name(question):
#             return 27
    
#     if any(kw in q_lower for kw in ['있는약', '보유', '재고', '가지고', '가진약']):
#         return 28
    
#     # 불명확군 (29~32)
#     crop = _extract_crop_from_question(question)
#     pest = _extract_pest_from_question(question)
    
#     if not crop and has_pesticide_keyword:
#         return 29
    
#     if crop and not pest and not has_symptom and has_pesticide_keyword:
#         return 30
    
#     if len(question.strip()) < 5:
#         return 31
    
#     if any(kw in q_lower for kw in ['안녕', '고마워', '감사', '안녕하세요', '반가워', '헬로']):
#         return 32
    
#     # 연관질문군 (33~35)
#     if phone:
#         from core import get_session
#         session = get_session(phone)
        
#         if session:
#             if any(kw in q_lower for kw in ['그거', '그', '그약', '저거', '그건', '아까']):
#                 return 33
            
#             if any(kw in q_lower for kw in ['그리고', '또', '추가로', '더', '그외']):
#                 return 34
            
#             if any(kw in q_lower for kw in ['다른약', '대신', '말고', '제외', '다른거']):
#                 return 35
    
#     # 기본값
#     if pest:
#         return 14
    
#     return 31


# def _is_damage_question(question):
#     """약해 질문 감지 (명시적)"""
#     q_lower = question.lower()
    
#     spray_context = any(kw in q_lower for kw in ['방제', '약', '뿌린', '살포', '친', '치고', '했더니', '쳤더니'])
#     damage_symptom = any(kw in q_lower for kw in [
#         '약해', '시들', '탔어', '타버렸', '오그라', '말렸', '구멍', '이상', 
#         '잎이탔', '갈색으로', '변했어', '말라'
#     ])
    
#     return spray_context and damage_symptom


# def _check_recent_spray_damage(question, phone):
#     """최근 방제 + 약해 증상 = 약해 의심 (암묵적)"""
    
#     # 1. 약해 증상 키워드 체크
#     q_lower = question.lower()
#     damage_symptoms = any(kw in q_lower for kw in [
#         '시들', '탔', '타버렸', '오그라', '말렸', '이상', '갈색으로', '말라',
#         '변색', '노랗게', '검게', '구멍'
#     ])
    
#     if not damage_symptoms:
#         return False
    
#     # 2. 최근 72시간 이내 방제 이력 확인
#     try:
#         from core import get_spray_history
#         history = get_spray_history(phone, 3, DB_PATH)  # 최근 3일
        
#         if history and len(history) > 0:
#             hours_ago = history[0].get('hours_ago', 999)
            
#             # 72시간(3일) 이내 방제 + 약해 증상 = 약해 의심
#             if hours_ago < 72:
#                 logger.info(f"⚠️ 약해 의심: 방제 {hours_ago:.1f}시간 전 + 증상 감지")
#                 return True
    
#     except Exception as e:
#         logger.error(f"❌ 방제이력 확인 오류: {e}")
    
#     return False


# def _extract_crop_from_question(question):
#     """질문에서 작물명 추출 (동의어 → 엑셀 시트명)"""
    
#     # 🔥 질문 정규화 (띄어쓰기 문제 해결)
#     question = normalize_agricultural_terms(question)
    
#     # 🔥 병해충명 먼저 제거 (작물명 오인식 방지)
#     question_for_crop = question
#     for main_pest, synonyms in PEST_SYNONYMS.items():
#         for synonym in synonyms:
#             if synonym in question_for_crop:
#                 question_for_crop = question_for_crop.replace(synonym, ' ')
    
#     # 🔥 일반 한국어 단어 제거 (작물명 오인식 방지)
#     # "무슨", "무엇", "무조건" 등을 작물 "무"로 오인하는 것 방지
#     common_words = [
#         '무슨', '무엇', '무조건', '무관', '무료', '무리', '무게',
#         '가장', '가능', '가까운', '가지고',
#         '나머지', '나중에',
#         '다음', '다른', '다시',
#         '어떤', '어느', '어디',
#         '이런', '이것', '저것',
#         '그런', '그것',
#     ]
    
#     for word in common_words:
#         question_for_crop = question_for_crop.replace(word, ' ')
    
#     # 1단계: 동의어 사전에서 검색 (우선순위)
#     for main_crop, synonyms in CROP_SYNONYMS.items():
#         for synonym in synonyms:
#             if synonym in question_for_crop:
#                 return main_crop
    
#     # 2단계: 엑셀 시트명 직접 매칭
#     try:
#         import pandas as pd
#         import re
        
#         # 엑셀 파일의 모든 시트명 가져오기
#         xl_file = pd.ExcelFile(EXCEL_PATH)
#         sheet_names = xl_file.sheet_names
        
#         # 질문에 포함된 시트명 찾기 (긴 이름부터 매칭)
#         # 예: "감자탄저병" 질문에서 "감자" 찾기
#         sorted_sheets = sorted(sheet_names, key=len, reverse=True)
        
#         for sheet in sorted_sheets:
#             # 🔥 짧은 작물명 (2글자 이하)은 단어 경계 확인
#             if len(sheet) <= 2:
#                 # 정규식으로 단어 경계 확인
#                 # 앞뒤에 공백, 구두점, 한국어 조사, 시작/끝이 있어야 함
#                 # 한국어 조사: 은/는/이/가/을/를/에/에서/의/와/과/도/만/부터/까지/로/으로
#                 pattern = r'(^|[\s,.?!~]|은|는|이|가|을|를|에|에서|의|와|과|도|만|부터|까지|로|으로){0}($|[\s,.?!~]|은|는|이|가|을|를|에|에서|의|와|과|도|만|부터|까지|로|으로)'.format(re.escape(sheet))
#                 if re.search(pattern, question_for_crop):
#                     return sheet
#             else:
#                 # 3글자 이상은 기존 방식 (포함 여부만 확인)
#                 if sheet in question_for_crop:
#                     return sheet
        
#     except Exception as e:
#         # 엑셀 읽기 실패 시 무시
#         pass
    
#     return None


# def _extract_pest_from_question(question):
#     """질문에서 병해충명 추출 (동의어 → 패턴 인식)"""
    
#     # 🔥 질문 정규화 (띄어쓰기 문제 해결)
#     question = normalize_agricultural_terms(question)
    
#     # 0단계: 취약 병해충 질문은 병명 추출 안함
#     q_lower = question.lower().replace(' ', '')
#     if any(kw in q_lower for kw in ['취약', '잘걸리는', '잘생기는', '주의할', '조심할', '흔한병', '흔한해충', '자주나는']):
#         return None
    
#     # 1단계: 동의어 사전에서 검색 (우선순위)
#     for main_pest, synonyms in PEST_SYNONYMS.items():
#         for synonym in synonyms:
#             if synonym in question:
#                 return main_pest
    
#     # 2단계: 명확한 병명 패턴 인식 (동의어에 없는 경우)
#     # "~병" 형태의 병명 추출
#     import re
    
#     # 병명 패턴: 2글자 이상 + "병"
#     disease_pattern = r'([가-힣]{2,}병)'
#     diseases = re.findall(disease_pattern, question)
    
#     if diseases:
#         # 너무 긴 병명은 오류일 가능성 높음 (예: "망고가취약한병")
#         valid_diseases = [d for d in diseases if len(d) <= 8]
#         if valid_diseases:
#             # 가장 긴 병명 반환 (더 구체적)
#             return max(valid_diseases, key=len)
    
#     # 3단계: 일반적인 해충명 키워드 추출
#     pest_patterns = [
#         r'([가-힣]+진딧물)',
#         r'([가-힣]+응애)',
#         r'([가-힣]+나방)',
#         r'([가-힣]+가루이)',
#         r'([가-힣]+총채[벌레]*)',
#         r'([가-힣]+깍지벌레)',
#         r'([가-힣]+노린재)',
#         r'([가-힣]+매미충)',
#         r'([가-힣]+선녀벌레)',
#     ]
    
#     for pattern in pest_patterns:
#         pests = re.findall(pattern, question)
#         if pests:
#             return pests[0]
    
#     return None


# def _contains_pesticide_name(question):
#     """질문에 약제명이 포함되어 있는지 체크"""
#     q_lower = question.lower()
    
#     pesticide_patterns = [
#         '수화제', '유제', '액제', '입제', '분제', '수용제',
#         '돌격대', '팡파레', '인시피오', '다이마이트', '파단'
#     ]
    
#     return any(pattern in q_lower for pattern in pesticide_patterns)



# def _extract_all_pests(question):
#     """질문에서 모든 병해충명 추출 (복수)"""
    
#     pests = []
    
#     # 동의어 사전에서 검색
#     for main_pest, synonyms in PEST_SYNONYMS.items():
#         for synonym in synonyms:
#             if synonym in question and main_pest not in pests:
#                 pests.append(main_pest)
    
#     # 명확한 병명 패턴 인식
#     import re
#     disease_pattern = r'([가-힣]{2,}병)'
#     diseases = re.findall(disease_pattern, question)
    
#     for disease in diseases:
#         if len(disease) <= 8 and disease not in pests:
#             # 동의어에 없는 경우만 추가
#             if not any(disease in PEST_SYNONYMS.get(p, []) for p in pests):
#                 pests.append(disease)
    
#     return pests


# def _extract_growth_stage(question):
#     """질문에서 생육단계 추출"""
    
#     q_lower = question.lower().replace(' ', '')
    
#     stages = {
#         '육묘': ['육묘', '모종', '육묘기', '육묘중'],
#         '정식': ['정식', '정식후', '정식전', '이식', '심은후'],
#         '개화': ['개화', '개화기', '꽃필때', '꽃피는', '개화중'],
#         '착과': ['착과', '착과기', '열매맺', '결실'],
#         '수확': ['수확', '수확기', '수확전', '수확후'],
#     }
    
#     for stage, keywords in stages.items():
#         if any(kw in q_lower for kw in keywords):
#             return stage
    
#     # 화방
#     import re
#     if re.search(r'[1-5]화방', q_lower):
#         return '화방기'
    
#     return None


# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# # Excel 검색 및 필터링
# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# def search_and_filter_pesticides(pest_name, recent_3_sprays, df):
#     """Excel에서 약제 검색 → 필터링 → 정렬"""
    
#     if df.empty or not pest_name:
#         return []
    
#     # 1. 동의어 확장
#     search_keywords = PEST_SYNONYMS.get(pest_name, [pest_name])
    
#     # 2. 병명이면 '병' 제거 버전도 추가 (엑셀 매칭률 향상)
#     if pest_name not in PEST_SYNONYMS:  # 동의어 사전에 없는 경우만
#         if '병' in pest_name and len(pest_name) >= 3:
#             # "탄저병" → ["탄저병", "탄저"]
#             without_disease = pest_name.replace('병', '')
#             if without_disease not in search_keywords:
#                 search_keywords = [pest_name, without_disease]
    
#     logger.info(f"🔍 검색 키워드: {search_keywords}")
    
#     # 3. Excel 검색
#     results = []
    
#     for _, row in df.iterrows():
#         pest_disease = str(row.get('적용병해충', '')).lower()
        
#         if any(keyword.lower() in pest_disease for keyword in search_keywords):
#             results.append({
#                 'product_name': str(row.get('제품명', '')),
#                 'ingredient': str(row.get('성분명', '')),
#                 'content': str(row.get('함량', '')),
#                 'formulation': str(row.get('제형', '')),
#                 'company': str(row.get('회사명', '')),
#                 'pest_disease': str(row.get('적용병해충', '')),
#                 'dilution': str(row.get('희석배수', '')),
#                 'usage': str(row.get('사용적기 및 방법', '')),
#                 'safety': str(row.get('안전사용기준', '')),
#                 'registration_date': str(row.get('등록일', ''))
#             })
    
#     logger.info(f"📊 초기 검색: {len(results)}개")
    
#     if not results:
#         return []
    
#     # 3. 최근 3회 사용 성분 제외
#     if recent_3_sprays:
#         excluded_ingredients = set()
        
#         for spray in recent_3_sprays:
#             pesticide_name = spray.get('pesticide_name', '')
#             if pesticide_name:
#                 ingredient = _find_ingredient_in_excel(pesticide_name, df)
#                 if ingredient:
#                     parts = re.split(r'[.,+]', ingredient)
#                     for part in parts:
#                         cleaned = re.sub(r'[^가-힣a-zA-Z]', '', part).strip().lower()
#                         if cleaned and len(cleaned) > 2:
#                             excluded_ingredients.add(cleaned)
        
#         if excluded_ingredients:
#             logger.info(f"⛔ 제외 성분: {excluded_ingredients}")
#             before = len(results)
#             results = [r for r in results if not _has_excluded_ingredient(r['ingredient'], excluded_ingredients)]
#             logger.info(f"⛔ 3회 제외: {before}개 → {len(results)}개")
    
#     if not results:
#         logger.warning("⚠️ 최근 3회 제외 후 남은 약제 없음")
#         return []
    
#     # 4. 우선약제 정렬
#     results = _prioritize_pesticides(results, pest_name)
    
#     # 5. 중복 제거
#     results = _remove_duplicates(results)
    
#     logger.info(f"✅ 최종 결과: {len(results)}개")
    
#     return results


# def _find_ingredient_in_excel(pesticide_name, df):
#     """Excel에서 약제명으로 성분 찾기"""
#     try:
#         matches = df[df['제품명'].str.contains(pesticide_name, na=False, case=False)]
#         if not matches.empty:
#             return str(matches.iloc[0].get('성분명', ''))
#     except:
#         pass
#     return None


# def _has_excluded_ingredient(ingredient, excluded_set):
#     """성분이 제외 목록에 있는지 체크"""
#     parts = re.split(r'[.,+]', ingredient)
    
#     for part in parts:
#         cleaned = re.sub(r'[^가-힣a-zA-Z]', '', part).strip().lower()
        
#         if cleaned in excluded_set:
#             return True
    
#     return False


# def _prioritize_pesticides(pesticides, pest_name):
#     """우선약제 정렬 + 등록일 최신순"""
#     normalized_pest = pest_name
    
#     if '응애' in pest_name:
#         normalized_pest = '응애'
#     elif '진딧물' in pest_name:
#         normalized_pest = '진딧물'
#     elif '나방' in pest_name:
#         normalized_pest = '나방류'
#     elif '가루이' in pest_name:
#         normalized_pest = '가루이류'
    
#     priority_list = PRIORITY_PESTICIDES.get(normalized_pest, [])
    
#     if not priority_list:
#         # 우선약제 없으면 전체를 등록일 최신순으로 정렬
#         return _sort_by_registration_date(pesticides)
    
#     priority_results = []
#     normal_results = []
    
#     for item in pesticides:
#         product_name = item['product_name'].lower()
#         is_priority = False
        
#         for priority_name in priority_list:
#             if priority_name.lower() in product_name:
#                 priority_results.append(item)
#                 is_priority = True
#                 break
        
#         if not is_priority:
#             normal_results.append(item)
    
#     # 일반 약제를 등록일 최신순으로 정렬
#     normal_results = _sort_by_registration_date(normal_results)
    
#     logger.info(f"⭐ 우선약제: {len(priority_results)}개, 일반: {len(normal_results)}개 (등록일순)")
    
#     return priority_results + normal_results


# def _sort_by_registration_date(pesticides):
#     """등록일 최신순 정렬"""
#     def get_date_key(item):
#         date_str = item.get('registration_date', '')
#         if not date_str or date_str == 'nan' or date_str == 'None':
#             return '0000-00-00'  # 날짜 없으면 가장 오래된 것으로 취급
#         return date_str
    
#     try:
#         # 등록일 최신순 (내림차순)
#         return sorted(pesticides, key=get_date_key, reverse=True)
#     except Exception as e:
#         logger.warning(f"⚠️ 등록일 정렬 실패: {e}")
#         return pesticides  # 정렬 실패 시 원본 그대로 반환


# def _normalize_ingredient(ing):
#     """성분명을 개별 성분으로 분리 후 정규화"""
#     if not ing or ing == 'nan':
#         return set()
    
#     # '.' 또는 ',' 또는 '+' 로 분리
#     parts = re.split(r'[.,+]', ing)
    
#     # 각 성분 정규화
#     normalized_set = set()
#     for part in parts:
#         # 공백, 특수문자, 숫자 제거
#         cleaned = re.sub(r'[^가-힣a-zA-Z]', '', part)
#         if cleaned:
#             normalized_set.add(cleaned.strip().lower())
    
#     return normalized_set


# def _remove_duplicates(pesticides):
#     """성분명 중복 제거 (하나도 안 겹칠 때만 허용)"""
#     seen_ingredients = set()
#     unique = []
    
#     for item in pesticides:
#         ing = item['ingredient']
#         normalized_set = _normalize_ingredient(ing)
        
#         # 교집합 개수 확인 - 하나도 안 겹칠 때만 허용
#         overlap_count = len(normalized_set.intersection(seen_ingredients))
        
#         if overlap_count == 0:  # 하나도 안 겹칠 때만
#             seen_ingredients.update(normalized_set)  # 모든 성분 추가
#             unique.append(item)
#             # logger.info(f"   ✅ 추가: {item['product_name']} (성분 {overlap_count}개 겹침)")  # 로그 간소화
#         else:
#             pass  # 로그 간소화: 제외된 약제는 표시하지 않음
    
#     logger.info(f"🔄 성분 중복 제거: {len(pesticides)}개 → {len(unique)}개")
    
#     return unique


# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# # 연속 방제 판단
# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# def judge_continuous_spray(hours, pest_type, temperature=25, severity='중등'):
#     """연속 방제 가능 여부 판단"""
    
#     logger.info(f"🔍 판단: {hours}시간, {pest_type}, {temperature}°C, {severity}")
    
#     # 1. 절대 금지 (12시간 미만)
#     if hours < 12:
#         return {
#             'allow': False,
#             'reason': '약해 위험 극대 - 최소 12시간 필요',
#             'wait': 12 - hours,
#             'condition': '',
#             'level': 'DANGER'
#         }
    
#     # 2. 병해충 특성 파악
#     is_disease = any(keyword in pest_type for keyword in DISEASES)
#     is_fast_pest = any(keyword in pest_type for keyword in FAST_BREEDING_PESTS)
#     is_slow_pest = any(keyword in pest_type for keyword in SLOW_BREEDING_PESTS)
    
#     # 3. 병(Disease) 처리
#     if is_disease:
#         if hours < 72:
#             return {
#                 'allow': False,
#                 'reason': '병은 약효 발현이 느림 - 72시간(3일) 대기 권장',
#                 'wait': 72 - hours,
#                 'condition': '환경 관리 우선 (통풍, 습도 낮추기)',
#                 'level': 'WAIT'
#             }
#         else:
#             return {
#                 'allow': True,
#                 'reason': '72시간 경과 - 효과 없으면 다른 성분 사용',
#                 'wait': 0,
#                 'condition': '다른 성분으로 변경 필수',
#                 'level': 'OK'
#             }
    
#     # 4. 고속 번식 해충
#     if is_fast_pest:
#         if hours >= 72:
#             return {
#                 'allow': True,
#                 'reason': '72시간 경과 - 저항성 가능성 높음',
#                 'wait': 0,
#                 'condition': '즉시 다른 성분으로 변경 필수',
#                 'level': 'URGENT'
#             }
        
#         elif hours >= 48:
#             if hours < 72:
#                 return {
#                     'allow': True,
#                     'reason': '48시간 경과했지만 72시간까지 대기 강력 권고',
#                     'wait': 72 - hours,
#                     'condition': f'⚠️ 가능하면 72시간({72-hours:.1f}시간 남음)까지 대기하세요. 긴급하면 다른 성분 사용',
#                     'level': 'CONDITIONAL_STRONG'
#                 }
#             else:
#                 return {
#                     'allow': True,
#                     'reason': '72시간 경과 - 저항성 가능성 높음',
#                     'wait': 0,
#                     'condition': '즉시 다른 성분으로 변경 필수',
#                     'level': 'URGENT'
#                 }
        
#         elif hours >= 24:
#             if temperature > 30:
#                 return {
#                     'allow': False,
#                     'reason': f'온도 {temperature}°C - 약해 위험 높음',
#                     'wait': 48 - hours,
#                     'condition': '온도 30°C 이하일 때 재방제',
#                     'level': 'WAIT'
#                 }
            
#             if severity == '심각':
#                 return {
#                     'allow': True,
#                     'reason': '24시간 경과 + 심각한 발생 + 적정 온도',
#                     'wait': 0,
#                     'condition': '다른 성분 + 희석배수 정확히 + 저녁 시간대 방제',
#                     'level': 'CONDITIONAL'
#                 }
#             else:
#                 return {
#                     'allow': False,
#                     'reason': '24시간 경과했지만 48시간까지 대기 권장',
#                     'wait': 48 - hours,
#                     'condition': '긴급하지 않으면 더 기다리기',
#                     'level': 'WAIT'
#                 }
        
#         else:
#             return {
#                 'allow': False,
#                 'reason': '24시간 미만 - 약효 발현 대기',
#                 'wait': 24 - hours,
#                 'condition': '희석배수, 살포 방법 재확인',
#                 'level': 'WAIT'
#             }
    
#     # 5. 저속 번식 해충
#     if is_slow_pest:
#         if hours < 72:
#             return {
#                 'allow': False,
#                 'reason': '저속 번식 해충 - 72시간(3일) 대기 권장',
#                 'wait': 72 - hours,
#                 'condition': '천천히 효과 나타남',
#                 'level': 'WAIT'
#             }
#         else:
#             return {
#                 'allow': True,
#                 'reason': '72시간 경과 - 재방제 가능',
#                 'wait': 0,
#                 'condition': '다른 성분 사용',
#                 'level': 'OK'
#             }
    
#     # 6. 기타
#     if hours < 48:
#         return {
#             'allow': False,
#             'reason': '일반 기준 48시간 대기',
#             'wait': 48 - hours,
#             'condition': '',
#             'level': 'WAIT'
#         }
#     else:
#         return {
#             'allow': True,
#             'reason': '48시간 경과',
#             'wait': 0,
#             'condition': '효과 없으면 다른 성분 사용',
#             'level': 'OK'
#         }


# def format_spray_judgment(judgment):
#     """판단 결과를 사용자 친화적인 문자열로 변환"""
    
#     if judgment['level'] == 'DANGER':
#         return f"""🚨🚨🚨 재방제 절대 금지 🚨🚨🚨

# 【이유】
# {judgment['reason']}

# 【대기 시간】
# 최소 {judgment['wait']:.1f}시간 더 기다려야 합니다.

# ❌ 약해 위험이 매우 높습니다!"""

#     elif judgment['level'] == 'WAIT':
#         return f"""⏰ 재방제 권장하지 않음

# 【이유】
# {judgment['reason']}

# 【권장 조치】
# 1. {judgment['wait']:.1f}시간 더 대기
# 2. {judgment['condition']}
# 3. 효과 재확인 후 판단"""

#     elif judgment['level'] == 'CONDITIONAL':
#         return f"""⚠️ 조건부 재방제 가능

# 【조건】
# {judgment['condition']}

# 모든 조건 충족 시에만 재방제하세요.
# 불확실하면 농업기술센터(1544-8572) 상담"""

#     elif judgment['level'] == 'CONDITIONAL_STRONG':
#         return f"""⚠️⚠️⚠️ 72시간 대기 강력 권고 ⚠️⚠️⚠️

# 【이유】
# {judgment['reason']}

# 【권장 조치】
# ✅ 가능하면 {judgment['wait']:.1f}시간 더 대기 (72시간까지)
# ✅ 대기 중 환경 관리 (통풍, 습도)
# ✅ 효과 재확인

# 【긴급 상황 시】
# {judgment['condition']}
# 아래 약제를 사용할 수 있습니다.
# (반드시 다른 성분으로 변경)"""

#     elif judgment['level'] == 'URGENT':
#         return f"""🚨 저항성 의심 - 즉시 성분 변경!

# 【이유】
# {judgment['reason']}

# 【필수 조치】
# ✅ 즉시 다른 성분으로 재방제
# ✅ 같은 성분은 2~3주 후 사용
# ✅ 2~3가지 성분 순환 사용"""

#     else:  # OK
#         return f"""✅ 재방제 가능

# 【이유】
# {judgment['reason']}

# 【조건】
# {judgment['condition']}"""


# def get_severity_from_question(question):
#     """질문에서 심각도 추정"""
    
#     q_lower = question.lower()
    
#     severe_keywords = [
#         '심각', '너무', '엄청', '많이', '가득', '온통', '전체', '다',
#         '죽겠', '망했', '큰일', '심해', '대량', '폭발'
#     ]
    
#     mild_keywords = [
#         '조금', '약간', '살짝', '몇개', '일부', '조금씩', '적게'
#     ]
    
#     if any(kw in q_lower for kw in severe_keywords):
#         return '심각'
#     elif any(kw in q_lower for kw in mild_keywords):
#         return '경미'
#     else:
#         return '중등'


# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# # 컨텍스트 수집
# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# def get_all_context(phone, question, question_type):
#     """질문에 필요한 모든 데이터 수집"""
    
#     from core import get_farm_info, get_spray_history, get_session, load_excel_data
    
#     logger.info(f"📦 컨텍스트 수집 시작: 유형 {question_type}")
    
#     context = {
#         'phone': phone,
#         'question': question,
#         'question_type': question_type,
#         'farm_info': None,
#         'crop_name': None,
#         'pest_name': None,
#         'spray_history': [],
#         'pesticides': [],
#         'exclude_info': None,
#         'warnings': [],
#         'severity': '중등',
#         'temperature': 25
#     }
    
#     # 1. 농가정보
#     if phone:
#         context['farm_info'] = get_farm_info(phone, DB_PATH)
#         # 🔍 디버그: get_farm_info 반환값 확인
#         logger.info(f"🔍 DEBUG: get_farm_info 반환값 전체 = {context['farm_info']}")
#         if context['farm_info']:
#             logger.info(f"✅ 농가정보: {context['farm_info'].get('name', '알수없음')}")
#             logger.info(f"🔍 DEBUG: name 필드 = {repr(context['farm_info'].get('name'))}")
    
#     # 2. 작물명 추출
#     crop = _extract_crop_from_question(question)
#     logger.info(f"🔍 질문에서 추출한 작물명: {crop}")
    
#     if not crop and phone:
#         session = get_session(phone)
#         if session and 'crop' in session:
#             crop = session['crop']
#             logger.info(f"📌 세션에서 작물명: {crop}")
    
#     if not crop and context['farm_info']:
#         crop = context['farm_info'].get('crop')
#         logger.info(f"🔍 DB에서 가져온 작물명 (저장 전): {crop}")
#         if crop:
#             logger.info(f"📌 DB에서 작물명: {crop}")
    
#     context['crop_name'] = crop
#     logger.info(f"✅ 최종 설정된 작물명 (crop_name): {context['crop_name']}")
    
#     # 3. 병해충명 추출
#     context['pest_name'] = _extract_pest_from_question(question)
#     if context['pest_name']:
#         logger.info(f"🐛 병해충명: {context['pest_name']}")
    
#     # 🔥 범위 넓은 질문 처리 (살균제, 살충제, 곰팡이약 등)
#     if not context['pest_name']:
#         q_lower = question.lower().replace(' ', '')
        
#         # 살균제/곰팡이약 → 대표 곰팡이병들
#         if any(kw in q_lower for kw in ['살균제', '곰팡이약', '곰팡이', '균제']):
#             if context['crop_name'] == '감귤':
#                 context['pest_name'] = '잿빛곰팡이병'  # 대표 곰팡이병
#                 context['broad_category'] = 'fungicide'  # 범위 넓은 질문 플래그
#                 logger.info(f"🔥 범위 넓은 질문: 살균제 → {context['pest_name']} 기반 검색")
#             else:
#                 context['pest_name'] = '흰가루병'  # 일반 작물 대표
#                 context['broad_category'] = 'fungicide'
#                 logger.info(f"🔥 범위 넓은 질문: 살균제 → {context['pest_name']} 기반 검색")
        
#         # 살충제 → 대표 해충들
#         elif any(kw in q_lower for kw in ['살충제', '해충약', '벌레약']):
#             if context['crop_name'] == '감귤':
#                 context['pest_name'] = '귤응애'
#                 context['broad_category'] = 'insecticide'
#                 logger.info(f"🔥 범위 넓은 질문: 살충제 → {context['pest_name']} 기반 검색")
#             else:
#                 context['pest_name'] = '진딧물'
#                 context['broad_category'] = 'insecticide'
#                 logger.info(f"🔥 범위 넓은 질문: 살충제 → {context['pest_name']} 기반 검색")
    
#     # 4. 심각도 추정
#     context['severity'] = get_severity_from_question(question)
    
#     # 5. 방제이력
#     if phone:
#         if question_type in [14, 15, 16, 17, 18, 19]:
#             days = 30
#         elif question_type in [25, 26]:
#             days = 90
#         elif question_type == 1:
#             days = 3
#         else:
#             days = 7
        
#         context['spray_history'] = get_spray_history(phone, days, DB_PATH)
#         logger.info(f"📋 방제이력: {len(context['spray_history'])}개 ({days}일)")
        
#         if context['spray_history']:
#             try:
#                 temp = float(context['spray_history'][0].get('temperature', 25))
#                 context['temperature'] = temp
#             except:
#                 pass
    
#     # 6. Excel 약제 검색
#     if question_type in [14, 15, 16, 17, 18, 19, 35]:
#         # 유형 15-17: 병해충명 없으면 방제 이력에서 가져오기
#         if question_type in [15, 16, 17]:
#             if not context.get('pest_name') and context['spray_history']:
#                 last_pest = context['spray_history'][0].get('pest_name', '')
#                 if last_pest:
#                     context['pest_name'] = last_pest
#                     logger.info(f"🐛 방제이력에서 병해충: {last_pest}")
        
#         if context['crop_name'] and context['pest_name']:
#             df = load_excel_data(context['crop_name'], EXCEL_PATH)
            
#             if not df.empty:
#                 context['pesticides'] = search_and_filter_pesticides(
#                     context['pest_name'],
#                     context['spray_history'][:3],
#                     df
#                 )
#                 logger.info(f"💊 약제 검색: {len(context['pesticides'])}개")
                
#                 if question_type in [15, 16, 17]:
#                     if context['spray_history']:
#                         last_spray = context['spray_history'][0]
#                         context['exclude_info'] = {
#                             'product': last_spray.get('pesticide_name', '알수없음'),
#                             'hours_ago': last_spray.get('hours_ago', 0),
#                             'ingredient': _find_ingredient_in_excel(
#                                 last_spray.get('pesticide_name', ''),
#                                 df
#                             )
#                         }
#             else:
#                 logger.warning(f"⚠️ Excel 시트 없음: {context['crop_name']}")
#         else:
#             if not context['crop_name']:
#                 logger.warning("⚠️ 작물명 없음")
#             if not context['pest_name']:
#                 logger.warning("⚠️ 병해충명 없음")
    
#     # 7. 경고 생성
#     context['warnings'] = _generate_warnings(context)
#     if context['warnings']:
#         logger.info(f"⚠️ 경고: {context['warnings']}")
    
#     return context


# def _generate_warnings(context):
#     """컨텍스트 기반 경고 생성"""
    
#     warnings = []
    
#     if context['spray_history']:
#         hours = context['spray_history'][0].get('hours_ago', 999)
        
#         if hours < 12:
#             warnings.append('DANGER_12H')
#         elif hours < 24:
#             warnings.append('WARNING_24H')
#         elif hours < 72:
#             warnings.append('INFO_72H')
    
#     if len(context['spray_history']) >= 3:
#         ingredients = []
#         for spray in context['spray_history'][:3]:
#             pest_name = spray.get('pesticide_name', '')
#             if pest_name and context.get('pesticides'):
#                 ingredients.append(pest_name)
        
#         if len(ingredients) != len(set(ingredients)):
#             warnings.append('INGREDIENT_DUP')
    
#     if context['question_type'] in [14, 15, 16, 17, 18, 19]:
#         if not context['pesticides']:
#             warnings.append('NO_PESTICIDES')
    
#     if context['temperature'] > 30:
#         warnings.append('HIGH_TEMP')
#     elif context['temperature'] < 15:
#         warnings.append('LOW_TEMP')
    
#     return warnings


# # def _create_empathy_message(question_type, context):
# #     """상황별 공감 메시지 생성 - 사용자 입장에서 강력한 공감 표현"""
    
# #     # 농가정보에서 이름 가져오기 (없으면 "고객"으로)
# #     farm_info = context.get('farm_info')
# #     if farm_info and farm_info.get('name'):
# #         farm_name = farm_info['name']  # 실제 농가명 사용
# #     else:
# #         farm_name = "고객"  # 이름 없으면 "고객님"으로 표시
    
# #     question = context.get('question', '')
# #     pest_name = context.get('pest_name', '병해충')
# #     crop_name = context.get('crop_name', '작물')
    
# #     # 방제 이력 정보
# #     spray_history = context.get('spray_history', [])
# #     hours = 0
# #     days = 0
# #     if spray_history:
# #         hours = spray_history[0].get('hours_ago', 0)
# #         days = hours / 24
    
# #     # 유형별 공감 메시지
# #     messages = {
# #         # 위험군 (1~6)
# #         1: f"😰 {farm_name}님, 방제 후 작물이 이상하다고 하시니 정말 당황스러우시겠습니다.\n   약해는 초기 대응이 중요하니 함께 확인해보겠습니다.",
        
# #         2: f"🤔 {farm_name}님, 약제를 섞어 쓰면 효과가 더 좋을까 궁금하신 거죠?\n   안전이 최우선이니 정확한 정보를 확인해보겠습니다.",
        
# #         3: f"🔍 {farm_name}님, 희석배수 때문에 고민이시군요.\n   정확하게 맞춰야 효과도 좋고 안전하니 꼼꼼히 확인해드리겠습니다.",
        
# #         4: f"⏰ {farm_name}님, 언제 방제해야 할지 고민되시죠?\n   시기가 정말 중요하니 최적의 타이밍을 알려드리겠습니다.",
        
# #         5: f"☁️ {farm_name}님, 날씨 때문에 방제 시기 잡기가 어려우시죠?\n   날씨를 고려한 최적의 타이밍을 알려드리겠습니다.",
        
# #         6: f"📋 {farm_name}님, 수확이 다가오니 안전간격이 걱정되시죠?\n   안전하게 출하할 수 있도록 정확히 확인해드리겠습니다.",
        
# #         # 증상 진단군 (7~13)
# #         7: f"🔍 {farm_name}님, \"{question}\" 이런 증상이 나타났다니 정말 걱정되시겠습니다.\n   정확히 진단해서 빠르게 대응할 수 있도록 도와드리겠습니다.",
        
# #         8: f"🍃 {farm_name}님, 잎 색깔이 이상하게 변했다니 걱정되시겠습니다.\n   영양 문제인지 병해충인지 정확히 확인해드리겠습니다.",
        
# #         9: f"💧 {farm_name}님, 작물이 시들시들해졌다니 정말 속상하시겠습니다.\n   원인을 빠르게 찾아서 대응할 수 있도록 도와드리겠습니다.",
        
# #         10: f"🔴 {farm_name}님, 잎에 이상한 반점이 생겼다니 걱정되시겠습니다.\n   병의 초기 증상일 수 있으니 빠르게 확인해드리겠습니다.",
        
# #         11: f"🐛 {farm_name}님, 벌레가 보인다니 빨리 잡고 싶으시겠죠?\n   어떤 해충인지 정확히 파악해서 효과적인 방법을 알려드리겠습니다.",
        
# #         12: f"💦 {farm_name}님, 잎이 끈적끈적해졌다니 불쾌하시겠습니다.\n   해충의 신호일 수 있으니 빠르게 확인해드리겠습니다.",
        
# #         13: f"🦠 {farm_name}님, 곰팡이가 생겼다니 번질까 정말 걱정되시겠습니다.\n   초기에 잡는 게 중요하니 빠르게 대응 방법을 알려드리겠습니다.",
        
# #         # 약제 추천군 (14~17)
# #         14: f"💊 {farm_name}님, {pest_name} 때문에 걱정이시군요.\n   {crop_name}에 효과 좋은 약제를 추천해드리겠습니다.",
        
# #         15: f"⏰ {farm_name}님, 방제했는데도 {pest_name}{get_josa(pest_name, '이/가')} 안 죽었다고 하시니 정말 걱정이 많으시겠습니다.\n   하지만 아직 약효가 나타나려면 시간이 더 필요해요. 조금만 더 기다려주세요!",
        
# #         16: f"⚠️ {farm_name}님, 방제했는데도 {pest_name}{get_josa(pest_name, '이/가')} 여전히 보이니 정말 걱정이 많으시겠습니다.\n   다시 치고 싶으시겠지만, 지금 치면 작물이 상할 수 있어요!",
        
# #         17: f"🚨 {farm_name}님, {days:.1f}일이나 지났는데도 {pest_name}{get_josa(pest_name, '이/가')} 안 죽었다니 정말 답답하시겠습니다.\n   저항성이 생겼을 가능성이 높으니 다른 성분으로 바꿔야 해요!",
        
# #         # 비병해충군 (20~24)
# #         20: f"🌱 {farm_name}님, 작물 상태가 좋지 않다니 걱정되시겠습니다.\n   영양 문제일 수 있으니 함께 확인해보겠습니다.",
        
# #         21: f"🌡️ {farm_name}님, 환경 스트레스로 작물이 힘들어하는 것 같아 걱정되시죠?\n   생리장해는 빠른 관리가 중요하니 대응 방법을 알려드리겠습니다.",
        
# #         22: f"🦋 {farm_name}님, 좋은 벌레인지 나쁜 벌레인지 헷갈리시죠?\n   잘못 죽이면 안 되니 정확하게 확인해드리겠습니다.",
        
# #         23: f"🌿 {farm_name}님, 잡초 때문에 정말 골치 아프시죠?\n   효과적인 제초 방법을 알려드리겠습니다.",
        
# #         24: f"📈 {farm_name}님, 작물 생육이 걱정되시죠?\n   건강하게 키우는 방법을 알려드리겠습니다.",
        
# #         # 정보군 (25~28)
# #         25: f"📝 {farm_name}님, 그동안 어떤 약을 쳤는지 궁금하시군요.\n   방제 기록을 함께 확인해보겠습니다.",
        
# #         26: f"📅 {farm_name}님, 언제 다시 방제해야 할지 궁금하시죠?\n   안전한 간격을 알려드리겠습니다.",
        
# #         27: f"ℹ️ {farm_name}님, 해당 약제에 대해 더 알고 싶으시군요.\n   상세한 정보를 확인해드리겠습니다.",
        
# #         28: f"💊 {farm_name}님, 창고에 있는 약을 쓸 수 있을지 궁금하시죠?\n   확인해드리겠습니다.",
        
# #         # 불명확군 (29~32)
# #         29: f"🤔 {farm_name}님, 어떤 작물에 대한 질문인지 알려주시면\n   더 정확하게 도와드릴 수 있어요!",
        
# #         30: f"🔍 {farm_name}님, 어떤 병해충인지 조금 더 자세히 말씀해주시면\n   딱 맞는 약제를 추천해드릴 수 있어요!",
        
# #         31: f"💬 {farm_name}님, 질문이 조금 짧아서 정확히 이해하기 어렵네요.\n   좀 더 자세히 말씀해주시면 더 잘 도와드릴 수 있어요!",
        
# #         32: f"👋 {farm_name}님, 반갑습니다!\n   오늘도 {crop_name} 농사로 고생이 많으시죠. 무엇을 도와드릴까요?",
        
# #         # 연관질문군 (33~35)
# #         33: f"💡 {farm_name}님, 아까 말씀하신 그 약제 관련 질문이시군요.\n   이어서 답변드리겠습니다.",
        
# #         34: f"➕ {farm_name}님, 추가로 궁금하신 게 있으시군요.\n   더 도와드리겠습니다.",
        
# #         35: f"🔄 {farm_name}님, 다른 약제가 필요하시군요.\n   대안을 찾아드리겠습니다.",
        
# #         # 작물정보군 (36)
# #         36: f"🛡️ {farm_name}님, {crop_name}에 어떤 병해충이 잘 생기는지 미리 알고 싶으시군요.\n   예방이 최선이니까요! 함께 확인해보겠습니다.",
        
# #         # 교차확인 (37)
# #         37: f"🔍 {farm_name}님, 여러 병해충을 한 번에 잡고 싶으시군요.\n   가능한 방법을 찾아드리겠습니다.",
        
# #         # 예방 (38)
# #         38: f"🛡️ {farm_name}님, 미리 예방하고 싶으시군요!\n   예방이 최선이죠. 방법을 알려드리겠습니다.",
        
# #         # 생육단계별 (46)
# #         46: f"🌱 {farm_name}님, {crop_name}의 생육 단계별 관리가 궁금하시군요.\n   단계별로 자세히 알려드리겠습니다.",
# #     }
    
# #     # 기본 메시지 (해당 유형이 없으면)
# #     default_message = f"💬 {farm_name}님, 질문 주셔서 감사합니다.\n   최선을 다해 답변드리겠습니다."
    
# #     return messages.get(question_type, default_message)

# def _create_empathy_message(question_type, context):
#     """상황별 공감 메시지 - 1~46번 전체 유형 대화체 업데이트"""
    
#     farm_info = context.get('farm_info')
#     farm_name = farm_info['name'] if farm_info and farm_info.get('name') else "농가"
#     pest_name = context.get('pest_name', '병해충')
#     crop_name = context.get('crop_name', '작물')
    
#     # 1~46번 전체 유형 메시지 셋
#     messages = {
#         # 위험군 (1~6)
#         1: f"😰 {farm_name}님, 방제 후에 작물이 이상해졌다니 정말 가슴이 덜컥하셨겠어요. 약해는 초기 대응이 생명이니 제가 얼른 같이 살펴볼게요.",
#         2: f"🤔 {farm_name}님, 약제를 섞어 쓰면 효과가 더 좋을까 궁금하시죠? 하지만 자칫하면 독이 될 수 있어 안전한 혼용인지 확인이 꼭 필요해요.",
#         3: f"🔍 {farm_name}님, 희석배수가 헷갈리시군요. 너무 진하면 약해가 나고, 연하면 효과가 없으니 딱 맞는 비율을 제가 꼼꼼히 챙겨드릴게요.",
#         4: f"⏰ {farm_name}님, 언제 약을 쳐야 가장 효과가 좋을지 고민되시죠? 작물의 컨디션과 병해충의 특성을 고려한 최적의 타이밍을 알려드릴게요.",
#         5: f"☁️ {farm_name}님, 변덕스러운 날씨 때문에 방제 일정 잡기가 참 힘드시죠? 비나 바람 조건을 고려해서 안전하게 뿌릴 수 있는 기준을 정리해 드릴게요.",
#         6: f"📋 {farm_name}님, 수확이 가까워지니 안전사용기준이 더 신경 쓰이시죠? 안심하고 출하하실 수 있도록 제가 정확하게 확인해 드릴게요.",
        
#         # 증상 진단군 (7~13)
#         7: f"🔍 {farm_name}님, 작물에 나타난 증상 때문에 걱정이 많으시죠? 어떤 원인인지 제가 차근차근 분석해서 해결 방법을 찾아보겠습니다.",
#         8: f"🍃 {farm_name}님, 잎 색깔이 변해서 많이 놀라셨죠? 단순한 영양 부족인지 병해충 때문인지 제가 세심하게 들여다볼게요.",
#         9: f"💧 {farm_name}님, 애써 키운 작물이 시들시들해지니 정말 속상하시겠어요. 원인을 빨리 찾아서 다시 생기를 찾을 수 있게 도와드릴게요.",
#         10: f"🔴 {farm_name}님, 잎에 생긴 반점이 번질까 봐 걱정되시죠? 어떤 병의 신호인지 확인해서 더 번지지 않게 막아보겠습니다.",
#         11: f"🐛 {farm_name}님, 벌레가 보이면 마음이 급해지기 마련이죠. 어떤 해충인지 정확히 알아야 한 번에 제대로 잡을 수 있습니다.",
#         12: f"🍯 {farm_name}님, 잎이 끈적거려서 당황하셨죠? 이건 해충이 보내는 신호일 수 있어요. 제가 어떤 녀석의 소행인지 밝혀드릴게요.",
#         13: f"🦠 {farm_name}님, 곰팡이가 보이면 금방 퍼질까 봐 무섭죠. 초기에 꽉 잡아야 하니 제가 빠른 대응 방법을 알려드릴게요.",
        
#         # 약제 추천군 (14~19)
#         14: f"💊 {farm_name}님, {pest_name} 때문에 고민이시군요. {crop_name}에 효과가 좋으면서도 안전한 약제들로 제가 엄선해 왔습니다.",
#         15: f"⏰ {farm_name}님, 방제 후에 효과가 바로 안 보여서 답답하시죠? 하지만 약효가 나타나려면 시간이 조금 필요해요. 우리 조금만 더 지켜볼까요?",
#         16: f"⚠️ {farm_name}님, 방제를 했는데도 여전히 병해충이 보여서 마음이 급하시겠지만, 지금 바로 또 뿌리면 작물이 너무 힘들어해요. 조금만 참아주세요!",
#         17: f"🚨 {farm_name}님, 3일이 지났는데도 그대로라면 저항성이 생긴 게 분명해요. 이제는 다른 전략으로 바꿔서 확실하게 잡아보겠습니다.",
#         18: f"🛡️ {farm_name}님, 미리미리 예방하려고 하시는군요! 역시 농사의 고수이십니다. 예방 차원에서 쓰기 좋은 약제들을 추천해 드릴게요.",
#         19: f"🔄 {farm_name}님, 다 잡은 줄 알았던 병해충이 다시 나와서 허탈하시죠? 지독한 녀석들이지만 이번엔 뿌리 뽑을 수 있게 도와드릴게요.",
        
#         # 비병해충군 (20~24)
#         20: f"🌱 {farm_name}님, 작물이 힘이 없는 게 영양 결핍 때문일 수도 있어요. 어떤 성분이 부족한지 확인해서 튼튼하게 키워보자고요.",
#         21: f"🌡️ {farm_name}님, 환경이 안 맞아서 작물이 스트레스를 받고 있나 봐요. 생리장해는 약보다는 환경 관리가 정답이니 제가 조절법을 알려드릴게요.",
#         22: f"🐞 {farm_name}님, 이 벌레가 우리 편인지 적군인지 궁금하시죠? 익충을 잘못 죽이면 손해니까 제가 똑똑하게 구분해 드릴게요.",
#         23: f"🌿 {farm_name}님, 잡초 때문에 허리 필 날 없으시죠? 조금이라도 덜 힘들게 관리하실 수 있는 방법을 함께 찾아보겠습니다.",
#         24: f"📈 {farm_name}님, 작물이 얼마나 잘 자라고 있는지 궁금하시군요. 건강한 성장을 위한 체크리스트를 정리해 드릴게요.",
        
#         # 정보/기능군 (25~28)
#         25: f"📝 {farm_name}님, 그동안 고생하며 관리하신 기록을 한눈에 보실 수 있게 제가 싹 정리해 왔습니다.",
#         26: f"📅 {farm_name}님, 다음 방제는 언제쯤 하면 좋을지 제가 날짜를 딱 짚어드릴게요. 안전한 간격을 지키는 게 중요하거든요.",
#         27: f"ℹ️ {farm_name}님, 궁금하신 약제에 대해 제가 아주 자세하고 알기 쉽게 설명해 드릴게요.",
#         28: f"📦 {farm_name}님, 창고에 있는 약을 알뜰하게 쓰시려는군요! 아직 쓸 수 있는 상태인지, 효과가 있을지 제가 확인해 드릴게요.",
        
#         # 미흡/일상 (29~32)
#         29: f"🤔 {farm_name}님, 어떤 작물을 키우시는지 제가 알면 더 정확한 약을 골라드릴 수 있어요! 작물 이름을 알려주세요.",
#         30: f"🔍 {farm_name}님, 어떤 녀석 때문에 고민인지 조금만 더 자세히 말씀해 주시면, 제가 딱 맞는 해결책을 가져올게요.",
#         31: f"💬 {farm_name}님, 질문이 조금 짧아서 제가 잘 이해하지 못했어요. 궁금하신 내용을 조금만 더 풀어서 말씀해 주시겠어요?",
#         32: f"👋 {farm_name}님, 안녕하세요! 오늘도 현장에서 땀 흘리시는 모습이 존경스럽습니다. 무엇을 도와드릴까요?",
        
#         # 연관/대체 (33~35)
#         33: f"💡 {farm_name}님, 아까 말씀하신 그 내용 이어서 더 자세히 설명해 드릴게요. 궁금한 점이 다 풀리실 거예요.",
#         34: f"➕ {farm_name}님, 추가로 궁금하신 게 더 있으시군요! 놓치는 부분 없도록 제가 끝까지 도와드리겠습니다.",
#         35: f"🔄 {farm_name}님, 다른 약제가 필요하시군요. 같은 효과를 내면서도 성분이 다른 대안들을 제가 찾아봤습니다.",
        
#         # 신규 유형 (36~46)
#         36: f"🛡️ {farm_name}님, {crop_name}을(를) 완벽하게 지키고 싶으시군요! 이 작물이 특히 조심해야 할 병해충들을 제가 정리해 드릴게요.",
#         37: f"🔍 {farm_name}님, 이 약으로 저 녀석까지 잡을 수 있을지 궁금하시죠? 제가 교차해서 꼼꼼히 확인해 드리겠습니다.",
#         38: f"🛡️ {farm_name}님, 병이 생기기 전에 미리 방어하고 싶으시군요! 예방이 최고의 방제죠. 효과적인 예방 전략을 알려드릴게요.",
#         39: f"📅 {farm_name}님, 작물이 쑥쑥 자라는 단계마다 방제법도 달라져야 해요. 지금 시기에 가장 적절한 관리법을 제안해 드릴게요.",
#         40: f"🔄 {farm_name}님, 계속 같은 약만 쓰면 내성이 생겨요. 똑똑하게 약을 바꿔가며 치는 '순환 방제'법을 알려드릴게요.",
#         41: f"🎯 {farm_name}님, 여러 병해충을 한 번에 소탕하고 싶으시군요! 일석이조의 효과를 볼 수 있는 약제를 제가 찾아보겠습니다.",
#         42: f"⚖️ {farm_name}님, 이 약이랑 저 약 중에 뭐가 더 좋을지 고민되시죠? 객관적인 정보를 바탕으로 제가 비교 분석해 드릴게요.",
#         43: f"⏱️ {farm_name}님, 한 번 치면 효과가 얼마나 갈지 궁금하시죠? 약효 지속 기간과 재방제 시기를 짚어드릴게요.",
#         44: f"❌ {farm_name}님, 아쉽게도 이 조합으로는 등록된 약이 없네요. 하지만 실망하지 마세요! 다른 안전한 대안을 제가 찾아봐 드릴게요.",
#         45: f"🔍 {farm_name}님, 여러 상황이 겹쳐서 많이 혼란스러우시죠? 복잡할수록 하나씩 차근차근 풀어나갈 수 있게 제가 분석해 드릴게요.",
#         46: f"🌱 {farm_name}님, {crop_name}의 생육 단계별 관리가 궁금하시군요. 지금이 가장 중요한 시기인 만큼 제가 맞춤형으로 알려드릴게요."
#     }
    
#     default_message = f"😊 {farm_name}님, 질문 주셔서 감사합니다. {crop_name} 농사에 실질적인 도움이 되는 답변을 드릴게요."
#     return messages.get(question_type, default_message)


# # def _create_personalized_header(context):
# #     """개인 맞춤 정보 헤더 생성 - 사용자가 맞춤 서비스를 받는다는 느낌 강화"""
    
# #     farm_info = context.get('farm_info')
# #     crop_name = context.get('crop_name', '알수없음')
# #     question_type = context.get('question_type', 31)  # 질문 유형 가져오기
    
# #     # 기본 헤더
# #     header_lines = ["━━━━━━━━━━━━━━━━━━━━━"]
    
# #     # 농가명이 있으면 개인화된 타이틀
# #     if farm_info and farm_info.get('name'):
# #         header_lines.append(f"📋 {farm_info['name']} 농가님 맞춤 분석")
# #     else:
# #         header_lines.append("📋 고객님 맞춤 분석 결과")
    
# #     header_lines.append("━━━━━━━━━━━━━━━━━━━━━")
# #     header_lines.append("")
    
# #     # ✨ 공감 메시지 추가 (농가명이 있을 때만)
# #     empathy_msg = _create_empathy_message(question_type, context)
# #     if empathy_msg:  # 공감 메시지가 있을 때만 추가
# #         header_lines.append(empathy_msg)
# #         header_lines.append("")
    
# #     # 재배 현황 헤더 (농가명이 있으면 개인화)
# #     if farm_info and farm_info.get('name'):
# #         header_lines.append(f"【{farm_info['name']}님의 재배 현황】")
# #     else:
# #         header_lines.append("【고객님의 재배 현황】")
    
# #     # 농가 정보 추가
# #     if farm_info:
# #         # 작물
# #         header_lines.append(f"• 재배 작물: {crop_name}")
        
# #         # 지역
# #         if farm_info.get('area') or farm_info.get('address'):
# #             area = farm_info.get('area') or farm_info.get('address')
# #             if area and area != 'None' and area != 'nan':
# #                 header_lines.append(f"• 재배 지역: {area}")
        
# #         # 면적
# #         if farm_info.get('size') or farm_info.get('farm_size'):
# #             size = farm_info.get('size') or farm_info.get('farm_size')
# #             if size and size != 'None' and size != 'nan':
# #                 header_lines.append(f"• 재배 면적: {size}")
        
# #         # 재배 방식
# #         if farm_info.get('cultivation_type'):
# #             cult_type = farm_info.get('cultivation_type')
# #             if cult_type and cult_type != 'None' and cult_type != 'nan':
# #                 header_lines.append(f"• 재배 방식: {cult_type}")
        
# #         # 연락처
# #         if farm_info.get('phone'):
# #             phone = farm_info.get('phone')
# #             if phone and phone != 'None' and phone != 'nan':
# #                 # 전화번호 포맷팅 (010-xxxx-xxxx 형태로)
# #                 if len(phone) == 11 and phone.startswith('010'):
# #                     formatted_phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
# #                     header_lines.append(f"• 연락처: {formatted_phone}")
# #                 else:
# #                     header_lines.append(f"• 연락처: {phone}")
# #     else:
# #         # 농가정보 없으면 최소한 작물만
# #         header_lines.append(f"• 재배 작물: {crop_name}")
    
# #     # 최근 방제 이력
# #     spray_history = context.get('spray_history', [])
# #     if spray_history and len(spray_history) > 0:
# #         last_spray = spray_history[0]
# #         hours = last_spray.get('hours_ago', 0)
# #         days = hours / 24
        
# #         header_lines.append("")
# #         header_lines.append("【최근 방제 이력】")
        
# #         # 방제 시점
# #         if days >= 1:
# #             header_lines.append(f"• {days:.1f}일 전 ({hours:.1f}시간 전) 방제하셨습니다")
# #         else:
# #             header_lines.append(f"• {hours:.1f}시간 전 방제하셨습니다")
        
# #         # 대상 병해충
# #         pest = last_spray.get('pest_name', '?')
# #         if pest and pest != '?':
# #             header_lines.append(f"• 대상 병해충: {pest}")
        
# #         # 사용 약제
# #         pesticide = last_spray.get('pesticide_name', '?')
# #         if pesticide and pesticide != '?':
# #             header_lines.append(f"• 사용 약제: {pesticide}")
        
# #         # 방제 온도
# #         temp = last_spray.get('temperature')
# #         if temp and temp != '?' and str(temp) != 'None' and str(temp) != 'nan':
# #             header_lines.append(f"• 방제 온도: {temp}°C")
    
# #     # 마무리
# #     header_lines.append("")
# #     header_lines.append("━━━━━━━━━━━━━━━━━━━━━")
# #     header_lines.append("👉 위 정보를 바탕으로 맞춤 분석한 결과입니다")
# #     header_lines.append("━━━━━━━━━━━━━━━━━━━━━")
# #     header_lines.append("")
    
# #     return '\n'.join(header_lines)

# def _create_personalized_header(context):
#     """불필요한 데이터 나열을 없애고 따뜻한 인사말만 남깁니다."""
    
#     farm_info = context.get('farm_info')
#     question_type = context.get('question_type', 31)
    
#     header_lines = ["━━━━━━━━━━━━━━━━━━━━━"]
    
#     # 1. 깔끔한 타이틀
#     if farm_info and farm_info.get('name'):
#         header_lines.append(f"📋 {farm_info['name']} 농가님 맞춤 조언")
#     else:
#         header_lines.append("📋 농가님 맞춤 조언")
    
#     header_lines.append("━━━━━━━━━━━━━━━━━━━━━\n")
    
#     # 2. 가장 중요한 공감 메시지 (여기서 모든 대화가 시작됩니다)
#     empathy_msg = _create_empathy_message(question_type, context)
#     header_lines.append(empathy_msg)
    
#     # 3. 마무리 (기존의 재배현황, 방제이력 리스트는 모두 삭제)
#     header_lines.append("\n━━━━━━━━━━━━━━━━━━━━━")
    
#     return '\n'.join(header_lines)


# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# # 템플릿 조립
# # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# def build_answer(question_type, context):
#     """유형에 맞는 템플릿 + 데이터 삽입"""
    
#     logger.info(f"🔧 답변 조립 시작: 유형 {question_type}")
    
#     # 유형 15~17 세분화
#     if question_type == 15 and context.get('exclude_info'):
#         hours = context['exclude_info'].get('hours_ago', 0)
#         if hours < 24:
#             question_type = 15
#         elif hours < 72:
#             question_type = 16
#         else:
#             question_type = 17
#         logger.info(f"📊 세분화: 유형 {question_type} (경과 {hours}시간)")
    
#     # 템플릿 선택
#     template = TEMPLATES.get(question_type, TEMPLATES[31])
    
#     # 필수 문구
    
#     # 재배방식 확인
#     farm_info = context.get('farm_info', {})
#     cultivation_type = farm_info.get('cultivation_type', '노지') if farm_info else '노지'
    
#     # 재배방식별 날씨 조건
#     from config import get_weather_condition
    
#     # context에 question_type 추가 (공감 메시지 생성용)
#     context['question_type'] = question_type
    
#     # ✨ 개인화 헤더 생성
#     personalized_header = _create_personalized_header(context)
    
#     data = {
#         'personalized_header': personalized_header,  # ✨ 개인화 헤더
#         'mandatory_top': MANDATORY_NOTICES['safety_top'],
#         'mandatory_bottom': MANDATORY_NOTICES['expert_bottom'].format(
#             tech_center_name=CONTACTS['tech_center_name'],
#             tech_center=CONTACTS['tech_center']
#         ),
#         'legal_disclaimer': MANDATORY_NOTICES['legal_disclaimer'],
#         'tech_center': f"{CONTACTS['tech_center_name']}({CONTACTS['tech_center']})",
#         'ai_limitation': MANDATORY_NOTICES['ai_limitation'],
#         'label_check': MANDATORY_NOTICES['label_check'],
#         'weather_condition': get_weather_condition(cultivation_type),
#         'effect_check': MANDATORY_NOTICES['effect_check'],
#         'resistance_management': MANDATORY_NOTICES['resistance_management'],
#         'protection_gear': MANDATORY_NOTICES['protection_gear'],
#         'question': context['question'],
#         'crop_name': context.get('crop_name', '미확인'),
#         'pest_name': context.get('pest_name', '미확인'),
#         # 템플릿용 한글 키 (유형 30, 31 등에서 사용)
#         '작물': context.get('crop_name', '감귤'),
#         '병해충': context.get('pest_name', '응애'),
#         '증상': '노랗게 변색',
#         '약제': '해당 약제',
#     }


import re
import requests
from datetime import datetime
from config import *
from answer_logic_data import *
from core import logger, load_excel_data

# ===== 질문 정규화 함수 =====
def normalize_agricultural_terms(question):
    """
    농업 용어의 띄어쓰기 자동 제거
    
    예시:
        "점박이 응애" → "점박이응애"
        "차 응애" → "차응애"
        "흰 가루 병" → "흰가루병"
        "잿빛 곰팡이 병" → "잿빛곰팡이병"
    
    작동 원리:
        병해충 접미사(응애, 진딧물, 병 등) 앞의 띄어쓰기를 제거하여
        "점박이 응애"처럼 띄어쓰기된 입력을 정규화
    """
    
    # 병해충 접미사 목록 (자주 사용되는 것들)
    pest_suffixes = [
        # 해충 접미사
        '응애', '진딧물', '나방', '벌레', '벌', '충', '선충', 
        '파리', '깍지벌레', '매미충', '노린재', '바구미', '가루이',
        '총채벌레', '풍뎅이', '굼벵이', '방아벌레', '잎벌레',
        '하늘소', '메뚜기', '여치', '달팽이', '무당벌레',
        
        # 병 접미사
        '병', '곰팡이', '무늬병', '썩음병', '마름병', '더뎅이병',
        '잘록병', '역병', '탄저병', '흰가루병', '노균병', '시들음병',
        '균핵병', '비단병', '녹병', '잎마름병', '흑병', '떡병'
    ]
    
    result = question
    
    for suffix in pest_suffixes:
        # 패턴: "한글2글자이상 + 공백 + 접미사"를 "한글+접미사"로 변경
        # 예: "점박이 응애" → "점박이응애"
        pattern = r'([가-힣]{2,})\s+(' + re.escape(suffix) + r')'
        result = re.sub(pattern, r'\1\2', result)
    
    return result

def get_josa(word, josa_type):
    """
    한국어 조사 자동 처리
    
    Args:
        word: 명사 (예: "응애", "잿빛곰팡이")
        josa_type: 조사 종류 ("이/가", "을/를", "은/는")
    
    Returns:
        적절한 조사 (예: "가", "를", "는")
    """
    if not word:
        return josa_type.split('/')[0]  # 기본값
    
    # 마지막 글자의 유니코드 값
    last_char = word[-1]
    
    # 한글이 아니면 기본값
    if not ('가' <= last_char <= '힣'):
        return josa_type.split('/')[0]
    
    # 받침 확인: (글자코드 - 0xAC00) % 28
    # 0이면 받침 없음, 1~27이면 받침 있음
    code = ord(last_char) - 0xAC00
    has_jongsung = (code % 28) != 0
    
    # 조사 선택
    if josa_type == "이/가":
        return "이" if has_jongsung else "가"
    elif josa_type == "을/를":
        return "을" if has_jongsung else "를"
    elif josa_type == "은/는":
        return "은" if has_jongsung else "는"
    elif josa_type == "과/와":
        return "과" if has_jongsung else "와"
    else:
        return josa_type.split('/')[0]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 질문 분류 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def classify_question_type(question, phone=None):
    """질문을 유형별로 분류"""
    
    # 🔥 질문 정규화 (띄어쓰기 문제 해결)
    question = normalize_agricultural_terms(question)
    
    q_lower = question.lower().replace(' ', '')

    # 💡 [추가] 방제 이력 상세 조회 (유형 25) 우선순위 상향
    # "언제", "무슨 약", "쳤더라", "기록", "며칠" 등의 키워드가 있으면 25번으로 보냄
   # ✅ [수정] 방제 이력/통계 조회 키워드 대폭 보강
    history_keywords = [
        '언제', '무슨약', '쳤더라', '쳤었지', '기록', '며칠', '어떤약', 
        '용량', '시간', '횟수', '몇번', '얼마나', '통계', '이력'
    ]
    # 질문에 '횟수' 등이 있고 '방제' 관련 언급이 있으면 25번으로 확실히 보냄
    if any(kw in q_lower for kw in history_keywords) and any(kw in q_lower for kw in ['방제', '약', '뿌린', '살포']):
        return 25
    
    # temp_has_pesticide = any(kw in q_lower for kw in ['약', '추천', '방제', '농약'])
    # has_pest = _extract_pest_from_question(question) is not None
    # # has_symptom = _extract_symptom_logic(q_lower) # 기존 symptom 체크 로직

    # if temp_has_pesticide and not has_pest and not has_symptom:
    #     return 30 # "무슨 병해충인지 알려달라"는 답변으로 유도
    
    # # 0. 공통 변수 추출
    # temp_has_pesticide = any(kw in q_lower for kw in [
    #     '약', '추천', '뿌려', '방제', '농약', '살포', '치료', '써', '쳐', 
    #     '살균제', '살충제', '약제', '약추천', '어떻게잡아', '죽이는'
    # ])
    
    # # 0. 공통 변수 추출 부분 수정
    # has_symptom = any(kw in q_lower for kw in [
    #     '왜', '무슨', '증상', '이유', '원인', '어째서',
    #     '생겼', '생김', '나왔', '났어', '나타났', '발생', '왔어', '왔음', '옴',
    #     '있어', '있음', '보여', '보임', '발견', '퍼졌', '번졌', '확대', '커졌', 
    #     '늘었', '심해졌', '변했', '바뀌었', '됐어', '되었', '이상해',
    #     # 👇 여기에 핵심 증상 키워드를 추가해야 7~13번 로직으로 진입합니다!
    #     '시들', '말라', '반점', '무늬', '벌레', '곰팡', '가루', '끈적', '점'
    # ])

    # ✅ [수정] has_symptom을 먼저 정의 (사용 전에)
    has_symptom = any(kw in q_lower for kw in [
        '왜', '무슨', '증상', '이유', '원인', '어째서',
        '생겼', '생김', '나왔', '났어', '나타났', '발생', '왔어', '왔음', '옴',
        '있어', '있음', '보여', '보임', '발견', '퍼졌', '번졌', '확대', '커졌', 
        '늘었', '심해졌', '변했', '바뀌었', '됐어', '되었', '이상해',
        '시들', '말라', '반점', '무늬', '벌레', '곰팡', '가루', '끈적', '점'
    ])
    
    temp_has_pesticide = any(kw in q_lower for kw in [
        '약', '추천', '뿌려', '방제', '농약', '살포', '치료', '써', '쳐', 
        '살균제', '살충제', '약제', '약추천', '어떻게잡아', '죽이는'
    ])
    has_pest = _extract_pest_from_question(question) is not None

    if temp_has_pesticide and not has_pest and not has_symptom:
        return 30  # "무슨 병해충인지 알려달라"는 답변으로 유도
    
    has_pest = _extract_pest_from_question(question) is not None
    

    # 1단계: 위험군 (1~6) - 가장 우선순위 높음
    if _is_damage_question(question): return 1
    if phone and _check_recent_spray_damage(question, phone): return 1
    if any(kw in q_lower for kw in ['섞어', '혼용', '같이써도', '함께', '같이뿌려']): return 2
    if any(kw in q_lower for kw in ['희석', '배수', '물양', '몇배', '물몇리터', '희석배수']): return 3
    if any(kw in q_lower for kw in ['언제쳐', '언제뿌려', '언제사용', '사용시기', '적기']): return 4
    if any(kw in q_lower for kw in ['날씨', '비올때', '비오면', '비온후', '비예보']): return 5
    if any(kw in q_lower for kw in ['안전사용', '수확전', '사용횟수', '최대횟수', '안전기준']): return 6
    
    # 2단계: 증상 진단군 (7~13) - 수정: 병해충명이 있더라도 '증상' 키워드가 있고 '약제요청'이 없으면 진단군 우선
    if has_symptom and not temp_has_pesticide:
        if any(kw in q_lower for kw in ['노랗', '빨갛', '갈색', '색이', '변색', '누렇', '황색', '적색']): return 8
        if any(kw in q_lower for kw in ['시들', '시듦', '축축', '늘어', '쳐짐', '말라', '시들시들', '축늘']): return 9
        if any(kw in q_lower for kw in ['반점', '점', '무늬', '얼룩', '점무늬', '검은점', '갈색점', '흰점', '흑점']): return 10
        if any(kw in q_lower for kw in ['벌레', '벌레가', '작은벌레', '벌레있', '벌레보여', '날아다녀', '기어다녀', '움직여']): return 11
        if any(kw in q_lower for kw in ['끈적', '분비', '진득', '이슬', '끈끈', '감로', '끈적끈적']): return 12
        if any(kw in q_lower for kw in ['곰팡이', '가루', '곰팡', '흰가루', '회색', '솜털', '곰팡이병']): return 13
        return 7

# 3단계: 작물 정보군 (36) - 키워드 대폭 보강
    if any(kw in q_lower for kw in [
        '취약', '잘걸리', '잘생기', '주의할병', '조심할병', 
        '많은병', '흔한병', '자주생기', '자주걸리', '주요병'
    ]):
        if _extract_crop_from_question(question) or phone: 
            return 36

    # 4단계: 새로운 유형 감지 (37~45)
    pests_all = _extract_all_pests(question)
    if len(pests_all) >= 2 and any(kw in q_lower for kw in ['도', '둘다', '같이', '함께', '도되나', '도잡나', '함께잡', '동시']): return 37
    if any(kw in q_lower for kw in ['예방', '미리', '생기기전', '방지', '예방약', '예방차원', '예방용']): return 38

    # 생육단계별 방제 (46)
    detected_stage = None
    for crop_key, keywords in CROP_GROWTH_KEYWORDS.items():
        for keyword in keywords:
            if keyword in q_lower:
                detected_stage = keyword
                break
        if detected_stage: break
    
    if detected_stage and (temp_has_pesticide or any(kw in q_lower for kw in ['방제', '어떻게', '관리'])): return 46

    # 5단계: 약제 추천군 (14~19)
    if has_pest or temp_has_pesticide:
        if any(kw in q_lower for kw in ['효과없', '안죽', '안듣', '그대로', '여전']): return 15
        if any(kw in q_lower for kw in ['또', '다시', '재발', '또생', '또나왔']): return 19
        return 14
    
    # 6단계: 기타 정보군 및 연관 질문
    if any(kw in q_lower for kw in ['영양', '결핍', '비료', '질소', '칼슘']): return 20
    if any(kw in q_lower for kw in ['일소', '냉해', '동해', '수분', '스트레스', '생리']): return 21
    if any(kw in q_lower for kw in ['익충', '무당벌레', '좋은벌레']): return 22
    if '잡초' in q_lower or ('풀' in q_lower and '제거' in q_lower): return 23
    if any(kw in q_lower for kw in ['이력', '기록', '언제쳤', '뭐뿌렸']): return 25
    if any(kw in q_lower for kw in ['다음', '다음방제', '언제가능']): return 26
    if _contains_pesticide_name(question): return 27
    if phone and any(kw in q_lower for kw in ['그거', '그약', '저거', '아까']): return 33
    if any(kw in q_lower for kw in ['안녕', '안녕하세요', '고마워']): return 32
    
    return 31 # 기본값


def _is_damage_question(question):
    """약해 질문 감지 (명시적)"""
    q_lower = question.lower()
    
    spray_context = any(kw in q_lower for kw in ['방제', '약', '뿌린', '살포', '친', '치고', '했더니', '쳤더니'])
    damage_symptom = any(kw in q_lower for kw in [
        '약해', '시들', '탔어', '타버렸', '오그라', '말렸', '구멍', '이상', 
        '잎이탔', '갈색으로', '변했어', '말라'
    ])
    
    return spray_context and damage_symptom


def _check_recent_spray_damage(question, phone):
    """최근 방제 + 약해 증상 = 약해 의심 (암묵적)"""
    
    # 💡 이 줄을 추가하여 q_lower를 정의해야 합니다.
    q_lower = question.lower().replace(' ', '')

    # 💡 '시들', '반점' 같은 일반 병 증상은 여기서 제외합니다.
    # 진짜 약해(화학적 피해) 의심 단어들만 남깁니다.
    damage_symptoms = any(kw in q_lower for kw in [
        '탔어', '타버렸', '오그라', '말렸', '구멍', '이상해'
    ])
    
    if not damage_symptoms:
        return False # '시들시들', '반점'은 질병 진단(7~13번)으로 보냅니다.
    
    # 2. 최근 72시간 이내 방제 이력 확인
    try:
        from core import get_spray_history
        history = get_spray_history(phone, 3, DB_PATH)  # 최근 3일
        
        if history and len(history) > 0:
            hours_ago = history[0].get('hours_ago', 999)
            
            # 72시간(3일) 이내 방제 + 약해 증상 = 약해 의심
            if hours_ago < 72:
                logger.info(f"⚠️ 약해 의심: 방제 {hours_ago:.1f}시간 전 + 증상 감지")
                return True
    
    except Exception as e:
        logger.error(f"❌ 방제이력 확인 오류: {e}")
    
    return False


def _extract_crop_from_question(question):
    """질문에서 작물명 추출 (동의어 → 엑셀 시트명)"""
    
    # 🔥 질문 정규화 (띄어쓰기 문제 해결)
    question = normalize_agricultural_terms(question)
    
    # 🔥 병해충명 먼저 제거 (작물명 오인식 방지)
    question_for_crop = question
    for main_pest, synonyms in PEST_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in question_for_crop:
                question_for_crop = question_for_crop.replace(synonym, ' ')
    
    # 🔥 일반 한국어 단어 제거 (작물명 오인식 방지)
    common_words = [
        '무슨', '무엇', '무조건', '무관', '무료', '무리', '무게',
        '가장', '가능', '가까운', '가지고',
        '나머지', '나중에',
        '다음', '다른', '다시',
        '어떤', '어느', '어디',
        '이런', '이것', '저것',
        '그런', '그것',
    ]
    
    for word in common_words:
        question_for_crop = question_for_crop.replace(word, ' ')
    
    # 1단계: 동의어 사전에서 검색 (우선순위)
    for main_crop, synonyms in CROP_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in question_for_crop:
                return main_crop
    
    # 2단계: 엑셀 시트명 직접 매칭
    try:
        import pandas as pd
        import re
        
        # 엑셀 파일의 모든 시트명 가져오기
        xl_file = pd.ExcelFile(EXCEL_PATH)
        sheet_names = xl_file.sheet_names
        
        # 질문에 포함된 시트명 찾기 (긴 이름부터 매칭)
        sorted_sheets = sorted(sheet_names, key=len, reverse=True)
        
        for sheet in sorted_sheets:
            if len(sheet) <= 2:
                pattern = r'(^|[\s,.?!~]|은|는|이|가|을|를|에|에서|의|와|과|도|만|부터|까지|로|으로){0}($|[\s,.?!~]|은|는|이|가|을|를|에|에서|의|와|과|도|만|부터|까지|로|으로)'.format(re.escape(sheet))
                if re.search(pattern, question_for_crop):
                    return sheet
            else:
                if sheet in question_for_crop:
                    return sheet
        
    except Exception as e:
        pass
    
    return None


def _extract_pest_from_question(question):
    """질문에서 병해충명 추출 (동의어 → 패턴 인식)"""
    import re
    
    # 1. 정규화 및 공백 제거 버전 준비
    question = normalize_agricultural_terms(question)
    q_clean = question.replace(' ', '') 
    
    # 2. [가장 중요] 정보 검색형 키워드가 있으면 병해충명을 추출하지 않음
    # 이렇게 해야 "어떤 병" 질문이 '유형 36(작물정보)'으로 안전하게 넘어갑니다.
    info_keywords = ['취약', '잘걸리', '잘생기', '주의할', '조심할', '흔한병', '흔한해충', '자주나는', '어떤병', '무슨병']
    if any(kw in q_clean for kw in info_keywords):
        return None

    # 3. [동의어 사전 매칭] (가장 정확한 방법)
    for main_pest, synonyms in PEST_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in question:
                return main_pest
    
    # 4. [해충 패턴 매칭] (진딧물, 응애 등 특정 어근)
    pest_patterns = [
        r'([가-힣]+진딧물)', r'([가-힣]+응애)', r'([가-힣]+나방)',
        r'([가-힣]+가루이)', r'([가-힣]+총채[벌레]*)', r'([가-힣]+깍지벌레)',
        r'([가-힣]+노린재)', r'([가-힣]+매미충)', r'([가-힣]+선녀벌레)',
    ]
    for pattern in pest_patterns:
        pests = re.findall(pattern, question)
        if pests:
            return pests[0]

    # 5. [일반 병명 패턴 매칭] (~병으로 끝나는 단어)
    # 💡 여기서 '어떤병', '무슨병' 등을 한 번 더 차단합니다.
    invalid_pests = ['어떤병', '무슨병', '어떤해충', '무슨해충', '이런병', '그런병', '모든병']
    disease_pattern = r'([가-힣]{2,}병)'
    diseases = re.findall(disease_pattern, question)
    
    if diseases:
        # 필터링: 제외 리스트에 없고 8글자 이하인 것만 선택
        valid_diseases = [d for d in diseases if len(d) <= 8 and d.replace(' ', '') not in invalid_pests]
        if valid_diseases:
            return max(valid_diseases, key=len) # 가장 구체적인(긴) 이름 반환
    
    return None

def _contains_pesticide_name(question):
    """질문에 약제명이 포함되어 있는지 체크"""
    q_lower = question.lower()
    
    pesticide_patterns = [
        '수화제', '유제', '액제', '입제', '분제', '수용제',
        '돌격대', '팡파레', '인시피오', '다이마이트', '파단'
    ]
    
    return any(pattern in q_lower for pattern in pesticide_patterns)



def _extract_all_pests(question):
    """질문에서 모든 병해충명 추출 (복수)"""
    
    pests = []
    
    for main_pest, synonyms in PEST_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in question and main_pest not in pests:
                pests.append(main_pest)
    
    import re
    disease_pattern = r'([가-힣]{2,}병)'
    diseases = re.findall(disease_pattern, question)
    
    for disease in diseases:
        if len(disease) <= 8 and disease not in pests:
            if not any(disease in PEST_SYNONYMS.get(p, []) for p in pests):
                pests.append(disease)
    
    return pests


def _extract_growth_stage(question):
    """질문에서 생육단계 추출"""
    
    q_lower = question.lower().replace(' ', '')
    
    stages = {
        '육묘': ['육묘', '모종', '육묘기', '육묘중'],
        '정식': ['정식', '정식후', '정식전', '이식', '심은후'],
        '개화': ['개화', '개화기', '꽃필때', '꽃피는', '개화중'],
        '착과': ['착과', '착과기', '열매맺', '결실'],
        '수확': ['수확', '수확기', '수확전', '수확후'],
    }
    
    for stage, keywords in stages.items():
        if any(kw in q_lower for kw in keywords):
            return stage
    
    import re
    if re.search(r'[1-5]화방', q_lower):
        return '화방기'
    
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Excel 검색 및 필터링
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def search_and_filter_pesticides(pest_name, recent_3_sprays, df):
    """Excel에서 약제 검색 → 필터링 → 정렬"""
    
    if df.empty or not pest_name:
        return []
    
    search_keywords = PEST_SYNONYMS.get(pest_name, [pest_name])
    
    if pest_name not in PEST_SYNONYMS:
        if '병' in pest_name and len(pest_name) >= 3:
            without_disease = pest_name.replace('병', '')
            if without_disease not in search_keywords:
                search_keywords = [pest_name, without_disease]
    
    logger.info(f"🔍 검색 키워드: {search_keywords}")
    
    results = []
    
    for _, row in df.iterrows():
        pest_disease = str(row.get('적용병해충', '')).lower()
        
        if any(keyword.lower() in pest_disease for keyword in search_keywords):
            results.append({
                'product_name': str(row.get('상표명', '')),
                'ingredient': str(row.get('품목명', '')),
                'content': str(row.get('주성분함량', '')),
                'formulation': str(row.get('제형', '')),
                'company': str(row.get('회사명', '')),
                'pest_disease': str(row.get('적용병해충', '')),
                'dilution': str(row.get('희석배수', '')),
                'usage': str(row.get('사용적기', '')),
                'safety': str(row.get('안전사용시기', '')),

                #  'product_name': str(row.get('제품명', '')),
                # 'ingredient': str(row.get('성분명', '')),
                # 'content': str(row.get('주성분함량', '')),
                # 'formulation': str(row.get('제형', '')),
                # 'company': str(row.get('회사명', '')),
                # 'pest_disease': str(row.get('적용병해충', '')),
                # 'dilution': str(row.get('희석배수', '')),
                # 'usage': str(row.get('사용적기 및 방법', '')),
                # 'safety': str(row.get('안전사용기준', '')),
                # 'registration_date': str(row.get('등록일', ''))
            })
    
    logger.info(f"📊 초기 검색: {len(results)}개")
    
    if not results:
        return []
    
    if recent_3_sprays:
        excluded_ingredients = set()
        for spray in recent_3_sprays:
            pesticide_name = spray.get('pesticide_name', '')
            if pesticide_name:
                ingredient = _find_ingredient_in_excel(pesticide_name, df)
                if ingredient:
                    parts = re.split(r'[.,+]', ingredient)
                    for part in parts:
                        cleaned = re.sub(r'[^가-힣a-zA-Z]', '', part).strip().lower()
                        if cleaned and len(cleaned) > 2:
                            excluded_ingredients.add(cleaned)
        
        if excluded_ingredients:
            logger.info(f"⛔ 제외 성분: {excluded_ingredients}")
            before = len(results)
            results = [r for r in results if not _has_excluded_ingredient(r['ingredient'], excluded_ingredients)]
            logger.info(f"⛔ 3회 제외: {before}개 → {len(results)}개")
    
    if not results:
        return []
    
    results = _prioritize_pesticides(results, pest_name)
    results = _remove_duplicates(results)
    
    logger.info(f"✅ 최종 결과: {len(results)}개")
    
    return results


def _find_ingredient_in_excel(pesticide_name, df):
    """Excel에서 약제명으로 성분 찾기"""
    try:
        matches = df[df['제품명'].str.contains(pesticide_name, na=False, case=False)]
        if not matches.empty:
            return str(matches.iloc[0].get('성분명', ''))
    except:
        pass
    return None


def _has_excluded_ingredient(ingredient, excluded_set):
    """성분이 제외 목록에 있는지 체크"""
    parts = re.split(r'[.,+]', ingredient)
    for part in parts:
        cleaned = re.sub(r'[^가-힣a-zA-Z]', '', part).strip().lower()
        if cleaned in excluded_set:
            return True
    return False


def _prioritize_pesticides(pesticides, pest_name):
    """우선약제 정렬 + 등록일 최신순"""
    normalized_pest = pest_name
    
    if '응애' in pest_name: normalized_pest = '응애'
    elif '진딧물' in pest_name: normalized_pest = '진딧물'
    elif '나방' in pest_name: normalized_pest = '나방류'
    elif '가루이' in pest_name: normalized_pest = '가루이류'
    
    priority_list = PRIORITY_PESTICIDES.get(normalized_pest, [])
    
    if not priority_list:
        return _sort_by_registration_date(pesticides)
    
    priority_results = []
    normal_results = []
    
    for item in pesticides:
        product_name = item['product_name'].lower()
        is_priority = False
        for priority_name in priority_list:
            if priority_name.lower() in product_name:
                priority_results.append(item)
                is_priority = True
                break
        if not is_priority:
            normal_results.append(item)
    
    normal_results = _sort_by_registration_date(normal_results)
    logger.info(f"⭐ 우선약제: {len(priority_results)}개, 일반: {len(normal_results)}개 (등록일순)")
    
    return priority_results + normal_results


def _sort_by_registration_date(pesticides):
    """등록일 최신순 정렬"""
    def get_date_key(item):
        date_str = item.get('registration_date', '')
        if not date_str or date_str == 'nan' or date_str == 'None':
            return '0000-00-00'
        return date_str
    
    try:
        return sorted(pesticides, key=get_date_key, reverse=True)
    except Exception as e:
        logger.warning(f"⚠️ 등록일 정렬 실패: {e}")
        return pesticides


def _normalize_ingredient(ing):
    """성분명을 개별 성분으로 분리 후 정규화"""
    if not ing or ing == 'nan':
        return set()
    parts = re.split(r'[.,+]', ing)
    normalized_set = set()
    for part in parts:
        cleaned = re.sub(r'[^가-힣a-zA-Z]', '', part)
        if cleaned:
            normalized_set.add(cleaned.strip().lower())
    return normalized_set


def _remove_duplicates(pesticides):
    """성분명 중복 제거 (하나도 안 겹칠 때만 허용)"""
    seen_ingredients = set()
    unique = []
    
    for item in pesticides:
        ing = item['ingredient']
        normalized_set = _normalize_ingredient(ing)
        overlap_count = len(normalized_set.intersection(seen_ingredients))
        
        if overlap_count == 0:
            seen_ingredients.update(normalized_set)
            unique.append(item)
    
    logger.info(f"🔄 성분 중복 제거: {len(pesticides)}개 → {len(unique)}개")
    return unique


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 연속 방제 판단
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def judge_continuous_spray(hours, pest_type, temperature=25, severity='중등'):
    """연속 방제 가능 여부 판단"""
    
    logger.info(f"🔍 판단: {hours}시간, {pest_type}, {temperature}°C, {severity}")
    
    if hours < 12:
        return {
            'allow': False,
            'reason': '약해 위험 극대 - 최소 12시간 필요',
            'wait': 12 - hours,
            'condition': '',
            'level': 'DANGER'
        }
    
    is_disease = any(keyword in pest_type for keyword in DISEASES)
    is_fast_pest = any(keyword in pest_type for keyword in FAST_BREEDING_PESTS)
    is_slow_pest = any(keyword in pest_type for keyword in SLOW_BREEDING_PESTS)
    
    if is_disease:
        if hours < 72:
            return {
                'allow': False,
                'reason': '병은 약효 발현이 느림 - 72시간(3일) 대기 권장',
                'wait': 72 - hours,
                'condition': '환경 관리 우선 (통풍, 습도 낮추기)',
                'level': 'WAIT'
            }
        else:
            return {
                'allow': True,
                'reason': '72시간 경과 - 효과 없으면 다른 성분 사용',
                'wait': 0,
                'condition': '다른 성분으로 변경 필수',
                'level': 'OK'
            }
    
    if is_fast_pest:
        if hours >= 72:
            return {
                'allow': True,
                'reason': '72시간 경과 - 저항성 가능성 높음',
                'wait': 0,
                'condition': '즉시 다른 성분으로 변경 필수',
                'level': 'URGENT'
            }
        elif hours >= 48:
            return {
                'allow': True,
                'reason': '48시간 경과했지만 72시간까지 대기 강력 권고',
                'wait': 72 - hours,
                'condition': f'⚠️ 가능하면 72시간({72-hours:.1f}시간 남음)까지 대기하세요. 긴급하면 다른 성분 사용',
                'level': 'CONDITIONAL_STRONG'
            }
        elif hours >= 24:
            if temperature > 30:
                return {
                    'allow': False,
                    'reason': f'온도 {temperature}°C - 약해 위험 높음',
                    'wait': 48 - hours,
                    'condition': '온도 30°C 이하일 때 재방제',
                    'level': 'WAIT'
                }
            if severity == '심각':
                return {
                    'allow': True,
                    'reason': '24시간 경과 + 심각한 발생 + 적정 온도',
                    'wait': 0,
                    'condition': '다른 성분 + 희석배수 정확히 + 저녁 시간대 방제',
                    'level': 'CONDITIONAL'
                }
            else:
                return {
                    'allow': False,
                    'reason': '24시간 경과했지만 48시간까지 대기 권장',
                    'wait': 48 - hours,
                    'condition': '긴급하지 않으면 더 기다리기',
                    'level': 'WAIT'
                }
        else:
            return {
                'allow': False,
                'reason': '24시간 미만 - 약효 발현 대기',
                'wait': 24 - hours,
                'condition': '희석배수, 살포 방법 재확인',
                'level': 'WAIT'
            }
    
    if is_slow_pest:
        if hours < 72:
            return {
                'allow': False,
                'reason': '저속 번식 해충 - 72시간(3일) 대기 권장',
                'wait': 72 - hours,
                'condition': '천천히 효과 나타남',
                'level': 'WAIT'
            }
        else:
            return {
                'allow': True,
                'reason': '72시간 경과 - 재방제 가능',
                'wait': 0,
                'condition': '다른 성분 사용',
                'level': 'OK'
            }
    
    if hours < 48:
        return {
            'allow': False,
            'reason': '일반 기준 48시간 대기',
            'wait': 48 - hours,
            'condition': '',
            'level': 'WAIT'
        }
    else:
        return {
            'allow': True,
            'reason': '48시간 경과',
            'wait': 0,
            'condition': '효과 없으면 다른 성분 사용',
            'level': 'OK'
        }


def format_spray_judgment(judgment):
    """판단 결과를 사용자 친화적인 문자열로 변환"""
    
    if judgment['level'] == 'DANGER':
        return f"""🚨🚨🚨 재방제 절대 금지 🚨🚨🚨

【이유】
{judgment['reason']}

【대기 시간】
최소 {judgment['wait']:.1f}시간 더 기다려야 합니다.

❌ 약해 위험이 매우 높습니다!"""

    elif judgment['level'] == 'WAIT':
        return f"""⏰ 재방제 권장하지 않음

【이유】
{judgment['reason']}

【권장 조치】
1. {judgment['wait']:.1f}시간 더 대기
2. {judgment['condition']}
3. 효과 재확인 후 판단"""

    elif judgment['level'] == 'CONDITIONAL':
        return f"""⚠️ 조건부 재방제 가능

【조건】
{judgment['condition']}

모든 조건 충족 시에만 재방제하세요.
불확실하면 농업기술센터(1544-8572) 상담"""

    elif judgment['level'] == 'CONDITIONAL_STRONG':
        return f"""⚠️⚠️⚠️ 72시간 대기 강력 권고 ⚠️⚠️⚠️

【이유】
{judgment['reason']}

【권장 조치】
✅ 가능하면 {judgment['wait']:.1f}시간 더 대기 (72시간까지)
✅ 대기 중 환경 관리 (통풍, 습도)
✅ 효과 재확인

【긴급 상황 시】
{judgment['condition']}
아래 약제를 사용할 수 있습니다.
(반드시 다른 성분으로 변경)"""

    elif judgment['level'] == 'URGENT':
        return f"""🚨 저항성 의심 - 즉시 성분 변경!

【이유】
{judgment['reason']}

【필수 조치】
✅ 즉시 다른 성분으로 재방제
✅ 같은 성분은 2~3주 후 사용
✅ 2~3가지 성분 순환 사용"""

    else:
        return f"""✅ 재방제 가능

【이유】
{judgment['reason']}

【조건】
{judgment['condition']}"""


def get_severity_from_question(question):
    """질문에서 심각도 추정"""
    q_lower = question.lower()
    severe_keywords = ['심각', '너무', '엄청', '많이', '가득', '온통', '전체', '다', '죽겠', '망했', '큰일', '심해', '대량', '폭발']
    mild_keywords = ['조금', '약간', '살짝', '몇개', '일부', '조금씩', '적게']
    
    if any(kw in q_lower for kw in severe_keywords): return '심각'
    elif any(kw in q_lower for kw in mild_keywords): return '경미'
    else: return '중등'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 컨텍스트 수집
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_all_context(phone, question, question_type):
    """질문에 필요한 모든 데이터 수집 및 작물명 정규화"""
    
    from core import get_farm_info, get_spray_history, get_session, load_excel_data
    
    logger.info(f"📦 컨텍스트 수집 시작: 유형 {question_type}")
    
    context = {
        'phone': phone,
        'question': question,
        'question_type': question_type,
        'farm_info': None,
        'crop_name': None,
        'pest_name': None,
        'spray_history': [],
        'pesticides': [],
        'exclude_info': None,
        'warnings': [],
        'severity': '중등',
        'temperature': 25
    }
    
    # 1. 농가 정보 가져오기 (기본 베이스)
    if phone:
        context['farm_info'] = get_farm_info(phone, DB_PATH)
        if context['farm_info']:
            logger.info(f"✅ 농가정보 확인됨: {context['farm_info'].get('name', '알수없음')}")

    # 2. [중요] 작물명 결정 로직 (우선순위: 질문 내 언급 > 회원 정보)
    # 2-1. 질문에서 먼저 작물을 찾습니다.
    crop = _extract_crop_from_question(question)
    
    if crop:
        logger.info(f"🔎 질문에서 작물 감지됨: {crop}")
    else:
        # 2-2. 질문에 없으면 DB에서 사용자가 가입 시 선택한 작물을 가져옵니다.
        if context['farm_info']:
            crop = context['farm_info'].get('crop')
            logger.info(f"📌 회원 정보에서 작물 가져옴: {crop}")

    # 3. [핵심] 작물명 정규화 (품종명/동의어를 엑셀 시트명으로 치환)
    # 예: '샤인머스캣' 입력 시 CROP_SYNONYMS를 뒤져서 '포도'로 변경
    if crop:
        normalized_name = crop
        for main_sheet_name, synonyms in CROP_SYNONYMS.items():
            if crop == main_sheet_name or crop in synonyms:
                normalized_name = main_sheet_name
                logger.info(f"🔄 작물명 정규화 완료: {crop} -> {normalized_name}")
                break
        crop = normalized_name

    context['crop_name'] = crop
    logger.info(f"✅ 최종 결정된 작물명(시트명): {context['crop_name']}")

    # 4. 병해충명 추출
    context['pest_name'] = _extract_pest_from_question(question)
    if context['pest_name']:
        logger.info(f"🐛 병해충명: {context['pest_name']}")
    
    # 범위 넓은 질문(살균제, 살충제 등) 처리
    if not context['pest_name']:
        q_lower = question.lower().replace(' ', '')
        if any(kw in q_lower for kw in ['살균제', '곰팡이약', '곰팡이', '균제']):
            context['pest_name'] = '잿빛곰팡이병' if context['crop_name'] == '감귤' else '흰가루병'
            context['broad_category'] = 'fungicide'
        elif any(kw in q_lower for kw in ['살충제', '해충약', '벌레약']):
            context['pest_name'] = '귤응애' if context['crop_name'] == '감귤' else '진딧물'
            context['broad_category'] = 'insecticide'

    # 5. 심각도 및 환경 정보
    context['severity'] = get_severity_from_question(question)
    
    # 6. 방제 이력 수집
    if phone:
        days = 30 if question_type in [14, 15, 16, 17, 18, 19] else (90 if question_type in [25, 26] else (3 if question_type == 1 else 7))
        context['spray_history'] = get_spray_history(phone, days, DB_PATH)
        if context['spray_history']:
            try:
                context['temperature'] = float(context['spray_history'][0].get('temperature', 25))
            except:
                pass

    # 7. Excel 약제 데이터 로드 및 필터링
    if question_type in [14, 15, 16, 17, 18, 19, 35]:
        # 유형 15-17: 병해충명 없으면 방제 이력에서 가져오기
        if question_type in [15, 16, 17] and not context.get('pest_name') and context['spray_history']:
            context['pest_name'] = context['spray_history'][0].get('pest_name', '')

        if context['crop_name'] and context['pest_name']:
            # 정규화된 crop_name('포도', '딸기' 등)으로 엑셀 시트를 로드합니다.
            df = load_excel_data(context['crop_name'], EXCEL_PATH)
            
            if not df.empty:
                context['pesticides'] = search_and_filter_pesticides(
                    context['pest_name'],
                    context['spray_history'][:3],
                    df
                )
                
                if question_type in [15, 16, 17] and context['spray_history']:
                    last_spray = context['spray_history'][0]
                    context['exclude_info'] = {
                        'product': last_spray.get('pesticide_name', '알수없음'),
                        'hours_ago': last_spray.get('hours_ago', 0),
                        'ingredient': _find_ingredient_in_excel(last_spray.get('pesticide_name', ''), df)
                    }

    # 8. 최종 경고 알림 생성
    context['warnings'] = _generate_warnings(context)
    
    return context


def _generate_warnings(context):
    """컨텍스트 기반 경고 생성"""
    warnings = []
    if context['spray_history']:
        hours = context['spray_history'][0].get('hours_ago', 999)
        if hours < 12: warnings.append('DANGER_12H')
        elif hours < 24: warnings.append('WARNING_24H')
        elif hours < 72: warnings.append('INFO_72H')
    
    if context['question_type'] in [14, 15, 16, 17, 18, 19] and not context['pesticides']:
        warnings.append('NO_PESTICIDES')
    
    if context['temperature'] > 30: warnings.append('HIGH_TEMP')
    elif context['temperature'] < 15: warnings.append('LOW_TEMP')
    
    return warnings


def _create_empathy_message(question_type, context):
    """상황별 공감 메시지 - 1~46번 전체 유형 대화체 업데이트"""
    
    farm_info = context.get('farm_info')
    farm_name = farm_info['name'] if farm_info and farm_info.get('name') else "농가"
    pest_name = context.get('pest_name', '병해충')
    crop_name = context.get('crop_name', '작물')
    
    messages = {
        1: f"😰 {farm_name}님, 방제 후에 작물이 이상해졌다니 정말 가슴이 덜컥하셨겠어요. 약해는 초기 대응이 생명이니 제가 얼른 같이 살펴볼게요.",
        2: f"🤔 {farm_name}님, 약제를 섞어 쓰면 효과가 더 좋을까 궁금하시죠? 하지만 자칫하면 독이 될 수 있어 안전한 혼용인지 확인이 꼭 필요해요.",
        3: f"🔍 {farm_name}님, 희석배수가 헷갈리시군요. 너무 진하면 약해가 나고, 연하면 효과가 없으니 딱 맞는 비율을 제가 꼼꼼히 챙겨드릴게요.",
        4: f"⏰ {farm_name}님, 언제 약을 쳐야 가장 효과가 좋을지 고민되시죠? 작물의 컨디션과 병해충의 특성을 고려한 최적의 타이밍을 알려드릴게요.",
        5: f"☁️ {farm_name}님, 변덕스러운 날씨 때문에 방제 일정 잡기가 참 힘드시죠? 비나 바람 조건을 고려해서 안전하게 뿌릴 수 있는 기준을 정리해 드릴게요.",
        6: f"📋 {farm_name}님, 수확이 가까워지니 안전사용기준이 더 신경 쓰이시죠? 안심하고 출하하실 수 있도록 제가 정확하게 확인해 드릴게요.",
        7: f"🔍 {farm_name}님, 작물에 나타난 증상 때문에 걱정이 많으시죠? 어떤 원인인지 제가 차근차근 분석해서 해결 방법을 찾아보겠습니다.",
        8: f"🍃 {farm_name}님, 잎 색깔이 변해서 많이 놀라셨죠? 단순한 영양 부족인지 병해충 때문인지 제가 세심하게 들여다볼게요.",
        9: f"💧 {farm_name}님, 애써 키운 작물이 시들시들해지니 정말 속상하시겠어요. 원인을 빨리 찾아서 다시 생기를 찾을 수 있게 도와드릴게요.",
        10: f"🔴 {farm_name}님, 잎에 생긴 반점이 번질까 봐 걱정되시죠? 어떤 병의 신호인지 확인해서 더 번지지 않게 막아보겠습니다.",
        11: f"🐛 {farm_name}님, 벌레가 보이면 마음이 급해지기 마련이죠. 어떤 해충인지 정확히 알아야 한 번에 제대로 잡을 수 있습니다.",
        12: f"🍯 {farm_name}님, 잎이 끈적거려서 당황하셨죠? 이건 해충이 보내는 신호일 수 있어요. 제가 어떤 녀석의 소행인지 밝혀드릴게요.",
        13: f"🦠 {farm_name}님, 곰팡이가 보이면 금방 퍼질까 봐 무섭죠. 초기에 꽉 잡아야 하니 제가 빠른 대응 방법을 알려드릴게요.",
        14: f"💊 {farm_name}님, {pest_name} 때문에 고민이시군요. {crop_name}에 효과가 좋으면서도 안전한 약제들로 제가 엄선해 왔습니다.",
        15: f"⏰ {farm_name}님, 방제 후에 효과가 바로 안 보여서 답답하시죠? 하지만 약효가 나타나려면 시간이 조금 필요해요. 우리 조금만 더 지켜볼까요?",
        16: f"⚠️ {farm_name}님, 방제를 했는데도 여전히 병해충이 보여서 마음이 급하시겠지만, 지금 바로 또 뿌리면 작물이 너무 힘들어해요. 조금만 참아주세요!",
        17: f"🚨 {farm_name}님, 3일이 지났는데도 그대로라면 저항성이 생긴 게 분명해요. 이제는 다른 전략으로 바꿔서 확실하게 잡아보겠습니다.",
        18: f"🛡️ {farm_name}님, 미리미리 예방하려고 하시는군요! 역시 농사의 고수이십니다. 예방 차원에서 쓰기 좋은 약제들을 추천해 드릴게요.",
        19: f"🔄 {farm_name}님, 다 잡은 줄 알았던 병해충이 다시 나와서 허탈하시죠? 지독한 녀석들이지만 이번엔 뿌리 뽑을 수 있게 도와드릴게요.",
        20: f"🌱 {farm_name}님, 작물이 힘이 없는 게 영양 결핍 때문일 수도 있어요. 어떤 성분이 부족한지 확인해서 튼튼하게 키워보자고요.",
        21: f"🌡️ {farm_name}님, 환경이 안 맞아서 작물이 스트레스를 받고 있나 봐요. 생리장해는 약보다는 환경 관리가 정답이니 제가 조절법을 알려드릴게요.",
        22: f"🐞 {farm_name}님, 이 벌레가 우리 편인지 적군인지 궁금하시죠? 익충을 잘못 죽이면 손해니까 제가 똑똑하게 구분해 드릴게요.",
        23: f"🌿 {farm_name}님, 잡초 때문에 허리 필 날 없으시죠? 조금이라도 덜 힘들게 관리하실 수 있는 방법을 함께 찾아보겠습니다.",
        24: f"📈 {farm_name}님, 작물이 얼마나 잘 자라고 있는지 궁금하시군요. 건강한 성장을 위한 체크리스트를 정리해 드릴게요.",
        25: f"📝 {farm_name}님, 그동안 고생하며 관리하신 기록을 한눈에 보실 수 있게 제가 싹 정리해 왔습니다.",
        26: f"📅 {farm_name}님, 다음 방제는 언제쯤 하면 좋을지 제가 날짜를 딱 짚어드릴게요. 안전한 간격을 지키는 게 중요하거든요.",
        27: f"ℹ️ {farm_name}님, 궁금하신 약제에 대해 제가 아주 자세하고 알기 쉽게 설명해 드릴게요.",
        28: f"📦 {farm_name}님, 창고에 있는 약을 알뜰하게 쓰시려는군요! 아직 쓸 수 있는 상태인지, 효과가 있을지 제가 확인해 드릴게요.",
        29: f"🤔 {farm_name}님, 어떤 작물을 키우시는지 제가 알면 더 정확한 약을 골라드릴 수 있어요! 작물 이름을 알려주세요.",
        30: f"🔍 {farm_name}님, 어떤 녀석 때문에 고민인지 조금만 더 자세히 말씀해 주시면, 제가 딱 맞는 해결책을 가져올게요.",
        31: f"💬 {farm_name}님, 질문이 조금 짧아서 제가 잘 이해하지 못했어요. 궁금하신 내용을 조금만 더 풀어서 말씀해 주시겠어요?",
        32: f"👋 {farm_name}님, 안녕하세요! 오늘도 현장에서 땀 흘리시는 모습이 존경스럽습니다. 무엇을 도와드릴까요?",
        33: f"💡 {farm_name}님, 아까 말씀하신 그 내용 이어서 더 자세히 설명해 드릴게요. 궁금한 점이 다 풀리실 거예요.",
        34: f"➕ {farm_name}님, 추가로 궁금하신 게 더 있으시군요! 놓치는 부분 없도록 제가 끝까지 도와드리겠습니다.",
        35: f"🔄 {farm_name}님, 다른 약제가 필요하시군요. 같은 효과를 내면서도 성분이 다른 대안들을 제가 찾아봤습니다.",
        36: f"🛡️ {farm_name}님, {crop_name}을(를) 완벽하게 지키고 싶으시군요! 이 작물이 특히 조심해야 할 병해충들을 제가 정리해 드릴게요.",
        37: f"🔍 {farm_name}님, 이 약으로 저 녀석까지 잡을 수 있을지 궁금하시죠? 제가 교차해서 꼼꼼히 확인해 드리겠습니다.",
        38: f"🛡️ {farm_name}님, 병이 생기기 전에 미리 방어하고 싶으시군요! 예방이 최고의 방제죠. 효과적인 예방 전략을 알려드릴게요.",
        39: f"📅 {farm_name}님, 작물이 쑥쑥 자라는 단계마다 방제법도 달라져야 해요. 지금 시기에 가장 적절한 관리법을 제안해 드릴게요.",
        40: f"🔄 {farm_name}님, 계속 같은 약만 쓰면 내성이 생겨요. 똑똑하게 약을 바꿔가며 치는 '순환 방제'법을 알려드릴게요.",
        41: f"🎯 {farm_name}님, 여러 병해충을 한 번에 소탕하고 싶으시군요! 일석이조의 효과를 볼 수 있는 약제를 제가 찾아보겠습니다.",
        42: f"⚖️ {farm_name}님, 이 약이랑 저 약 중에 뭐가 더 좋을지 고민되시죠? 객관적인 정보를 바탕으로 제가 비교 분석해 드릴게요.",
        43: f"⏱️ {farm_name}님, 한 번 치면 효과가 얼마나 갈지 궁금하시죠? 약효 지속 기간과 재방제 시기를 짚어드릴게요.",
        44: f"❌ {farm_name}님, 아쉽게도 이 조합으로는 등록된 약이 없네요. 하지만 실망하지 마세요! 다른 안전한 대안을 제가 찾아봐 드릴게요.",
        45: f"🔍 {farm_name}님, 여러 상황이 겹쳐서 많이 혼란스러우시죠? 복잡할수록 하나씩 차근차근 풀어나갈 수 있게 제가 분석해 드릴게요.",
        46: f"🌱 {farm_name}님, {crop_name}의 생육 단계별 관리가 궁금하시군요. 지금이 가장 중요한 시기인 만큼 제가 맞춤형으로 알려드릴게요."
    }
    
    default_message = f"😊 {farm_name}님, 질문 주셔서 감사합니다. {crop_name} 농사에 실질적인 도움이 되는 답변을 드릴게요."
    return messages.get(question_type, default_message)


def _create_personalized_header(context):
    """구분선을 최소화하고 인사말과 공감을 하나로 묶음"""
    farm_info = context.get('farm_info')
    question_type = context.get('question_type', 31)
    
    name = farm_info.get('name') if farm_info and farm_info.get('name') else "농가"
    empathy_msg = _create_empathy_message(question_type, context)
    
    # 💡 선을 한 번만 긋고 인사말과 공감을 붙여서 반환합니다.
    header = f"""━━━━━━━━━━━━━━━━━━━━━
📋 {name} 농가님 맞춤 조언
{empathy_msg}
━━━━━━━━━━━━━━━━━━━━━"""
    return header

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 템플릿 조립
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def build_answer(question_type, context):
    """유형에 맞는 템플릿 + 데이터 삽입 및 최종 텍스트 정제"""
    
    logger.info(f"🔧 답변 조립 시작: 유형 {question_type}")
    
    # 유형 15(최근방제)의 경우 시간에 따라 16, 17로 자동 전환
    if question_type == 15 and context.get('exclude_info'):
        hours = context['exclude_info'].get('hours_ago', 0)
        if hours < 24: question_type = 15
        elif hours < 72: question_type = 16
        else: question_type = 17
    
    template = TEMPLATES.get(question_type, TEMPLATES[31])
    farm_info = context.get('farm_info', {})
    cultivation_type = farm_info.get('cultivation_type', '노지') if farm_info else '노지'
    
    from config import get_weather_condition
    
    context['question_type'] = question_type
    personalized_header = _create_personalized_header(context)
    
    # 템플릿용 데이터 매핑
    data = {
        'personalized_header': personalized_header,
        'mandatory_top': MANDATORY_NOTICES['safety_top'],
        'mandatory_bottom': MANDATORY_NOTICES['expert_bottom'].format(
            tech_center_name=CONTACTS['tech_center_name'], tech_center=CONTACTS['tech_center']
        ),
        'legal_disclaimer': MANDATORY_NOTICES['legal_disclaimer'],
        'tech_center': f"{CONTACTS['tech_center_name']}({CONTACTS['tech_center']})",
        'ai_limitation': MANDATORY_NOTICES['ai_limitation'],
        'label_check': MANDATORY_NOTICES['label_check'],
        'weather_condition': get_weather_condition(cultivation_type),
        'effect_check': MANDATORY_NOTICES['effect_check'],
        'resistance_management': MANDATORY_NOTICES['resistance_management'],
        'protection_gear': MANDATORY_NOTICES['protection_gear'],
        'question': context['question'],
        'crop_name': context.get('crop_name', '미확인'),
        'pest_name': context.get('pest_name', '미확인'),
        '작물': context.get('crop_name', '감귤'),
        '병해충': context.get('pest_name', '응애'),
        '증상': '노랗게 변색',
        '약제': '해당 약제',
    }
       
    # 유형별 데이터 업데이트
    if question_type == 1:
        data.update(_prepare_damage_data(context))
    
    elif question_type in [2, 3, 4, 5, 6]:
        data.update({
            'pesticide_name': context.get('user_input_pesticide', '해당 약제')
        })
    
    elif question_type in [7, 8, 9, 10, 11, 12, 13]:
        data.update(_prepare_diagnosis_data(context))
    
    elif question_type in [14, 15, 16, 17, 18, 19]:
        data.update(_prepare_pesticide_data(context, question_type))
    
    elif question_type == 20:
        data.update(_prepare_nutrient_data(context))
    
    elif question_type == 21:
        data.update(_prepare_physiological_data(context))
    
    elif question_type == 22:
        data.update(_prepare_insect_data(context))
    
    elif question_type in [23, 24]:
        data.update({'ai_advice': call_ai_simple(context['question'])})
    
    elif question_type == 25:
        data.update(_prepare_history_data(context))
    
    elif question_type == 26:
        data.update(_prepare_next_spray_data(context))
    
    elif question_type == 27:
        data.update(_prepare_pesticide_info_data(context))
    
    elif question_type == 28:
        data.update(_prepare_inventory_data(context))
    
    elif question_type in [33, 34, 35]:
        data.update(_prepare_linked_data(context))
    
    elif question_type == 36:
        data.update(_prepare_vulnerable_pests_data(context))

    elif question_type == 37:
        data.update(_prepare_cross_check_data(context))
    
    elif question_type == 38:
        data.update(_prepare_prevention_data(context))
    
    elif question_type == 39:
        data.update(_prepare_growth_stage_data(context))
    
    elif question_type == 40:
        data.update(_prepare_rotation_data(context))
    
    elif question_type == 41:
        data.update(_prepare_multiple_pests_data(context))
    
    elif question_type == 42:
        data.update(_prepare_comparison_data(context))
    
    elif question_type == 43:
        data.update(_prepare_duration_data(context))
    
    elif question_type == 44:
        data.update(_prepare_no_registration_data(context))
    
    elif question_type == 45:
        data.update(_prepare_complex_situation_data(context))
    
    elif question_type == 46:
        # 유형 46번도 생육단계 로직을 공유합니다.
        data.update(_prepare_growth_stage_data(context))

    # 템플릿 포맷팅 및 최종 정제
    try:
        answer = template.format(**data)
        
        # 💡 [핵심 정제 로직] 
        # 1. AI 모델이 강조를 위해 넣는 ** 기호를 모두 제거
        answer = answer.replace('**', '')
        
        # 2. 불필요하게 넓은 3줄 공백을 2줄로 압축
        while '\n\n\n' in answer:
            answer = answer.replace('\n\n\n', '\n\n')
            
        logger.info("✅ 답변 조립 및 텍스트 정제 완료")
        return answer.strip()

    except KeyError as e:
        logger.error(f"❌ 템플릿 키 누락: {e}")
        return f"""답변 생성 중 오류가 발생했습니다.
누락된 정보: {e}

{MANDATORY_NOTICES['expert_bottom'].format(
    tech_center_name=CONTACTS['tech_center_name'],
    tech_center=CONTACTS['tech_center']
)}"""
    except Exception as e:
        logger.error(f"❌ 답변 조립 오류: {e}")
        import traceback
        traceback.print_exc()
        return f"""답변 생성 중 오류가 발생했습니다.

{MANDATORY_NOTICES['expert_bottom'].format(
    tech_center_name=CONTACTS['tech_center_name'],
    tech_center=CONTACTS['tech_center']
)}"""

# 유형별 데이터 준비 함수들
def _prepare_damage_data(context):
    """약해 관련 데이터 준비"""
    
    if not context['spray_history']:
        return {
            'pesticide_name': '알수없음',
            'hours': '?',
            'temperature': '?',
            'diagnosis': '최근 방제 기록이 없습니다.'
        }
    
    last_spray = context['spray_history'][0]
    temp = last_spray.get('temperature', '?')
    hours = last_spray.get('hours_ago', 0)
    
    diagnosis = []
    try:
        temp_num = float(temp)
        if temp_num > 30:
            diagnosis.append(f"• 온도 {temp}°C (부적정, 30°C 이상 약해 위험)")
        elif temp_num < 15:
            diagnosis.append(f"• 온도 {temp}°C (부적정, 15°C 이하 효과 낮음)")
        else:
            diagnosis.append(f"• 온도 {temp}°C (적정 범위)")
    except:
        diagnosis.append(f"• 온도 {temp}°C")
    
    diagnosis.append("• 희석배수 오류 가능성 - 라벨 재확인 필요")
    diagnosis.append("• 과도한 농도 또는 중복 방제 의심")
    
    if hours < 12:
        diagnosis.append(f"• 방제 후 {hours:.1f}시간 (12시간 미만 - 약해 위험 매우 높음)")
    
    return {
        'pesticide_name': last_spray.get('pesticide_name', '알수없음'),
        'hours': f"{hours:.1f}",
        'temperature': str(temp),
        'diagnosis': '\n'.join(diagnosis)
    }


def _prepare_diagnosis_data(context):
    """증상 진단 데이터 준비 - 확장된 지식 검색 감지 로직"""
    
    crop_name = context.get('crop_name')
    question = context.get('question', '')
    ai_text = call_ai_diagnosis(question, crop_name)
    
    # 🔍 더 넓은 범위를 커버하는 확장 키워드 리스트
    knowledge_keywords = [
        '설명', '알려', '뭐야', '뭔지', '무엇', '증상', '특징', 
        '알고', '궁금', '정보', '어때', '어떤', '어떻게', '가르쳐', 
        '말해', '원인', '이유'
    ]
    
    # 💡 띄어쓰기를 없앤 질문에서 키워드가 하나라도 포함되어 있는지 확인
    clean_question = question.replace(' ', '')
    is_knowledge_query = any(kw in clean_question for kw in knowledge_keywords)
    
    recent_spray_warning = ""
    
    # 지식 검색이 아닐 때만 '최근 방제 경고'를 생성
    if not is_knowledge_query and context.get('spray_history'):
        last_spray = context['spray_history'][0]
        hours = last_spray.get('hours_ago', 999)
        
        if hours < 72:
            days = hours / 24
            pesticide = last_spray.get('pesticide_name', '알수없음')
            recent_spray_warning = f"""
⚠️⚠️⚠️ 최근 방제 이력 감지 ⚠️⚠️⚠️
• 방제 후: {hours:.1f}시간 ({days:.1f}일)
• 약제: {pesticide}
❌ 추가 방제 절대 금지
━━━━━━━━━━━━━━━━━━━━━
"""
    
    data = {
        'ai_diagnosis': ai_text,
        'suspected_pest': '전문가 확인 필요',
        'suspected_disease': '전문가 확인 필요',
        'nutrient_solution': '영양제 엽면시비 권장',
        'pesticides_list': '정확한 진단 후 약제 추천 가능',
        'recent_spray_warning': recent_spray_warning
    }
    
    # 병해충/병명 정보 설정 (기존 로직 유지)
    if context.get('pesticides'):
        data['pesticides_list'] = _format_pesticides_list(context['pesticides'][:5], context.get('pest_name'))
        if context.get('pest_name'):
            pest = context['pest_name']
            data['suspected_pest'] = pest
            if '병' in pest or '무늬' in pest or '썩음' in pest or '마름' in pest:
                data['suspected_disease'] = pest
            else:
                data['suspected_disease'] = f"{pest} 증상"
    
    return data

def _prepare_pesticide_data(context, question_type):
    """약제 추천 데이터 준비"""
    
    data = {
        'pesticide_count': len(context.get('pesticides', [])),
        'pesticides_list': '',
        'spray_warning': '',
        'exclude_notice': '',
        'ai_explanation': '',
        'spray_judgment': '',
        'conditional_pesticides': '',
        'hours': '0',
        'days': '0',
        'previous_pesticide': '알수없음',
        'previous_ingredient': '알수없음',
        'temperature': '?'
    }
    
    data['spray_warning'] = _format_spray_warning(context)
    
    # AI 설명 또는 추천 불가 이유
    if context.get('pesticides'):
        # 약제가 있으면 AI 설명
        if context.get('broad_category'):
            # 🔥 범위 넓은 질문인 경우 특별 설명
            crop_name = context.get('crop_name', '해당 작물')
            if context['broad_category'] == 'fungicide':
                data['ai_explanation'] = f"""
⚠️ [중요: AI 추천은 참고용입니다]
{crop_name}에는 주로 잿빛곰팡이병, 검은점무늬병, 흰가루병 등이 문제됩니다.
아래 목록은 {crop_name}의 주요 곰팡이병에 등록된 **'성분'**이며, 
실제 효과와 안전성은 농약사 전문가와 반드시 상의해야 합니다.

【AI 방제 가이드】
• 저항성 관리: 2~3가지 성분 순환 사용
• 습도 관리: 곰팡이는 습도 70% 이상에서 증식 → 통풍 개선 우선
• 예방 우선: 발병 초기에 사용해야 효과 높음
"""
            elif context['broad_category'] == 'insecticide':
                data['ai_explanation'] = f"""
⚠️ [중요: AI 추천은 참고용입니다]
{crop_name}에는 주로 응애류, 진딧물류, 깍지벌레류 등이 문제됩니다.
아래 목록은 {crop_name}의 주요 해충에 등록된 **'성분'**이며,
실제 효과와 안전성은 농약사 전문가와 반드시 상의해야 합니다.

【AI 방제 가이드】
• 저항성 관리: 같은 성분 연속 사용 금지
• 잎 뒷면까지: 응애, 진딧물은 잎 뒷면에 주로 서식
• 조기 방제: 개체수가 적을 때 방제해야 효과 높음
"""
        elif context.get('pest_name'):
            # 일반 질문인 경우
            data['ai_explanation'] = call_ai_simple(context['pest_name'])
    else:
        # 약제가 없으면 이유 설명
        if not context.get('crop_name'):
            data['ai_explanation'] = """
⚠️ 약제 추천 불가 이유

【작물명 미등록】
현재 농가정보에 작물명이 등록되어 있지 않습니다.

【해결 방법】
1. 앱 메뉴 → 농가정보 
2. 작물명 입력 및 저장
3. 다시 질문하기

※ 작물명이 등록되어야 해당 작물에 등록된 약제를 정확하게 추천해드릴 수 있습니다.
"""
        elif context.get('spray_history') and len(context['spray_history']) >= 3:
            recent_products = [h.get('pesticide_name', '알수없음') for h in context['spray_history'][:3]]
            data['ai_explanation'] = f"""
⚠️ 약제 추천 불가 이유

【최근 3회 사용 성분 모두 제외】
약제 저항성 방지를 위해 최근 사용한 성분들을 자동으로 제외했습니다.

최근 사용 약제:
• {recent_products[0] if len(recent_products) > 0 else '알수없음'}
• {recent_products[1] if len(recent_products) > 1 else '알수없음'}
• {recent_products[2] if len(recent_products) > 2 else '알수없음'}

【해결 방법】
1. 다른 병해충을 검색하거나
2. 앱 메뉴 → 방제이력 → 이력 삭제
3. 또는 72시간 대기 후 재시도

※ 같은 성분을 반복 사용하면 저항성이 생겨 효과가 없어집니다.
"""
        else:
            data['ai_explanation'] = f"""
⚠️ 약제 추천 불가 이유

【등록 약제 없음】
[{context.get('crop_name', '알수없음')}] 작물의 [{context.get('pest_name', '알수없음')}]에 대한 등록 약제가 데이터베이스에 없습니다.

【가능한 원인】
• 해당 조합으로 등록된 농약이 없음
• 병해충명이 정확하지 않음
• 작물명이 정확하지 않음

【해결 방법】
1. 병해충명을 다르게 표현해서 재검색
   (예: "흰가루병" → "흰가루")
2. 농업기술센터(1544-8572) 문의
3. 앱 메뉴 → 건의사항에 등록 요청

※ 정확한 진단과 약제 추천은 전문가 상담을 권장합니다.
"""
    
    if context.get('pesticides'):
        # 🔥 범위 넓은 질문은 성분 중심 포맷
        if context.get('broad_category'):
            data['pesticides_list'] = _format_pesticides_by_ingredient(context['pesticides'], context.get('crop_name'))
        else:
            # 일반 질문은 기존 포맷
            data['pesticides_list'] = _format_pesticides_list(context['pesticides'], context.get('pest_name'))
        data['exclude_notice'] = f"※ 최근 3회 사용 성분은 자동으로 제외되었습니다."
    else:
        # 약제 없음 - 원인별로 다른 메시지 표시
        if not context.get('crop_name'):
            data['pesticides_list'] = "❌ 작물명 정보가 필요합니다\n\n농가정보에서 작물명을 등록해주세요."
            data['exclude_notice'] = "※ 작물명이 등록되어야 정확한 약제를 추천할 수 있습니다."
        elif context.get('spray_history') and len(context['spray_history']) >= 3:
            data['pesticides_list'] = "❌ 추천 가능한 약제 없음\n(최근 3회 사용 성분 모두 제외됨)"
            data['exclude_notice'] = "※ 모든 약제가 최근 3회 제외 대상입니다. 다른 병해충을 검색하거나 방제이력을 삭제해보세요."
        else:
            data['pesticides_list'] = "❌ 해당 작물/병해충에 대한\n등록 약제가 없습니다"
            data['exclude_notice'] = f"※ [{context.get('crop_name', '?')}] 작물의 [{context.get('pest_name', '?')}]에 등록된 약제가 없습니다."

    
    if question_type in [15, 16, 17] and context.get('exclude_info'):
        hours = context['exclude_info'].get('hours_ago', 0)
        days = hours / 24
        
        judgment = judge_continuous_spray(
            hours,
            context.get('pest_name', ''),
            context.get('temperature', 25),
            context.get('severity', '중등')
        )
        
        data.update({
            'hours': f"{hours:.1f}",
            'days': f"{days:.1f}",
            'previous_pesticide': context['exclude_info'].get('product', '알수없음'),
            'previous_ingredient': context['exclude_info'].get('ingredient', '알수없음'),
            'spray_judgment': format_spray_judgment(judgment)
        })
        
        # 유형 16번(CONDITIONAL_STRONG)은 무조건 약제 제공
        if judgment['allow'] and context.get('pesticides'):
            if judgment['level'] == 'CONDITIONAL_STRONG':
                # 48~72시간: 강력 권고하지만 약제는 제공
                data['conditional_pesticides'] = f"""
【긴급 시 사용 가능 약제】
(72시간 대기가 어려운 긴급 상황에만)

{data['pesticides_list']}

⚠️ 조건: 다른 성분으로 변경 필수"""
            else:
                data['conditional_pesticides'] = f"""
【조건부 추천 약제】
(아래 조건 충족 시에만 사용)

{data['pesticides_list']}

⚠️ 조건: {judgment.get('condition', '다른 성분 사용')}
"""
        else:
            data['conditional_pesticides'] = ""
    
    return data


def _prepare_nutrient_data(context):
    """영양결핍 데이터 준비"""
    
    ai_text = call_ai_diagnosis(context['question'], context.get('crop_name'))
    
    return {
        'ai_diagnosis': ai_text,
        'nutrient_solution': """1. 해당 영양소 엽면시비
2. 토양 검사 후 밑거름 조정
3. pH 측정 및 조정"""
    }


def _prepare_physiological_data(context):
    """생리장해 데이터 준비"""
    
    ai_text = call_ai_diagnosis(context['question'], context.get('crop_name'))
    
    return {
        'ai_diagnosis': ai_text,
        'physiological_solution': """1. 환경 조건 개선 (온도, 습도, 일조)
2. 물 관리 (과습/건조 방지)
3. 통풍 개선"""
    }


def _prepare_insect_data(context):
    """익충 구분 데이터 준비"""
    
    ai_text = call_ai_diagnosis(context['question'], context.get('crop_name'))
    
    return {
        'insect_type': '익충 또는 해충 (AI 판단)',
        'insect_action': ai_text
    }


def _prepare_history_data(context):
    """사용자가 묻는 특정 날짜나 마지막 방제 기록을 상세히 추출"""
    history = context.get('spray_history', [])
    question = context.get('question', '')
    
    if not history:
        return {
            'spray_history_list': '📋 아직 기록된 방제 일지가 없습니다.\n방제 후 일지를 작성하시면 AI가 분석해 드립니다.',
            'recent_ingredients': '없음',
            'last_spray_hours': '0',
            'next_spray_time': '언제든지 가능'
        }

# ✅ [추가] "이번 달 횟수" 같은 통계 질문 처리 로직
    if any(kw in q_lower for kw in ['횟수', '몇번', '통계', '이번달', '이달']):
        from datetime import datetime
        current_month = datetime.now().strftime('%Y-%m')
        # 이번 달 기록만 필터링
        this_month_records = [h for h in history if str(h.get('spray_date', '')).startswith(current_month)]
        count = len(this_month_records)
        
        summary = f"📊 이번 달({datetime.now().month}월)에는 총 **{count}회** 방제를 하셨습니다.\n"
        if count > 0:
            last_p = this_month_records[0].get('pesticide_name', '알수없음')
            summary += f"최근에는 **{last_p}** 약제를 사용하셨네요."
        
        return {
            'spray_history_list': summary,
            'recent_ingredients': this_month_records[0].get('pesticide_name', '없음') if count > 0 else '없음',
            'last_spray_hours': f"{history[0].get('hours_ago', 0):.1f}",
            'next_spray_time': "이력 참조"
        }
    # 1. 질문에서 날짜 추출 (예: "2월 4일" -> "02-04")
    import re
    # '2월 4일', '02/04', '2.4' 등 다양한 패턴 대응
    date_match = re.search(r'(\d+)월\s*(\d+)일|(\d+)/(\d+)|(\d+)\.(\d+)', question)
    
    target_record = None
    search_date_msg = ""

    if date_match:
        # 매칭된 그룹 중 숫자가 있는 그룹을 찾아 월/일 설정
        m, d = 0, 0
        groups = date_match.groups()
        if groups[0]: m, d = groups[0], groups[1]
        elif groups[2]: m, d = groups[2], groups[3]
        elif groups[4]: m, d = groups[4], groups[5]
        
        target_date_str = f"{str(m).zfill(2)}-{str(d).zfill(2)}" # 예: "02-04"
        search_date_msg = f"🔍 {m}월 {d}일 기록을 찾아보았습니다."
        
        # 전체 기록 중 해당 날짜가 포함된 데이터 필터링
        for h in history:
            if target_date_str in h.get('spray_date', ''):
                target_record = h
                break
    
    # 2. 특정 날짜를 못 찾았거나 "언제야?"처럼 마지막 기록을 물어본 경우
    if not target_record:
        target_record = history[0] # 가장 최신 기록
        if not search_date_msg:
            search_date_msg = "📋 가장 최근에 등록하신 방제 기록입니다."
        else:
            search_date_msg = f"⚠️ 해당 날짜({target_date_str}) 기록이 없어 가장 최근 기록을 보여드립니다."

    # 3. 방제일지 데이터 추출 (treatment_log_page.dart 필드 기준)
    res_date = target_record.get('spray_date', '알수없음')
    res_pest = target_record.get('pest_name', '알수없음')
    res_pesticide = target_record.get('pesticide_name', '알수없음')
    res_temp = target_record.get('temperature', '?')
    res_dilution = target_record.get('dilution', '기록없음') # 희석배수
    res_memo = target_record.get('memo', '내용 없음') # 메모 필드

    # 4. 출력용 텍스트 조립
    detail_text = f"""{search_date_msg}

【상세 내역】
• 일시: {res_date}
• 대상 병해충: {res_pest}
• 사용 약제: {res_pesticide}
• 희석 배수: {res_dilution}
• 당시 온도: {res_temp}°C
• 현장 메모: {res_memo}"""

    # 5. 다음 방제 가능 시간 계산 (72시간 기준)
    hours_ago = target_record.get('hours_ago', 999)
    if hours_ago < 72:
        next_time = f"⏰ 약 {72 - hours_ago:.1f}시간 후 가능"
    else:
        next_time = "✅ 지금 바로 가능"

    return {
        'days': 30, # 조회 기간 (기본값)
        'spray_history_list': detail_text,
        'recent_ingredients': res_pesticide,
        'last_spray_hours': f"{hours_ago:.1f}",
        'next_spray_time': next_time
    }

def _prepare_next_spray_data(context):
    """다음 방제시기 데이터 준비"""
    
    history = context.get('spray_history', [])
    
    if not history:
        return {
            'last_spray_date': '없음',
            'hours': '0',
            'days': '0',
            'last_pesticide': '없음',
            'recommended_date': '언제든지',
            'spray_status': '✅ 방제 가능'
        }
    
    last = history[0]
    hours = last.get('hours_ago', 0)
    days = hours / 24
    
    from datetime import timedelta
    last_date = last.get('spray_date', '알수없음')
    
    try:
        last_dt = datetime.fromisoformat(last_date)
        recommended_dt = last_dt + timedelta(hours=72)
        recommended_date = recommended_dt.strftime('%Y-%m-%d %H시')
    except:
        recommended_date = '72시간 후'
    
    if hours >= 72:
        status = '✅ 방제 가능'
    else:
        status = f'⏰ 대기 중 ({72-hours:.1f}시간 남음)'
    
    return {
        'last_spray_date': last_date,
        'hours': f"{hours:.1f}",
        'days': f"{days:.1f}",
        'last_pesticide': last.get('pesticide_name', '알수없음'),
        'recommended_date': recommended_date,
        'spray_status': status
    }


def _prepare_pesticide_info_data(context):
    """약제정보 데이터 준비"""
    
    pesticide_name = context.get('user_input_pesticide', '해당 약제')
    
    return {
        'pesticide_name': pesticide_name,
        'pesticide_info': """(라벨 확인 필요)
- 성분: 라벨 참조
- 함량: 라벨 참조
- 적용 작물/병해충: 라벨 참조""",
        'dilution': '라벨 확인'
    }


def _prepare_inventory_data(context):
    """재고확인 데이터 준비"""
    
    user_pesticide = context.get('user_input_pesticide', '해당 약제')
    
    return {
        'user_pesticide': user_pesticide,
        'applicability': """【사용 가능 여부】
라벨에서 다음을 확인하세요:
1. 적용 작물에 포함되는지
2. 적용 병해충에 포함되는지
3. 유효기간이 남았는지

사용 가능하면 희석배수를 라벨에서 확인 후 사용하세요."""
    }


def _prepare_linked_data(context):
    """연관질문 데이터 준비"""
    
    from core import get_session
    
    session = get_session(context.get('phone')) if context.get('phone') else None
    
    if not session:
        return {
            'previous_question': '이전 대화 없음',
            'previous_recommendations': '없음',
            'linked_answer': '이전 대화를 찾을 수 없습니다.',
            'additional_answer': '추가 정보를 제공할 수 없습니다.',
            'excluded_pesticides': '없음'
        }
    
    return {
        'previous_question': session.get('question', '?'),
        'previous_recommendations': '이전 추천 약제 참조',
        'linked_answer': '이전 맥락을 고려한 답변입니다.',
        'additional_answer': '추가 정보입니다.',
        'excluded_pesticides': '이전 추천 약제'
    }


def _prepare_vulnerable_pests_data(context):
    """작물별 취약 병해충 데이터 준비"""
    
    from core import load_excel_data
    from collections import Counter
    
    crop_name = context.get('crop_name', '알수없음')
    
    if not crop_name or crop_name == '알수없음':
        return {
            'vulnerable_pests': '작물명을 알 수 없어 분석할 수 없습니다.'
        }
    
    # 엑셀 로드
    df = load_excel_data(crop_name, EXCEL_PATH)
    
    if df.empty:
        return {
            'vulnerable_pests': f'{crop_name}에 대한 등록 약제 데이터가 없습니다.'
        }
    
    # 적용병해충 칼럼 분석
    if '적용병해충' not in df.columns:
        return {
            'vulnerable_pests': '병해충 정보를 찾을 수 없습니다.'
        }
    
    # 병해충 빈도 계산
    pest_counter = Counter()
    
    for pest_disease in df['적용병해충']:
        if pest_disease and str(pest_disease).strip() and str(pest_disease) != 'nan':
            pest_name = str(pest_disease).strip()
            pest_counter[pest_name] += 1
    
    if not pest_counter:
        return {
            'vulnerable_pests': f'{crop_name}에 등록된 병해충 정보가 없습니다.'
        }
    
    # 상위 15개 추출
    top_pests = pest_counter.most_common(15)
    
    # 포맷팅
    result_lines = []
    for i, (pest, count) in enumerate(top_pests, 1):
        # 등급 표시
        if count >= 50:
            level = "🔴 매우 높음"
        elif count >= 20:
            level = "🟠 높음"
        elif count >= 10:
            level = "🟡 보통"
        else:
            level = "🟢 낮음"
        
        result_lines.append(f"{i}. {pest} - {level} (등록 약제 {count}개)")
    
    return {
        'vulnerable_pests': '\n'.join(result_lines)
    }


# def _format_spray_warning(context):
#     """방제 경고 포맷"""
    
#     if not context.get('spray_history'):
#         return "✅ 최근 방제 기록 없음 - 안전"
    
#     last = context['spray_history'][0]
#     hours = last.get('hours_ago', 0)
#     days = hours / 24
    
#     if hours < 12:
#         return f"""🚨🚨🚨 12시간 이내 방제 이력! 🚨🚨🚨
# 최근 방제: {hours:.1f}시간 전
# ❌ 추가 방제 절대 금지 (약해 위험 극대)
# ✅ 72시간 (3일) 대기 필수"""
    
#     elif hours < 24:
#         return f"""🚨🚨🚨 24시간 이내 방제 이력! 🚨🚨🚨
# 최근 방제: {hours:.1f}시간 전
# ❌ 추가 방제 절대 금지 (약해 위험)
# ✅ 72시간 (3일) 대기 필수"""
    
#     elif hours < 72:
#         # 48~72시간: 강력 권고
#         if hours >= 48:
#             return f"""⚠️⚠️⚠️ 72시간 대기 강력 권고 ⚠️⚠️⚠️
# 최근 방제: {hours:.1f}시간 전 ({days:.1f}일)
# 이전 병해충: {last.get('pest_name', '알수없음')}

# 【경고】
# ❌ 병해충이 달라도 연속 방제는 약해 위험!
# ❌ 작물에 화학적 스트레스 누적

# 【권장 조치】
# ✅ 가능하면 72시간({72-hours:.1f}시간 남음)까지 대기
# ✅ 긴급 시에만 아래 약제 사용
# ✅ 희석배수 정확히 준수 필수"""
#         # 24~48시간: 일반 경고
#         else:
#             return f"""⚠️ 최근 방제: {hours:.1f}시간 전 ({days:.1f}일)
# ⚠️ 72시간 미만 - 가능하면 더 대기
# (긴급 상황 아니면 72시간까지 대기 권장)"""
    
#     else:
#         return f"""✅ 최근 방제: {hours:.1f}시간 전 ({days:.1f}일)
# ✅ 방제 간격 충분 (72시간 이상)"""

def _format_spray_warning(context):
    """방제 경고 포맷 - 앞부분의 불필요한 빈 줄 제거"""
    if not context.get('spray_history'):
        return "✅ 최근 방제 기록이 없어서 안전하게 방제하실 수 있는 상태입니다."
    
    last = context['spray_history'][0]
    hours = last.get('hours_ago', 0)
    days = hours / 24
    pesticide = last.get('pesticide_name', '알 수 없는 약제')
    pest = last.get('pest_name', '병해충')
    
    # 💡 f""" 바로 뒤에 글자를 붙여서 빈 줄을 방지합니다.
    if hours < 12:
        return f"⚠️ 데이터를 확인해보니 약 {hours:.1f}시간 전에 {pest} 방제를 위해 '{pesticide}'를 이미 살포하셨네요.\n현재 12시간이 지나지 않았기 때문에 지금 바로 다른 약을 뿌리면 작물에 심각한 약해가 발생할 수 있습니다.\n최소 72시간(3일) 정도는 작물이 충분히 회복할 시간을 준 뒤에 다음 방제를 시작하시는 것을 강력히 권장합니다."

    elif hours < 72:
        return f"⏰ 조금만 더 대기해 주세요!\n약 {hours:.1f}시간({days:.1f}일) 전에 '{pesticide}'을(를) 이미 사용하셨군요.\n현재 상황은 아직 약효가 충분히 나타나기 전입니다. 너무 급하게 다음 약을 치면 작물이 화학적 스트레스를 크게 받을 수 있어요.\n가능하면 72시간(3일)까지는 밭 상태를 지켜보며 기다려 주시는 것이 가장 안전합니다."

    else:
        return f"✅ 이전 방제로부터 {days:.1f}일이 지나서, 이제는 안전하게 방제를 준비하셔도 괜찮은 시기입니다."


# def _format_pesticides_list(pesticides, pest_name=None):
#     """전체 약제 표시 (우선 약제에만 ⭐ 표시)"""
    
#     if not pesticides:
#         return "❌ 추천 가능한 약제 없음"
    
#     # 1. 우선 약제 이름 목록 파악
#     priority_names = []
#     if pest_name:
#         # 병해충 정규화
#         normalized_pest = pest_name
#         if '응애' in pest_name:
#             normalized_pest = '응애'
#         elif '진딧물' in pest_name:
#             normalized_pest = '진딧물'
#         elif '나방' in pest_name:
#             normalized_pest = '나방류'
#         elif '가루이' in pest_name:
#             normalized_pest = '가루이류'
#         elif '총채' in pest_name:
#             normalized_pest = '총채벌레류'
        
#         priority_names = PRIORITY_PESTICIDES.get(normalized_pest, [])
    
#     # 2. 전체 약제 표시 (최대 10개)
#     display_list = pesticides[:10]
    
#     if not display_list:
#         return "❌ 추천 가능한 약제 없음"
    
#     # 3. 포맷팅
#     result = []
    
#     for i, p in enumerate(display_list, 1):
#         # 이 약제가 우선 약제인지 체크
#         is_priority = False
#         if priority_names:
#             product_name = p['product_name'].lower()
#             for priority_name in priority_names:
#                 if priority_name.lower() in product_name:
#                     is_priority = True
#                     break
        
#         priority_mark = "⭐ 우선 추천" if is_priority else ""
#         result.append(f"""
# {i}. {p['product_name']} {priority_mark}
#    • 성분: {p['ingredient']}
#    • 함량: {p['content']}
#    • 제형: {p['formulation']}
#    • 희석배수: {p['dilution']}
#    • 회사: {p['company']}
# """)
    
#     return ''.join(result)

def _format_pesticides_list(pesticides, pest_name=None):
    """전체 약제 표시 (우선 추천 ⭐ 표시 및 최대 5개 제한 적용)"""
    
    if not pesticides:
        return "❌ 현재 농가 상황에 추천 가능한 약제가 없습니다."
    
    # 1. 우선 추천 약제 대상 파악 (병해충명 정규화 로직 포함)
    priority_names = []
    if pest_name:
        normalized_pest = pest_name
        # 병해충 그룹핑 정규화
        if '응애' in pest_name:
            normalized_pest = '응애'
        elif '진딧물' in pest_name:
            normalized_pest = '진딧물'
        elif '나방' in pest_name:
            normalized_pest = '나방류'
        elif '가루이' in pest_name:
            normalized_pest = '가루이류'
        elif '총채' in pest_name:
            normalized_pest = '총채벌레류'
        
        # answer_logic_data.py의 PRIORITY_PESTICIDES에서 목록 가져오기
        priority_names = PRIORITY_PESTICIDES.get(normalized_pest, [])
    
    # 2. 약제 추천 개수를 최대 5개로 제한
    display_list = pesticides[:5]
    
    # 3. 답변 메시지 조립
    result = []
    for i, p in enumerate(display_list, 1):
        # 해당 약제가 우선 추천 목록에 포함되는지 확인
        is_priority = False
        if priority_names:
            product_name = p['product_name'].lower()
            for priority_name in priority_names:
                if priority_name.lower() in product_name:
                    is_priority = True
                    break
        
        # 우선 추천일 경우 별표 마크 추가
        priority_mark = "⭐ 우선 추천" if is_priority else ""
        
        # 개별 약제 정보 포맷팅 (내용 누락 없이 친절한 말투 적용)
        result.append(f"""
{i}. {p['product_name']} {priority_mark}
   • 성분: {p['ingredient']}
   • 함량: {p['content']}
   • 제형: {p['formulation']}
   • 희석배수: {p['dilution']}
   • 회사: {p['company']}
""")
    
    return ''.join(result)


def _format_pesticides_by_ingredient(pesticides, crop_name=None):
    """성분 중심 포맷팅 (범위 넓은 질문용)"""
    
    if not pesticides:
        return "❌ 추천 가능한 약제 없음"
    
    # 성분별로 그룹핑
    ingredient_groups = {}
    for p in pesticides:
        ingredient = p['ingredient']
        if ingredient not in ingredient_groups:
            ingredient_groups[ingredient] = []
        ingredient_groups[ingredient].append(p)
    
    # 성분 리스트 (최대 15개)
    ingredients = list(ingredient_groups.keys())[:15]
    
    result = []
    result.append(f"[{crop_name} 등록 성분 예시]\n")
    
    for ingredient in ingredients:
        # 작용기작 정보는 추후 추가 가능
        # 지금은 성분명만
        products = ingredient_groups[ingredient]
        product_count = len(products)
        
        # 대표 제품 1개
        example_product = products[0]['product_name']
        
        result.append(f"• {ingredient}")
        result.append(f"  (제품 예: {example_product} 외 {product_count-1}개)\n")
    
    result.append(f"\n💡 총 {len(ingredients)}개 성분, {len(pesticides)}개 제품")
    
    return ''.join(result)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 딸기 화방 관련 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _extract_flower_cluster_info(question, context):
    """딸기 화방 정보 추출"""
    q_lower = question.lower()
    
    # 화방 번호 추출
    cluster_num = None
    cluster_patterns = [
        r'(\d+)화방', 
        r'제?(\d+)화방',
        r'(\d)화방',
    ]
    
    for pattern in cluster_patterns:
        match = re.search(pattern, question)
        if match:
            cluster_num = int(match.group(1))
            break
    
    # 화방 상태 추출
    cluster_state = None
    if any(kw in q_lower for kw in ['수확', '수확중', '수확완료']):
        cluster_state = '수확중'
    elif any(kw in q_lower for kw in ['개화', '꽃', '꽃핀', '꽃피']):
        cluster_state = '개화중'
    elif any(kw in q_lower for kw in ['착과', '열매맺', '결실']):
        cluster_state = '착과중'
    elif any(kw in q_lower for kw in ['분화', '꽃눈']):
        cluster_state = '분화중'
    
    # 시기 추정
    current_month = datetime.now().month
    estimated_stage = None
    
    if current_month in [12, 1]:  # 12-1월
        estimated_stage = "1화방 수확중, 2화방 개화중"
    elif current_month in [2]:  # 2월
        estimated_stage = "1화방 수확완료, 2화방 착과중"
    elif current_month in [3, 4]:  # 3-4월
        estimated_stage = "2화방 수확중, 3,4화방 관리"
    elif current_month in [5]:  # 5월
        estimated_stage = "후기 관리, 연속 수확"
    
    return {
        'cluster_num': cluster_num,
        'cluster_state': cluster_state,
        'estimated_stage': estimated_stage,
        'current_month': current_month
    }



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI 호출
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def call_ai_reasoning(prompt, max_tokens=1000):
    """Excel 데이터 기반 복잡한 추론"""
    
    try:
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        logger.info(f"🤖 AI 추론 호출: {len(prompt)}자 프롬프트")
        response = requests.post(VLLM_API, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            ai_text = data['choices'][0]['message']['content'].strip()
            logger.info(f"✅ AI 추론: {len(ai_text)}자")
            return ai_text
        else:
            logger.warning(f"⚠️ AI 응답 실패: {response.status_code}")
            return "AI 분석을 완료할 수 없습니다. 전문가 상담이 필요합니다."
            
    except requests.exceptions.Timeout:
        logger.warning("⚠️ AI 타임아웃")
        return "AI 분석 시간이 초과되었습니다. 전문가 상담이 필요합니다."
    except Exception as e:
        logger.error(f"❌ AI 추론 오류: {e}")
        return "AI 분석 중 오류가 발생했습니다. 전문가 상담이 필요합니다."


def call_ai_simple(pest_name):
    """병해충 간단 설명만 요청"""
    
    prompt = f"""농민이 이해하기 쉽게 '{pest_name}'을(를) 3줄 이내로 설명해주세요.

설명에 포함할 내용:
- 크기, 색상, 특징
- 주로 피해 입히는 부위
- 번식 속도 (빠름/보통/느림)

답변:"""
    
    try:
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300,
            "temperature": 0.3
        }
        
        logger.info(f"🤖 AI 호출: {pest_name} 설명")
        response = requests.post(VLLM_API, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            ai_text = data['choices'][0]['message']['content'].strip()
            logger.info(f"✅ AI 응답: {len(ai_text)}자")
            return ai_text
        else:
            logger.warning(f"⚠️ AI 응답 실패: {response.status_code}")
            return f"({pest_name}에 대한 설명)"
            
    except requests.exceptions.Timeout:
        logger.warning("⚠️ AI 타임아웃")
        return f"({pest_name}에 대한 설명)"
    except Exception as e:
        logger.error(f"❌ AI 호출 오류: {e}")
        return f"({pest_name}에 대한 설명)"


def call_ai_diagnosis(question, crop_name=None):
    """증상 진단 요청"""
    
    logger.info(f"🔍 call_ai_diagnosis 호출 - crop_name: {crop_name}")
    
    crop_info = f"작물: {crop_name}\n" if crop_name else ""
    logger.info(f"🔍 AI 프롬프트 작물 정보: '{crop_info.strip()}'")
    
    prompt = f"""{crop_info}증상: {question}

위 증상의 원인을 3~5줄로 진단해주세요.

포함할 내용:
- 가능성 높은 병해충 또는 원인 (1~3가지)
- 각 원인의 특징적 증상
- 구분 방법

❌ 약제는 추천하지 마세요.

답변:"""
    
    try:
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        logger.info(f"🤖 AI 진단 호출")
        response = requests.post(VLLM_API, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            ai_text = data['choices'][0]['message']['content'].strip()
            logger.info(f"✅ AI 진단: {len(ai_text)}자")
            
            ai_text = _remove_pesticide_recommendations(ai_text)
            
            return ai_text
        else:
            logger.warning(f"⚠️ AI 응답 실패: {response.status_code}")
            return """증상 분석:
1. 병해충 가능성 확인 필요
2. 환경 조건 확인 (온도, 습도)
3. 전문가 진단 권장"""
            
    except requests.exceptions.Timeout:
        logger.warning("⚠️ AI 타임아웃")
        return """증상 분석:
1. 병해충 가능성 확인 필요
2. 환경 조건 확인 (온도, 습도)
3. 전문가 진단 권장"""
    except Exception as e:
        logger.error(f"❌ AI 진단 오류: {e}")
        return """증상 분석:
1. 병해충 가능성 확인 필요
2. 환경 조건 확인 (온도, 습도)
3. 전문가 진단 권장"""


def _remove_pesticide_recommendations(text):
    """AI 응답에서 약제 추천 부분 제거"""
    
    pesticide_keywords = [
        '추천', '권장', '사용', '살포', '방제약', '농약',
        '약제', '희석', '배수', '처리'
    ]
    
    lines = text.split('\n')
    filtered_lines = []
    
    for line in lines:
        keyword_count = sum(1 for kw in pesticide_keywords if kw in line.lower())
        if keyword_count < 2:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def test_ai_connection():
    """AI 연결 테스트"""
    
    try:
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": "안녕하세요"}
            ],
            "max_tokens": 50,
            "temperature": 0.3
        }
        
        response = requests.post(VLLM_API, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ AI 연결 성공")
            return True
        else:
            logger.warning(f"⚠️ AI 연결 실패: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ AI 연결 오류: {e}")
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 유형 37~45 데이터 준비 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _prepare_cross_check_data(context):
    """유형 37: 교차 확인 데이터 준비"""
    
    from core import load_excel_data
    
    question = context['question']
    crop_name = context.get('crop_name', '알수없음')
    
    # 여러 병해충 추출
    pests = _extract_all_pests(question)
    
    if len(pests) < 2:
        return {
            'ai_analysis': "2개 이상의 병해충명이 필요합니다. 다시 구체적으로 질문해주세요."
        }
    
    pest1, pest2 = pests[0], pests[1]
    
    # Excel 로드
    df = load_excel_data(crop_name, EXCEL_PATH)
    
    if df.empty:
        return {
            'ai_analysis': f"{crop_name} 작물 데이터가 없습니다."
        }
    
    # pest1 약제들의 적용병해충 데이터
    pest1_pesticides = search_and_filter_pesticides(pest1, [], df)
    
    # 적용병해충 정보만 추출
    pest1_data = []
    for p in pest1_pesticides:
        pest1_data.append({
            'product_name': p['product_name'],
            'pest_disease': p['pest_disease']
        })
    
    # AI 프롬프트
    prompt = f"""작물: {crop_name}
질문: "{question}"

[{pest1} 약제들의 적용병해충 데이터]
총 {len(pest1_data)}개 약제

"""
    
    for i, p in enumerate(pest1_data[:20], 1):  # 최대 20개
        prompt += f"{i}. {p['product_name']} - 적용병해충: {p['pest_disease']}\n"
    
    prompt += f"""

분석 요청:
1. 위 {pest1} 약제들 중 "{pest2}"가 적용병해충에 포함된 약제 찾기
2. 포함된 약제 개수와 제품명 나열
3. 포함 안된 약제 개수
4. 결론: "{pest1} 약제로 {pest2}도 잡을 수 있나요?"에 대한 답변

⚠️ Excel 데이터에 있는 정보만 사용
⚠️ 없으면 "확인 필요"

답변:
"""
    
    ai_analysis = call_ai_reasoning(prompt, max_tokens=800)
    
    return {
        'ai_analysis': ai_analysis
    }


def _prepare_prevention_data(context):
    """유형 38: 예방 데이터 준비"""
    
    from core import load_excel_data
    
    crop_name = context.get('crop_name', '알수없음')
    pest_name = context.get('pest_name', '알수없음')
    
    if crop_name == '알수없음' or pest_name == '알수없음':
        return {
            'ai_prevention_guide': "작물명과 병해충명이 필요합니다."
        }
    
    # Excel 로드
    df = load_excel_data(crop_name, EXCEL_PATH)
    
    if df.empty:
        return {
            'ai_prevention_guide': f"{crop_name} 작물 데이터가 없습니다."
        }
    
    # 해당 병해충 약제들의 사용적기 정보 추출
    pest_pesticides = search_and_filter_pesticides(pest_name, [], df)
    
    usage_data = []
    for p in pest_pesticides[:10]:  # 최대 10개
        usage_info = p.get('usage', '')
        if usage_info and str(usage_info) != 'nan':
            usage_data.append(usage_info)
    
    # AI 프롬프트
    prompt = f"""작물: {crop_name}
병해충: {pest_name}

[Excel 데이터 - 사용적기 및 방법]
"""
    
    for i, usage in enumerate(usage_data, 1):
        prompt += f"{i}. {usage}\n"
    
    prompt += f"""

위 데이터를 분석하여:
1. {pest_name}의 발생 시기/조건 파악
2. 발생 전 관리 방법 추출
3. 예방적 환경 관리 요령 정리

⚠️ Excel에 명시된 내용만 사용
⚠️ 없으면 "확인 필요"

답변 형식:
【{pest_name} 특성 분석】
• 발생 조건: ...
• 주 발생 시기: ...
• 번식 속도: ...

【예방 관리 포인트】
1. ...
2. ...

【환경 관리】
• ...
"""
    
    ai_prevention_guide = call_ai_reasoning(prompt, max_tokens=600)
    
    return {
        'ai_prevention_guide': ai_prevention_guide
    }


def _prepare_growth_stage_data(context):
    """유형 39: 생육주기 데이터 준비"""
    
    from core import load_excel_data
    
    crop_name = context.get('crop_name', '알수없음')
    pest_name = context.get('pest_name', '알수없음')
    question = context['question']
    
    growth_stage = _extract_growth_stage(question)
    
    # 기본 pesticides_list
    pesticides_list = _format_pesticides_list(context.get('pesticides', []), pest_name)
    
    if crop_name == '알수없음' or pest_name == '알수없음':
        return {
            'growth_stage': growth_stage or '확인 필요',
            'ai_growth_stage_guide': "작물명과 병해충명이 필요합니다.",
            'pesticides_list': pesticides_list
        }
    
    # Excel 로드
    df = load_excel_data(crop_name, EXCEL_PATH)
    
    if df.empty:
        return {
            'growth_stage': growth_stage or '확인 필요',
            'ai_growth_stage_guide': f"{crop_name} 작물 데이터가 없습니다.",
            'pesticides_list': pesticides_list
        }
    
    # 해당 병해충 약제들의 사용적기 + 안전사용기준 정보
    pest_pesticides = search_and_filter_pesticides(pest_name, [], df)
    
    usage_safety_data = []
    for p in pest_pesticides[:15]:
        usage_safety_data.append({
            'product_name': p['product_name'],
            'usage': p.get('usage', ''),
            'safety': p.get('safety', '')
        })
    
    # AI 프롬프트
    prompt = f"""작물: {crop_name}
병해충: {pest_name}
생육단계: {growth_stage or '확인 필요'}
질문: "{question}"

[약제별 사용적기 및 안전사용기준 데이터]
"""
    
    for i, p in enumerate(usage_safety_data, 1):
        prompt += f"\n{i}. {p['product_name']}\n"
        prompt += f"   사용적기: {p['usage']}\n"
        prompt += f"   안전기준: {p['safety']}\n"
    
    prompt += f"""

분석:
1. {growth_stage or '해당 생육단계'}에서 사용 시 제약사항 찾기
2. 주의해야 할 약제 또는 제형 파악
3. 안전사용기준 확인

⚠️ Excel 데이터에 없으면 "라벨 확인 필요"

답변 형식:
【생육단계: {growth_stage or '확인 필요'}】

【Excel 데이터 분석 결과】
• 제약 없음: ○개
• 주의 필요: ○개
• 명시 없음: ○개 (라벨 확인 필요)

【주의사항】
• ...
"""
    
    ai_growth_stage_guide = call_ai_reasoning(prompt, max_tokens=600)
    
    return {
        'growth_stage': growth_stage or '확인 필요',
        'ai_growth_stage_guide': ai_growth_stage_guide,
        'pesticides_list': pesticides_list
    }


def _prepare_rotation_data(context):
    """유형 40: 성분 계통 변경 데이터 준비"""
    
    from core import load_excel_data
    
    crop_name = context.get('crop_name', '알수없음')
    pest_name = context.get('pest_name', '알수없음')
    
    # 제외 정보
    exclude_info = context.get('exclude_info', {})
    previous_pesticide = exclude_info.get('product', '알수없음')
    previous_ingredient = exclude_info.get('ingredient', '알수없음')
    
    # 약제 목록
    pesticides = context.get('pesticides', [])
    pesticides_list = _format_pesticides_list(pesticides, pest_name)
    exclude_notice = f"({previous_pesticide} 및 최근 3회 성분 제외)"
    
    if crop_name == '알수없음' or pest_name == '알수없음':
        return {
            'previous_pesticide': previous_pesticide,
            'previous_ingredient': previous_ingredient,
            'ai_rotation_guide': "작물명과 병해충명이 필요합니다.",
            'pesticides_list': pesticides_list,
            'exclude_notice': exclude_notice
        }
    
    # Excel 로드
    df = load_excel_data(crop_name, EXCEL_PATH)
    
    if df.empty:
        return {
            'previous_pesticide': previous_pesticide,
            'previous_ingredient': previous_ingredient,
            'ai_rotation_guide': f"{crop_name} 작물 데이터가 없습니다.",
            'pesticides_list': pesticides_list,
            'exclude_notice': exclude_notice
        }
    
    # 모든 약제의 성분 추출
    all_ingredients = []
    for p in pesticides[:20]:
        ingredient = p.get('ingredient', '')
        if ingredient and ingredient not in all_ingredients:
            all_ingredients.append(ingredient)
    
    # AI 프롬프트
    prompt = f"""병해충: {pest_name}
최근 사용 성분: {previous_ingredient}

[가용 약제 성분 목록]
"""
    
    for i, ing in enumerate(all_ingredients, 1):
        prompt += f"{i}. {ing}\n"
    
    prompt += f"""

분석:
1. {previous_ingredient}와 다른 계열 찾기
2. 3가지 성분 순환 조합 제안
3. 각 성분의 특징 비교

⚠️ Excel에 있는 성분만 사용

답변 형식:
【성분 분석】
최근 사용: {previous_ingredient}

【다른 계열 약제】
• ... (계열명)
• ... (계열명)

【추천 순환 조합】
1차: ...
2차: ... (다른 계열)
3차: ... (다른 계열)
→ 1차로 돌아가서 반복

【각 성분 특징】
• ...: 속효성/잔효성/침투이행성 등
"""
    
    ai_rotation_guide = call_ai_reasoning(prompt, max_tokens=600)
    
    return {
        'previous_pesticide': previous_pesticide,
        'previous_ingredient': previous_ingredient,
        'ai_rotation_guide': ai_rotation_guide,
        'pesticides_list': pesticides_list,
        'exclude_notice': exclude_notice
    }


def _prepare_multiple_pests_data(context):
    """유형 41: 복합 병해충 데이터 준비"""
    
    from core import load_excel_data
    
    question = context['question']
    crop_name = context.get('crop_name', '알수없음')
    
    # 여러 병해충 추출
    pests = _extract_all_pests(question)
    
    if len(pests) < 2:
        return {
            'ai_analysis': "2개 이상의 병해충명이 필요합니다."
        }
    
    pest1, pest2 = pests[0], pests[1]
    
    # Excel 로드
    df = load_excel_data(crop_name, EXCEL_PATH)
    
    if df.empty:
        return {
            'ai_analysis': f"{crop_name} 작물 데이터가 없습니다."
        }
    
    # 각 병해충 약제 검색
    pest1_pesticides = search_and_filter_pesticides(pest1, [], df)
    pest2_pesticides = search_and_filter_pesticides(pest2, [], df)
    
    # 약제명만 추출
    pest1_names = [p['product_name'] for p in pest1_pesticides]
    pest2_names = [p['product_name'] for p in pest2_pesticides]
    
    # AI 프롬프트
    prompt = f"""작물: {crop_name}
질문: "{question}"

[{pest1} 약제] ({len(pest1_names)}개)
{', '.join(pest1_names[:30])}

[{pest2} 약제] ({len(pest2_names)}개)
{', '.join(pest2_names[:30])}

분석:
1. 두 목록의 교집합 찾기 (둘 다에 등록된 약제)
2. 교집합 약제 개수와 제품명
3. 결론: 한 번에 잡을 수 있는지 여부

⚠️ Excel 데이터에 있는 약제명만 사용

답변 형식:
【분석 결과】
• {pest1} 약제: {len(pest1_names)}개
• {pest2} 약제: {len(pest2_names)}개
• 둘 다 등록: ○개

【둘 다 등록된 약제】
1. ...
2. ...

【권장 방식】
(교집합이 적으면 개별 방제 권장)
"""
    
    ai_analysis = call_ai_reasoning(prompt, max_tokens=600)
    
    return {
        'ai_analysis': ai_analysis
    }


def _prepare_comparison_data(context):
    """유형 42: 약제 비교 데이터 준비"""
    
    from core import load_excel_data
    
    question = context['question']
    crop_name = context.get('crop_name', '알수없음')
    
    # 약제명 2개 추출 (간단한 패턴)
    import re
    
    # "A랑 B", "A과 B", "A와 B" 패턴
    product_pattern = r'([가-힣a-zA-Z0-9]+)(?:랑|과|와|하고|,)\s*([가-힣a-zA-Z0-9]+)'
    matches = re.search(product_pattern, question)
    
    if not matches:
        return {
            'ai_comparison': "2개의 약제명이 필요합니다. 예: 'A와 B 중 뭐가 나아요?'"
        }
    
    product1 = matches.group(1)
    product2 = matches.group(2)
    
    # Excel 로드
    df = load_excel_data(crop_name, EXCEL_PATH)
    
    if df.empty:
        return {
            'ai_comparison': f"{crop_name} 작물 데이터가 없습니다."
        }
    
    # 약제 정보 찾기
    try:
        p1_data = df[df['제품명'].str.contains(product1, na=False, case=False)].iloc[0]
        p2_data = df[df['제품명'].str.contains(product2, na=False, case=False)].iloc[0]
    except:
        return {
            'ai_comparison': f"{product1} 또는 {product2} 약제를 찾을 수 없습니다."
        }
    
    # AI 프롬프트
    prompt = f"""약제 비교 요청
질문: "{question}"

[Excel 데이터 비교]
구분 | {product1} | {product2}
성분 | {p1_data.get('성분명', '')} | {p2_data.get('성분명', '')}
함량 | {p1_data.get('함량', '')} | {p2_data.get('함량', '')}
제형 | {p1_data.get('제형', '')} | {p2_data.get('제형', '')}
적용병해충 | {p1_data.get('적용병해충', '')} | {p2_data.get('적용병해충', '')}
등록일 | {p1_data.get('등록일', '')} | {p2_data.get('등록일', '')}

객관적 차이만 제시:
1. 성분 차이
2. 제형 차이
3. 적용 범위 차이
4. 등록 시기 차이

⚠️ 우열 판단 금지
⚠️ "더 좋다/나쁘다" 표현 금지
⚠️ 객관적 사실만

답변 형식:
【약제 비교】 (객관적 데이터만)

【성분】
• {product1}: ...
• {product2}: ...
→ (같은/다른) 성분

【적용 범위】
• {product1}: ...
• {product2}: ...
→ 차이 설명

【결론】
❌ 어느 것이 더 나은지 판단 불가
✅ 위 차이를 고려하여 농약사와 상담
✅ 두 약제 순환 사용 시 저항성 방지
"""
    
    ai_comparison = call_ai_reasoning(prompt, max_tokens=600)
    
    return {
        'ai_comparison': ai_comparison
    }


def _prepare_duration_data(context):
    """유형 43: 약효 지속기간 데이터 준비"""
    
    from core import load_excel_data
    
    question = context['question']
    crop_name = context.get('crop_name', '알수없음')
    pest_name = context.get('pest_name', '알수없음')
    
    # 약제명 추출 (간단)
    pesticide_name = '해당 약제'
    for keyword in question.split():
        if len(keyword) > 2:
            pesticide_name = keyword
            break
    
    if crop_name == '알수없음' or pest_name == '알수없음':
        return {
            'ai_duration_guide': "작물명과 병해충명이 필요합니다."
        }
    
    # Excel 로드
    df = load_excel_data(crop_name, EXCEL_PATH)
    
    if df.empty:
        return {
            'ai_duration_guide': f"{crop_name} 작물 데이터가 없습니다."
        }
    
    # 해당 약제 또는 병해충 약제들의 사용적기 정보
    pest_pesticides = search_and_filter_pesticides(pest_name, [], df)
    
    usage_data = []
    for p in pest_pesticides[:10]:
        usage_data.append({
            'product_name': p['product_name'],
            'usage': p.get('usage', '')
        })
    
    # AI 프롬프트
    prompt = f"""작물: {crop_name}
병해충: {pest_name}
질문: "{question}"

[Excel 데이터 - 사용적기]
"""
    
    for i, p in enumerate(usage_data, 1):
        prompt += f"{i}. {p['product_name']}: {p['usage']}\n"
    
    prompt += f"""

분석:
1. 약제의 잔효성 정보 추출
2. 재살포 간격 정보 추출
3. {pest_name} 번식 속도 고려

⚠️ Excel에 없으면 일반론만

답변 형식:
【약효기간 분석】

【Excel 데이터 기반】
• 재살포 간격: ○일 간격 (라벨 명시)
• 적용 시기: ...
• 사용 횟수: ...

【{pest_name} 특성】
• 번식 속도: ...
• 권장 재방제: ○일 간격

【예상 약효기간】
• 잔효성: 약 ○-○일
• 다음 방제: ○일 후 재확인
"""
    
    ai_duration_guide = call_ai_reasoning(prompt, max_tokens=500)
    
    return {
        'ai_duration_guide': ai_duration_guide
    }


def _prepare_no_registration_data(context):
    """유형 44: 미등록 데이터 준비"""
    
    from core import load_excel_data
    import pandas as pd
    
    crop_name = context.get('crop_name', '알수없음')
    pest_name = context.get('pest_name', '알수없음')
    
    if crop_name == '알수없음' or pest_name == '알수없음':
        return {
            'ai_alternative_guide': "작물명과 병해충명이 필요합니다."
        }
    
    # 유사 병해충 찾기
    similar_pests = []
    for main_pest, synonyms in PEST_SYNONYMS.items():
        if pest_name in main_pest or main_pest in pest_name:
            if main_pest != pest_name:
                similar_pests.append(main_pest)
    
    # 유사 작물 찾기
    similar_crops = []
    try:
        xl_file = pd.ExcelFile(EXCEL_PATH)
        all_crops = xl_file.sheet_names
        
        for crop in all_crops:
            if crop_name in crop or crop in crop_name:
                if crop != crop_name:
                    similar_crops.append(crop)
    except:
        pass
    
    # AI 프롬프트
    prompt = f"""등록 약제 없음
요청: {crop_name} - {pest_name}
결과: 등록 약제 0개

[유사 병해충]
{', '.join(similar_pests[:5]) if similar_pests else '없음'}

[유사 작물]
{', '.join(similar_crops[:5]) if similar_crops else '없음'}

분석:
1. 병해충명 오인식 가능성
2. 유사 병해충 제안
3. 유사 작물 약제 활용 가능성

⚠️ Excel에 있는 것만 제안

답변 형식:
【등록 약제 없음】
{crop_name} - {pest_name} 조합 미등록

【가능성 1: 병해충명 확인】
유사한 이름으로 등록된 것:
• "..." → "..." (○개)

혹시 이것들을 찾으셨나요?

【가능성 2: 유사 작물 약제】
{crop_name}과 유사한 작물:
• ... (○개 약제)

→ 농약사 상담 시 유사 작물 약제 사용 가능 여부 확인

⚠️ 반드시 전문가 확인 후 사용
"""
    
    ai_alternative_guide = call_ai_reasoning(prompt, max_tokens=500)
    
    return {
        'ai_alternative_guide': ai_alternative_guide
    }


def _prepare_complex_situation_data(context):
    """유형 45: 복잡 상황 데이터 준비 (단정 금지)"""
    
    question = context['question']
    crop_name = context.get('crop_name', '알수없음')
    pest_name = context.get('pest_name', '알수없음')
    
    # 상황 요소들 수집
    pests = _extract_all_pests(question)
    growth_stage = _extract_growth_stage(question)
    
    spray_history = context.get('spray_history', [])
    last_spray = spray_history[0] if spray_history else None
    
    hours = last_spray.get('hours_ago', 0) if last_spray else 999
    
    # 날씨 정보
    q_lower = question.lower()
    weather_keywords = []
    if '비' in q_lower or '비온' in q_lower:
        weather_keywords.append('비 예보')
    if '바람' in q_lower or '강풍' in q_lower:
        weather_keywords.append('바람 강함')
    if '더워' in q_lower or '고온' in q_lower:
        weather_keywords.append('고온')
    
    # AI 프롬프트 (단정 금지)
    prompt = f"""당신은 농업 AI 보조입니다. 다음 복잡한 상황을 분석하되, 절대 단정적으로 답변하지 마세요.

【상황】
- 작물: {crop_name}
- 병해충: {', '.join(pests) if pests else pest_name}
- 생육단계: {growth_stage or '확인 필요'}
- 최근 방제: {hours:.1f}시간 전
- 날씨: {', '.join(weather_keywords) if weather_keywords else '정보 없음'}
- 농민 우려: "{question}"

【분석 원칙】
1. 단정 금지: "~해야 합니다" (X) → "~를 고려할 수 있습니다" (O)
2. 가능성 표현: "~일 수 있습니다", "~가능성이 있습니다"
3. 전문가 확인 필수: 모든 제안에 "전문가 확인 필요" 명시
4. 우선순위만 제시: "이것이 정답"이 아닌 "이것을 먼저 고려"
5. 위험 경고: 확실하지 않은 것은 명확히 경고

【답변 형식】
【상황 정리】
• (객관적 사실만)

【고려사항】
1. ...를 고려할 수 있습니다
2. ...가능성이 있습니다

【우선순위 제안】 (참고용)
1순위: ... 확인
2순위: ... 고려 가능
3순위: ... 검토 가능

⚠️ 이는 참고 의견일 뿐이며,
최종 결정은 전문가 확인 후 내려야 합니다.

답변:
"""
    
    ai_analysis = call_ai_reasoning(prompt, max_tokens=800)
    
    # 단정 표현 필터링 (2차 안전장치)
    forbidden_phrases = [
        "해야 합니다", "하세요", "하십시오",
        "이것이 정답", "확실합니다", "틀림없습니다",
        "반드시 이렇게", "무조건"
    ]
    
    for phrase in forbidden_phrases:
        if phrase in ai_analysis:
            logger.warning(f"⚠️ 단정 표현 감지: {phrase}")
            ai_analysis = ai_analysis.replace(phrase, "[전문가 확인 필요]")
    
    return {
        'ai_analysis': ai_analysis
    }

def _prepare_growth_stage_data(context):
    """유형 46: 생육단계별 방제 데이터 준비 (모든 작물)"""
    
    from core import load_excel_data
    
    question = context['question']
    crop_name = context.get('crop_name', '알수없음')
    pest_name = context.get('pest_name', '알수없음')
    
    # 생육단계 정보 추출
    stage_info = _extract_growth_stage_info(question, context, crop_name)
    
    # Excel 로드
    df = load_excel_data(crop_name, EXCEL_PATH)
    
    if df.empty:
        return {
            'cluster_analysis': f"{crop_name} 작물 데이터를 불러올 수 없습니다.",
            'growth_stage': '확인필요',
            'growth_stage_guide': "",
            'pest_specific_section': "",
            'safety_warning': "",
            'nutrition_guide': ""
        }
    
    # 병해충 검색
    spray_history = context.get('spray_history', [])
    pesticides = search_and_filter_pesticides(pest_name, spray_history, df) if pest_name != '알수없음' else []
    
    # AI 프롬프트 - 작물별 생육단계 분석
    prompt = f"""당신은 {crop_name} 재배 전문가입니다.

【현재 상황】
- 작물: {crop_name}
- 농민 질문: "{question}"
- 생육단계: {stage_info['stage'] or '명시 안됨'}
- 현재 월: {stage_info['current_month']}월
- 병해충: {pest_name}

【{crop_name} 생육단계별 특성】

작물마다 생육단계의 특성이 다릅니다. {crop_name}의 경우:
- 주요 생육단계와 그 특징
- 각 단계별 주요 관리 포인트
- 시기별 주요 병해충

【답변 형식】

【생육단계 분석】
(현재 질문에서 파악된 생육단계 정리)

【생육단계별 가이드】
- 현재 예상 단계: ...
- 주요 고려사항:
  1. 안전간격: ...
  2. 주요 관리: ...
  3. 환경 관리: ...

【병해충 방제 전략】
- {pest_name}의 특성 (병해충명이 있는 경우)
- 현 시기 방제 포인트
- 주의사항

【안전간격 경고】
(수확 관련 단계이면 반드시 명시)

【영양 관리】
(생육단계별 영양 요구도)

답변:
"""
    
    ai_analysis = call_ai_reasoning(prompt, max_tokens=800)
    
    # AI 답변을 파싱해서 각 섹션 추출
    cluster_analysis = ""
    growth_stage_guide = ""
    pest_strategy = ""
    safety_warning = ""
    nutrition_guide = ""
    
    # 간단한 파싱
    if "【생육단계 분석】" in ai_analysis:
        cluster_analysis = ai_analysis.split("【생육단계 분석】")[1].split("【")[0].strip()
    elif "【단계 분석】" in ai_analysis:
        cluster_analysis = ai_analysis.split("【단계 분석】")[1].split("【")[0].strip()
    
    if "【생육단계별 가이드】" in ai_analysis:
        growth_stage_guide = ai_analysis.split("【생육단계별 가이드】")[1].split("【")[0].strip()
    
    if "【병해충 방제 전략】" in ai_analysis:
        pest_strategy = ai_analysis.split("【병해충 방제 전략】")[1].split("【")[0].strip()
    
    if "【안전간격 경고】" in ai_analysis:
        safety_warning = ai_analysis.split("【안전간격 경고】")[1].split("【")[0].strip()
    
    if "【영양 관리】" in ai_analysis:
        nutrition_guide = ai_analysis.split("【영양 관리】")[1].split("【")[0].strip() if "【영양 관리】" in ai_analysis else ai_analysis.split("【영양 관리】")[1].strip()
    
    # 파싱 실패 시 전체를 cluster_analysis에
    if not cluster_analysis and not growth_stage_guide:
        cluster_analysis = ai_analysis
    
    # 약제 리스트 포맷팅
    exclude_history = spray_history[:3] if spray_history else []
    
    # exclude_notice 생성
    if exclude_history:
        exclude_notice = "※ 최근 3회 사용 성분은 자동으로 제외되었습니다."
    else:
        exclude_notice = ""
    
    pesticides_list = _format_pesticides_list(pesticides, pest_name) if pesticides else "❌ 등록된 약제가 없습니다."
    
    # 병해충명 유무에 따른 섹션 생성
    if pest_name == '알수없음' or not pesticides:
        # 병해충명 없음 → 구체적 정보 요청
        pest_specific_section = f"""【구체적인 병해충명이 필요합니다】

현재 일반적인 생육단계 관리 정보만 제공 가능합니다.
약제 추천을 받으려면 구체적인 병해충명을 알려주세요.

【다음처럼 질문해주세요】

✅ 좋은 질문 예시:
• "{crop_name} {stage_info['stage'] or '생육단계'} 응애 약 추천"
• "{crop_name} {stage_info['stage'] or '생육단계'} 잿빛곰팡이"
• "{crop_name} {stage_info['stage'] or '생육단계'} 진딧물"
• "{crop_name} {stage_info['stage'] or '생육단계'} 흰가루병"

【{stage_info['current_month']}월 주의 병해충】
"""
        # 시기별 주요 병해충 안내
        if stage_info['current_month'] in [12, 1, 2]:
            pest_specific_section += """• 잿빛곰팡이병 (저온다습)
• 흰가루병
• 응애류"""
        elif stage_info['current_month'] in [3, 4, 5]:
            pest_specific_section += """• 응애류 (온도 상승)
• 진딧물
• 총채벌레"""
        elif stage_info['current_month'] in [6, 7, 8]:
            pest_specific_section += """• 응애류
• 진딧물
• 나방류"""
        else:
            pest_specific_section += """• 응애류
• 진딧물
• 흰가루병"""
            
        pest_specific_section += f"""

💡 증상이 확실하지 않다면:
→ {CONTACTS['tech_center_name']}({CONTACTS['tech_center']}) 상담"""
        
    else:
        # 병해충명 있음 → 약제 추천
        pest_specific_section = f"""【병해충 방제 전략】
• 대상 병해충: {pest_name}

{pest_strategy}

━━━━━━━━━━━━━━━━━━━━━
【추천 약제】 (총 {len(pesticides)}개)
{exclude_notice}

{pesticides_list}"""
    
    return {
        'crop_name': crop_name,
        'growth_stage': stage_info['stage'] or '확인필요',
        'estimated_stage': stage_info.get('estimated_stage', ''),
        'current_month': stage_info['current_month'],
        'cluster_analysis': cluster_analysis or f"{crop_name} 생육단계 정보를 파악하기 어렵습니다.",
        'growth_stage_guide': growth_stage_guide or "생육 단계를 더 구체적으로 알려주세요.",
        'pest_specific_section': pest_specific_section,
        'safety_warning': safety_warning or "수확 관련 단계라면 안전간격을 반드시 확인하세요.",
        'nutrition_guide': nutrition_guide or "생육단계별 영양 관리는 기술센터에 문의하세요.",
    }


def _extract_growth_stage_info(question, context, crop_name):
    """생육단계 정보 추출 (모든 작물)"""
    q_lower = question.lower()
    
    # 생육단계 추출
    stage = None
    if crop_name in CROP_GROWTH_KEYWORDS:
        for keyword in CROP_GROWTH_KEYWORDS[crop_name]:
            if keyword in q_lower or keyword in question:
                stage = keyword
                break
    
    # 현재 월
    current_month = datetime.now().month
    
    # 작물별 예상 단계 (간단한 버전)
    estimated_stage = ""
    if crop_name == '딸기':
        if current_month in [12, 1]:
            estimated_stage = "1화방 수확중, 2화방 개화중"
        elif current_month in [2]:
            estimated_stage = "1화방 수확완료, 2화방 착과중"
        elif current_month in [3, 4]:
            estimated_stage = "2화방 수확중, 3,4화방 관리"
        elif current_month in [5]:
            estimated_stage = "후기 관리, 연속 수확"
    elif crop_name == '감귤':
        if current_month in [4, 5]:
            estimated_stage = "개화기"
        elif current_month in [6, 7]:
            estimated_stage = "착과기, 생리낙과기"
        elif current_month in [8, 9, 10]:
            estimated_stage = "비대기, 착색기"
        elif current_month in [11, 12, 1, 2]:
            estimated_stage = "수확기, 월동기"
    elif crop_name == '고추':
        if current_month in [4, 5]:
            estimated_stage = "정식기, 활착기"
        elif current_month in [6, 7]:
            estimated_stage = "개화기, 착과기"
        elif current_month in [7, 8, 9, 10]:
            estimated_stage = "수확기"
    # 다른 작물들도 추가 가능
    
    return {
        'stage': stage,
        'estimated_stage': estimated_stage,
        'current_month': current_month
    }

    """유형 46: 딸기 화방별 방제 데이터 준비"""
    
    from core import load_excel_data
    
    question = context['question']
    crop_name = context.get('crop_name', '딸기')
    pest_name = context.get('pest_name', '알수없음')
    
    # 화방 정보 추출
    cluster_info = _extract_flower_cluster_info(question, context)
    
    # Excel 로드
    df = load_excel_data(crop_name, EXCEL_PATH)
    
    if df.empty:
        return {
            'cluster_analysis': "딸기 작물 데이터를 불러올 수 없습니다.",
            'growth_stage_guide': "",
            'pest_strategy': "",
            'pesticides_list': "",
            'pesticide_count': 0,
            'safety_warning': "",
            'nutrition_guide': ""
        }
    
    # 병해충 검색
    spray_history = context.get('spray_history', [])
    pesticides = search_and_filter_pesticides(pest_name, spray_history, df) if pest_name != '알수없음' else []
    
    # AI 프롬프트 - 화방별 분석
    prompt = f"""당신은 딸기 재배 전문가입니다.

【현재 상황】
- 농민 질문: "{question}"
- 화방 번호: {cluster_info['cluster_num'] or '명시 안됨'}
- 화방 상태: {cluster_info['cluster_state'] or '추정 필요'}
- 현재 월: {cluster_info['current_month']}월
- 시기 추정: {cluster_info['estimated_stage']}
- 병해충: {pest_name}

【딸기 화방별 특성 (필수 적용)】

▶ 1화방 특성:
- 착과수: 9-10개 (최대)
- 과중/당도가 가장 높음
- 수세 소모가 큼
- 과다착과 시 뿌리 손상 → 2화방 영향

▶ 2화방 특성:
- 착과수: 6개 권장
- 1화방 수세 영향 받음
- 영양상태 취약기
- 12-1월: 개화기 (저온다습)
- 2-3월: 착과·비대기

▶ 3-4화방 이후:
- 착과수 점점 감소 (4개, 3개)
- 연속 착과로 수세 약화
- 병 저항성 낮아짐

【시기별 주의사항】

▶ 12-1월 (1화방 수확 + 2화방 개화):
- 안전간격 짧은 약제 필수
- 잿빛곰팡이병 고위험
- 저온다습 주의

▶ 2월 (2화방 착과·비대):
- 수세 회복 중요
- 응애류 발생 시작
- 흰가루병 증가

▶ 3-5월 (연속 수확):
- 안전간격 최우선
- 친환경 자재 병행
- 수세 지속 관리

【답변 형식】

【화방 상황 분석】
(현재 질문에서 파악된 화방 상태 정리)

【생육단계별 가이드】
- 현재 예상 단계: ...
- 주요 고려사항:
  1. 안전간격: ...
  2. 다음 화방: ...
  3. 수세 관리: ...

【병해충 방제 전략】
- {pest_name}의 특성
- 현 시기 방제 포인트
- 주의사항

【안전간격 경고】
(수확 중이면 반드시 명시)

【영양 관리】
(화방별 영양 요구도)

답변:
"""
    
    ai_analysis = call_ai_reasoning(prompt, max_tokens=800)
    
    # AI 답변을 파싱해서 각 섹션 추출
    cluster_analysis = ""
    growth_stage_guide = ""
    pest_strategy = ""
    safety_warning = ""
    nutrition_guide = ""
    
    # 간단한 파싱 (AI 답변을 섹션별로 나누기)
    if "【화방 상황 분석】" in ai_analysis:
        cluster_analysis = ai_analysis.split("【화방 상황 분석】")[1].split("【")[0].strip()
    
    if "【생육단계별 가이드】" in ai_analysis:
        growth_stage_guide = ai_analysis.split("【생육단계별 가이드】")[1].split("【")[0].strip()
    
    if "【병해충 방제 전략】" in ai_analysis:
        pest_strategy = ai_analysis.split("【병해충 방제 전략】")[1].split("【")[0].strip()
    
    if "【안전간격 경고】" in ai_analysis:
        safety_warning = ai_analysis.split("【안전간격 경고】")[1].split("【")[0].strip()
    
    if "【영양 관리】" in ai_analysis:
        nutrition_guide = ai_analysis.split("【영양 관리】")[1].split("【")[0].strip() if "【영양 관리】" in ai_analysis else ai_analysis.split("【영양 관리】")[1].strip()
    
    # 파싱 실패 시 전체를 cluster_analysis에
    if not cluster_analysis and not growth_stage_guide:
        cluster_analysis = ai_analysis
    
    # 약제 리스트 포맷팅
    exclude_history = spray_history[:3] if spray_history else []
    
    # exclude_notice 생성
    if exclude_history:
        exclude_notice = "※ 최근 3회 사용 성분은 자동으로 제외되었습니다."
    else:
        exclude_notice = ""
    
    pesticides_list = _format_pesticides_list(pesticides, pest_name) if pesticides else "❌ 등록된 약제가 없습니다."
    
    # 병해충명 유무에 따른 섹션 생성
    if pest_name == '알수없음' or not pesticides:
        # 병해충명 없음 → 구체적 정보 요청
        pest_specific_section = f"""【구체적인 병해충명이 필요합니다】

현재 일반적인 화방 관리 정보만 제공 가능합니다.
약제 추천을 받으려면 구체적인 병해충명을 알려주세요.

【다음처럼 질문해주세요】

✅ 좋은 질문 예시:
• "딸기 {cluster_info['cluster_num'] or '1'}화방 응애 약 추천"
• "딸기 {cluster_info['cluster_num'] or '2'}화방 개화기 잿빛곰팡이"
• "딸기 {cluster_info['cluster_num'] or '1'}화방 수확중 흰가루병"
• "딸기 {cluster_info['cluster_num'] or '2'}화방 착과기 진딧물"

【{cluster_info['current_month']}월 주의 병해충】
"""
        # 시기별 주요 병해충 안내
        if cluster_info['current_month'] in [12, 1]:
            pest_specific_section += """• 잿빛곰팡이병 (저온다습)
• 흰가루병
• 응애류"""
        elif cluster_info['current_month'] in [2, 3]:
            pest_specific_section += """• 응애류 (온도 상승)
• 흰가루병
• 진딧물"""
        elif cluster_info['current_month'] in [4, 5]:
            pest_specific_section += """• 진딧물
• 총채벌레
• 잿빛곰팡이병"""
        else:
            pest_specific_section += """• 응애류
• 진딧물
• 흰가루병"""
            
        pest_specific_section += f"""

💡 증상이 확실하지 않다면:
→ {CONTACTS['tech_center_name']}({CONTACTS['tech_center']}) 상담"""
        
    else:
        # 병해충명 있음 → 약제 추천
        pest_specific_section = f"""【병해충 방제 전략】
• 대상 병해충: {pest_name}

{pest_strategy}

━━━━━━━━━━━━━━━━━━━━━
【추천 약제】 (총 {len(pesticides)}개)
{exclude_notice}

{pesticides_list}"""
    
    return {
        'cluster_num': cluster_info['cluster_num'] or '확인필요',
        'cluster_state': cluster_info['cluster_state'] or '추정필요',
        'estimated_stage': cluster_info['estimated_stage'],
        'current_month': cluster_info['current_month'],
        'cluster_analysis': cluster_analysis or "화방 정보를 파악하기 어렵습니다.",
        'growth_stage_guide': growth_stage_guide or "생육 단계를 더 구체적으로 알려주세요.",
        'pest_specific_section': pest_specific_section,
        'safety_warning': safety_warning or "수확 중이라면 안전간격을 반드시 확인하세요.",
        'nutrition_guide': nutrition_guide or "화방별 영양 관리는 기술센터에 문의하세요.",
    }

# ================================================================
# 【복붙 위치】 answer_logic.py 맨 아래
#   ★ v5 RAG 블록 전체를 지우고 이걸로 교체.
#     (지우는 범위: "def rag_classify_intent" ~ "def answer_question_rag" 끝까지)
# ----------------------------------------------------------------
# RAG v6 — 4대 수정
#   (1) product_info 의도 신규: "인시피오 효과 어때?" → 추천 5개가 아니라
#       그 약제 하나의 객관 사실(성분·함량·제형·희석·회사·적용병해충)만. 효과 평가 금지.
#   (2) 병명 화이트리스트: 진단 시 ① 코드가 작물 엑셀의 실제 병명목록을 뽑아 프롬프트에 주입
#       (젬마는 그 목록에서만 의심병명 선택) ② 답변 후 ○○병을 추출해 목록에 없으면 문장 제거
#       → "잎도마도병" 같은 창작 병명 원천 박멸
#   (3) 혼용 강화: mix 의도는 권장하지 않고 "라벨/농약사 확인" 명확히 안내
#   (4) 성분 지정 시 recommend 강제: "흰가루병 클로로탈로닐 들어간거"가 diagnose로 새서
#       약제표 못 띄우던 문제 → 성분 지정 있으면 무조건 recommend
#
# ★ 재사용: CROP_SYNONYMS, PEST_SYNONYMS, PRIORITY_PESTICIDES, MANDATORY_NOTICES, CONTACTS,
#    DB_PATH, EXCEL_PATH, _extract_crop_from_question, _extract_pest_from_question,
#    search_and_filter_pesticides, _format_pesticides_list, call_ai_reasoning,
#    load_excel_data, normalize_agricultural_terms, logger
# ================================================================

# ----- 약제명 감지 (product_info 의도용) -----
def rag_detect_product_query(question):
    """질문에 등록 약제명 + 정보/효과 질문이 있으면 그 약제명 반환."""
    ql = question.replace(' ', '')
    info_kw = ['효과', '어때', '어떄', '어떤가', '성분', '뭐야', '뭔지', '정보', '알려', '함량', '제형', '희석', '괜찮','좋아']
    if not any(k in ql for k in info_kw):
        return None
    flat = []
    for v in PRIORITY_PESTICIDES.values():
        flat += v
    for name in sorted(set(flat), key=len, reverse=True):
        if name in question:
            return name
    return None


# ----- 의도 분류 -----
def rag_classify_intent(question):
    ql = question.lower().replace(' ', '')
    # ★ product_info 최우선 (특정 약제 정보/효과 질문)
    if rag_detect_product_query(question):
        return 'product_info'
    if any(k in ql for k in ['언제쳤', '뭐뿌렸', '쳤더라', '쳤었지', '기록', '이력', '며칠', '횟수', '몇번', '얼마나']):
        return 'history'
    if any(k in ql for k in ['섞어', '혼용', '같이써', '같이뿌', '함께뿌', '함께써', '같이쳐', '섞을']):
        return 'mix'
    if any(k in ql for k in ['희석', '몇배', '물몇', '수확전', '안전사용', '최대횟수', '안전기준']):
        return 'safety'
    if any(k in ql for k in ['언제쳐', '언제뿌려', '언제사용', '사용시기', '적기', '언제가능', '시기']):
        return 'timing'
    pest_req_kw = ['약', '추천', '방제', '농약', '살포', '치료', '살충', '살균']
    has_symptom = any(k in ql for k in ['왜', '원인', '이유', '무슨병', '뭐가문제', '노랗', '갈색', '점생', '점이',
                                        '시들', '반점', '무늬', '끈적', '곰팡', '가루', '발생하는', '생겼', '변색',
                                        '뭔병', '무슨병이', '번지', '누런'])
    if has_symptom and not any(k in ql for k in pest_req_kw):
        return 'diagnose'
    if any(k in ql for k in pest_req_kw + ['잡', '죽이', '조치', '어떻게', '뭐쳐', '뭐써']):
        return 'recommend'
    return 'general'


# ----- 작물명 떼고 병해충 추출 -----
def rag_extract_pest_clean(question, crop):
    import re
    q = normalize_agricultural_terms(question)
    if crop:
        names = [crop]
        for main, syns in CROP_SYNONYMS.items():
            if crop == main or crop in syns:
                names += [main] + syns
        for nm in sorted(set(names), key=len, reverse=True):
            if nm:
                q = q.replace(nm, ' ')
    for main_pest, syns in PEST_SYNONYMS.items():
        for s in syns:
            if s in q:
                return s
    for pat in [r'([가-힣]+진딧물)', r'([가-힣]+응애)', r'([가-힣]+나방)',
                r'([가-힣]+가루이)', r'([가-힣]+총채[벌레]*)', r'([가-힣]+깍지벌레)',
                r'([가-힣]+노린재)', r'([가-힣]+매미충)', r'([가-힣]+선녀벌레)']:
        m = re.findall(pat, q)
        if m:
            return m[0]
    invalid = ['어떤병', '무슨병', '이런병', '그런병', '모든병', '이병', '발병', '질병', '무병']
    diseases = re.findall(r'([가-힣]{1,}병)', q)
    valid = [d for d in diseases if 2 <= len(d) <= 6 and d not in invalid]
    if valid:
        return min(valid, key=len)
    return None


# ----- 질문에서 성분명 추출 -----
def rag_extract_ingredient(question):
    import re
    m = re.search(r'([가-힣A-Za-z]{3,})\s*(?:성분|계열|계통|들어간|함유|든)', question)
    if m:
        cand = m.group(1).strip()
        bad = ['무슨', '어떤', '이런', '그런', '다른', '같은', '해당', '특정']
        if cand and cand not in bad and not cand.endswith('병'):
            return cand
    return None


# ----- 성분으로 약제 2차 필터 -----
def rag_filter_by_ingredient(pesticides, ingredient):
    if not ingredient or not pesticides:
        return pesticides
    key = ingredient.replace(' ', '').lower()
    out = []
    for p in pesticides:
        ing = str(p.get('ingredient', '')).replace(' ', '').lower()
        ing2 = str(p.get('ingredient_pure', '')).replace(' ', '').lower()
        if key in ing or key in ing2:
            out.append(p)
    return out


# ----- nan/None 정리 -----
def rag_clean_pesticide_values(pesticides):
    for p in pesticides:
        for k, v in list(p.items()):
            sv = str(v).strip()
            if sv in ('nan', 'None', 'NaN', ''):
                p[k] = '해당없음' if k in ('dilution', 'content', 'safety', 'usage') else ''
    return pesticides


# ----- ★ v6 신규: 작물 엑셀에서 실제 병명 목록 추출 (병명 화이트리스트) -----
def rag_get_crop_diseases(df, top_n=25):
    """현재 작물 시트의 적용병해충 중 '병'으로 끝나는 실제 병명을 빈도순으로."""
    from collections import Counter
    if df is None or df.empty or '적용병해충' not in df.columns:
        return []
    c = Counter()
    for v in df['적용병해충'].dropna().astype(str):
        name = v.strip()
        # 괄호 부가설명 제거: "잿빛곰팡이병(전착효과)" → "잿빛곰팡이병"
        name = name.split('(')[0].strip()
        if name.endswith('병'):
            c[name] += 1
    return [name for name, _ in c.most_common(top_n)]


# ----- ★ v6 신규: 특정 약제 1개의 객관 정보 조회 (product_info용) -----
def rag_find_product(df, product_name):
    """상표명으로 약제를 찾아 객관 정보 반환. 같은 약제 여러 행이면 적용병해충 합침."""
    if df is None or df.empty or '상표명' not in df.columns:
        return None
    m = df[df['상표명'].astype(str).str.contains(product_name, na=False)]
    if m.empty:
        return None
    r = m.iloc[0]
    pests = sorted({str(x).strip() for x in m['적용병해충'].dropna().astype(str)})
    info = {
        'product_name': str(r.get('상표명', '')),
        'ingredient': str(r.get('품목명', '')),
        'content': str(r.get('주성분함량', '')),
        'formulation': str(r.get('제형', '')),
        'company': str(r.get('회사명', '')),
        'dilution': str(r.get('희석배수', '')),
        'pest_disease': ', '.join(pests) if pests else str(r.get('적용병해충', '')),
    }
    for k, v in list(info.items()):
        if str(v).strip() in ('nan', 'None', 'NaN', ''):
            info[k] = '해당없음'
    return info


# ----- 사실 검색 (Zone A) -----
def rag_retrieve_facts(question, phone, intent):
    from core import get_farm_info, get_spray_history
    facts = {'crop': None, 'pest': None, 'intent': intent, 'crop_source': 'none',
             'pesticides': [], 'recent_spray': None, 'history': [],
             'crop_products': set(), 'cultivation_type': '노지',
             'ingredient_query': None, 'eco_request': False,
             'crop_diseases': [], 'product_query': None, 'product_info': None,
             'ingredient_no_match': False}

    farm = get_farm_info(phone, DB_PATH) if phone else None
    if farm:
        facts['cultivation_type'] = farm.get('cultivation_type', '노지') or '노지'

    if any(k in question.replace(' ', '') for k in ['친환경', '유기농', '천연', '무농약', '저독성']):
        facts['eco_request'] = True

    skip_extract = intent in ('mix', 'history')

    # 작물 결정
    crop = None
    if not skip_extract:
        crop = _extract_crop_from_question(question)
        if crop:
            facts['crop_source'] = 'question'
        elif farm and farm.get('crop'):
            crop = farm['crop']
            for main, syns in CROP_SYNONYMS.items():
                if crop == main or crop in syns:
                    crop = main
                    break
            facts['crop_source'] = 'farm'
        facts['crop'] = crop
        facts['pest'] = rag_extract_pest_clean(question, crop)
        facts['ingredient_query'] = rag_extract_ingredient(question)

    # 최근 방제 (작물 일치 시만)
    history = get_spray_history(phone, 90, DB_PATH) if phone else []
    if history:
        facts['history'] = history[:5]
        last = history[0]
        last_crop = (last.get('crop') or '').strip()
        if last_crop:
            for main, syns in CROP_SYNONYMS.items():
                if last_crop == main or last_crop in syns:
                    last_crop = main
                    break
        if facts['crop'] and last_crop and last_crop == facts['crop']:
            facts['recent_spray'] = last
        else:
            facts['recent_spray'] = None

    # 엑셀 로드가 필요한 의도들
    if intent in ('recommend', 'safety', 'timing', 'diagnose', 'product_info') and facts['crop']:
        df = load_excel_data(facts['crop'], EXCEL_PATH)
        if df is not None and not df.empty:
            try:
                if '상표명' in df.columns:
                    facts['crop_products'] = {
                        str(v).strip() for v in df['상표명'].dropna().astype(str) if len(str(v).strip()) >= 3
                    }
            except Exception:
                pass

            # ★ 진단용 병명 화이트리스트
            if intent == 'diagnose':
                facts['crop_diseases'] = rag_get_crop_diseases(df)

            # ★ product_info: 특정 약제 객관 정보
            if intent == 'product_info':
                pq = rag_detect_product_query(question)
                facts['product_query'] = pq
                if pq:
                    facts['product_info'] = rag_find_product(df, pq)

            # 약제 검색 (병해충 있을 때)
            if facts['pest']:
                found = search_and_filter_pesticides(facts['pest'], history[:3], df)
                if facts['ingredient_query']:
                    before = len(found)
                    found = rag_filter_by_ingredient(found, facts['ingredient_query'])
                    logger.info(f"[RAG] 🧪 성분필터 '{facts['ingredient_query']}': {before}개 → {len(found)}개")
                    # ★ 성분 지정했는데 0개 = 그 병해충엔 그 성분이 등록 안 됨
                    if before > 0 and len(found) == 0:
                        facts['ingredient_no_match'] = True
                facts['pesticides'] = rag_clean_pesticide_values(found)

    return facts


# ----- 프롬프트 -----
def rag_build_prompt(facts, question, intent):
    crop = facts['crop'] or '미상'
    pest = facts['pest'] or '미상'
    has_pest_list = bool(facts['pesticides'])

    rs = facts['recent_spray']
    recent_txt = ""
    if rs:
        recent_txt = (f"- 최근 방제: {rs.get('spray_date','')} / {rs.get('pest_name','')} / "
                      f"{rs.get('pesticide_name','')} ({rs.get('hours_ago','?')}시간 전)\n")

    crop_caveat = ""
    if facts['crop_source'] == 'farm':
        crop_caveat = ("[주의] 작물명은 질문에 없어 가입정보로 추정했다. 단정하지 말고 "
                       "'등록하신 작물 기준' 정도로 부드럽게 표현하라.\n")

    pest_status = ("- 등록 약제: 시스템이 표로 별도 표시함(너는 약제 제품명을 나열하지 마라)\n"
                   if has_pest_list else "- 등록 약제: 없음(약제 제품명을 만들지 말 것)\n")

    eco_line = ""
    if facts.get('eco_request'):
        eco_line = ("[참고] 사용자가 친환경/유기농을 원하나 등록 약제는 일반 화학약제 위주다. "
                    "친환경 자재만 따로 구분해 제공하기 어렵다는 점을 한 문장으로 솔직히 알리고, "
                    "통풍·예방 등 비약제 관리를 함께 안내하라. 친환경 제품명을 지어내지 마라.\n")

    hard_rules = (
        "★★ 절대 규칙 ★★\n"
        "1) 약제 제품명·성분명·희석배수·효과를 절대 지어내지 마라. '표로 제공된 약제'만 실재한다.\n"
        "2) 표(|)나 마크다운 표를 그리지 마라. 'OOO','[제품명]' 같은 빈칸/예시도 쓰지 마라.\n"
        "3) 번호(1. 2. 3.)·불릿(•)·별표(**)를 쓰지 말고 자연스러운 문단으로 써라.\n"
        "4) 모르는 정보는 추측 말고 '확인이 필요하다'고만 하라.\n\n"
    )
    common_tone = "- 질문의 작물·증상에 맞춰 구체적으로, 상투구는 피하라.\n"

    # product_info 전용 (객관 사실, 평가 금지)
    if intent == 'product_info':
        pinfo = facts.get('product_info')
        pq = facts.get('product_query') or '해당 약제'
        if pinfo:
            data_block = (f"[{pq} 등록 정보]\n"
                          f"- 상표명: {pinfo['product_name']}\n"
                          f"- 성분(품목명): {pinfo['ingredient']}\n"
                          f"- 주성분함량: {pinfo['content']}\n"
                          f"- 제형: {pinfo['formulation']}\n"
                          f"- 희석배수: {pinfo['dilution']}\n"
                          f"- 등록 적용병해충: {pinfo['pest_disease']}\n"
                          f"- 회사: {pinfo['company']}\n")
            guide = ("[작성 지시]\n"
                     f"사용자가 '{pq}'의 효과/정보를 물었다. 위 등록 정보를 바탕으로 그 약제가 어떤 약인지 "
                     "객관적 사실로만 설명하라(성분·함량·제형·등록된 적용 병해충). "
                     "★'효과가 좋다/나쁘다', '추천한다' 같은 평가는 절대 하지 마라. "
                     "등록된 적용 병해충 범위만 사실대로 전하고, 구체 희석·사용법은 라벨 확인으로 안내하라.\n"
                     + common_tone)
        else:
            data_block = f"[정보] '{pq}' 약제를 {crop} 등록 데이터에서 찾지 못함\n"
            guide = ("[작성 지시]\n"
                     f"'{pq}' 약제를 현재 작물({crop}) 등록 데이터에서 찾지 못했다. "
                     "정보를 지어내지 말고, 작물이 맞는지 확인하거나 농약사에 문의하라고 안내하라.\n" + common_tone)
        return hard_rules + f"[의도] {intent}\n\n" + data_block + f"\n[사용자 질문]\n{question}\n\n" + guide

    # 진단 병명 화이트리스트 주입
    if intent == 'diagnose':
        dz = facts.get('crop_diseases', [])
        if dz:
            disease_line = ("[이 작물에 '실제로 등록된' 병해충 목록 — 의심 병명은 반드시 이 안에서만 골라라]\n"
                            f"{', '.join(dz)}\n"
                            "★위 목록에 없는 병명은 절대 만들어내지 마라. 목록 밖 병명을 쓰면 안 된다.\n")
        else:
            disease_line = "★병명을 함부로 단정하지 말고, 확실하지 않으면 여러 원인이 가능하다고만 하라. 없는 병명 창작 금지.\n"

        if has_pest_list:
            drug_line = ("아래 표로 '엑셀 등록 약제'가 제공되니, 가장 의심되는 병해충에 그 약제를 쓸 수 있다고 "
                         "한 문장으로 연결하라(제품명 나열 금지, '아래 표의 등록 약제'로 지칭).\n")
        else:
            drug_line = ("★등록 약제 정보가 없으므로 '아래 표','약제 사용' 표현을 쓰지 마라. "
                         "'정확한 병명 확인 후 약제를 선택해야 한다'고만 안내하라.\n")

        guide = ("[작성 지시]\n" + disease_line +
                 "위 목록 중 증상에 맞는 의심 병명을 1~3개 고르고 구분 포인트를 간단히 설명한 뒤, "
                 "즉시 할 수 있는 환경관리 조치를 2~3문장 안내하라.\n" + drug_line + eco_line +
                 "확정 진단은 현장 확인이 필요함을 마지막에 덧붙여라.\n" + common_tone)
        data_block = (f"[확정 데이터]\n- 작물: {crop}\n- 병해충: {pest}\n" + pest_status + recent_txt + crop_caveat)
        return hard_rules + f"[의도] {intent}\n\n" + data_block + f"\n[사용자 질문]\n{question}\n\n" + guide

    # 나머지 의도
    if has_pest_list:
        rec_drug_line = "약제 제품명은 쓰지 마라(아래 표로 보여준다).\n"
    elif facts.get('ingredient_no_match'):
        iq = facts.get('ingredient_query', '해당 성분')
        rec_drug_line = (f"★중요: '{pest}'에는 '{iq}' 성분으로 등록된 약제가 데이터에 없다. "
                         f"'{iq}' 성분 약제가 {pest}에 등록돼 있지 않다는 사실을 분명히 알리고, "
                         "그 성분이 이 병해충에 맞지 않을 수 있으니 농약사 확인을 권하라. 약제명을 지어내지 마라.\n")
    else:
        rec_drug_line = "★등록 약제가 없으므로 약제명을 언급하지 말고, 병명 확정 후 다시 문의하라고 안내하라.\n"

    guide = {
        'recommend': ("[작성 지시]\n"
                      "이 병해충에 맞는 즉시 조치와 방제 방향을 3~4문장으로 설명하라.\n"
                      "최근 방제 이력이 있으면 저항성 관점에서 한 문장 덧붙여라(다른 계통 약제 권장).\n"
                      + rec_drug_line + eco_line + common_tone),
        'timing':  "[작성 지시] 이 병해충의 방제 적기와 살포조건을 설명하라. 약제 제품명·희석수치는 쓰지 마라.\n" + common_tone,
        'safety':  ("[작성 지시] 안전사용 핵심(희석·수확전일수·보호장비)의 중요성을 설명하라. "
                    "구체 숫자는 지어내지 말고 '라벨/표 확인'으로 안내하라.\n" + common_tone),
        # ★ v6: 혼용은 권장 안 함 + 라벨 확인
        'mix':     ("[작성 지시] 약제 혼용은 약해·침전 위험이 있어 '권장하지 않는다'는 점을 분명히 하라. "
                    "특정 조합의 가능/불가를 단정하지 말고, 반드시 각 약제 라벨의 혼용 가능 여부를 확인하거나 "
                    "농약사·농업기술센터에 문의하라고 안내하라. 굳이 해야 한다면 소량 예비혼합 테스트를 권하라. "
                    "특정 작물·잡초·조합을 멋대로 가정하지 마라.\n" + common_tone),
        'history': "[작성 지시] 위 방제기록을 요약하고 재방제 주의를 안내하라. 새 사실·약제 만들지 말 것.\n" + common_tone,
        'general': "[작성 지시] 일반 관리 방향을 안내하라. 약제 제품명·수치 단정 금지.\n" + common_tone,
    }.get(intent, "[작성 지시] 안전하게 안내하라.\n" + common_tone)

    if intent in ('mix', 'history'):
        data_block = "[확정 데이터]\n" + recent_txt
    else:
        data_block = (f"[확정 데이터]\n- 작물: {crop}\n- 병해충: {pest}\n" + pest_status + recent_txt + crop_caveat)

    return hard_rules + f"[의도] {intent}\n\n" + data_block + f"\n[사용자 질문]\n{question}\n\n" + guide


# ----- 후처리: 가짜 표/플레이스홀더 제거 -----
def rag_strip_fake_table(text):
    import re
    kept = []
    ph = ['ooo', '○○○', '△△△', '▽▽▽', '◈◈◈', 'xxx', '[제품명', '[성분', '제품명 1', '제품명 2']
    for ln in text.split('\n'):
        low = ln.lower()
        if ln.count('|') >= 2:
            continue
        if re.match(r'^\s*\|?[\s:\-]+\|', ln):
            continue
        if any(t in low for t in ph):
            continue
        kept.append(ln)
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(kept)).strip()


# ----- ★ v6 신규: 진단 답변에서 목록에 없는 가짜 병명 문장 제거 -----
def rag_strip_fake_disease(text, valid_diseases):
    """답변의 ○○병 중 작물 실제 병명목록과 안 맞는 것이 든 문장을 제거."""
    if not valid_diseases:
        return text, []
    import re
    removed = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    kept = []
    for s in sentences:
        found = re.findall(r'([가-힣]{2,}병)', s)
        bad_names = []
        for d in found:
            ok = any(d in vd or vd in d for vd in valid_diseases)
            if not ok:
                bad_names.append(d)
        if bad_names:
            removed.extend(bad_names)
            continue  # 가짜 병명 든 문장은 통째 제거
        kept.append(s)
    out = ' '.join(kept).strip()
    if removed:
        logger.info(f"[RAG] 🚫 가짜 병명 차단(엑셀 미등록): {removed}")
    return out, removed


# ----- 후처리: 미등록 약제명 차단 -----
def rag_strip_unregistered(text, facts):
    if facts['intent'] not in ('recommend', 'diagnose'):
        return text, []
    displayed = {p.get('product_name', '') for p in facts['pesticides']}
    safe = set(displayed)
    if facts.get('recent_spray'):
        rp = facts['recent_spray'].get('pesticide_name', '')
        if rp:
            safe.add(rp.strip())
    removed = []
    for prod in facts.get('crop_products', set()):
        if prod in safe:
            continue
        if prod in text:
            removed.append(prod)
            text = re.sub(r'[^.!?\n]*' + re.escape(prod) + r'[^.!?\n]*[.!?]?', '', text)
    if removed:
        logger.info(f"[RAG] 🛡️ 화이트리스트 차단(미등록 약제): {removed}")
    text = re.sub(r'[ \t]{2,}', ' ', text).strip()
    return text, removed


# ----- 약제 상세 블록 -----
def rag_pesticide_block(facts):
    if not facts['pesticides']:
        return ""
    try:
        from config import get_weather_condition
        weather = get_weather_condition(facts.get('cultivation_type', '노지'))
    except Exception:
        weather = MANDATORY_NOTICES.get('weather_condition', '')
    block = "\n💊 추천 약제 (식약처 등록 데이터)\n━━━━━━━━━━━━━━━━━━━━━\n"
    block += MANDATORY_NOTICES['safety_top'] + "\n"
    block += _format_pesticides_list(facts['pesticides'], facts['pest'])
    block += "\n" + MANDATORY_NOTICES['label_check']
    block += "\n" + weather
    block += "\n" + MANDATORY_NOTICES['effect_check']
    block += "\n" + MANDATORY_NOTICES['resistance_management']
    block += "\n" + MANDATORY_NOTICES['protection_gear']
    return block


# ----- ★ v6 신규: product_info 약제 단일 카드 -----
def rag_product_card(facts):
    pinfo = facts.get('product_info')
    if not pinfo:
        return ""
    card = "\n💊 약제 정보 (식약처 등록 데이터)\n━━━━━━━━━━━━━━━━━━━━━\n"
    card += f"• 제품명: {pinfo['product_name']}\n"
    card += f"• 성분: {pinfo['ingredient']}\n"
    card += f"• 함량: {pinfo['content']}\n"
    card += f"• 제형: {pinfo['formulation']}\n"
    card += f"• 희석배수: {pinfo['dilution']}\n"
    card += f"• 등록 적용병해충: {pinfo['pest_disease']}\n"
    card += f"• 회사: {pinfo['company']}\n"
    card += "\n" + MANDATORY_NOTICES['label_check']
    return card


# ----- 안전문구 -----
def rag_safety_block():
    return (
        "\n━━━━━━━━━━━━━━━━━━━━━\n"
        + MANDATORY_NOTICES['expert_bottom'].format(
            tech_center_name=CONTACTS['tech_center_name'], tech_center=CONTACTS['tech_center'])
        + "\n" + MANDATORY_NOTICES['legal_disclaimer']
    )


# ----- 오케스트레이터 -----
def answer_question_rag(question, phone=None):
    intent = rag_classify_intent(question)
    facts = rag_retrieve_facts(question, phone, intent)

    # ★ v6: 성분 지정이 있으면 recommend 강제 ("클로로탈로닐 들어간거"가 diagnose로 새는 것 방지)
    if intent in ('diagnose', 'general') and facts.get('ingredient_query') and facts.get('pest'):
        intent = 'recommend'
        facts['intent'] = 'recommend'
    # 병명 명시됐는데 general이면 recommend 승격
    if intent == 'general' and facts.get('pest'):
        intent = 'recommend'
        facts['intent'] = 'recommend'

    prompt = rag_build_prompt(facts, question, intent)
    raw = call_ai_reasoning(prompt, max_tokens=700)

    # 후처리: 가짜표 → (진단)가짜병명 → 미등록약제 → 별표
    guarded = rag_strip_fake_table(raw)
    if intent == 'diagnose':
        guarded, _ = rag_strip_fake_disease(guarded, facts.get('crop_diseases', []))
    guarded, removed = rag_strip_unregistered(guarded, facts)
    guarded = guarded.replace('**', '')

    final = guarded
    if intent == 'product_info':
        final += rag_product_card(facts)
    elif intent in ('recommend', 'diagnose') and facts['pesticides']:
        final += rag_pesticide_block(facts)
    final += rag_safety_block()

    logger.info(f"[RAG] 의도={intent} | 작물={facts['crop']}({facts['crop_source']}) | "
                f"병해충={facts['pest']} | 성분={facts.get('ingredient_query')} | "
                f"약제={facts.get('product_query') or len(facts['pesticides'])} | 차단={removed}")
    return final