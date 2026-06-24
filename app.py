import csv
import io
import re
from pathlib import Path

import pandas as pd
import streamlit as st


PHONE_COLUMN = "phone"
PHONE_COLUMN_KEYWORDS = ("telefon", "phone", "gsm", "cep", "mobile", "tel")
EXCEL_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}
TEXT_EXTENSIONS = {".txt", ".csv"}


def normalize_phone(raw_value):
    if raw_value is None or pd.isna(raw_value):
        return None

    digits = re.sub(r"\D", "", str(raw_value))

    if digits.endswith("0") and re.search(r"\.0$", str(raw_value).strip()):
        digits = digits[:-1]

    if digits.startswith("0090"):
        digits = digits[4:]
    elif digits.startswith("90"):
        digits = digits[2:]
    elif digits.startswith("0"):
        digits = digits[1:]

    if len(digits) != 10 or not digits.startswith("5"):
        return None

    return f"+90{digits}"


def extract_phone_numbers_from_values(values):
    unique_numbers = []
    seen = set()

    for value in values:
        for candidate in re.findall(r"(?:\+|00)?\d[\d\s()./-]{8,}\d", str(value)):
            phone = normalize_phone(candidate)
            if phone and phone not in seen:
                seen.add(phone)
                unique_numbers.append(phone)

    return unique_numbers


def extract_phone_numbers(text: str):
    return extract_phone_numbers_from_values([text])


def find_phone_columns(dataframe):
    matched_columns = []

    for column in dataframe.columns:
        normalized_name = str(column).strip().casefold()
        if any(keyword in normalized_name for keyword in PHONE_COLUMN_KEYWORDS):
            matched_columns.append(column)

    return matched_columns


def extract_phone_numbers_from_excel(file_bytes: bytes, extension: str):
    engine = "xlrd" if extension == ".xls" else "openpyxl"
    sheets = pd.read_excel(
        io.BytesIO(file_bytes),
        sheet_name=None,
        dtype=str,
        engine=engine,
    )
    values = []

    for dataframe in sheets.values():
        phone_columns = find_phone_columns(dataframe)
        source_columns = phone_columns or dataframe.columns

        for column in source_columns:
            values.extend(dataframe[column].dropna().tolist())

    return extract_phone_numbers_from_values(values)


