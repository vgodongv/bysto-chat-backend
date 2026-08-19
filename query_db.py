"""
🌾 병해충 리포트 자동 파싱 및 INSERT (완성 버전)

리포트 텍스트를 자동으로 파싱하여 pest_simple 테이블에 모두 INSERT
"""

import sqlite3
import re

# 📋 리포트 텍스트
REPORT = """[주간 병해충 제7호·6.16~30]
🔴경보: 과수화상병(사과·배)
🟠주의보: 과수가지검은마름병, 갈색날개매미충·미국선녀벌레·꽃매미(과수)
🟡예보: 고추 역병·탄저·흰가루·노균병, 옥수수·벼 비래해충(열대거세미나방·멸강·애멸구), 시설채소 총채벌레·진딧물·바이러스
👉장마철 진입, 과수화상병 사전방제 필수!"""


class PestParser:
    """병해충 리포트 파서"""
    
    def __init__(self, db='bysto_farm.db'):
        self.db = db
        self.create_table()
    
    def create_table(self):
        """테이블 생성"""
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pest_simple (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_range TEXT,
                alert_level TEXT,
                pest TEXT,
                insect TEXT,
                crops TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def parse_and_insert(self, text):
        """텍스트 파싱 후 모두 INSERT"""
        
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        
        print("\n" + "="*70)
        print("🌾 병해충 리포트 자동 파싱 및 INSERT")
        print("="*70)
        
        # 1️⃣ 날짜 추출
        date_match = re.search(r'(\d+\.\d+~\d+)', text)
        date_range = date_match.group(1) if date_match else ''
        print(f"\n📅 날짜: {date_range}\n")
        
        # 2️⃣ 경보 파싱
        print("🔴 경보:")
        self._parse_section(text, '🔴경보:', '🟠|🟡|👉', date_range, '경보', cursor)
        
        # 3️⃣ 주의보 파싱
        print("\n🟠 주의보:")
        self._parse_section(text, '🟠주의보:', '🟡|👉', date_range, '주의보', cursor)
        
        # 4️⃣ 예보 파싱
        print("\n🟡 예보:")
        self._parse_section(text, '🟡예보:', '👉', date_range, '예보', cursor)
        
        # 5️⃣ 주의사항 파싱
        print("\n👉 주의사항:")
        caution_match = re.search(r'👉(.+?)$', text, re.MULTILINE | re.DOTALL)
        if caution_match:
            caution_text = caution_match.group(1).strip()
            # 콤마로 분리
            for item in caution_text.split(','):
                item = item.strip()
                if item:
                    cursor.execute('''
                        INSERT INTO pest_simple 
                        (date_range, alert_level, pest, insect, crops, summary)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (date_range, '주의', None, None, None, item))
                    print(f"  ✅ {item}")
        
        conn.commit()
        conn.close()
        
        print("\n" + "="*70)
        print("✨ 모든 데이터 저장 완료!")
        print("="*70 + "\n")
    
    def _parse_section(self, text, start_pattern, end_pattern, date_range, level, cursor):
        """각 섹션 (경보/주의보/예보) 파싱"""
        
        # 섹션 추출
        pattern = f'{re.escape(start_pattern)}\\s*(.+?)(?={end_pattern}|$)'
        match = re.search(pattern, text, re.DOTALL)
        
        if not match:
            return
        
        content = match.group(1).strip()
        
        # 콤마로 분리 (각 항목: 병해충·병해충(작물))
        items = content.split(',')
        
        for item in items:
            item = item.strip()
            if not item:
                continue
            
            # 작물 추출: (...)
            crops_match = re.search(r'\(([^)]+)\)', item)
            crops = crops_match.group(1).replace('·', ', ') if crops_match else None
            
            # 병해충/해충 추출: ()를 제외한 부분
            names_str = re.sub(r'\([^)]*\)', '', item).strip()
            
            # ·로 분리
            names = names_str.split('·')
            
            for name in names:
                name = name.strip()
                if not name:
                    continue
                
                # 병과 해충 구분
                if '병' in name or name in ['바이러스']:
                    pest = name
                    insect = None
                else:
                    pest = None
                    insect = name
                
                # INSERT
                cursor.execute('''
                    INSERT INTO pest_simple 
                    (date_range, alert_level, pest, insect, crops, summary)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (date_range, level, pest, insect, crops, None))
                
                # 화면 출력
                target = pest or insect
                if crops:
                    print(f"  ✅ {target} ({crops})")
                else:
                    print(f"  ✅ {target}")


# ===== 실행 =====

if __name__ == "__main__":
    
    # 1️⃣ 파서 생성
    parser = PestParser()
    
    # 2️⃣ 자동 파싱 및 INSERT
    parser.parse_and_insert(REPORT)
    
    # 3️⃣ 저장된 데이터 확인
    print("\n📋 저장된 데이터 확인:\n")
    
    conn = sqlite3.connect('bysto_farm.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM pest_simple ORDER BY alert_level, id')
    rows = cursor.fetchall()
    
    current_level = None
    level_emoji = {'경보': '🔴', '주의보': '🟠', '예보': '🟡', '주의': '👉'}
    
    for row in rows:
        level = row['alert_level']
        
        if level != current_level:
            current_level = level
            emoji = level_emoji.get(level, '•')
            print(f"{emoji} {level}:")
        
        target = row['pest'] or row['insect'] or ''
        crops = row['crops'] or ''
        summary = row['summary'] or ''
        
        if crops:
            print(f"  • {target} ({crops})")
        elif summary:
            print(f"  • {summary}")
        else:
            print(f"  • {target}")
    
    conn.close()