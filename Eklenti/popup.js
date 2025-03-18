document.addEventListener('DOMContentLoaded', function() {
    const csvFileInput = document.getElementById('csvFile');
    const selectFileButton = document.getElementById('selectFile');
    const startProcessButton = document.getElementById('startProcess');
    const statusDiv = document.getElementById('status');

    if (!csvFileInput || !selectFileButton || !startProcessButton || !statusDiv) {
        console.error('Gerekli HTML elementleri bulunamadı!');
        return;
    }

    let selectedFile = null;

    // CSV dosyası seçme butonu
    selectFileButton.addEventListener('click', () => {
        csvFileInput.click();
    });

    // CSV dosyası seçildiğinde
    csvFileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            selectedFile = file;
            startProcessButton.disabled = false;
            showStatus('Dosya seçildi: ' + file.name, 'success');
        }
    });

    // İşlemi başlat butonu
    startProcessButton.addEventListener('click', async () => {
        if (!selectedFile) {
            showStatus('Lütfen önce bir CSV dosyası seçin!', 'error');
            return;
        }

        try {
            startProcessButton.disabled = true;
            selectFileButton.disabled = true;
            showStatus('Dosya okunuyor...', 'success');

            const records = await readCSVFile(selectedFile);
            if (!records || records.length === 0) {
                throw new Error('CSV dosyası boş veya geçersiz format!');
            }

            showStatus('İşlem başlatılıyor...', 'success');

            // Background script'e mesaj gönder
            chrome.runtime.sendMessage({
                action: 'startBatchExtraction',
                records: records
            }, (response) => {
                if (chrome.runtime.lastError) {
                    showStatus('Hata: ' + chrome.runtime.lastError.message, 'error');
                } else if (response && response.status === 'success') {
                    showStatus('İşlem başarıyla tamamlandı!', 'success');
                } else {
                    showStatus('Hata: ' + (response?.message || 'Bilinmeyen hata'), 'error');
                }
                startProcessButton.disabled = false;
                selectFileButton.disabled = false;
            });

        } catch (error) {
            console.error('Hata:', error);
            showStatus('Hata: ' + error.message, 'error');
            startProcessButton.disabled = false;
            selectFileButton.disabled = false;
        }
    });

    // CSV dosyasını okuma fonksiyonu
    async function readCSVFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (event) => {
                try {
                    const csv = event.target.result;
                    const lines = csv.split('\n');
                    const headers = lines[0].split(';');
                    const records = [];

                    for (let i = 1; i < lines.length; i++) {
                        const line = lines[i].trim();
                        if (!line) continue;

                        const values = line.split(';');
                        if (values.length !== headers.length) continue;

                        const record = {};
                        headers.forEach((header, index) => {
                            record[header.trim()] = values[index].trim();
                        });

                        records.push(record);
                    }

                    resolve(records);
                } catch (error) {
                    reject(error);
                }
            };

            reader.onerror = () => reject(new Error('Dosya okuma hatası!'));
            reader.readAsText(file);
        });
    }

    // Durum mesajı gösterme fonksiyonu
    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = type;
        statusDiv.style.display = 'block';
    }
});