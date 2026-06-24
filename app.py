import io
import re
import csv

import streamlit as st


PHONE_COLUMN = "phone"


def normalize_phone(raw_value: str):
    digits = re.sub(r"\D", "", raw_value)

    if digits.startswith("0090"):
        digits = digits[4:]
    elif digits.startswith("90"):
        digits = digits[2:]
    elif digits.startswith("0"):
        digits = digits[1:]

    if len(digits) != 10:
        return None

    return f"+90{digits}"


def extract_phone_numbers(text: str):
    candidates = re.findall(r"(?:\+|00)?\d[\d\s()./-]{8,}\d", text)
    unique_numbers = []
    seen = set()

    for candidate in candidates:
        phone = normalize_phone(candidate)
        if phone and phone not in seen:
            seen.add(phone)
            unique_numbers.append(phone)

    return unique_numbers


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


st.set_page_config(page_title="Dialify", layout="centered")

st.title("Dialify")
st.write("Metin belgesindeki telefon numaralarını temizleyip CSV formatına çevirir.")

uploaded_file = st.file_uploader(
    "Metin belgesi yükle",
    type=["txt", "csv"],
    accept_multiple_files=False,
)

if uploaded_file:
    raw_text = decode_file(uploaded_file.getvalue())
    numbers = extract_phone_numbers(raw_text)

    st.metric("Bulunan tekil numara", len(numbers))

    if numbers:
        st.dataframe([{PHONE_COLUMN: number} for number in numbers], use_container_width=True)
        st.download_button(
            "CSV indir",
            data=convert_to_csv(numbers),
            file_name="phone_numbers.csv",
            mime="text/csv",
        )
    else:
        st.warning("Geçerli telefon numarası bulunamadı.")
else:
    st.info("Başında +90, 90 veya 0 olan Türkiye numaralarını algılar.")
