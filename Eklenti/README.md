# Amazon Product Review Scraper Extension

Bu Chrome uzantısı, Amazon.de üzerindeki ürün açıklamalarını ve kategorilerini toplu olarak çekmenizi ve CSV formatında kaydetmenizi sağlar.

## Özellikler

- Toplu ASIN işleme
- Paralel sekme yönetimi (5 sekme eş zamanlı)
- Otomatik kategori ve açıklama çekme
- CSV formatında dışa aktarma
- Performans optimizasyonu

## Kurulum

1. Bu repoyu bilgisayarınıza klonlayın
2. Chrome tarayıcınızda `chrome://extensions/` adresine gidin
3. Geliştirici modunu açın (sağ üst köşedeki düğme)
4. "Paketlenmemiş öğe yükle" seçeneğini tıklayın
5. Klonladığınız repo klasörünü seçin

## Kullanım

1. Uzantı simgesine tıklayarak popup penceresini açın
2. ASIN'leri her satıra bir tane gelecek şekilde giriş alanına yapıştırın
3. "Başlat" düğmesine tıklayın
4. İşlem tamamlandığında CSV dosyası otomatik olarak indirilecektir

## Dosya Yapısı

- `manifest.json`: Uzantı yapılandırması
- `popup.html` ve `popup.js`: Kullanıcı arayüzü
- `content.js`: Sayfa içi işlemler
- `amazon_batch_scraper.js`: Ana işlem mantığı

## Teknik Detaylar

- Manifest V3 kullanılmıştır
- Paralel işlem için Chrome Tabs API kullanılmıştır
- Performans optimizasyonu için gereksiz içerik yüklenmesi engellenir
- CSV çıktısı UTF-8 formatında oluşturulur

## İzinler

- `activeTab`: Aktif sekme erişimi
- `scripting`: Sayfa içi script çalıştırma
- `tabs`: Sekme yönetimi
- `downloads`: CSV indirme

## Host İzinleri

- `*://*.amazon.de/*`: Amazon.de domain erişimi

## Güvenlik

- Sadece Amazon.de domaininde çalışır
- Hassas veri toplanmaz
- Kullanıcı verisi saklanmaz

## Performans

- 5 paralel sekme ile hızlı veri çekimi
- Gereksiz içerik yüklenmesini engelleyen optimizasyonlar
- Otomatik sekme kapatma ile bellek yönetimi