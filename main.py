from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Page config
st.set_page_config(
    page_title="PantauGizi Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Path setup 
APP_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

GIZI_PATH          = APP_DIR / "train_gizi.csv"
BMI_PATH           = APP_DIR / "train_bmi.csv"
FEEDBACK_TRAIN_PATH = APP_DIR / "feedback_train.csv"
FEEDBACK_VAL_PATH   = APP_DIR / "feedback_val.csv"

# COLOUR PALETTE
# Palet utama kategori makanan
GREEN_PALETTE = [
    "#0077B6",  # biru laut (Makanan Pokok)
    "#00B4D8",  # cyan terang (Lauk-Pauk)
    "#52B788",  # hijau sage (Sayuran)
    "#F4A261",  # oranye pastel (Buah-buahan)
    "#E76F51",  # oranye tua cadangan
    "#A8DADC",  # aqua muda cadangan
]

# Makronutrien dengan warna yang konsisten untuk memudahkan pengenalan visual di seluruh dashboard
NUTRISI_COLORS = {
    "protein":     "#2196F3",   # biru cerah
    "lemak":       "#FF9800",   # amber
    "karbohidrat": "#9C27B0",   # ungu
}

# Status gizi dengan warna yang konsisten untuk memudahkan pengenalan visual di seluruh dashboard
BMI_COLORS = {
    "Sangat Kurus":          "#5C85D6",   # biru medium (kekurangan ekstrim)
    "Kurus":                 "#74C0FC",   # biru muda
    "Normal":                "#40C057",   # hijau segar ✓
    "Kelebihan Berat Badan": "#FFB347",   # oranye pastel
    "Obesitas":              "#E03131",   # merah tegas
}

# Sentimen teal positif dan coral negatif untuk analisis feedback orang tua, memberikan kontras yang jelas dan mudah dikenali di seluruh visualisasi terkait sentimen.
SENTIMENT_COLORS = {
    "positif": "#00897B",   # teal
    "negatif": "#E53935",   # merah coral
}

# Urutan kategori untuk memastikan konsistensi visual di seluruh grafik yang menampilkan kelompok pangan, jenjang sekolah, dan status gizi.
FOOD_ORDER   = ["Makanan Pokok","Lauk-Pauk","Sayuran","Buah-buahan"]
AGE_ORDER    = ["PAUD","TK","SD","SMP","SMA/SMK"]
STATUS_ORDER = ["Sangat Kurus","Kurus","Normal","Kelebihan Berat Badan","Obesitas"]

# Custom CSS untuk styling dashboard
st.markdown("""
<style>
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #1b5e20 !important;
    font-size: 24px !important;
    font-weight: 800 !important;
}
h1,h2,h3 { color:#1b5e20 !important; font-weight:700 !important; }
hr { border-color:#c8e6c9; }
.insight-box {
    background:#f7faf8;
    border-left:5px solid #2e7d32;
    border-radius:0 14px 14px 0;
    padding:16px 18px;
    margin:10px 0 16px 0;
    font-size:14px;
    line-height:1.7;
    color:#2b2b2b;
}
.small-card {
    background:#ffffff;
    border:1px solid #e3f2e3;
    border-radius:16px;
    padding:16px;
    box-shadow:0 8px 24px rgba(27,94,32,0.06);
}
</style>
""", unsafe_allow_html=True)

# Helper functions
def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def fig_layout(fig, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e8f5e9", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#e8f5e9", zeroline=False)
    return fig


def add_section_title(title: str, subtitle: str = "") -> None:
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f"<p style='color:#5f6b66;font-size:13px;margin-top:-10px;'>{subtitle}</p>",
                    unsafe_allow_html=True)


def insight_box(html: str) -> None:
    st.markdown(f"<div class='insight-box'>{html}</div>", unsafe_allow_html=True)

# Data loading
@st.cache_data
def load_data():
    # Gizi
    df_gizi = safe_read_csv(GIZI_PATH)
    if not df_gizi.empty:
        df_gizi.columns = [c.strip().lower() for c in df_gizi.columns]
        df_gizi["energi_kkal_per_100g"] = pd.to_numeric(
            df_gizi.get("energi_kkal_per_100g", pd.Series(dtype=float)), errors="coerce"
        )
        df_gizi["isi_piringku"] = df_gizi["isi_piringku"].astype(str).str.strip()

    # BMI
    df_bmi = safe_read_csv(BMI_PATH)
    if not df_bmi.empty:
        df_bmi.columns = [c.strip().lower() for c in df_bmi.columns]
        df_bmi["age_group"] = pd.Categorical(
            df_bmi["age_group"], categories=AGE_ORDER, ordered=True
        )
        df_bmi["nutritional_status"] = pd.Categorical(
            df_bmi["nutritional_status"], categories=STATUS_ORDER, ordered=True
        )
        df_bmi["gender_label"] = df_bmi["gender"].map({1: "Laki-laki", 0: "Perempuan"})

    # Feedback
    train = safe_read_csv(FEEDBACK_TRAIN_PATH)
    val   = safe_read_csv(FEEDBACK_VAL_PATH)
    df_feedback = pd.concat([train, val], ignore_index=True) if not (train.empty and val.empty) else pd.DataFrame()
    if not df_feedback.empty:
        df_feedback.columns = [c.strip().lower() for c in df_feedback.columns]
        df_feedback["label"]  = df_feedback["label"].str.strip()
        df_feedback["aspect"] = df_feedback["aspect"].str.strip()

    return df_gizi, df_bmi, df_feedback

