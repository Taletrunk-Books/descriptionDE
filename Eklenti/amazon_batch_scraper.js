let csvContent = "id;ean;asin;rank;sp1_stock;sp2_stock;kategori;açıklama\n";
let currentBatchNumber = 0;
let batchSize = 20;
let totalProcessed = 0;

// API endpoint'i
const API_URL = 'http://localhost:8000/api/v1/amazon/batch';
const BATCH_STATUS_URL = 'http://localhost:8000/api/v1/amazon/batch-status';

async function closeTab(tabId) {
    try {
        await chrome.tabs.remove(tabId);
        console.log(`Sekme kapatıldı: ${tabId}`);
    } catch (error) {
        console.error(`Sekme kapatma hatası (${tabId}):`, error);
    }
}

// Kategori çekme fonksiyonu
function extractCategory() {
    try {
        // Önce normal kategori elementlerini kontrol et
        const categoryElement = document.querySelector('#wayfinding-breadcrumbs_feature_div') ||
                              document.querySelector('#nav-subnav .nav-a-content');

        if (categoryElement) {
            // HTML etiketlerini temizle ve metni düzenle
            return categoryElement.textContent
                .replace(/\s+/g, ' ')
                .trim();
        }

        // Eğer normal kategori bulunamazsa, aplus_feature_div içindeki kategoriyi kontrol et
        const aplusDiv = document.getElementById('aplus_feature_div');
        if (aplusDiv) {
            const categoryText = aplusDiv.querySelector('h2')?.textContent;
            if (categoryText) {
                return categoryText.trim();
            }
        }

        return 'Kategori bulunamadı';
    } catch (error) {
        console.error('Kategori çekme hatası:', error);
        return 'Hata: Kategori çekilemedi';
    }
}

// Açıklama çekme fonksiyonu
function getDescription() {
    try {
        // Ürün açıklaması elementini bul
        const descriptionElement = document.querySelector('#feature-bullets .a-list-item') || 
                                 document.querySelector('#bookDescription_feature_div .a-expander-content');

        if (descriptionElement) {
            // HTML etiketlerini temizle ve metni düzenle
            return descriptionElement.textContent
                .replace(/\s+/g, ' ')
                .trim();
        }
 

        // Eğer normal açıklama bulunamazsa, aplus_feature_div içindeki a-spacing-base sınıfına sahip paragrafı kontrol et
        const aplusDiv = document.getElementById('aplus_feature_div');
        if (aplusDiv) {
            const descriptionParagraph = aplusDiv.querySelector('p.a-spacing-base');
            if (descriptionParagraph) {
                return descriptionParagraph.textContent
                    .replace(/\s+/g, ' ')
                    .trim();
            }
        }
// Önce normal açıklama alanlarını kontrol et
        const descriptionElement1 = document.querySelector('#feature-bullets .a-list-item') || 
        document.querySelector('#productDescription p span') ||
        document.querySelector('#productDescription p') ||
        document.querySelector('#bookDescription_feature_div .a-expander-content');

        if (descriptionElement1) {
        // Eğer span elementi varsa, tüm span'leri birleştir
        if (descriptionElement1.tagName === 'SPAN') {
            const spans = document.querySelectorAll('#productDescription p span');
            return Array.from(spans)
                .map(span => span.textContent)
                .join(' ')
                .replace(/\s+/g, ' ')
                .trim();
        }

        return descriptionElement1.textContent
            .replace(/\s+/g, ' ')
            .trim();
        }
        return 'Veri çekilemedi';
    } catch (error) {
        // Önce normal açıklama alanlarını kontrol et
        const descriptionElement = document.querySelector('#feature-bullets .a-list-item') || 
        document.querySelector('#productDescription p span') ||
        document.querySelector('#productDescription p') ||
        document.querySelector('#bookDescription_feature_div .a-expander-content');

        if (descriptionElement) {
        // Eğer span elementi varsa, tüm span'leri birleştir
        if (descriptionElement.tagName === 'SPAN') {
            const spans = document.querySelectorAll('#productDescription p span');
            return Array.from(spans)
                .map(span => span.textContent)
                .join(' ')
                .replace(/\s+/g, ' ')
                .trim();
        }

        return descriptionElement.textContent
            .replace(/\s+/g, ' ')
            .trim();
        }
        console.error('Açıklama çekme hatası:', error);
        return 'Veri çekilemedi111111';
    }
}

