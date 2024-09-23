# discord nick checker

bu basit kod rastgele discord kullanici adlari olusturur ve bu adlarin kullanilabilir olup olmadigini kontrol eder

## kutuphaneler

- `httpx`
- `PyYAML`
- `pyopenssl`
- `extvip`

## kurulum

1. kutuphaneleri yuklemek icin:

    ```bash
    pip install -r requirements.txt
    ```

2. calistir:

    ```bash
    python main.py
    ```

## config

yazilimi acinca istenecek bilgiler:

- prefix
- kullanici adi uzunlugu
- sayilar ve ozel karakterler
- residential proxy bilgisi
- webhook url (opt)

## not

- residential proxy kullanmaniz sart.
- renkleri bozuk goruyorsanız microsoft store'den Windows Terminal diye aratıp indirin o terminali kullanin.
- used.txt dosyasin da benim checklediklerim var silmeyin o isimleri tekrar uretmesin diye
