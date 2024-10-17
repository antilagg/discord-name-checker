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

## notesz

- Residential proxy usage is required.
- Do not delete the `used.txt` file; it contains the usernames I've already checked to avoid generating them again.