// Sayfa yükleme optimizasyonu için script
function injectOptimizationScript() {
    // Gereksiz resimleri kaldır
    const images = document.getElementsByTagName('img');
    for (let img of images) {
        img.remove();
    }

    // Gereksiz scriptleri kaldır
    const scripts = document.getElementsByTagName('script');
    for (let script of scripts) {
        script.remove();
    }

    // Gereksiz stilleri kaldır
    const styles = document.getElementsByTagName('style');
    for (let style of styles) {
        style.remove();
    }
}

// ASIN'leri gruplara böl
function chunkArray(array, size) {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
        chunks.push(array.slice(i, i + size));
    }
    return chunks;
}

// ASIN format düzeltme fonksiyonu
function normalizeAsin(asin) {
    if (!asin) return null;
    
    // Boşlukları temizle
    asin = asin.toString().trim();
    
    // Sadece rakam ve harflerden oluşan karakterleri al
    asin = asin.replace(/[^A-Z0-9]/gi, '');
    
    // 10 karakterden kısa ve sadece rakamlardan oluşuyorsa başına 0 ekle
    if (asin.length < 10 && /^\d+$/.test(asin)) {
        asin = '0'.repeat(10 - asin.length) + asin;
    }
    
    // ASIN formatı kontrolü
    if (asin.length !== 10) {
        console.warn(`Geçersiz ASIN uzunluğu: ${asin}`);
        return null;
    }
    
    return asin.toUpperCase();
}

// Toplu veri gönderme fonksiyonu
async function sendBatchToApi(products) {
    try {
        const response = await fetch('http://localhost:8000/api/v1/amazon/process-batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ products })
        });

        if (!response.ok) {
            throw new Error(`API Hatası: ${response.status}`);
        }

        const data = await response.json();
        console.log('Batch işleme sonucu:', data);
        
        return data;
    } catch (error) {
        console.error('Batch gönderme hatası:', error);
        // Hata durumunda 3 kez yeniden dene
        for (let i = 0; i < 3; i++) {
            try {
                await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                const response = await fetch('http://localhost:8000/api/v1/amazon/process-batch', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ products })
                });
                if (response.ok) {
                    return await response.json();
                }
            } catch (retryError) {
                console.error(`Yeniden deneme ${i + 1} başarısız:`, retryError);
            }
        }
        throw error;
    }
}

// CSV indirme fonksiyonunu güncelle
function downloadCSV(data) {
    let csvContent = "id;ean;asin;rank;sp1_stock;sp2_stock;kategori;açıklama\n";
    
    data.forEach(item => {
        const row = [
            item.id,
            item.ean,
            item.asin,
            item.rank,
            item.sp1_stock,
            item.sp2_stock,
            item.category || '',
            item.description || ''
        ].join(';');
        csvContent += row + '\n';
    });

    // CSV'yi indir
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'amazon_descriptions_final.csv';
    link.click();
}

// İlerleme durumunu güncelle
function updateProgress(current, total) {
    const progress = Math.round((current / total) * 100);
    console.log(`İlerleme: ${progress}% (${current}/${total})`);
}

