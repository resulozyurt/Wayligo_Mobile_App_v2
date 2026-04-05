import uuid
import httpx
from core.config import settings
from fastapi import UploadFile

def upload_to_supabase(file: UploadFile, bucket: str, folder: str = "general"):
    """
    Dosyayı Supabase Storage'a doğrudan REST API üzerinden yükler.
    Ağır kütüphaneler ve derleme hatalarından tamamen bağımsızdır.
    """
    try:
        # Dosya adını benzersiz yapmak için UUID ekliyoruz
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"
        
        # Dosyanın içindeki byteları okuyoruz
        file_content = file.file.read()
        
        # 1. Supabase Storage Endpoint URL'imizi oluşturuyoruz
        # Format: {SUPABASE_URL}/storage/v1/object/{bucket}/{filename}
        upload_url = f"{settings.SUPABASE_URL}/storage/v1/object/{bucket}/{unique_filename}"
        
        # 2. Yetkilendirme (Service Role Key) ve Dosya Tipini ayarlıyoruz
        headers = {
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": file.content_type
        }
        
        # 3. HTTPX ile doğrudan dosyayı fırlatıyoruz (POST işlemi)
        response = httpx.post(upload_url, headers=headers, content=file_content, timeout=60.0)
        
        # Eğer yükleme başarılıysa (HTTP 200 veya HTTP 201)
        if response.status_code in (200, 201):
            # Dosyanın dışarıdan erişilebilir Public URL'ini oluşturup döndürüyoruz
            public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{unique_filename}"
            return public_url
        else:
            print(f"Supabase Yükleme Hatası: {response.text}")
            return None
            
    except Exception as e:
        print(f"Storage Servis Hatası: {e}")
        return None