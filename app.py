from flask import Flask, request, jsonify
import urllib.request
import urllib.parse
import json

# 1. Gunicorn이 웹서버를 구동할 수 있도록 Flask 객체 생성
app = Flask(__name__)

# 서버가 잘 켜졌나 확인용 메인 페이지
@app.route("/", methods=["GET", "POST"])
def home():
    return "네이버 뉴스 검색 서버가 정상 작동 중입니다!"

# 2. 카카오톡과 연동되는 네이버 뉴스 검색 라우트
@app.route("/naver-news", methods=["POST"])
def naver_news():
    data = request.get_json(silent=True) or {}
    
    # 카카오 빌더 파라미터 창에서 설정한 이름 'keyword'로 검색어를 가져옵니다.
    y = data.get("action", {}).get("params", {}).get("keyword", "").strip()

    if not y:
        return jsonify({
            "version": "2.0",
            "template": {"outputs": [{"simpleText": {"text": "검색할 단어가 입력되지 않았습니다."}}]}
        })

    # 🔑 발급받으신 네이버 API 키를 입력하세요.
    client_id = "tKIzERCZIsxKz_nj2b47"
    client_secret = "WNWnJAzZY8"
    
    # 검색어 URL 인코딩 및 API 요청 주소 생성 (최신 뉴스 5개 정확도순)
    enc_text = urllib.parse.quote(y)
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_text}&display=5&sort=sim"

    req_api = urllib.request.Request(url)
    req_api.add_header("X-Naver-Client-Id", client_id)
    req_api.add_header("X-Naver-Client-Secret", client_secret)

    try:
        response = urllib.request.urlopen(req_api)
        rescode = response.getcode()
        
        if rescode == 200:
            api_data = json.loads(response.read().decode('utf-8'))
            
            titles = []
            for item in api_data['items']:
                # 네이버 API 특유의 <b> 태그와 따옴표 기호(&quot;)를 깔끔하게 지우기
                title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                titles.append(title)

            # 검색 결과가 있을 때 카카오톡으로 보낼 문장 조립
            if titles:
                result_text = f"📰 네이버에서 ['{y}'] 관련 뉴스를 찾았습니다!\n\n" + "\n\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])
            else:
                result_text = f"['{y}']에 대한 검색 결과를 찾지 못했습니다."
        else:
            result_text = f"⚠️ 네이버 API 접근 실패 (에러 코드: {rescode})"

    except Exception as e:
        result_text = f"조회 과정 중 오류가 발생했습니다: {str(e)}"

    # 카카오톡 챗봇이 이해할 수 있는 JSON 포맷으로 최종 응답
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": result_text
                    }
                }
            ]
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