// Tek bir ASIN için veri çekme işlemi
async function processSingleAsin(record, tab) {
    try {
        // Sayfayı yükle
        await chrome.tabs.update(tab.id, {
            url: `https://www.amazon.de/dp/${record.asin}`
        });

        // Sayfanın yüklenmesini bekle
        await new Promise((resolve) => {
            const timeout = setTimeout(() => {
                chrome.tabs.onUpdated.removeListener(listener);
                resolve();
            }, 5000);

            function listener(tabId, info) {
                if (tabId === tab.id && info.status === 'complete') {
                    clearTimeout(timeout);
                    chrome.tabs.onUpdated.removeListener(listener);
                    resolve();
                }
            }
            chrome.tabs.onUpdated.addListener(listener);
        });

        // Optimizasyon scriptini enjekte et
        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            function: injectOptimizationScript
        }).catch(() => null);

        // Kısa bekleme
        await new Promise(resolve => setTimeout(resolve, 500));

        // Veri çekme
        const [descriptionResult, categoryResult, titleResult] = await Promise.all([
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: getDescription
            }).catch(() => [{ result: 'Veri çekilemedi' }]),
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: extractCategory
            }).catch(() => [{ result: 'Veri çekilemedi' }]),
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: getTitle
            }).catch(() => [{ result: 'Veri çekilemedi' }])
        ]);

        return {
            category: categoryResult[0]?.result || 'Veri çekilemedi',
            description: descriptionResult[0]?.result || 'Veri çekilemedi',
            title: titleResult[0]?.result || 'Veri çekilemedi'
        };
    } catch (error) {
        console.error(`ASIN işleme hatası (${record.asin}):`, error);
        return null;
    }
}

// Batch durumunu kontrol et
async function checkBatchStatus(totalProducts) {
    try {
        const response = await fetch(`http://localhost:8000/api/v1/amazon/batch-status?total_products=${totalProducts}&batch_size=20`);
        
        if (!response.ok) {
            throw new Error(`API Hatası: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Batch durumu:', data);
        
        return data;
    } catch (error) {
        console.error('Batch durumu kontrol hatası:', error);
        // Hata durumunda 3 kez yeniden dene
        for (let i = 0; i < 3; i++) {
            try {
                await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                const response = await fetch(`http://localhost:8000/api/v1/amazon/batch-status?total_products=${totalProducts}&batch_size=20`);
                if (response.ok) {
                    return await response.json();
                }
            } catch (retryError) {
                console.error(`Yeniden deneme ${i + 1} başarısız:`, retryError);
            }
        }
        throw error;
    }
}

// Batch numarasını storage'dan al
async function getLastBatchNumber() {
    try {
        const result = await chrome.storage.local.get('lastBatchNumber');
        return result.lastBatchNumber || 0;
    } catch (error) {
        console.error('Batch numarası alınamadı:', error);
        return 0;
    }
}

// Batch numarasını storage'a kaydet
async function saveBatchNumber(batchNumber) {
    try {
        await chrome.storage.local.set({ lastBatchNumber: batchNumber });
        console.log('Batch numarası kaydedildi:', batchNumber);
    } catch (error) {
        console.error('Batch numarası kaydedilemedi:', error);
    }
}

