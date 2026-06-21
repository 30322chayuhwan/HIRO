import urllib.request
import urllib.parse
import json

# 🔑 발급받으신 네이버 API 키를 아래에 입력하세요.
CLIENT_ID = "tKIzERCZIsxKz_nj2b47"
CLIENT_SECRET = "WNWnJAzZY8"

def save_naver_news(query, display_count=5):
    """네이버 뉴스 API를 호출하고 결과를 텍스트 파일로 저장하는 함수"""
    
    # 검색어를 URL 인코딩
    enc_text = urllib.parse.quote(query)
    
    # 네이버 뉴스 검색 API URL (display: 검색 결과 개수, sort: sim은 정확도순)
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_text}&display={display_count}&sort=sim"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)

    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        
        if rescode == 200:
            response_body = response.read()
            data = json.loads(response_body.decode('utf-8'))
            
            # 📁 텍스트 파일로 저장하기
            with open("naver_news_result.txt", "w", encoding="utf-8") as f:
                f.write(f"📰 '{query}' 관련 네이버 뉴스 검색 결과\n")
                f.write("=" * 40 + "\n\n")
                
                for i, item in enumerate(data['items']):
                    # 네이버 API는 검색어에 <b> 태그를 붙여서 주므로 깔끔하게 제거
                    title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                    link = item['link']
                    
                    f.write(f"{i+1}. {title}\n")
                    f.write(f"링크: {link}\n\n")
            
            print(f"✅ 성공! '{query}' 검색 결과가 'naver_news_result.txt' 파일에 저장되었습니다.")
        else:
            print(f"⚠️ API 에러 발생: 에러 코드 {rescode}")
            
    except Exception as e:
        print(f"⚠️ 실행 중 오류 발생: {e}")

# ==========================================
# 테스트 실행 (원하는 검색어로 바꿔보세요)
# ==========================================
if __name__ == "__main__":
    save_naver_news("학교 괴담")