# Sidebar
def sidebar_navigation() -> str:
    try:
        from streamlit_option_menu import option_menu
        with st.sidebar:
            st.markdown(
                "<div style='text-align:center;padding:12px 0 8px;'>"
                "<img src='https://i.imgur.com/zAJoBB8.png' width='180'></div>",
                unsafe_allow_html=True,
            )
            st.markdown("<hr style='border-color:#c8e6c9;margin:8px 0 12px;'>", unsafe_allow_html=True)
            selected = option_menu(
                menu_title=None,
                options=["Overview","Dinner Recommendation","Anthropometric Analysis","Parent Feedback Analysis"],
                icons=["house","egg-fried","bar-chart","chat-left-text"],
                default_index=0,
                styles={
                    "container":       {"padding":"0!important","background-color":"transparent"},
                    "icon":            {"color":"white","font-size":"18px"},
                    "nav-link":        {
                        "font-size":"14px","text-align":"left","margin":"4px 0",
                        "padding":"10px 12px","border-radius":"12px",
                        "hover-color":"rgba(255,255,255,0.12)",
                    },
                    "nav-link-selected":{"background-color":"rgba(255,255,255,0.18)"},
                },
            )
            st.divider()
            st.markdown(
                "<div style='font-size:11px;opacity:0.8;line-height:1.6;'>"
                "Coding Camp 2026 powered by DBS Foundation<br>"
                "CC26-PRU424  PantauGizi Dashboard"
                "</div>",
                unsafe_allow_html=True,
            )
        return selected
    except ImportError:
        with st.sidebar:
            st.image("https://i.imgur.com/zAJoBB8.png", width=180)
            st.markdown("-")
            selected = st.radio(
                "Navigasi",
                ["Overview","Dinner Recommendation","Anthropometric Analysis","Parent Feedback Analysis"],
            )
            st.markdown("-")
            st.caption("Coding Camp 2026 powered by DBS Foundation\nCC26-PRU424  PantauGizi Dashboard")
        return selected

# Overview Page
def show_overview(df_gizi, df_bmi, df_feedback):
    st.title("PantauGizi Dashboard")
    st.markdown("<p style='color:#5f6b66;'>Sistem Rekomendasi Menu Berbasis AI untuk Siswa Indonesia</p>",
                unsafe_allow_html=True)
    st.divider()

    n_menu     = len(df_gizi) if not df_gizi.empty else 0
    n_siswa    = len(df_bmi)  if not df_bmi.empty  else 0
    n_feedback = len(df_feedback) if not df_feedback.empty else 0
    n_aspek    = df_feedback["aspect"].nunique() if not df_feedback.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🍽️ Total Menu",      f"{n_menu:,}")
    c2.metric("👦 Data Siswa",      f"{n_siswa:,}")
    c3.metric("💬 Total Feedback",  f"{n_feedback:,}")
    c4.metric("📌 Aspek ABSA",      f"{n_aspek}")

    st.divider()

    add_section_title("Ringkasan Proyek")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🍽️ Dinner Recommendation")
        with st.container(border=True):
            st.markdown("#### 📌 Latar Belakang")
            st.write("""
            Dataset menu (131 item) dipetakan berdasarkan konsep
            Isi Piringku untuk menghitung distribusi energi dan
            makronutrien pada setiap kelompok pangan.
            """)
        with st.container(border=True):
            st.markdown("#### ❓ Pertanyaan Analisis")
            st.markdown("""
            **Q1.** Bagaimana distribusi rata-rata makronutrien dan energi
            pada tiap kategori Isi Piringku?

            **Q2.** Bagaimana kebutuhan kalori dan makronutrien siswa
            berdasarkan status gizi dan jenjang sekolah?
            """)

    with col2:
        st.markdown("### 💬 Parent Feedback Analysis")
        with st.container(border=True):
            st.markdown("#### 📌 Latar Belakang")
            st.write("""
            Feedback orang tua sebanyak 6.202 ulasan GoFood Review
            dianalisis menggunakan Aspect-Based Sentiment Analysis (ABSA)
            untuk mengungkap sentimen terhadap aspek rasa, porsi,
            dan kebersihan.
            """)
        with st.container(border=True):
            st.markdown("#### ❓ Pertanyaan Analisis")
            st.markdown("""
            **Q3.** Bagaimana perbandingan ulasan positif dan negatif
            pada aspek rasa, porsi, dan kebersihan?
            """)

    if not df_gizi.empty and not df_bmi.empty and not df_feedback.empty:
        st.divider()
        add_section_title("Snapshot Data")
        c1, c2, c3 = st.columns(3)

        with c1:
            cnt = df_gizi["isi_piringku"].value_counts().reindex(FOOD_ORDER, fill_value=0)
            fig = px.bar(
                x=cnt.index, y=cnt.values,
                color=cnt.index, color_discrete_sequence=GREEN_PALETTE,
                labels={"x":"Kategori","y":"Jumlah Menu"},
                title="Distribusi Menu (Isi Piringku)",
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig_layout(fig, 320), use_container_width=True)

        with c2:
            cnt2 = df_bmi["nutritional_status"].value_counts().reindex(STATUS_ORDER, fill_value=0)
            fig2 = px.bar(
                x=cnt2.index, y=cnt2.values,
                color=cnt2.index,
                color_discrete_map=BMI_COLORS,
                labels={"x":"Status Gizi","y":"Jumlah Siswa"},
                title="Distribusi Status Gizi Siswa",
            )
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig_layout(fig2, 320), use_container_width=True)

        with c3:
            fb_sum = (
                df_feedback.groupby(["aspect","label"])
                .size().reset_index(name="n")
            )
            fig3 = px.bar(
                fb_sum, x="aspect", y="n", color="label",
                color_discrete_map=SENTIMENT_COLORS,
                barmode="group",
                labels={"aspect":"Aspek","n":"Jumlah Ulasan","label":"Sentimen"},
                title="Sentimen per Aspek (ABSA)",
            )
            st.plotly_chart(fig_layout(fig3, 320), use_container_width=True)


