import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# المفاتيح الحقيقية والمضبوطة (تم تعديل حرف الـ d)
IMGBB_API_KEY = "6a825e1e8521eff83622a9412abf261b"
SERPAPI_API_KEY = "d5545b36f64268b43d10954c8fd820d6d4c3bef54b830533c3c2fb78d4645b87"

@app.route('/search-image', methods=['POST'])
def search_image():
    if 'image' not in request.files:
        return jsonify({"error": "مفيش صورة وصلت للسيرفر"}), 400
    
    file = request.files['image']
    if file.filename == '':
         return jsonify({"error": "لم يتم اختيار صورة"}), 400

    try:
        # 1. نرفع الصورة على ImgBB
        print("جاري رفع الصورة على ImgBB...")
        imgbb_url = "https://api.imgbb.com/1/upload"
        payload = {"key": IMGBB_API_KEY}
        files = {"image": file.read()}
        
        upload_res = requests.post(imgbb_url, params=payload, files=files)
        upload_data = upload_res.json()
        
        if not upload_data.get("success"):
            return jsonify({"error": "حصلت مشكلة وإحنا بنرفع الصورة"}), 500
            
        image_public_url = upload_data["data"]["url"]
        print(f"تم الرفع بنجاح! الرابط: {image_public_url}")
        
        # 2. نكلم SerpApi للبحث في جوجل لانس
        print("جاري البحث في جوجل لانس...")
        serpapi_url = "https://serpapi.com/search"
        serp_params = {
            "engine": "google_lens",
            "url": image_public_url,
            "api_key": SERPAPI_API_KEY,
            "hl": "ar" # عشان النتايج ترجع بالعربي
        }
        
        serp_res = requests.get(serpapi_url, params=serp_params)
        serp_data = serp_res.json()
        
        print("تم استلام الرد من SerpApi بنجاح!")
        
        if "error" in serp_data:
             return jsonify({"error": f"خطأ من API البحث: {serp_data['error']}"}), 400

        # 3. نستخرج النتايج الحقيقية
        visual_matches = serp_data.get("visual_matches", [])
        matches = []
        
        # هناخد أول 5 نتايج عشان نعرضهم في الكروت
        for match in visual_matches[:5]:
            matches.append({
                "title": match.get("title", "نتيجة مطابقة"),
                "link": match.get("link", "#"),
                # جوجل لو جاب صورة للموقع هيعرضها، لو لأ هيعرض صورتك
                "thumbnail": match.get("thumbnail", image_public_url) 
            })
            
        if not matches:
            return jsonify({"error": "جوجل ملقاش أي مواقع مطابقة للصورة دي!"}), 404
            
        return jsonify({
            "status": "success", 
            "matches": matches
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "حصلت مشكلة فنية في السيرفر"}), 500

if __name__ == '__main__':
    print("=======================================")
    print("السيرفر شغال بالمفاتيح المظبوطة 100%!")
    print("http://127.0.0.1:5000")
    print("=======================================")
    app.run(debug=True, port=5000)