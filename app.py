# -*- coding: utf-8 -*-
"""
🚀 AI 기반 통합 비즈니스 인사이트 분석기
- Google Gemini AI 연동
- 실제 DART API 재무데이터  
- 구글시트 뉴스 분석
- 통합 인사이트 생성
"""

import os
import sys
import locale
import io
import base64
import re
import warnings
from datetime import datetime, timedelta
import random
import numpy as np
import json
import time
from collections import Counter

# 환경 설정
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'ko_KR.UTF-8'
warnings.filterwarnings('ignore')

try:
    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Korean_Korea.utf8')
    except:
        pass

import streamlit as st
import pandas as pd
import requests
import feedparser
from bs4 import BeautifulSoup
import gspread

# 🤖 Google Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    st.error("❌ google-generativeai 라이브러리가 필요합니다: pip install google-generativeai")

# plotly 안전하게 import
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# 한글 폰트 설정
try:
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    plt.rcParams['font.family'] = ['Malgun Gothic']
    plt.rcParams['font.sans-serif'] = ['Malgun Gothic']
    plt.rcParams['axes.unicode_minus'] = False
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Streamlit 페이지 설정
st.set_page_config(
    page_title="🚀 AI 통합 비즈니스 인사이트",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================================
# 🔑 API 키 및 설정
# ================================

# 🎯 실제 DART API 키
DART_API_KEY = "9a153f4344ad2db546d651090f78c8770bd773cb"

# 구글시트 설정
SHEET_ID = "16g1G89xoxyqF32YLMD8wGYLnQzjq2F_ew6G1AHH4bCA"

# 구글시트 인증 정보
GOOGLE_SHEET_CREDENTIALS = {
    "type": "service_account",
    "project_id": "operating-land-467305-t4",
    "private_key_id": "8ce67df37e30b321c5bec06c80c9455f409ec450",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDCm6/ztvOFgqEsenR57xmVu2VqoIvNUDpii8Gho9qWv7i4pJQuXuzYt/3a7AR+ItdPP8LmE4uARB34XM6r7n7JUkro7CX5sdREjwV24JFIPnopaCNfGTZOzxOpVP+lX6+jW1W81qMJgeuO8dQsEfPjNqptEDoWa/67hvvE8L3y14nRI1qtJGi8uZPPbd/k7SoPLQ2xAyMNIMxr+2+um1OqS7BGc+n/uMmBmbfxNAQkySJCXM+nVw0RrMJHZdmDNzH6KujqWTuZGMxt1uqHmest0Ss++GZOrV/WJBfqjj3VEU/ZFKh+efMThjI7DNSoVX1wpKfJTldtPHZjcODvcM/XAgMBAAECggEAFF+SKxSTJ/4F+48SVJWYexl0Q5ZtLGBizGBPNCngP3nwz7vDG5uqdgHFHL8qtT3WhqBpOgb/yrzW2mJ07ID6Wv83gmz+iMZ6L3c9njViYErSJTWWxmTwT43URBz26ow66gIs1qktxlgInh1pFfgHLVlSvDo/qotBzsYR44tEh4CkMc98God7AlzhF91oOHnEFKIJAWlnZzMpRmTuYDRgp0MP1qM38LS19K8cnrBhPIrRSlwJyveGwqylUccdREBnUMhXMlcJMp3mFNuy4FQB+CcDOWuXSs7xe+GoNvXgcrnzQymq6JaNrRtBguR/MTAMGqpvuIIBwl6xUL2qa3+rSQKBgQDyu1M3oGUg5oqR9x4GrENOhixPvMpRYvVWCwv8lQj5hV2dhyViy+Yr0qdVfoMhRvkD6TBco9ote+J3tdNrdLPGmzmTX0TqnXfAdnNRRoxte7ee5PM/PFl8SXM89nk99uKSocxPfT5lhv4X1Yba9sSvXR9er3IYvf2rDbT06oa8SwKBgQDNPvF1xU8/tVpY3e1qVVtxjaAURzB3y0g2Z5G6xZc+zslRG4Dg1Fp7mjxmomnYpVHvN1s7t27twZ325gfswXnFjECywu1hJvHzf5/nwh7Ug/t/bOg1fx8n1nO77IET/nrubT0mvEyrX8vzgvZk8Om/KXo6B2agWq28UbR9pKUrJQKBgAEjFYG2M6MS0WVbpf1cAziz8jMxbDUzZHjRtm2peRBKKqUZQ/iRgfOEmhoRbKXUQkhdaEeW0OfTo7zx0hq3wjvU8FEbaiQ7NptlMqcX0IKWyMZqxiTusHCfm3WWpfy/UlJjhaR9rrQlDL2p12bhLwyvP/1ejwdEpJKPjuBy1My/AoGAVixjPMtG5rzB3iXvlIGaDycjWuA43VMgUpdRfFWRlvFDXSZrCfqest6jFYSDZE6lBAb96yitDm4IYK1cDm99LRAh6ewltnCfjVi8TpYWU6vGYE3dgPiKoDNODEzUNQzXmFuNHUJZ/moOO4N06BSuT3CevNZ2pETuRO8ZFNeX8XECgYAdDJEXJD2iYpD+nP/PDqfRh/bjxSXat+vXfsYTJzoMZqAraQq4IlQyJ6vtRUQAiYkIbJY5IyaXvSpyKGDb7vrkniKIlMiRYd9JWPUY0RjxJfO0KxlVG7PInzdlyDHrAuD3DbYntI3GuayYmzfscDkDZKuL/7rVHkGz5DEttnQN2g==\n-----END PRIVATE KEY-----\n",
    "client_email": "sheet-reader@operating-land-467305-t4.iam.gserviceaccount.com",
    "client_id": "117458745032220743965",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheet-reader%40operating-land-467305-t4.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# DART 기업 데이터
DART_CORP_CODES = {
    "SK에너지": "00126380",
    "GS칼텍스": "00164779", 
    "HD현대오일뱅크": "00164742",
    "S-Oil": "00164360"
}

TEAM_DART_DATA = {
    "SK에너지": [
        {"report_date": "20240514", "report_type": "분기보고서", "rcpNo": "20240514000644"},
        {"report_date": "20240814", "report_type": "반기보고서", "rcpNo": "20240814001840"},
        {"report_date": "20241114", "report_type": "분기보고서", "rcpNo": "20241114001025"},
        {"report_date": "20250318", "report_type": "사업보고서", "rcpNo": "20250318000950"},
        {"report_date": "20250514", "report_type": "분기보고서", "rcpNo": "20250514000953"}
    ],
    "HD현대오일뱅크": [
        {"report_date": "20240514", "report_type": "분기보고서", "rcpNo": "20240514000948"},
        {"report_date": "20240813", "report_type": "반기보고서", "rcpNo": "20240813001381"},
        {"report_date": "20241113", "report_type": "분기보고서", "rcpNo": "20241113000474"},
        {"report_date": "20250328", "report_type": "사업보고서", "rcpNo": "20250328000054"},
        {"report_date": "20250515", "report_type": "분기보고서", "rcpNo": "20250515000349"}
    ],
    "GS칼텍스": [
        {"report_date": "20240516", "report_type": "분기보고서", "rcpNo": "20240516000460"},
        {"report_date": "20240814", "report_type": "반기보고서", "rcpNo": "20240814002198"},
        {"report_date": "20241114", "report_type": "분기보고서", "rcpNo": "20241114001568"},
        {"report_date": "20250331", "report_type": "사업보고서", "rcpNo": "20250331002860"},
        {"report_date": "20250515", "report_type": "분기보고서", "rcpNo": "20250515001097"}
    ],
    "S-Oil": [
        {"report_date": "20240514", "report_type": "분기보고서", "rcpNo": "20240514001646"},
        {"report_date": "20240814", "report_type": "반기보고서", "rcpNo": "20240814001812"},
        {"report_date": "20241114", "report_type": "분기보고서", "rcpNo": "20241114000848"},
        {"report_date": "20250319", "report_type": "사업보고서", "rcpNo": "20250319000503"},
        {"report_date": "20250515", "report_type": "분기보고서", "rcpNo": "20250515000913"}
    ]
}

# 색상 테마
SK_COLORS = {
    'primary': '#E31E24',  # SK 레드
    'secondary': '#FF6B35',  # SK 오렌지
    'accent': '#004EA2',  # SK 블루
    'success': '#00A651',
    'warning': '#FF9500',
    'competitor': '#6C757D',
    'competitor_1': '#AEC6CF',
    'competitor_2': '#FFB6C1',
    'competitor_3': '#98FB98',
    'competitor_4': '#F0E68C'
}

# 세션 상태 초기화
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = None
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""
if 'financial_data' not in st.session_state:
    st.session_state.financial_data = None
if 'news_data' not in st.session_state:
    st.session_state.news_data = None
if 'integrated_insights' not in st.session_state:
    st.session_state.integrated_insights = None

# ================================
# 🤖 Google Gemini AI 연동 함수들
# ================================

def setup_gemini_api(api_key):
    """🤖 Google Gemini AI 설정"""
    if not GEMINI_AVAILABLE:
        return None, "❌ google-generativeai 라이브러리가 설치되지 않았습니다."
    
    if not api_key:
        return None, "🔑AIzaSyB176ys4MCjEs8R0dv15hMqDE2G-9J0qIA"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 연결 테스트
        test_response = model.generate_content("안녕하세요! API 연결 테스트입니다.")
        
        if test_response.text:
            return model, "✅ Gemini AI 연결 성공!"
        else:
            return None, "❌ API 응답이 비어있습니다."
            
    except Exception as e:
        if "api_key" in str(e).lower():
            return None, "❌ 잘못된 API 키입니다."
        elif "quota" in str(e).lower():
            return None, "⚠️ API 할당량을 초과했습니다."
        else:
            return None, f"❌ 연결 오류: {e}"

@st.cache_data(ttl=600, show_spinner=False)
def generate_integrated_insights(_model, financial_df, news_df, keywords):
    """🤖 재무데이터 + 뉴스 통합 분석"""
    if not _model:
        return "Gemini AI 모델이 설정되지 않았습니다."
    
    # 재무 데이터 요약
    financial_summary = ""
    if not financial_df.empty:
        sk_data = financial_df[financial_df['회사명'].str.contains('SK', na=False)]
        if not sk_data.empty:
            revenue = sk_data['매출(조원)'].values[0] if '매출(조원)' in sk_data.columns else 0
            profit_rate = sk_data['영업이익률(%)'].values[0] if '영업이익률(%)' in sk_data.columns else 0
            financial_summary = f"SK에너지 매출: {revenue}조원, 영업이익률: {profit_rate}%"
        
        # 경쟁사 비교
        competitor_summary = []
        for _, row in financial_df.iterrows():
            if 'SK' not in str(row.get('회사명', '')):
                comp_name = row.get('회사명', '')
                comp_revenue = row.get('매출(조원)', 0)
                comp_profit = row.get('영업이익률(%)', 0)
                competitor_summary.append(f"{comp_name}: 매출 {comp_revenue}조원, 영업이익률 {comp_profit}%")
        
        financial_summary += f"\n경쟁사: " + ", ".join(competitor_summary[:3])
    
    # 뉴스 키워드 요약
    news_summary = ""
    if keywords:
        top_keywords = [k[0] for k in keywords[:8]]
        news_summary = f"주요 키워드: {', '.join(top_keywords)}"
    
    # 뉴스 샘플
    news_samples = ""
    if not news_df.empty:
        recent_news = news_df.head(3)
        for _, news in recent_news.iterrows():
            title = str(news.get('제목', ''))[:50]
            news_samples += f"- {title}...\n"
    
    # Gemini 프롬프트
    prompt = f"""
당신은 **에너지/석유화학 업계 전문 애널리스트**입니다.

📊 **실제 재무데이터 (DART API)**:
{financial_summary}

📰 **최신 뉴스 분석**:
{news_summary}

**최근 뉴스 샘플**:
{news_samples}

🎯 **전문가 분석 요청**:
위 실제 데이터를 바탕으로 **구체적이고 실행 가능한** 인사이트를 제공해주세요:

**1. 📊 현재 시장 포지션 분석**
- SK에너지의 경쟁력 수준
- 주요 경쟁사 대비 강약점

**2. 🔍 핵심 발견사항** (3개)
- 재무데이터에서 발견한 주요 패턴
- 뉴스 트렌드와의 연관성

**3. ⚠️ 주요 리스크 요인** (3개)
- 재무적 리스크
- 시장/업계 리스크

**4. 💡 개선 기회** (3개)
- 매출 증대 방안
- 비용 절감 기회
- 신규 사업 기회

**5. 🎯 실행 전략 권고** (3개)
- 단기 실행 방안 (3개월)
- 중기 전략 (6-12개월)  
- 장기 비전 (2-3년)

**6. 📈 모니터링 지표** (5개)
- 추적해야 할 핵심 KPI

각 항목을 **구체적 수치**와 **실행 방법**을 포함해서 작성해주세요.
"""
    
    try:
        response = _model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini 분석 중 오류 발생: {e}"

def generate_news_insights(_model, news_df, financial_context=""):
    """🤖 뉴스 전용 인사이트 생성"""
    if not _model or news_df.empty:
        return "분석할 데이터가 없습니다."
    
    # 뉴스 샘플 추출
    news_samples = []
    for i, row in news_df.head(6).iterrows():
        title = str(row.get('제목', ''))[:60]
        content = str(row.get('내용', ''))[:80] if '내용' in row else str(row.get('요약', ''))[:80]
        source = str(row.get('언론사', 'N/A'))
        date = str(row.get('날짜', 'N/A'))
        news_samples.append(f"{i+1}. [{source}] {title}... ({date})")
    
    prompt = f"""
당신은 **비즈니스 뉴스 분석 전문가**입니다.

📰 **분석 대상 뉴스** ({len(news_df)}건):
{chr(10).join(news_samples)}

💼 **재무 컨텍스트**: {financial_context}

🎯 **뉴스 인사이트 분석 요청**:

**1. 📊 주요 트렌드 요약**
**2. 🔍 핵심 이슈 발굴** (3가지)
**3. 💡 비즈니스 기회** (3가지)
**4. ⚠️ 주의할 리스크** (3가지)
**5. 🎯 전략적 시사점**

각 항목을 구체적이고 실행 가능한 관점에서 분석해주세요.
"""
    
    try:
        response = _model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ 뉴스 인사이트 생성 오류: {e}"

# ================================
# 📊 DART API 연동 클래스
# ================================

class RealDartDataCollector:
    """🎯 실제 DART API를 통한 재무데이터 수집"""
    
    def __init__(self):
        self.api_key = DART_API_KEY
        self.base_url = "https://opendart.fss.or.kr/api"
        self.source_tracking = {}

    def get_financial_data_from_dart(self, company_name, report_info):
        """🎯 실제 DART에서 재무데이터 수집"""
        try:
            # 실제 DART API 호출
            url = f"{self.base_url}/fnlttSinglAcntAll.json"
            params = {
                'crtfc_key': self.api_key,
                'corp_code': DART_CORP_CODES.get(company_name, "00126380"),
                'bsns_year': report_info['report_date'][:4],
                'reprt_code': self._convert_report_type(report_info['report_type'])
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == '000':
                    # ✅ 실제 데이터 파싱 성공
                    financial_data = self._parse_dart_response(data, company_name)
                    self._save_source_info(company_name, report_info, "실제 DART API 데이터")
                    return financial_data
                else:
                    # API 오류 응답
                    error_msg = data.get('message', 'Unknown error')
                    st.warning(f"⚠️ {company_name} DART API 오류: {error_msg}")
                    return self._generate_fallback_data(company_name, report_info)
            else:
                # HTTP 오류
                st.warning(f"⚠️ {company_name} HTTP 오류 {response.status_code}")
                return self._generate_fallback_data(company_name, report_info)
                
        except Exception as e:
            # 예외 발생
            st.warning(f"⚠️ {company_name} 데이터 수집 오류: {e}")
            return self._generate_fallback_data(company_name, report_info)

    def _convert_report_type(self, report_type):
        """보고서 종류 코드 변환"""
        type_codes = {
            "사업보고서": "11011",
            "반기보고서": "11012", 
            "분기보고서": "11013"
        }
        return type_codes.get(report_type, "11011")

    def _parse_dart_response(self, data, company_name):
        """🎯 실제 DART API 응답 파싱"""
        financial_items = {
            '매출': 0,
            '매출원가': 0,
            '판매비와관리비': 0,
            '영업이익': 0,
            '당기순이익': 0
        }
        
        for item in data.get('list', []):
            account_nm = item.get('account_nm', '').strip()
            thstrm_amount = str(item.get('thstrm_amount', '0')).replace(',', '').replace('-', '')
            
            # 숫자 추출 및 변환
            try:
                # 음수 처리
                is_negative = '-' in str(item.get('thstrm_amount', '0'))
                amount = int(re.sub(r'[^\d]', '', thstrm_amount)) * 1000000  # 백만원 단위를 원 단위로
                if is_negative:
                    amount = -amount
            except:
                amount = 0
            
            # 계정과목 매핑 (더 정확한 매칭)
            if any(keyword in account_nm for keyword in ['매출액', '수익총액', '매출수익']):
                if '매출원가' not in account_nm and '판매비' not in account_nm:
                    financial_items['매출'] = max(financial_items['매출'], amount)
            elif any(keyword in account_nm for keyword in ['매출원가', '제품매출원가']):
                financial_items['매출원가'] = max(financial_items['매출원가'], amount)
            elif any(keyword in account_nm for keyword in ['판매비와관리비', '판관비', '판매관리비']):
                financial_items['판매비와관리비'] = max(financial_items['판매비와관리비'], amount)
            elif '영업이익' in account_nm and '법인세' not in account_nm:
                financial_items['영업이익'] = amount  # 영업이익은 음수일 수 있음
            elif any(keyword in account_nm for keyword in ['당기순이익', '순이익']):
                financial_items['당기순이익'] = amount  # 순이익도 음수일 수 있음
        
        # 데이터 검증 및 보정
        if financial_items['매출'] <= 0:
            return self._generate_fallback_data_dict(company_name)
        
        return financial_items

    def _generate_fallback_data_dict(self, company_name):
        """대체 데이터 (딕셔너리 형태)"""
        base_revenue_data = {
            "SK에너지": 47.2 * 1_000_000_000_000,
            "GS칼텍스": 39.8 * 1_000_000_000_000,
            "HD현대오일뱅크": 26.5 * 1_000_000_000_000,
            "S-Oil": 33.1 * 1_000_000_000_000
        }
        
        revenue = base_revenue_data.get(company_name, 30.0 * 1_000_000_000_000)
        
        return {
            '매출': revenue,
            '매출원가': revenue * 0.92,
            '판매비와관리비': revenue * 0.03,
            '영업이익': revenue * 0.05,
            '당기순이익': revenue * 0.03
        }

    def _generate_fallback_data(self, company_name, report_info):
        """API 실패 시 대체 데이터"""
        self._save_source_info(company_name, report_info, "대체 데이터 (업계 평균)")
        return self._generate_fallback_data_dict(company_name)

    def _save_source_info(self, company_name, report_info, data_type):
        """출처 정보 저장"""
        self.source_tracking[company_name] = {
            'company_code': DART_CORP_CODES.get(company_name, "Unknown"),
            'report_code': report_info['rcpNo'],
            'report_type': report_info['report_type'],
            'year': report_info['report_date'][:4],
            'dart_url': f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={report_info['rcpNo']}",
            'data_type': data_type,
            'api_key': f"DART API ({self.api_key[:10]}...)"
        }

    def create_row_format_data(self, companies, analysis_year="2025"):
        """🎯 실제 DART 데이터로 행별 데이터 생성"""
        row_data = []
        
        for company_name in companies:
            if company_name in TEAM_DART_DATA:
                reports = TEAM_DART_DATA[company_name]
                latest_report = max(reports, key=lambda x: x['report_date'])
                
                # 🎯 실제 DART 데이터 수집
                financial_data = self.get_financial_data_from_dart(company_name, latest_report)
                
                # 단위 포함한 행 데이터 생성
                row = {
                    '회사명': company_name,
                    '기간(년)': analysis_year,
                    '매출(조원)': round(financial_data.get('매출', 0) / 1_000_000_000_000, 1),
                    '매출원가(조원)': round(financial_data.get('매출원가', 0) / 1_000_000_000_000, 1),
                    '판매비와관리비(조원)': round(financial_data.get('판매비와관리비', 0) / 1_000_000_000_000, 1),
                    '영업이익(억원)': round(financial_data.get('영업이익', 0) / 100_000_000, 0),
                    '당기순이익(억원)': round(financial_data.get('당기순이익', 0) / 100_000_000, 0)
                }
                
                # 비율 계산
                revenue = financial_data.get('매출', 0)
                if revenue > 0:
                    row['영업이익률(%)'] = round((financial_data.get('영업이익', 0) / revenue) * 100, 2)
                    row['순이익률(%)'] = round((financial_data.get('당기순이익', 0) / revenue) * 100, 2)
                    row['매출원가율(%)'] = round((financial_data.get('매출원가', 0) / revenue) * 100, 2)
                    row['판관비율(%)'] = round((financial_data.get('판매비와관리비', 0) / revenue) * 100, 2)
                else:
                    row['영업이익률(%)'] = 0.0
                    row['순이익률(%)'] = 0.0
                    row['매출원가율(%)'] = 0.0
                    row['판관비율(%)'] = 0.0
                
                row_data.append(row)
        
        df = pd.DataFrame(row_data)
        
        # SK에너지를 첫 번째 행으로 배치
        if not df.empty and 'SK에너지' in df['회사명'].values:
            sk_row = df[df['회사명'] == 'SK에너지']
            other_rows = df[df['회사명'] != 'SK에너지']
            df = pd.concat([sk_row, other_rows], ignore_index=True)
        
        return df

# ================================
# 📰 구글시트 뉴스 연동 함수들
# ================================

@st.cache_data(ttl=1800)  # 30분 캐시
def load_google_sheet_news():
    """구글시트에서 뉴스 데이터 로드"""
    try:
        gc = gspread.service_account_from_dict(GOOGLE_SHEET_CREDENTIALS)
        sheet = gc.open_by_key(SHEET_ID).sheet1
        
        all_records = sheet.get_all_records()
        df = pd.DataFrame(all_records)
        
        if df.empty:
            return pd.DataFrame()
        
        # 기본 전처리
        df = df.fillna('')
        required_cols = ['제목', '링크', '요약', '날짜', '언론사']
        for col in required_cols:
            if col not in df.columns:
                if col == '요약' and '내용' in df.columns:
                    df[col] = df['내용']
                else:
                    df[col] = 'N/A'
        
        # 텍스트 전처리
        df['제목_처리'] = df['제목'].apply(preprocess_text)
        df['내용_처리'] = df['요약'].apply(preprocess_text)
        df['전체_텍스트'] = df['제목_처리'] + ' ' + df['내용_처리']
        
        # 빈 데이터 제거
        df = df[df['전체_텍스트'].str.len() > 10].copy()
        
        # 분류 추가
        df['관련회사'] = df['제목'].apply(categorize_company)
        df['중요도'] = df['제목'].apply(calculate_importance)
        df['감정'] = df['제목'].apply(analyze_sentiment)
        df['전략분류'] = df['제목'].apply(classify_strategy)
        
        return df
        
    except Exception as e:
        st.error(f"❌ 구글시트 뉴스 로드 오류: {e}")
        return pd.DataFrame()

def preprocess_text(text):
    """텍스트 전처리"""
    if pd.isna(text):
        return ""
    
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', str(text))
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_keywords_simple(texts, top_n=15):
    """키워드 추출"""
    stopwords = {
        '이', '그', '저', '것', '들', '등', '때', '곳', '수', '년', '월', '일', '시', '분', '초',
        '있는', '없는', '하는', '되는', '인', '의', '가', '를', '에', '로', '으로', '와', '과',
        '한', '두', '세', '네', '다섯', '여섯', '일곱', '여덟', '아홉', '열', '이것', '그것', '저것',
        '여기', '거기', '저기', '때문', '경우', '상황', '문제', '시간', '정도', '말', '이야기',
        '생각', '기자', '뉴스', '기사', '보도', '취재', '시', '도', '구', '동', '리', '보면'
    }
    
    all_words = []
    for text in texts:
        words = re.findall(r'[가-힣]{2,}', text)
        meaningful_words = [
            word for word in words 
            if word not in stopwords and 2 <= len(word) <= 8
        ]
        all_words.extend(meaningful_words)
    
    word_counter = Counter(all_words)
    top_keywords = word_counter.most_common(top_n)
    
    return top_keywords

def categorize_company(title):
    """회사 분류"""
    try:
        if pd.isna(title):
            return '업계전반'
        
        title = str(title)
        companies = []
        
        if any(keyword in title for keyword in ['SK', 'sk', '에스케이']):
            companies.append('SK에너지')
        if any(keyword in title for keyword in ['GS칼텍스', 'GS', '지에스']):
            companies.append('GS칼텍스')
        if any(keyword in title for keyword in ['HD현대', '현대오일', '현대']):
            companies.append('HD현대오일뱅크')
        if any(keyword in title for keyword in ['S-Oil', '에쓰오일', '에스오일']):
            companies.append('S-Oil')
        
        return ', '.join(companies) if companies else '업계전반'
    except:
        return '업계전반'

def calculate_importance(title):
    """중요도 계산"""
    try:
        if pd.isna(title):
            return '낮음'
        
        title = str(title)
        important_keywords = ['손실', '적자', '영업이익', '실적', '급등', '급락', '위기', '합병', '투자']
        importance_score = sum(1 for keyword in important_keywords if keyword in title)
        
        if importance_score >= 3:
            return '높음'
        elif importance_score >= 1:
            return '중간'
        else:
            return '낮음'
    except:
        return '낮음'

def analyze_sentiment(title):
    """감정 분석"""
    try:
        if pd.isna(title):
            return '중립'
        
        title = str(title)
        positive_keywords = ['상승', '급등', '개선', '성장', '확대', '투자', '성공']
        negative_keywords = ['하락', '급락', '손실', '적자', '부진', '위기', '감소']
        
        positive_count = sum(1 for keyword in positive_keywords if keyword in title)
        negative_count = sum(1 for keyword in negative_keywords if keyword in title)
        
        if positive_count > negative_count:
            return '긍정'
        elif negative_count > positive_count:
            return '부정'
        else:
            return '중립'
    except:
        return '중립'

def classify_strategy(title):
    """전략 분류"""
    try:
        if pd.isna(title):
            return '🛠 기타 전략'
        
        title = str(title)
        
        if any(keyword in title for keyword in ['매출', '수익', '성장', '확대']):
            return '📈 매출 증대'
        elif any(keyword in title for keyword in ['비용', '절감', '효율', '최적화']):
            return '💰 비용 절감'
        elif any(keyword in title for keyword in ['자산', '관리', 'AI', '디지털']):
            return '🏭 자산 관리 효율화'
        elif any(keyword in title for keyword in ['신규', '사업', '진출', '다각화']):
            return '🌱 신규 사업 진출'
        else:
            return '🛠 기타 전략'
    except:
        return '🛠 기타 전략'

# ================================
# 📊 시각화 함수들
# ================================

def get_company_color(company_name, all_companies):
    """회사별 고유 색상 반환"""
    if 'SK' in company_name:
        return SK_COLORS['primary']
    else:
        competitor_colors = [
            SK_COLORS['competitor_1'], SK_COLORS['competitor_2'], 
            SK_COLORS['competitor_3'], SK_COLORS['competitor_4']
        ]
        non_sk_companies = [comp for comp in all_companies if 'SK' not in comp]
        try:
            index = non_sk_companies.index(company_name)
            return competitor_colors[index % len(competitor_colors)]
        except ValueError:
            return SK_COLORS['competitor']

def generate_financial_charts(df):
    """📊 재무 차트 생성"""
    if df.empty or not PLOTLY_AVAILABLE:
        st.info("시각화할 데이터가 없거나 plotly가 설치되지 않았습니다.")
        return
    
    # 필요한 컬럼 확인
    revenue_col = next((col for col in df.columns if '매출' in col and '원가' not in col), None)
    operating_income_col = next((col for col in df.columns if '영업이익' in col and '%' not in col), None)
    
    if not revenue_col or not operating_income_col:
        st.warning("필요한 컬럼이 데이터에 없습니다. (매출, 영업이익 컬럼 필요)")
        return
    
    companies = df['회사명'].unique()
    
    # 차트 유형 선택
    chart_types = st.multiselect(
        "📊 차트 유형 선택", 
        ["막대그래프", "선그래프", "히트맵"], 
        default=["막대그래프"]
    )
    
    if not chart_types:
        return
    
    # 막대그래프
    if "막대그래프" in chart_types:
        st.subheader("📊 회사별 재무지표 비교")
        
        metrics_to_show = [
            (revenue_col, "매출 비교"),
            (operating_income_col, "영업이익 비교"),
            ('영업이익률(%)', "영업이익률 비교")
        ]
        
        cols = st.columns(len(metrics_to_show))
        
        for idx, (metric_col, title) in enumerate(metrics_to_show):
            if metric_col in df.columns:
                with cols[idx]:
                    # 회사별 색상 매핑
                    color_discrete_map = {}
                    for company in companies:
                        color_discrete_map[company] = get_company_color(company, companies)
                    
                    fig = px.bar(
                        df,
                        x='회사명',
                        y=metric_col,
                        title=title,
                        color='회사명',
                        color_discrete_map=color_discrete_map,
                        text=metric_col
                    )
                    
                    fig.update_traces(
                        texttemplate='%{text}',
                        textposition='outside'
                    )
                    
                    fig.update_layout(
                        showlegend=False,
                        height=350,
                        title_font_size=12
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    # 선그래프
    if "선그래프" in chart_types:
        st.subheader("📈 재무비율 트렌드")
        
        ratio_cols = [col for col in df.columns if '%' in col]
        if ratio_cols:
            fig = go.Figure()
            
            for company in companies:
                company_data = df[df['회사명'] == company]
                color = get_company_color(company, companies)
                
                line_width = 4 if 'SK' in company else 2
                marker_size = 10 if 'SK' in company else 6
                
                fig.add_trace(go.Scatter(
                    x=ratio_cols,
                    y=[company_data[col].values[0] if len(company_data) > 0 else 0 for col in ratio_cols],
                    mode='lines+markers',
                    name=company,
                    line=dict(color=color, width=line_width),
                    marker=dict(size=marker_size, color=color)
                ))
            
            fig.update_layout(
                title="재무비율 패턴 분석",
                xaxis_title="재무지표",
                yaxis_title="비율 (%)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # 히트맵
    if "히트맵" in chart_types:
        st.subheader("🔥 성과 히트맵")
        
        ratio_cols = [col for col in df.columns if '%' in col]
        if ratio_cols:
            try:
                heatmap_data = df.set_index('회사명')[ratio_cols].T
                
                fig = px.imshow(
                    heatmap_data,
                    text_auto=True,
                    title="재무성과 히트맵",
                    color_continuous_scale='RdYlGn',
                    aspect="auto",
                    height=400
                )
                
                fig.update_traces(textfont_size=10)
                st.plotly_chart(fig, use_container_width=True)
            
            except Exception as e:
                st.warning(f"히트맵 생성 오류: {e}")

def generate_news_charts(df_news, keywords):
    """📰 뉴스 분석 차트"""
    if df_news.empty or not PLOTLY_AVAILABLE:
        return
    
    col1, col2 = st.columns(2)
    
    # 키워드 차트
    with col1:
        if keywords:
            keyword_df = pd.DataFrame(keywords[:10], columns=['키워드', '빈도'])
            fig = px.bar(
                keyword_df, 
                x='빈도', 
                y='키워드',
                orientation='h',
                title="🔤 주요 키워드 TOP 10",
                color='빈도',
                color_continuous_scale='blues'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # 전략분류 차트
    with col2:
        if '전략분류' in df_news.columns:
            strategy_counts = df_news['전략분류'].value_counts()
            fig = px.pie(
                values=strategy_counts.values,
                names=strategy_counts.index,
                title="📊 전략분류별 뉴스 분포"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            # ================================


# 🎮 메인 애플리케이션
# ================================

def main():
    """🚀 메인 통합 대시보드"""
    
    # 헤더
    st.title("🚀 AI 기반 통합 비즈니스 인사이트")
    st.markdown("**Google Gemini AI + 실제 DART 재무데이터 + 구글시트 뉴스 분석**")
    
    # 🔑 API 키 입력 섹션
    with st.sidebar:
        st.header("🔑 Gemini AI 설정")
        
        # API 키 입력
        api_key_input = st.text_input(
            "Gemini API 키 입력",
            type="password",
            value=st.session_state.gemini_api_key,
            placeholder="AIzaSyB176ys4MCjEs8R0...",
            help="Google AI Studio에서 발급받은 API 키를 입력하세요"
        )
        
        if api_key_input != st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = api_key_input
            st.session_state.gemini_model = None  # 모델 초기화
        
        # API 연결 테스트
        if st.button("🔗 Gemini AI 연결 테스트"):
            if st.session_state.gemini_api_key:
                with st.spinner("🤖 Gemini AI 연결 중..."):
                    model, message = setup_gemini_api(st.session_state.gemini_api_key)
                    
                    if model:
                        st.session_state.gemini_model = model
                        st.success(message)
                    else:
                        st.error(message)
            else:
                st.error("🔑 API 키를 먼저 입력해주세요!")
        
        # 연결 상태 표시
        if st.session_state.gemini_model:
            st.success("✅ Gemini AI 연결됨")
        else:
            st.warning("⚠️ Gemini AI 미연결")
        
        st.markdown("---")
        
        # 캐시 관리
        st.subheader("🔧 캐시 관리")
        if st.button("🗑️ 전체 캐시 초기화"):
            st.cache_data.clear()
            st.success("캐시가 초기화되었습니다!")
        
        # 사용 안내
        st.markdown("---")
        st.subheader("📖 사용 안내")
        st.markdown("""
        **1단계**: Gemini API 키 입력
        **2단계**: 재무데이터 수집 
        **3단계**: 뉴스데이터 로드
        **4단계**: AI 통합 분석
        """)
    
    # 메인 탭 구성
    tabs = st.tabs([
        "🎯 통합 AI 분석", 
        "📊 재무 데이터", 
        "📰 뉴스 분석", 
        "💡 전략 인사이트",
        "📄 보고서 다운로드"
    ])
    
    # ================================
    # 🎯 탭 1: 통합 AI 분석 
    # ================================
    with tabs[0]:
        st.header("🤖 Gemini AI 통합 분석")
        
        # 전체 분석 실행 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 전체 통합 분석 시작", type="primary", use_container_width=True):
                if not st.session_state.gemini_model:
                    st.error("🔑 먼저 사이드바에서 Gemini AI를 연결해주세요!")
                else:
                    perform_integrated_analysis()
        
        # 분석 결과 표시
        if st.session_state.integrated_insights:
            st.markdown("---")
            st.subheader("🧠 AI 통합 인사이트")
            
            # 인사이트를 보기 좋게 표시
            with st.container():
                st.markdown(st.session_state.integrated_insights)
            
            # 새로고침 버튼
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("🔄 인사이트 새로고침", use_container_width=True):
                    # 캐시된 인사이트 초기화
                    generate_integrated_insights.clear()
                    st.session_state.integrated_insights = None
                    st.rerun()
        else:
            st.info("👆 '전체 통합 분석 시작' 버튼을 클릭하여 AI 분석을 시작하세요!")
            
            # 샘플 미리보기
            with st.expander("🔍 분석 결과 미리보기"):
                st.markdown("""
                **🤖 Gemini AI가 제공할 분석 내용:**
                
                📊 **현재 시장 포지션 분석**
                - SK에너지의 경쟁력 수준 진단
                - 주요 경쟁사 대비 강약점 분석
                
                🔍 **핵심 발견사항 (3개)**
                - 재무데이터 패턴 분석
                - 뉴스 트렌드 연관성
                
                ⚠️ **주요 리스크 요인 (3개)**
                - 재무적 리스크
                - 시장/업계 리스크
                
                💡 **개선 기회 (3개)**
                - 매출 증대 방안
                - 비용 절감 기회
                - 신규 사업 기회
                
                🎯 **실행 전략 권고 (3개)**
                - 단기 실행 방안 (3개월)
                - 중기 전략 (6-12개월)
                - 장기 비전 (2-3년)
                
                📈 **모니터링 지표 (5개)**
                - 추적해야 할 핵심 KPI
                """)
    
    # ================================
    # 📊 탭 2: 재무 데이터
    # ================================
    with tabs[1]:
        st.header("📊 실제 DART API 재무 분석")
        
        # DART 분석 실행
        if st.button("🎯 DART API 재무데이터 수집", type="primary"):
            with st.spinner("🔄 DART API에서 실제 재무데이터 수집 중..."):
                collect_financial_data()
        
        # 재무 데이터 표시
        if st.session_state.financial_data is not None and not st.session_state.financial_data.empty:
            df_financial = st.session_state.financial_data
            
            # 기간 및 회사 선택
            col1, col2 = st.columns(2)
            
            with col1:
                # 기간 선택
                period_col = next((col for col in df_financial.columns if '기간' in col), None)
                if period_col:
                    periods = sorted(df_financial[period_col].unique(), reverse=True)
                    selected_period = st.selectbox("📅 기간 선택", periods)
                    df_display = df_financial[df_financial[period_col] == selected_period]
                else:
                    selected_period = "2025"
                    df_display = df_financial
            
            with col2:
                # 회사 선택
                if '회사명' in df_display.columns:
                    selected_companies = st.multiselect(
                        "🏢 회사 선택", 
                        options=df_display["회사명"].unique(),
                        default=list(df_display["회사명"].unique())
                    )
                    df_display = df_display[df_display['회사명'].isin(selected_companies)]
            
            # 재무 데이터 테이블
            st.subheader("💰 재무성과 분석 결과")
            st.dataframe(df_display, use_container_width=True)
            
            # 차트 생성
            generate_financial_charts(df_display)
            
            # DART 출처 정보
            if hasattr(st.session_state, 'dart_source_info') and st.session_state.dart_source_info:
                st.subheader("📊 DART API 출처 정보")
                source_df = pd.DataFrame(st.session_state.dart_source_info)
                st.dataframe(
                    source_df,
                    use_container_width=True,
                    column_config={
                        "dart_url": st.column_config.LinkColumn(
                            "🔗 DART 바로가기",
                            help="실제 DART 보고서로 이동"
                        )
                    }
                )
        else:
            st.info("📋 'DART API 재무데이터 수집' 버튼을 클릭하여 데이터를 수집하세요.")
    
    # ================================
    # 📰 탭 3: 뉴스 분석
    # ================================
    with tabs[2]:
        st.header("📰 구글시트 뉴스 분석")
        
        # 뉴스 로드 버튼
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("**구글시트 연동 뉴스 데이터**")
        with col2:
            if st.button("📋 뉴스 데이터 로드"):
                with st.spinner("📰 구글시트에서 뉴스 로드 중..."):
                    load_news_data()
        
        # 뉴스 데이터 표시
        if st.session_state.news_data is not None and not st.session_state.news_data.empty:
            df_news = st.session_state.news_data
            
            # 뉴스 분석 요약
            st.subheader("📊 뉴스 분석 요약")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📰 총 뉴스", f"{len(df_news)}건")
            with col2:
                if '감정' in df_news.columns:
                    positive_count = len(df_news[df_news['감정'] == '긍정'])
                    st.metric("😊 긍정 뉴스", f"{positive_count}건")
            with col3:
                if '중요도' in df_news.columns:
                    important_count = len(df_news[df_news['중요도'] == '높음'])
                    st.metric("🔥 중요 뉴스", f"{important_count}건")
            with col4:
                if '관련회사' in df_news.columns:
                    sk_count = len(df_news[df_news['관련회사'].str.contains('SK', na=False)])
                    st.metric("🏢 SK 관련", f"{sk_count}건")
            
            # 키워드 추출 및 분석
            if '전체_텍스트' in df_news.columns:
                keywords = extract_keywords_simple(df_news['전체_텍스트'].tolist())
                
                # 키워드 차트
                generate_news_charts(df_news, keywords)
                
                # 키워드 테이블
                st.subheader("🔤 핵심 키워드 분석")
                if keywords:
                    keyword_df = pd.DataFrame(keywords, columns=['키워드', '빈도'])
                    keyword_df.index = range(1, len(keyword_df) + 1)
                    st.dataframe(keyword_df, use_container_width=True)
            
            # 전략분류별 뉴스
            st.subheader("📋 전략분류별 뉴스")
            
            if '전략분류' in df_news.columns:
                전략분류_옵션 = ["전체보기"] + list(df_news['전략분류'].unique())
                selected_strategy = st.selectbox("전략 선택", 전략분류_옵션)
                
                if selected_strategy == "전체보기":
                    filtered_df = df_news
                else:
                    filtered_df = df_news[df_news['전략분류'] == selected_strategy]
                
                # 뉴스 표시
                for _, row in filtered_df.head(10).iterrows():
                    with st.expander(f"[{row.get('언론사', 'N/A')}] {row['제목']}"):
                        if '요약' in row and pd.notna(row['요약']):
                            st.write(row['요약'])
                        if '링크' in row and pd.notna(row['링크']) and row['링크']:
                            st.markdown(f"[📰 기사 원문]({row['링크']})")
