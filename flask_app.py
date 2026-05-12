from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

IMGBB_API_KEY = "6a825e1e8521eff83622a9412abf261b"
SERPAPI_API_KEY = "d5545b36f64268b43d10954c8fd820d6d4c3bef54b830533c3c2fb78d4645b87"

@app.route('/search-image', methods=['POST', 'GET'])
def search_image():
    if request.method == 'GET':
        return "السيرفر شغال وزي الفل يا هندسة! ارجع للموقع وارفع الصورة.", 200

    if 'image' not in request.files:
        return jsonify({"error": "مفيش صورة وصلت"}), 400
    
    file = request.files['image']
    try:
        imgbb_url = "https://api.imgbb.com/1/upload"
        upload_res = requests.post(imgbb_url, params={"key": IMGBB_API_KEY}, files={"image": file.read()})
        upload_json = upload_res.json()
        
        if "data" not in upload_json:
            return jsonify({"error": "مشكلة في رفع الصورة على ImgBB"})
            
        image_public_url = upload_json["data"]["url"]
        
        serp_params = {
            "engine": "google_lens",
            "url": image_public_url,
            "api_key": SERPAPI_API_KEY,
            "hl": "ar"
        }
        serp_res = requests.get("https://serpapi.com/search", params=serp_params)
        serp_data = serp_res.json()
        
        if "error" in serp_data:
            return jsonify({"error": f"رسالة من API البحث: {serp_data['error']}", "image_url": image_public_url})
            
        visual_matches = serp_data.get("visual_matches", [])
        
        if not visual_matches:
            return jsonify({"error": "جوجل ملقاش كروت مشابهة للصورة.", "image_url": image_public_url})
            
        matches = []
        for match in visual_matches[:5]:
            # هنا بنحاول نسحب الصورة الأصلية لو موجودة
            full_res_image = match.get("original", match.get("image", match.get("thumbnail", image_public_url)))
            
            matches.append({
                "title": match.get("title", "نتيجة مطابقة"),
                "link": match.get("link", "#"),
                "thumbnail": match.get("thumbnail", image_public_url),
                "full_image": full_res_image # ضفنا الرابط الجديد هنا
            })
            
        return jsonify({"status": "success", "matches": matches, "image_url": image_public_url})
        
    except Exception as e:
        return jsonify({"error": f"خطأ فني: {str(e)}"}), 500
