# discord nick checker

this simple script generates random Discord usernames and checks if they are available.

## lib

- `httpx`
- `PyYAML`
- `pyopenssl`
- `extvip`

## installation

1. to install the required libraries:

    ```bash
    pip install -r requirements.txt
    ```

2. run the sc:

    ```bash
    python main.py
    ```

## cfg

the script will prompt for the following information:

- Prefix
- Username length
- Numbers and special characters
- Residential proxy information
- Webhook URL (optional)

## notes

- residential proxy kullanmaniz sart.
- used.txt dosyasin da benim checklediklerim var silmeyin o isimleri tekrar uretmesin diye