def extract_phone_numbers_from_upload(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    extension = Path(uploaded_file.name).suffix.casefold()

    if extension in EXCEL_EXTENSIONS:
        return extract_phone_numbers_from_excel(file_bytes, extension)

    return extract_phone_numbers(decode_file(file_bytes))


def convert_to_csv(numbers: list[str]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([PHONE_COLUMN])
    writer.writerows([[number] for number in numbers])
    return output.getvalue().encode("utf-8-sig")


def decode_file(file_bytes: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1254", "latin-1"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return file_bytes.decode("utf-8", errors="ignore")


st.set_page_config(page_title="Alperen Sal Beni", layout="centered")

st.markdown(
    """
    <style>
        :root {
            --bg: #090b10;
            --panel: #11151d;
            --panel-2: #171c26;
            --text: #f7f1e8;
            --muted: #a9b0bd;
            --line: rgba(247, 241, 232, 0.12);
            --orange: #ff7a3d;
            --yellow: #ffd166;
            --green: #35d0a2;
            --red: #ff5f6d;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 122, 61, 0.16), transparent 28rem),
                radial-gradient(circle at bottom right, rgba(53, 208, 162, 0.14), transparent 28rem),
                var(--bg);
            color: var(--text);
        }

        .block-container {
            max-width: 920px;
            padding: 2rem 1.25rem 4rem;
        }

        .roast-shell {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
            background: linear-gradient(180deg, rgba(17, 21, 29, 0.96), rgba(12, 15, 21, 0.98));
            box-shadow: 0 30px 90px rgba(0, 0, 0, 0.42);
        }

        .top-bar {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-bottom: 1px solid var(--line);
            padding: 0.85rem 1rem;
            background: rgba(255, 255, 255, 0.03);
            color: var(--muted);
            font-size: 0.82rem;
            font-weight: 800;
        }

        .dot {
            width: 0.72rem;
            height: 0.72rem;
            border-radius: 999px;
            display: inline-block;
        }

        .dot.red { background: var(--red); }
        .dot.yellow { background: var(--yellow); }
        .dot.green { background: var(--green); }

        .hero {
            padding: 2.25rem 2rem 1.55rem;
        }

        .warning-pill {
            display: inline-flex;
            border: 1px solid rgba(255, 122, 61, 0.35);
            border-radius: 999px;
            padding: 0.45rem 0.75rem;
            background: rgba(255, 122, 61, 0.13);
            color: #ffd1bd;
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0;
            margin-bottom: 1rem;
        }

        .hero h1 {
            max-width: 780px;
            margin: 0;
            color: var(--text);
            font-size: clamp(2.25rem, 6.4vw, 4.9rem);
            line-height: 0.94;
            letter-spacing: 0;
        }

        .hero p {
            max-width: 720px;
            margin: 1rem 0 0;
            color: var(--muted);
            font-size: 1.04rem;
            line-height: 1.65;
        }

        .howto {
            display: grid;
            gap: 0.75rem;
            padding: 0 2rem 2rem;
        }

        .step {
            display: grid;
            grid-template-columns: 2.25rem 1fr;
            gap: 0.85rem;
            align-items: start;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.9rem 1rem;
            background: rgba(255, 255, 255, 0.035);
        }

        .step-num {
            display: grid;
            place-items: center;
            width: 2.25rem;
            height: 2.25rem;
            border-radius: 8px;
            background: var(--orange);
            color: #190b05;
            font-weight: 950;
        }

        .step strong {
            display: block;
            color: var(--text);
            font-size: 0.98rem;
            margin-bottom: 0.2rem;
        }

        .step span {
            color: var(--muted);
            font-size: 0.94rem;
            line-height: 1.5;
        }

        .upload-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin: 1.15rem 0 0.6rem;
            color: var(--text);
            font-size: 1rem;
            font-weight: 900;
        }

        .upload-title span {
            color: var(--muted);
            font-size: 0.84rem;
            font-weight: 800;
        }

        div[data-testid="stFileUploader"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem;
            background: var(--panel);
        }

        div[data-testid="stFileUploader"] section {
            border: 1px dashed rgba(255, 209, 102, 0.45);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.035);
        }

        div[data-testid="stFileUploader"] * {
            color: var(--text) !important;
        }

        div[data-testid="stFileUploader"] small {
            color: var(--muted) !important;
        }

        div[data-testid="stFileUploader"] button {
            border-radius: 8px;
            border: 1px solid rgba(255, 209, 102, 0.35);
            background: #202633;
            color: var(--text) !important;
            font-weight: 900;
        }

        div[data-testid="stMetric"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.85rem 1rem;
            background: var(--panel-2);
        }

        div[data-testid="stMetric"] * {
            color: var(--text) !important;
        }

        .empty-note {
            border: 1px solid var(--line);
            border-left: 5px solid var(--yellow);
            border-radius: 8px;
            padding: 0.95rem 1rem;
            background: var(--panel);
            color: var(--muted);
            line-height: 1.55;
        }

        .empty-note strong {
            color: var(--text);
        }

        .stDownloadButton button {
            width: 100%;
            min-height: 3.15rem;
            border-radius: 8px;
            border: 0;
            background: var(--green);
            color: #04100c;
            font-weight: 950;
        }

        .stDownloadButton button:hover {
            border: 0;
            background: #56e6ba;
            color: #04100c;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
        }

        div[data-testid="stAlert"] {
            border-radius: 8px;
        }

        @media (max-width: 720px) {
            .block-container {
                padding-top: 1rem;
            }

            .hero, .howto {
                padding-left: 1.15rem;
                padding-right: 1.15rem;
            }

            .upload-title {
                align-items: flex-start;
                flex-direction: column;
                gap: 0.25rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="roast-shell">
        <div class="top-bar">
            <span class="dot red"></span>
            <span class="dot yellow"></span>
            <span class="dot green"></span>
            <span>alperen-artık-excel-de-atıyor.exe</span>
        </div>
        <div class="hero">
            <div class="warning-pill">ALPEREN, BAK BU BUTONA BASINCA OLUYOR</div>
            <h1>Artık numara ayıklamak için insan çağırmıyoruz.</h1>
            <p>Alperen dosyayı yüklüyor, site telefon sütununu buluyor, 0212/0216 gibi sabit hatları ayıklıyor, sadece 05xx cep numaralarını <strong>+90</strong> formatında <strong>phone</strong> CSV'sine çeviriyor. Bu kadar, gerçekten bu kadar.</p>
        </div>
        <div class="howto">
            <div class="step"><div class="step-num">1</div><div><strong>TXT, CSV veya Excel dosyasını aşağıya bırak.</strong><span>Excel'de bir sürü kolon varsa sorun değil; telefon, gsm, cep, phone gibi sütunları bulmaya çalışır.</span></div></div>
            <div class="step"><div class="step-num">2</div><div><strong>Site sadece cep numaralarını toplasın.</strong><span>0530 gibi mobil numaralar kalır. 0212 / 0216 gibi sabit hatlar listeye alınmaz.</span></div></div>
            <div class="step"><div class="step-num">3</div><div><strong>CSV indir ve kimseyi tekrar yorma.</strong><span>Tekrarlı numaralar temizlenir. Çıkan dosyada tek kolon vardır: phone.</span></div></div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="upload-title">
        <div>Dosyayı buraya yükle</div>
        <span>TXT, CSV, XLSX, XLS veya XLSM</span>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Metin veya Excel belgesi yükle",
    type=["txt", "csv", "xlsx", "xls", "xlsm"],
    accept_multiple_files=False,
    label_visibility="collapsed",
)

if uploaded_file:
    try:
        numbers = extract_phone_numbers_from_upload(uploaded_file)
    except Exception as error:
        st.error(f"Dosya okunamadı. Alperen, dosya gerçekten Excel/TXT/CSV mi? Detay: {error}")
        numbers = []

    st.markdown(
        """
        <div class="upload-title">
            <div>Sonuç</div>
            <span>Alperen, buradan sonrası indirme butonu</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.metric("Bulunan tekil cep numarası", len(numbers))

    if numbers:
        st.dataframe([{PHONE_COLUMN: number} for number in numbers], use_container_width=True)
        st.download_button(
            "CSV indir",
            data=convert_to_csv(numbers),
            file_name="phone_numbers.csv",
            mime="text/csv",
        )
    else:
        st.warning("Geçerli cep telefonu numarası bulunamadı. Sabit hatları özellikle almıyorum, haberin olsun Alperen.")
else:
    st.markdown(
        """
        <div class="empty-note">
            <strong>Özet:</strong> TXT, CSV veya Excel yükle. Sistem Excel'de telefon sütununu bulur, sadece <strong>05xx</strong> cep numaralarını bırakır, sabit hatları ve tekrarları siler, <strong>phone</strong> sütunlu CSV verir. Olay bu.
        </div>
        """,
        unsafe_allow_html=True,
    )
