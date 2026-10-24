# Digital Footprint Checker

A bulk tool for investigators: upload an Excel list of mobile numbers (or type them in), and get back one formatted Excel report showing, for each number, whether it appears on **WhatsApp, Telegram, Instagram, Facebook and Snapchat**.

I first built this during my internship at the Indian Cyber Crime Coordination Centre (I4C), Ministry of Home Affairs, to replace a manual, one-number-at-a-time process.

> **This public version is a safe re-implementation.** The platform checkers in `engine/` are **stubs that return simulated results** — the real lookup logic and any real data are not included. Everything around them (input handling, number normalisation, bulk pipeline, web UI, Excel reporting) is the real thing. The sample input uses fictional numbers.

**Stack:** Python · Flask · pandas · openpyxl · JavaScript · HTML/CSS

---

## How it works

```
Excel upload / manual entry ─▶ normalise (+91 format) ─▶ run each platform checker ─▶ results table ─▶ formatted Excel report
```

- **`core/normalizer.py`** cleans numbers the way they actually arrive from spreadsheets: Excel floats like `9000000001.0`, spaces, `91…` and `+91…` prefixes. Anything that isn't a valid Indian mobile number is skipped and logged, not guessed.
- **`core/bulk_runner.py`** reads the sheet, normalises each number, calls every checker in `engine/`, and writes one row per number with a timestamp.
- **`engine/*.py`** — one module per platform, each exposing `signal(number) -> bool`. Adding a platform means adding one file.
- **`core/decision.py`** — a weighted score across platforms for a single "active online" verdict.
- **`FOOTPRINT_UI/`** — Flask web app: add numbers by hand or upload a sheet, process, and download a styled Excel report (colour-coded YES/NO, styled header, auto-sized columns).

## Run it

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Command line, using the sample sheet:

```bash
python main.py           # reads input/numbers.xlsx, writes output/results.xlsx
```

Web UI:

```bash
cd FOOTPRINT_UI
python app.py            # http://127.0.0.1:5000
```

The input sheet needs a column named `Mobile Number`.

## Privacy

Phone numbers are personal data. Uploaded files and generated reports are written to `FOOTPRINT_UI/temp_uploads/` and `temp_outputs/`, which are git-ignored so they can never be committed by accident. File names coming from the browser are reduced to their base name before use, so a request can't read or write outside those folders.

## Author

Anand Kumar — B.S. Data Science & AI, IIT Guwahati · [GitHub](https://github.com/anand-kumar011) · [LinkedIn](https://linkedin.com/in/anandk0040)
