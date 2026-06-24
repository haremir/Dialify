# Dialify

TXT, CSV veya Excel dosyalarındaki telefon numaralarını temizleyip `phone` sütunlu CSV dosyasına çeviren basit Streamlit uygulaması.

## Özellikler

- `.txt`, `.csv`, `.xlsx`, `.xls` ve `.xlsm` dosyası yükleme
- Excel dosyalarında `telefon`, `phone`, `gsm`, `cep`, `mobile`, `tel` gibi sütunları otomatik yakalama
- Sadece Türkiye cep telefonu numaralarını alma (`05xx` / `+905xx`)
- `0212`, `0216` gibi sabit hatları ayıklama
- Telefon numaralarını `+90` formatına çevirme
- Tekrar eden numaraları temizleme
- `phone` sütunlu CSV indirme

## Çalıştırma

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud

Streamlit Cloud ayarlarında main file path olarak `app.py` seçilmesi yeterlidir.