# 🍽️ PantauGizi Dashboard

PantauGizi Dashboard merupakan aplikasi visualisasi data berbasis Streamlit yang dikembangkan untuk mendukung program **Makan Bergizi Gratis (MBG)** melalui analisis nutrisi menu, profil antropometri siswa, serta sentimen umpan balik orang tua.

Dashboard ini mengintegrasikan tiga sumber data utama:

1. Dataset Menu Makanan (Dinner Recommendation)
2. Dataset Antropometri Siswa (Anthropometric Analysis)
3. Dataset Feedback Orang Tua (Parent Feedback Analysis)

---

## 🚀 Setup Environment

### Menggunakan Anaconda

```bash
conda create --name pantau-gizi-ds python=3.9
conda activate pantau-gizi-ds
pip install -r requirements.txt
```

### Menggunakan Virtual Environment

```bash
python -m venv venv

# MacOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

---

## ▶️ Menjalankan Dashboard

```bash
streamlit run main.py
```

Setelah berhasil dijalankan, aplikasi dapat diakses melalui:

```text
https://dashboardpantaugizi.streamlit.app
```

---

## 📂 Struktur Proyek

```text
pantaugizi-dashboard/
│
├── main.py
├── requirements.txt
├── README.md
│
├── train_gizi.csv
├── train_bmi.csv
├── feedback_train.csv
├── feedback_val.csv
```

---

# Dashboard Features

## 1. Overview

Menampilkan ringkasan proyek dan statistik utama dataset:

- Total menu makanan
- Total data siswa
- Total feedback orang tua
- Jumlah aspek ABSA

Serta snapshot visual:

- Distribusi menu berdasarkan kategori Isi Piringku
- Distribusi status gizi siswa
- Distribusi sentimen feedback orang tua

---

## 2. Dinner Recommendation

Analisis nutrisi menu berdasarkan pedoman **Isi Piringku**.

### Pertanyaan Analisis

**Q1. Bagaimana distribusi rata-rata makronutrien dan energi pada tiap kategori Isi Piringku?**

Visualisasi:

- Distribusi kategori makanan
- Rata-rata makronutrien per kategori
- Radar chart profil nutrisi
- Distribusi energi per kategori
- Korelasi makronutrien
- Top menu berdasarkan energi dan protein

---

## 3. Anthropometric Analysis

Analisis status gizi dan kebutuhan energi siswa berdasarkan data antropometri.

### Pertanyaan Analisis

**Q2. Bagaimana kebutuhan kalori dan makronutrien siswa berdasarkan status gizi dan jenjang sekolah?**

Visualisasi:

- Distribusi status gizi
- Distribusi stunting
- Distribusi usia dan gender
- BMR per jenjang sekolah
- BMR per status gizi
- Kebutuhan makronutrien harian

---

## 4. Parent Feedback Analysis

Analisis sentimen umpan balik orang tua menggunakan pendekatan **Aspect-Based Sentiment Analysis (ABSA)**.

### Pertanyaan Analisis

**Q3. Bagaimana perbandingan ulasan positif dan negatif pada aspek rasa, porsi, dan kebersihan?**

Visualisasi:

- Distribusi sentimen per aspek
- Persentase sentimen
- Distribusi rating
- Heatmap aspek dan sentimen
- Ringkasan hasil ABSA

---

# Data Dictionary

## Dataset 1 — train_gizi.csv

Dataset informasi menu makanan dan kandungan gizinya.

| Kolom | Tipe Data | Deskripsi |
|---------|---------|---------|
| kode | String | Kode unik menu makanan |
| nama | String | Nama menu makanan |
| kategori | String | Kategori bahan makanan |
| isi_piringku | String | Kelompok pangan berdasarkan pedoman Isi Piringku |
| energi_kkal_per_100g | Float | Kandungan energi per 100 gram |
| protein | Float | Skor relatif kandungan protein |
| lemak | Float | Skor relatif kandungan lemak |
| karbohidrat | Float | Skor relatif kandungan karbohidrat |

### Kategori Isi Piringku

- Makanan Pokok
- Lauk-Pauk
- Sayuran
- Buah-buahan

---

## Dataset 2 — train_bmi.csv

Dataset antropometri siswa untuk analisis status gizi dan kebutuhan energi.

| Kolom | Tipe Data | Deskripsi |
|---------|---------|---------|
| age_group | String | Jenjang pendidikan siswa |
| gender | Integer | Jenis kelamin (1 = Laki-laki, 0 = Perempuan) |
| nutritional_status | String | Status gizi berdasarkan BMI-for-age |
| stunting_status | String | Status stunting siswa |
| bmr_kcal | Float | Nilai BMR (Basal Metabolic Rate) yang telah dinormalisasi |
| protein_g | Float | Kebutuhan protein harian |
| lemak_g | Float | Kebutuhan lemak harian |
| karbo_g | Float | Kebutuhan karbohidrat harian |

### Jenjang Sekolah

- PAUD
- TK
- SD
- SMP
- SMA/SMK

### Status Gizi

- Sangat Kurus
- Kurus
- Normal
- Kelebihan Berat Badan
- Obesitas

### Status Stunting

- Normal
- Stunting
- Stunting Berat

---

## Dataset 3 — feedback_train.csv & feedback_val.csv

Dataset ulasan orang tua yang digunakan untuk Aspect-Based Sentiment Analysis (ABSA).

| Kolom | Tipe Data | Deskripsi |
|---------|---------|---------|
| final_text | Text | Teks ulasan yang telah dibersihkan |
| rating | Integer | Rating ulasan (1–5) |
| aspect | String | Aspek yang dibahas dalam ulasan |
| label | String | Label sentimen |

### Aspek ABSA

- rasa
- porsi
- kebersihan

### Label Sentimen

- positif
- negatif

---

# 🎯 Business Questions

### Q1. Dinner Recommendation

Bagaimana distribusi rata-rata makronutrien dan energi pada tiap kategori Isi Piringku?

### Q2. Anthropometric Analysis

Bagaimana kebutuhan kalori dan makronutrien siswa berdasarkan status gizi dan jenjang sekolah?

### Q3. Parent Feedback Analysis

Bagaimana perbandingan ulasan positif dan negatif pada aspek rasa, porsi, dan kebersihan?

---

# Tech Stack

- Python 3.9
- Streamlit
- Pandas
- NumPy
- Plotly
- Streamlit Option Menu

---

# 👨‍💻 Tim Pengembang

| ID Peserta | Nama | Role | Status |
|------------|------|------|---------|
| CDCC281D6X0002 | T. Sofia Chairani | Data Scientist | Aktif |
| CDCC359D6Y0603 | Raihan Okta Rahman | Data Scientist | Aktif |
| CACC833D6Y2370 | Muhammad Ubaidillah Rosyid | AI Engineer | Aktif |
| CFCC005D6X2030 | Lauren Tamara Wijaya | FullStack Developer | Aktif |
