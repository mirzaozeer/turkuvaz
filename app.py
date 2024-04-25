import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import re
import pickle

with open("data/transfer_oneri.pkl", 'rb') as f:
    transfer_oneri = pickle.load(f)

def urun_transfer(transfer_veri, urun_kodu):
    if urun_kodu in transfer_veri:
        data = transfer_veri[urun_kodu]
        detay = {'verici': [], 'alici': [], 'miktar': []}

        for item in data:
            match = re.search(r"U\d+_miktar_\('(\w+)',_'(\w+)'\) = (\d+\.\d+)", item)
            if match:
                detay['verici'].append(match.group(1))
                detay['alici'].append(match.group(2))
                detay['miktar'].append(float(match.group(3)))
        return detay
    else:
        st.error(f"Ürün kodu {urun_kodu} bulunamadı.")
        return {'verici': [], 'alici': [], 'miktar': []}

# Sankey diyagramını oluşturma fonksiyonu
def sankey_grafik(transfer_detay):
    kombin_liste = transfer_detay['verici'] + transfer_detay['alici']
    genel_aglar = list(pd.unique(kombin_liste))

    renkler = ["blue" if node.startswith('V') else "red" for node in genel_aglar]
    kaynak_indeks = [genel_aglar.index(v) for v in transfer_detay['verici']]
    hedef_index = [genel_aglar.index(a) for a in transfer_detay['alici']]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=50,
            line=dict(color="black", width=0.5),
            label=genel_aglar,
            color=renkler
        ),
        link=dict(
            source=kaynak_indeks,
            target=hedef_index,
            value=transfer_detay['miktar']
        ))])

    fig.update_layout(
        title_text="<b>Mağazalar Arası Ürün Akışı</b>",
        title_font=dict(size=16),
        font_size=10,
        title_x=0.5,
        width=700,
        height=800
    )
    return fig



st.set_page_config(layout="centered")

left, middle, right = st.columns([1,1,1])

middle.image('data/d-r-logo-png-transparent.png', caption='Turkuvaz Medya Grup', width=250)

st.markdown("""
<style>
.centered {
    text-align: center;
}
</style>
<div class="centered">
    <h1>Stok Transfer Optimizasyonu</h1>
</div>
""", unsafe_allow_html=True)



urun_kodları = list(transfer_oneri.keys())
# Ürün kodu giriş alanı
product_code = st.text_input("Ürün kodunu girin","")

if st.button('Görselleştir'):
    if product_code:
        transfer_detayları = urun_transfer(transfer_oneri, product_code)
        fig = sankey_grafik(transfer_detayları)
        st.plotly_chart(fig)