// processAsins fonksiyonunu güncelle
async function processAsins(records, startBatch = 0) {
    console.log('İşlem başlıyor...');
    const results = [];
    const totalRecords = records.length;
    let processedCount = 0;

    // ASIN'leri normalize et ve geçersiz olanları filtrele
    const validRecords = records.filter(record => {
        const normalizedAsin = normalizeAsin(record.asin);
        return normalizedAsin && normalizedAsin.length === 10;
    });

    const invalidRecords = records.filter(record => {
        const normalizedAsin = normalizeAsin(record.asin);
        return !normalizedAsin || normalizedAsin.length !== 10;
    });

    console.log(`Toplam kayıt: ${totalRecords}`);
    console.log(`Geçerli ASIN: ${validRecords.length}`);
    console.log(`Geçersiz ASIN: ${invalidRecords.length}`);
    console.log(`Başlangıç batch numarası: ${startBatch}`);

    // Batch durumunu kontrol et
    const batchStatus = await checkBatchStatus(validRecords.length);
    let currentBatch = startBatch;
    
    if (batchStatus && batchStatus.last_completed_batch > 0 && startBatch === 0) {
        currentBatch = batchStatus.last_completed_batch;
        console.log(`Kaldığı yerden devam ediliyor: Batch ${currentBatch}`);
    }

    // 10 sekme oluştur
    const tabs = [];
    for (let i = 0; i < 10; i++) {
        const tab = await chrome.tabs.create({
            url: 'https://www.amazon.de/dp/null',
            active: false
        });
        tabs.push(tab);
    }

    // Ana batch'leri oluştur
    for (let i = currentBatch * batchSize; i < validRecords.length; i += batchSize) {
        const batch = validRecords.slice(i, i + batchSize);
        const currentBatchNumber = Math.floor(i / batchSize) + 1;
        console.log(`\nBatch ${currentBatchNumber} başlıyor (${batch.length} kayıt)`);

        // Her batch'i 10'ar kayıtlık gruplara böl
        for (let j = 0; j < batch.length; j += 10) {
            const chunk = batch.slice(j, j + 10);
            console.log(`\nChunk ${Math.floor(j / 10) + 1} işleniyor (${chunk.length} kayıt)`);

            // Her ASIN için ilgili sekmeyi kullan
            const promises = chunk.map(async (record, index) => {
                const tab = tabs[index];
                try {
                    const result = await processSingleAsin(record, tab);
                    if (result) {
                        const productData = {
                            id: record.id,
                            ean: record.ean,
                            asin: record.asin,
                            rank: record.rank,
                            sp1_stock: record.sp1_stock,
                            sp2_stock: record.sp2_stock,
                            category: result.category,
                            description: result.description,
                            title: result.title
                        };
                        console.log('İşlenen ürün:', productData);
                        results.push(productData);
                    }
                } catch (error) {
                    console.error(`ASIN işleme hatası (${record.asin}):`, error);
                }
            });

            await Promise.all(promises);
            processedCount += chunk.length;
            updateProgress(processedCount, validRecords.length);
        }

        // Her batch sonunda API'ye gönder
        if (results.length > 0) {
            try {
                console.log(`Batch ${currentBatchNumber} API'ye gönderiliyor...`);
                await sendBatchToApi(results);
                console.log(`Batch ${currentBatchNumber} başarıyla kaydedildi`);
                
                // Batch numarasını kaydet
                await saveBatchNumber(currentBatchNumber);
                
                // Sonuçları temizle
                results.length = 0;
            } catch (error) {
                console.error('API Hatası:', error);
                // Hata durumunda kaldığımız batch'i kaydet
                console.log(`Hata nedeniyle Batch ${currentBatchNumber}'de duruldu`);
                await saveBatchNumber(currentBatchNumber);
                break;
            }
        }
    }

    // Tüm sekmeleri kapat
    for (const tab of tabs) {
        try {
            await chrome.tabs.remove(tab.id);
        } catch (error) {
            console.error('Sekme kapatma hatası:', error);
        }
    }

    console.log('\nİşlem tamamlandı!');
    updateProgress(validRecords.length, validRecords.length);
}

// Mesaj dinleyici
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'startBatchExtraction') {
        console.log('Toplu çekme işlemi başlatılıyor...');
        
        // İşlemi başlat ve sonucu bekle
        processAsins(message.records, message.startBatch)
            .then(() => {
                console.log('İşlem başarıyla tamamlandı');
                sendResponse({ status: 'success', message: 'İşlem tamamlandı' });
            })
            .catch(error => {
                console.error('İşlem hatası:', error);
                sendResponse({ status: 'error', message: error.message });
            });
        
        // Asenkron işlem için true döndür
        return true;
    }
});

// Background script yüklendiğinde
console.log('Background script yüklendi');

function getTitle() {
    try {
        // Önce productTitle elementini kontrol et
        const titleElement = document.getElementById('productTitle');
        if (titleElement) {
            return titleElement.textContent.trim();
        }

        // Eğer bulunamazsa, h1 elementini kontrol et
        const h1Element = document.querySelector('h1');
        if (h1Element) {
            return h1Element.textContent.trim();
        }

        // Son olarak, aplus_feature_div içindeki h2 elementini kontrol et
        const aplusDiv = document.getElementById('aplus_feature_div');
        if (aplusDiv) {
            const h2Element = aplusDiv.querySelector('h2');
            if (h2Element) {
                return h2Element.textContent.trim();
            }
        }

        return 'Veri çekilemedi';
    } catch (error) {
        console.error('Başlık çekme hatası:', error);
        return 'Veri çekilemedi';
    }
}