def show_dinner_recommendation(df_gizi: pd.DataFrame):
    if df_gizi.empty:
        st.error("❌ File `train_gizi.csv` tidak ditemukan atau kosong.")
        return

    st.title("🍽️ Dinner Recommendation")
    st.markdown("<p style='color:#5f6b66;'>Analisis nutrisi menu berdasarkan pedoman Isi Piringku</p>",
                unsafe_allow_html=True)
    st.divider()

    df = df_gizi.copy()
    df_main = df[df["isi_piringku"].isin(FOOD_ORDER)].copy()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Distribusi Kategori",
        "🥩 Makronutrien per Kategori",
        "⚡ Energi per Kategori",
        "🔥 Korelasi Gizi",
        "🏆 Top Menu",
    ])

    with tab1:
        add_section_title("Distribusi Kelompok Pangan", "Jumlah menu per kategori Isi Piringku.")
        cnt = df_main["isi_piringku"].value_counts().reindex(FOOD_ORDER, fill_value=0).reset_index()
        cnt.columns = ["isi_piringku","jumlah"]
        fig = px.bar(
            cnt, x="isi_piringku", y="jumlah",
            text="jumlah",
            color="isi_piringku", color_discrete_sequence=GREEN_PALETTE,
            category_orders={"isi_piringku": FOOD_ORDER},
            labels={"isi_piringku":"Kategori","jumlah":"Jumlah Menu"},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig_layout(fig), use_container_width=True)

        insight_box("""
        <b>Insight:</b> Lauk-Pauk mendominasi dataset menu (69 item) yang mencerminkan keberagaman
        sumber protein hewani dan nabati di Indonesia. Buah-buahan (14 item) dan Makanan Pokok
        (13 item) lebih terbatas  sistem rekomendasi perlu mempertimbangkan variasi pilihan
        agar menu tidak monoton.
        """)

        st.subheader("Detail per Kategori Bahan Makanan")
        cnt_kat = df["kategori"].value_counts().reset_index()
        cnt_kat.columns = ["kategori","jumlah"]
        fig2 = px.bar(
            cnt_kat.sort_values("jumlah", ascending=True),
            x="jumlah", y="kategori", orientation="h",
            color="jumlah",
            # ← diganti: Blues lebih bersih daripada Greens untuk kontras dengan layout
            color_continuous_scale="Blues",
            text="jumlah",
            labels={"jumlah":"Jumlah","kategori":"Kategori"},
        )
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig_layout(fig2, 400), use_container_width=True)

    with tab2:
        add_section_title(
            "Q1  Rata-rata Makronutrien per Kategori Isi Piringku",
            "Nilai protein, lemak, karbohidrat (normalized score) menunjukkan ranking relatif antar kategori."
        )
        macro_avg = (
            df_main.groupby("isi_piringku")[["protein","lemak","karbohidrat"]]
            .mean()
            .reindex(FOOD_ORDER)
            .reset_index()
        )
        macro_melt = macro_avg.melt(
            id_vars="isi_piringku",
            value_vars=["protein","lemak","karbohidrat"],
            var_name="Nutrisi", value_name="Skor Relatif",
        )
        fig = px.bar(
            macro_melt, x="isi_piringku", y="Skor Relatif", color="Nutrisi",
            barmode="group",
            color_discrete_map=NUTRISI_COLORS,
            category_orders={"isi_piringku": FOOD_ORDER},
            labels={"isi_piringku":"Kategori Isi Piringku"},
        )
        st.plotly_chart(fig_layout(fig), use_container_width=True)

        add_section_title("Profil Nutrisi Radar per Kategori")
        # Warna radar diselaraskan dengan GREEN_PALETTE
        RADAR_COLORS = ["#0077B6","#00B4D8","#52B788","#F4A261"]
        fig_radar = go.Figure()
        categories_radar = ["Protein","Lemak","Karbohidrat"]
        for idx, cat in enumerate(FOOD_ORDER):
            row = macro_avg[macro_avg["isi_piringku"] == cat]
            
            if len(row) == 0: continue
            protein = row["protein"].values[0]
            lemak = row["lemak"].values[0]
            karbohidrat = row["karbohidrat"].values[0]
            
            vals = [protein, lemak, karbohidrat]
            vals += vals[:1]
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=vals,
                    theta=categories_radar + categories_radar[:1],
                    fill="toself",
                    name=cat,
                    line=dict(color=RADAR_COLORS[idx % len(RADAR_COLORS)])
                )
            )
        st.plotly_chart(fig_radar, use_container_width=True)
    insight_box("""
        <b>Insight Q1  Makronutrien:</b><br>
        • <b>Lauk-Pauk</b> memiliki skor protein dan lemak tertinggi → sumber utama
          pembangun dan pelengkap energi padat.<br>
        • <b>Makanan Pokok</b> unggul dalam karbohidrat → bahan bakar utama aktivitas siswa.<br>
        • <b>Sayuran</b> memiliki skor makronutrien paling rendah, tetapi kaya serat & mikronutrien.<br>
        • <b>Buah-buahan</b> mengandung karbohidrat alami cukup tinggi sekaligus sumber vitamin.
        """)

    with tab3:
        add_section_title(
            "Distribusi Energi (kkal/100g) per Kategori",
            "Nilai energi asli (tidak dinormalisasi)."
        )
        c1, c2 = st.columns(2)
        with c1:
            fig = px.box(
                df_main, x="isi_piringku", y="energi_kkal_per_100g",
                color="isi_piringku", color_discrete_sequence=GREEN_PALETTE,
                points="all",
                category_orders={"isi_piringku": FOOD_ORDER},
                labels={"isi_piringku":"Kategori","energi_kkal_per_100g":"Energi (kkal/100g)"},
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig_layout(fig, 420), use_container_width=True)

        with c2:
            eng_avg = (
                df_main.groupby("isi_piringku")["energi_kkal_per_100g"]
                .mean().round(1)
                .reindex(FOOD_ORDER)
                .reset_index()
            )
            eng_avg.columns = ["isi_piringku","energi_rata"]
            fig2 = px.bar(
                eng_avg, x="isi_piringku", y="energi_rata",
                text="energi_rata",
                color="isi_piringku", color_discrete_sequence=GREEN_PALETTE,
                category_orders={"isi_piringku": FOOD_ORDER},
                labels={"isi_piringku":"Kategori","energi_rata":"Energi Rata-rata (kkal/100g)"},
            )
            fig2.update_traces(textposition="outside")
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig_layout(fig2, 420), use_container_width=True)

        insight_box(f"""
        <b>Insight  Energi:</b><br>
        • Lauk-Pauk rata-rata <b>~{eng_avg[eng_avg.isi_piringku=='Lauk-Pauk']['energi_rata'].values[0]:.0f} kkal/100g</b> 
          paling padat kalori, perlu diimbangi sayur dan buah.<br>
        • Makanan Pokok <b>~{eng_avg[eng_avg.isi_piringku=='Makanan Pokok']['energi_rata'].values[0]:.0f} kkal/100g</b>
           sumber energi karbohidrat yang stabil.<br>
        • Sayuran & Buah jauh lebih rendah kalori, mendukung pola makan <i>Isi Piringku</i>
          (½ piring sayur + buah).
        """)

    with tab4:
        add_section_title(
            "Q1  Korelasi antar Makronutrien",
            "Matriks korelasi protein, lemak, karbohidrat (data train_gizi.csv)."
        )
        corr = df[["protein","lemak","karbohidrat"]].corr().round(2)
        fig = px.imshow(
            corr, text_auto=True,
            # ← diganti: RdBu lebih jelas untuk korelasi negatif/positif
            color_continuous_scale="RdBu",
            zmin=-1, zmax=1,
            labels={"color":"Korelasi"},
        )
        fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

        insight_box("""
        <b>Insight  Korelasi:</b><br>
        • <b>Protein ↔ Lemak</b>: korelasi positif kuat  makanan berprotein tinggi
          umumnya juga tinggi lemak (daging, telur).<br>
        • <b>Karbohidrat ↔ Protein/Lemak</b>: korelasi negatif  makanan pokok & buah
          tinggi karbohidrat namun rendah protein/lemak.<br>
        • Pola ini mendukung desain menu seimbang:
          lauk-pauk (protein+lemak) + makanan pokok (karbohidrat) + sayur/buah.
        """)

        add_section_title("Scatter Matrix Makronutrien")
        fig2 = px.scatter_matrix(
            df_main,
            dimensions=["protein","lemak","karbohidrat"],
            color="isi_piringku",
            color_discrete_sequence=GREEN_PALETTE,
            labels={"protein":"Protein","lemak":"Lemak","karbohidrat":"Karbohidrat"},
        )
        fig2.update_layout(height=500, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    with tab5:
        add_section_title("Top 10 Menu berdasarkan Energi & Makronutrien")
        c1, c2 = st.columns(2)

        with c1:
            top_e = df.nlargest(10, "energi_kkal_per_100g")
            fig = px.bar(
                top_e, x="energi_kkal_per_100g", y="nama",
                orientation="h",
                color="isi_piringku", color_discrete_sequence=GREEN_PALETTE,
                text="energi_kkal_per_100g",
                labels={"energi_kkal_per_100g":"Energi (kkal/100g)","nama":"Nama Menu"},
                title="Top 10 Menu  Energi Tertinggi",
            )
            fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
            fig.update_layout(yaxis=dict(autorange="reversed"), showlegend=True)
            st.plotly_chart(fig_layout(fig, 500), use_container_width=True)

        with c2:
            top_p = df.nlargest(10, "protein")
            fig2 = px.bar(
                top_p, x="protein", y="nama",
                orientation="h",
                color="isi_piringku", color_discrete_sequence=GREEN_PALETTE,
                labels={"protein":"Protein (skor)","nama":"Nama Menu"},
                title="Top 10 Menu  Protein Tertinggi (Skor Relatif)",
            )
            fig2.update_layout(yaxis=dict(autorange="reversed"), showlegend=True)
            st.plotly_chart(fig_layout(fig2, 500), use_container_width=True)

    if st.checkbox("Tampilkan data mentah menu"):
        cols = [c for c in ["kode","nama","kategori","isi_piringku","energi_kkal_per_100g"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True)


# Anthropometric Analysis Page
def show_anthropometric(df_bmi: pd.DataFrame):
    if df_bmi.empty:
        st.error("File `train_bmi.csv` tidak ditemukan atau kosong.")
        return

    st.title("📊 Anthropometric Analysis")
    st.markdown("<p style='color:#5f6b66;'>Analisis BMI, status gizi, stunting & kebutuhan kalori siswa</p>",
                unsafe_allow_html=True)
    st.divider()

    df = df_bmi.copy()

    with st.sidebar:
        st.markdown("### Filter Anthropometric")
        sel_age = st.multiselect("Jenjang Sekolah", options=AGE_ORDER, default=AGE_ORDER)
        sel_status = st.multiselect("Status Gizi", options=STATUS_ORDER, default=STATUS_ORDER)

    if sel_age:
        df = df[df["age_group"].isin(sel_age)]
    if sel_status:
        df = df[df["nutritional_status"].isin(sel_status)]

    if df.empty:
        st.warning("Tidak ada data sesuai filter.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Siswa", f"{len(df):,}")
    c2.metric("Jenjang Dipilih", len(sel_age))
    pct_normal = (df["nutritional_status"] == "Normal").mean() * 100
    c3.metric("% Normal", f"{pct_normal:.1f}%")
    pct_stunting = (df["stunting_status"] != "Normal").mean() * 100
    c4.metric("% Stunting", f"{pct_stunting:.1f}%")

    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Status Gizi",
        "🦴 Stunting",
        "⚖️ Distribusi Usia & Gender",
        "🔥 BMR per Jenjang",
        "📊 BMR per Status Gizi",
        "🥗 Makronutrien Harian",
    ])

    with tab1:
        add_section_title("Distribusi Status Gizi Siswa", "Berdasarkan klasifikasi WHO BMI-for-age.")
        c1, c2 = st.columns(2)

        with c1:
            cnt = df["nutritional_status"].value_counts().reindex(STATUS_ORDER, fill_value=0).reset_index()
            cnt.columns = ["status","jumlah"]
            fig = px.bar(
                cnt, x="status", y="jumlah",
                text="jumlah",
                color="status",
                color_discrete_map=BMI_COLORS,
                category_orders={"status": STATUS_ORDER},
                labels={"status":"Status Gizi","jumlah":"Jumlah Siswa"},
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig_layout(fig), use_container_width=True)

        with c2:
            fig2 = px.pie(
                cnt, names="status", values="jumlah",
                color="status", color_discrete_map=BMI_COLORS,
                hole=0.4,
            )
            fig2.update_traces(textposition="inside", textinfo="percent+label")
            fig2.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", height=420)
            st.plotly_chart(fig2, use_container_width=True)

        add_section_title("Distribusi Status Gizi per Jenjang Sekolah")
        pivot = (
            df.groupby(["age_group","nutritional_status"])
            .size().reset_index(name="jumlah")
        )
        fig3 = px.density_heatmap(
            pivot, x="age_group", y="nutritional_status", z="jumlah",
            # ← diganti: Viridis lebih mudah dibaca untuk heatmap
            color_continuous_scale="Viridis",
            category_orders={"age_group": AGE_ORDER, "nutritional_status": STATUS_ORDER},
            labels={"age_group":"Jenjang","nutritional_status":"Status Gizi","jumlah":"Jumlah"},
        )
        st.plotly_chart(fig_layout(fig3, 380), use_container_width=True)

        insight_box("""
        <b>Insight:</b> Distribusi status gizi relatif merata di semua kategori (<i>balanced dataset</i>),
        mencerminkan keberagaman kondisi gizi siswa Indonesia. Siswa SD (7–12 tahun) mendominasi
        data (1.350 siswa)  sesuai target utama program MBG.
        """)

    with tab2:
        add_section_title("Distribusi Status Stunting", "Normal, Stunting, Stunting Berat.")
        c1, c2 = st.columns(2)

        # ← warna stunting diperbarui: lebih soft dan mudah dibedakan
        STUNT_COLORS = {
            "Normal":         "#40C057",   # hijau segar
            "Stunting":       "#FFA94D",   # oranye
            "Stunting Berat": "#E03131",   # merah tegas
        }

        with c1:
            cnt_stunt = df["stunting_status"].value_counts().reset_index()
            cnt_stunt.columns = ["status","jumlah"]
            fig = px.bar(
                cnt_stunt, x="status", y="jumlah",
                text="jumlah",
                color="status",
                color_discrete_map=STUNT_COLORS,
                labels={"status":"Stunting Status","jumlah":"Jumlah Siswa"},
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig_layout(fig), use_container_width=True)

        with c2:
            stunt_age = (
                df.groupby(["age_group","stunting_status"])
                .size().reset_index(name="jumlah")
            )
            fig2 = px.bar(
                stunt_age, x="age_group", y="jumlah",
                color="stunting_status",
                color_discrete_map=STUNT_COLORS,
                barmode="stack",
                category_orders={"age_group": AGE_ORDER},
                labels={"age_group":"Jenjang","jumlah":"Jumlah","stunting_status":"Status"},
            )
            st.plotly_chart(fig_layout(fig2), use_container_width=True)

        insight_box("""
        <b>Insight:</b> Stunting (growth faltering) ditemukan di semua jenjang  terutama berdampingan
        dengan status gizi Kurus dan Sangat Kurus. Sistem PantauGizi dapat membantu intervensi dini
        dengan merekomendasikan menu tinggi protein & kalori bagi siswa berisiko.
        """)

    with tab3:
        add_section_title("Distribusi Usia & Gender")
        c1, c2 = st.columns(2)

        with c1:
            cnt_age = df["age_group"].value_counts().reindex(AGE_ORDER, fill_value=0).reset_index()
            cnt_age.columns = ["jenjang","jumlah"]
            fig = px.bar(
                cnt_age, x="jenjang", y="jumlah",
                text="jumlah",
                color="jenjang", color_discrete_sequence=GREEN_PALETTE,
                category_orders={"jenjang": AGE_ORDER},
                labels={"jenjang":"Jenjang","jumlah":"Jumlah Siswa"},
                title="Distribusi Jenjang Sekolah",
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig_layout(fig), use_container_width=True)

        with c2:
            cnt_gender = df["gender_label"].value_counts().reset_index()
            cnt_gender.columns = ["gender","jumlah"]
            fig2 = px.pie(
                cnt_gender, names="gender", values="jumlah",
                color="gender",
                # ← diganti: biru medium & pink yang lebih soft
                color_discrete_sequence=["#339AF0","#F06595"],
                hole=0.35,
                title="Distribusi Gender",
            )
            fig2.update_traces(textposition="inside", textinfo="percent+label")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=420)
            st.plotly_chart(fig2, use_container_width=True)

    with tab4:
        add_section_title(
            "Q2  Distribusi Kebutuhan Kalori (BMR) per Jenjang & Status Gizi",
            "Nilai BMR dinormalisasi (RobustScaler). Ranking relatif antar kelompok tetap valid."
        )
        order = [s for s in AGE_ORDER if s in df["age_group"].cat.categories.tolist()]
        fig = px.box(
            df.sort_values("age_group"),
            x="age_group", y="bmr_kcal",
            color="nutritional_status",
            category_orders={"age_group": order, "nutritional_status": STATUS_ORDER},
            color_discrete_map=BMI_COLORS,
            points="outliers",
            labels={"age_group":"Jenjang","bmr_kcal":"BMR (skor normalized)","nutritional_status":"Status Gizi"},
        )
        st.plotly_chart(fig_layout(fig, 520), use_container_width=True)

        insight_box("""
        <b>Insight Q2  Kalori per Jenjang:</b><br>
        • Kebutuhan kalori meningkat seiring usia: <b>PAUD → TK → SD → SMP → SMA/SMK</b>.<br>
        • Siswa <b>Obesitas</b> memiliki BMR paling tinggi di setiap jenjang karena berat badan
          lebih besar membutuhkan energi basal lebih banyak.<br>
        • Siswa <b>Sangat Kurus</b> memiliki BMR terendah  tetap harus mendapat asupan minimum
          untuk mendukung pertumbuhan.<br>
        • Variasi BMR terbesar ada di jenjang SMA/SMK dan SMP, sesuai masa pubertas.
        """)

    with tab5:
        add_section_title("Q2  Distribusi BMR per Status Gizi")
        order2 = [s for s in STATUS_ORDER if s in df["nutritional_status"].cat.categories.tolist()]
        fig = px.box(
            df,
            x="nutritional_status", y="bmr_kcal",
            points="outliers",
            category_orders={"nutritional_status": order2},
            color="nutritional_status",
            color_discrete_map=BMI_COLORS,
            labels={"nutritional_status":"Status Gizi","bmr_kcal":"BMR (skor normalized)"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig_layout(fig, 500), use_container_width=True)

        fig2 = px.violin(
            df,
            x="nutritional_status", y="bmr_kcal",
            box=True, points=False,
            category_orders={"nutritional_status": order2},
            color="nutritional_status",
            color_discrete_map=BMI_COLORS,
            labels={"nutritional_status":"Status Gizi","bmr_kcal":"BMR (skor normalized)"},
            title="Violin Plot BMR per Status Gizi",
        )
        fig2.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", height=420)
        st.plotly_chart(fig2, use_container_width=True)

    with tab6:
        add_section_title(
            "Q2  Kebutuhan Makronutrien Harian per Status Gizi",
            "Protein (15%), Lemak (30%), Karbohidrat (55%) dari BMR masing-masing siswa."
        )
        macro_avg = (
            df.groupby("nutritional_status", observed=True)[["protein_g","lemak_g","karbo_g"]]
            .mean()
            .reindex(STATUS_ORDER)
            .reset_index()
        )
        macro_melt = macro_avg.melt(
            id_vars="nutritional_status",
            value_vars=["protein_g","lemak_g","karbo_g"],
            var_name="Makronutrien", value_name="Skor Relatif",
        )
        macro_melt["Makronutrien"] = macro_melt["Makronutrien"].replace(
            {"protein_g":"Protein","lemak_g":"Lemak","karbo_g":"Karbohidrat"}
        )
        fig = px.bar(
            macro_melt,
            x="nutritional_status", y="Skor Relatif",
            color="Makronutrien", barmode="group",
            # ← diselaraskan dengan NUTRISI_COLORS
            color_discrete_map=NUTRISI_COLORS,
            category_orders={"nutritional_status": STATUS_ORDER},
            labels={"nutritional_status":"Status Gizi"},
        )
        st.plotly_chart(fig_layout(fig, 480), use_container_width=True)

        insight_box("""
        <b>Insight Q2  Makronutrien per Status Gizi:</b><br>
        • Siswa <b>Obesitas</b> membutuhkan makronutrien tertinggi secara absolut karena BMR-nya besar.
          Namun komposisinya harus diarahkan ke kontrol karbohidrat dan lemak.<br>
        • Siswa <b>Sangat Kurus</b> memiliki kebutuhan terendah  perlu intervensi penambahan porsi
          karbohidrat dan protein secara bertahap.<br>
        • Karbohidrat selalu mendominasi (55% kalori), diikuti lemak (30%) dan protein (15%),
          sesuai standar gizi anak Indonesia.
        """)

        add_section_title("Kebutuhan Makronutrien per Jenjang Sekolah")
        macro_age = (
            df.groupby("age_group", observed=True)[["protein_g","lemak_g","karbo_g"]]
            .mean()
            .reindex(AGE_ORDER)
            .reset_index()
        )
        macro_age_melt = macro_age.melt(
            id_vars="age_group",
            value_vars=["protein_g","lemak_g","karbo_g"],
            var_name="Makronutrien", value_name="Skor Relatif",
        )
        macro_age_melt["Makronutrien"] = macro_age_melt["Makronutrien"].replace(
            {"protein_g":"Protein","lemak_g":"Lemak","karbo_g":"Karbohidrat"}
        )
        fig2 = px.bar(
            macro_age_melt,
            x="age_group", y="Skor Relatif",
            color="Makronutrien",
            barmode="stack",
            # ← diselaraskan dengan NUTRISI_COLORS
            color_discrete_map=NUTRISI_COLORS,
            category_orders={"age_group": AGE_ORDER},
            labels={"age_group":"Jenjang"},
        )
        st.plotly_chart(fig_layout(fig2), use_container_width=True)

    if st.checkbox("Tampilkan data mentah BMI"):
        show_cols = [c for c in [
            "age_group","gender_label","nutritional_status","stunting_status",
            "bmr_kcal","protein_g","lemak_g","karbo_g"
        ] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True)


# Parent Feedback Analysis Page
def show_feedback_analysis(df_feedback: pd.DataFrame):
    if df_feedback.empty:
        st.error("❌ File feedback tidak ditemukan atau kosong.")
        return

    st.title("💬 Parent Feedback Analysis")
    st.markdown("<p style='color:#5f6b66;'>Aspect-Based Sentiment Analysis (ABSA)  Rasa, Porsi, Kebersihan</p>",
                unsafe_allow_html=True)
    st.divider()

    df = df_feedback.copy()
    target_aspects = ["rasa","porsi","kebersihan"]
    df = df[df["aspect"].isin(target_aspects) & df["label"].isin(["positif","negatif"])]

    summary = (
        df.groupby("aspect")["label"]
        .value_counts().unstack(fill_value=0)
        .reset_index()
    )
    for col in ["positif","negatif"]:
        if col not in summary.columns:
            summary[col] = 0
    summary["total"]       = summary["positif"] + summary["negatif"]
    summary["positif_pct"] = (summary["positif"] / summary["total"] * 100).round(1)
    summary["negatif_pct"] = (summary["negatif"] / summary["total"] * 100).round(1)
    summary = summary.sort_values("total", ascending=False).reset_index(drop=True)

    top_aspect = summary.iloc[0]["aspect"] if not summary.empty else "rasa"

    total_fb  = len(df)
    total_pos = (df["label"] == "positif").sum()
    total_neg = (df["label"] == "negatif").sum()
    avg_rating = df["rating"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Ulasan",  f"{total_fb:,}")
    c2.metric("✅ Positif",    f"{total_pos:,}", f"{total_pos/total_fb*100:.1f}%")
    c3.metric("❌ Negatif",    f"{total_neg:,}", f"-{total_neg/total_fb*100:.1f}%")
    c4.metric("⭐ Avg Rating", f"{avg_rating:.2f} / 5")

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Q3  Overview Sentimen",
        "🔍 Q3  Detail per Aspek",
        "⭐ Distribusi Rating",
        "📋 Tabel Ringkasan ABSA",
    ])

    with tab1:
        add_section_title(
            "Q3  Distribusi Sentimen Positif & Negatif per Aspek",
            "Sumber: feedback_train.csv + feedback_val.csv (6.202 ulasan)."
        )
        c1, c2 = st.columns(2)

        with c1:
            fb_long = summary.melt(
                id_vars="aspect",
                value_vars=["positif","negatif"],
                var_name="label", value_name="jumlah",
            )
            fig = px.bar(
                fb_long, x="aspect", y="jumlah", color="label",
                barmode="group",
                text="jumlah",
                color_discrete_map=SENTIMENT_COLORS,
                category_orders={"aspect": ["rasa","porsi","kebersihan"]},
                labels={"aspect":"Aspek","jumlah":"Jumlah Ulasan","label":"Sentimen"},
                title="Perbandingan Sentimen per Aspek",
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig_layout(fig), use_container_width=True)

        with c2:
            fig2 = px.bar(
                fb_long, x="aspect", y="jumlah", color="label",
                barmode="relative",
                color_discrete_map=SENTIMENT_COLORS,
                category_orders={"aspect": ["rasa","porsi","kebersihan"]},
                labels={"aspect":"Aspek","jumlah":"Jumlah","label":"Sentimen"},
                title="Proporsi Sentimen (%) per Aspek",
            )
            fig2.update_layout(barnorm="percent", yaxis_title="Persentase (%)")
            st.plotly_chart(fig_layout(fig2), use_container_width=True)

        add_section_title("Persentase Sentimen per Aspek (Donut)")
        cols3 = st.columns(3)
        for i, row in summary.iterrows():
            with cols3[i % 3]:
                fig3 = go.Figure(go.Pie(
                    labels=["Positif","Negatif"],
                    values=[row["positif"], row["negatif"]],
                    hole=0.55,
                    marker_colors=[SENTIMENT_COLORS["positif"], SENTIMENT_COLORS["negatif"]],
                    textinfo="percent+label",
                ))
                fig3.update_layout(
                    title_text=f"Aspek: {row['aspect'].capitalize()}",
                    showlegend=False,
                    height=300,
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=40, b=10),
                )
                st.plotly_chart(fig3, use_container_width=True)

        insight_box(f"""
        <b>Insight Q3  Sentimen per Aspek:</b><br>
        • <b>Rasa</b> mendominasi ulasan ({summary[summary.aspect=='rasa']['total'].values[0]:,} ulasan)
          dengan sentimen positif <b>{summary[summary.aspect=='rasa']['positif_pct'].values[0]:.1f}%</b>
           orang tua umumnya puas dengan cita rasa menu.<br>
        • <b>Porsi</b> menjadi perhatian kedua terbesar ({summary[summary.aspect=='porsi']['total'].values[0]:,} ulasan)
          dengan positif <b>{summary[summary.aspect=='porsi']['positif_pct'].values[0]:.1f}%</b>
           masih ada keluhan porsi kurang.<br>
        • <b>Kebersihan</b> paling sedikit dibahas ({summary[summary.aspect=='kebersihan']['total'].values[0]:,} ulasan)
          namun sentimen negatif cukup tinggi (<b>{summary[summary.aspect=='kebersihan']['negatif_pct'].values[0]:.1f}%</b>)
           perlu prioritas perbaikan.
        """)

    with tab2:
        add_section_title("Q3  Distribusi Jumlah Ulasan per Aspek")

        asp_cnt = df["aspect"].value_counts().reset_index()
        asp_cnt.columns = ["aspect","jumlah"]
        fig = px.bar(
            asp_cnt.sort_values("jumlah", ascending=True),
            x="jumlah", y="aspect", orientation="h",
            text="jumlah",
            color="jumlah",
            # ← diganti: Teal lebih segar daripada Greens
            color_continuous_scale="Teal",
            labels={"jumlah":"Jumlah Ulasan","aspect":"Aspek"},
            title="Total Ulasan per Aspek",
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig_layout(fig, 320), use_container_width=True)

        add_section_title("Heatmap Aspek × Sentimen")
        hm = summary.set_index("aspect")[["positif","negatif"]]
        fig2 = px.imshow(
            hm, text_auto=True,
            # ← diganti: RdYlGn tetap tapi lebih terang
            color_continuous_scale="RdYlGn",
            labels={"x":"Sentimen","y":"Aspek","color":"Jumlah"},
            aspect="auto",
        )
        fig2.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.bar(
            summary.sort_values("positif_pct", ascending=True),
            x="positif_pct", y="aspect",
            orientation="h", text="positif_pct",
            color="positif_pct",
            # ← diganti: Teal konsisten dengan chart di atas
            color_continuous_scale="Teal",
            labels={"positif_pct":"% Positif","aspect":"Aspek"},
            title="Persentase Sentimen Positif per Aspek",
        )
        fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig_layout(fig3, 320), use_container_width=True)

    with tab3:
        add_section_title("Distribusi Rating Ulasan per Aspek")
        rating_dist = (
            df.groupby(["aspect","rating"])
            .size().reset_index(name="jumlah")
        )
        # ← warna rating per aspek — 3 warna harmonis
        ASPECT_COLORS = ["#0077B6","#52B788","#F4A261"]
        fig = px.bar(
            rating_dist, x="rating", y="jumlah",
            color="aspect",
            barmode="group",
            color_discrete_sequence=ASPECT_COLORS,
            category_orders={"aspect":["rasa","porsi","kebersihan"]},
            labels={"rating":"Rating (1–5)","jumlah":"Jumlah","aspect":"Aspek"},
            title="Distribusi Rating per Aspek",
        )
        st.plotly_chart(fig_layout(fig), use_container_width=True)

        add_section_title("Rata-rata Rating per Aspek")
        avg_r = df.groupby("aspect")["rating"].mean().reset_index()
        avg_r.columns = ["aspect","avg_rating"]
        avg_r["avg_rating"] = avg_r["avg_rating"].round(2)
        fig2 = px.bar(
            avg_r, x="aspect", y="avg_rating",
            text="avg_rating",
            color="aspect", color_discrete_sequence=ASPECT_COLORS,
            labels={"aspect":"Aspek","avg_rating":"Rata-rata Rating"},
            title="Rata-rata Rating (skala 1–5) per Aspek",
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False, yaxis=dict(range=[0, 5.5]))
        st.plotly_chart(fig_layout(fig2, 380), use_container_width=True)

        insight_box("""
        <b>Insight  Rating:</b><br>
        • Aspek <b>Rasa</b> mendapat rata-rata rating tertinggi (~4.1)  konsisten dengan
          dominasi sentimen positifnya.<br>
        • Aspek <b>Kebersihan</b> rating rata-rata ~3.2 dan distribusi bimodal (banyak rating 1–2 & 5)
          → tanggapan sangat terpolar, perlu penanganan segera.<br>
        • Aspek <b>Porsi</b> rating ~3.6  keluhan porsi kurang banyak muncul di rating 2–3.
        """)

    with tab4:
        add_section_title("Tabel Ringkasan ABSA", "Rekap sentimen per aspek.")
        display_df = summary.rename(columns={
            "aspect":"Aspek","positif":"Positif","negatif":"Negatif",
            "total":"Total","positif_pct":"% Positif","negatif_pct":"% Negatif",
        })[["Aspek","Positif","Negatif","Total","% Positif","% Negatif"]]
        display_df["Aspek"] = display_df["Aspek"].str.capitalize()

        st.dataframe(
            display_df.style.format({"% Positif":"{:.1f}%","% Negatif":"{:.1f}%"}),
            use_container_width=True,
        )

        st.divider()
        st.markdown("### Kesimpulan & Rekomendasi")
        insight_box(f"""
        <b>Kesimpulan Bisnis (Q3):</b><br>
        • Aspek yang paling banyak dibahas: <b>{top_aspect.capitalize()}</b>
          ({summary.iloc[0]['total']:,} ulasan).<br>
        • <b>Rasa</b>: sentimen positif dominan (74.9%)  pertahankan kualitas
          bumbu dan cita rasa khas.<br>
        • <b>Porsi</b>: 40% negatif → perlu evaluasi standar porsi per jenjang
          (kebutuhan kalori SD vs SMA berbeda).<br>
        • <b>Kebersihan</b>: 55.4% negatif dan volume terkecil  kemungkinan
          underreported. Perlu SOP kebersihan & pengemasan yang lebih ketat.<br><br>
        <b>Catatan Modelling:</b><br>
        • Gunakan <i>stratified split</i> per aspek untuk mengatasi ketidakseimbangan data
          (rasa jauh lebih banyak dari kebersihan).<br>
        • Evaluasi dengan <b>F1-score macro</b> agar performa model lebih adil antar kelas.<br>
        • Pertimbangkan augmentasi data untuk aspek kebersihan (298 sampel).
        """)

    if st.checkbox("Tampilkan data mentah feedback"):
        st.dataframe(df[["final_text","rating","label","aspect"]].sample(min(200, len(df))),
                     use_container_width=True)

# Main
def main():
    df_gizi, df_bmi, df_feedback = load_data()
    page = sidebar_navigation()

    if page == "Overview":
        show_overview(df_gizi, df_bmi, df_feedback)
    elif page == "Dinner Recommendation":
        show_dinner_recommendation(df_gizi)
    elif page == "Anthropometric Analysis":
        show_anthropometric(df_bmi)
    elif page == "Parent Feedback Analysis":
        show_feedback_analysis(df_feedback)

if __name__ == "__main__":
    main()
