import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_summary(data: dict) -> str:
    """Gemini API kullanarak rapor özeti oluşturur"""
    prompt = f"""
Aşağıdaki haftalık raporu kısa ve anlaşılır bir şekilde özetle:

Tarih: {data.get('date_range', 'Belirtilmemiş')}
Bu hafta yapılanlar: {data.get('done', 'Belirtilmemiş')}
Tamamlanan işler: {data.get('completed', 'Belirtilmemiş')}
Gelecek hafta yapılacaklar: {data.get('next_week', 'Belirtilmemiş')}
Problemler: {data.get('problems', 'Belirtilmemiş')}

Lütfen madde madde ve net bir özet oluştur. Profesyonel bir dille yaz.
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Gemini API hatası: {e}")
        # Hata durumunda basit bir özet döndür
        return f"""
HAFTALIK RAPOR ÖZETİ

📅 Tarih: {data.get('date_range', 'Belirtilmemiş')}

✅ Bu Hafta Yapılanlar:
{data.get('done', 'Belirtilmemiş')}

🏁 Tamamlanan İşler:
{data.get('completed', 'Belirtilmemiş')}

➡️ Gelecek Hafta:
{data.get('next_week', 'Belirtilmemiş')}

⚠️ Problemler:
{data.get('problems', 'Belirtilmemiş')}
"""