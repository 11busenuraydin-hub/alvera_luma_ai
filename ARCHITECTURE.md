# ALVÉRA Luma AI – Mimari Doküman

## 1. Proje Tanımı
ALVÉRA Luma AI, ALVÉRA cilt bakım markası için geliştirilen Flask tabanlı yapay zekâ destekli web uygulamasıdır.

## 2. Kullanılan Teknolojiler
- Python: Backend geliştirme dili
- Flask: Web uygulaması ve API yönetimi
- Groq API: Yapay zekâ yanıtlarının oluşturulması
- HTML: Kullanıcı arayüzü
- GitHub: Kaynak kodu ve versiyon yönetimi
- Render: Canlı uygulama barındırma

## 3. Sistem Mimarisi
Kullanıcı → Web Arayüzü → Flask Routes → AI Service → Groq API

Groq API tarafından üretilen yanıt, Flask üzerinden kullanıcı arayüzüne iletilir.

## 4. Proje Katmanları
- run.py: Flask uygulamasını başlatır.
- app/__init__.py: Uygulama fabrikası ve başlangıç yapılandırması.
- app/routes.py: HTTP istekleri ve yönlendirmeler.
- app/services/ai_service.py: Yapay zekâ servis entegrasyonu.
- app/templates/: HTML arayüz dosyaları.
- app/database.py: Veritabanı işlemleri için ayrılmış katman.
- config.py: Yapılandırma dosyası.

## 5. Güvenlik
API anahtarı .env dosyasında tutulur ve GitHub'a yüklenmez. Uygulama ortam değişkenleri üzerinden yapılandırılır.

## 6. Proje Bağlantıları
- GitHub: https://github.com/11busenuraydin-hub/alvera_luma_ai
- Canlı Uygulama: https://alvera-luma-ai.onrender.com

## 7. Geliştirme ve Dağıtım
Kodlar yerel geliştirme ortamında hazırlanır, Git ile GitHub'a aktarılır ve Render üzerinde yayınlanır.
