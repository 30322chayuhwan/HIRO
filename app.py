from flask import Flask, request, jsonify
import urllib.request
import urllib.parse
import json

# Gunicorn이 웹서버를 구동할 때 이 'app' 변수를 찾습니다!
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    return "네이버 뉴스 검색 전용 서버입니다."

@app.route("/naver-news", methods=["POST"])
def naver_news():
    data = request.get_json(silent=True) or {}
    y = data.get("action", {}).get("params", {}).get("keyword", "").strip()

    if not y:
        return jsonify({"version": "2.0", "template": {"outputs": [{"simpleText": {"text": "검색어가 없습니다."}}]}})

    client_id = "tKIzERCZIsxKz_nj2b47"
    client_secret = "WNWnJAzZY8"
    
    enc_text = urllib.parse.quote(y)
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_text}&display=5&sort=sim"

    req_api = urllib.request.Request(url)
    req_api.add_header("X-Naver-Client-Id", client_id)
    req_api.add_header("X-Naver-Client-Secret", client_secret)

    try:
        response = urllib.request.urlopen(req_api)
        if response.getcode() == 200:
            api_data = json.loads(response.read().decode('utf-8'))
            
            titles = []
            # 📁 파일 저장 기능
            with open("naver_news_result.txt", "w", encoding="utf-8") as f:
                f.write(f"📰 '{y}' 뉴스 검색 결과\n\n")
                for i, item in enumerate(api_data['items']):
                    title = item['title'].replace('<b>', '').replace('</b>', '')
                    titles.append(title)
                    f.write(f"{i+1}. {title}\n링크: {item['link']}\n\n")

            result_text = f"📰 ['{y}'] 검색 및 파일 저장 완료!\n\n" + "\n".join([f"- {t}" for t in titles])
        else:
            result_text = "⚠️ 네이버 API 호출 실패"
    except Exception as e:
        result_text = f"오류 발생: {str(e)}"

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": result_text}}]
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
