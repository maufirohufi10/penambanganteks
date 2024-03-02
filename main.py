import streamlit as st
import pandas as pd
from datetime import date, timedelta
from bs4 import BeautifulSoup
import requests
import base64


def ambil_artikel_kompas(url_artikel):
    response = requests.get(url_artikel)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        article_content = soup.find('div', class_='read__content').find_all('p')
        konten = ''.join([p.get_text() for p in article_content])
        return konten
    return ""

def scrape_news_data(base_url, tanggal_mulai, tanggal_selesai):
    data = []

    current_date = tanggal_mulai
    while current_date <= tanggal_selesai:
        url = base_url.format(current_date.year, current_date.month, current_date.day)
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            news_elements = soup.find_all('h3', class_='article__title article__title--medium')

            for element in news_elements:
                judul = element.a.text
                url_artikel = element.a['href']

                article_response = requests.get(url_artikel)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                elemen_tgl_jam = article_soup.find('div', class_='read__time')
                tgl_jam = elemen_tgl_jam.text.strip() if elemen_tgl_jam else ""
                tgl_jam = tgl_jam.replace('Kompas.com -', '')

                elemen_link_artikel = article_soup.find('a', class_='article__link')
                link_artikel = elemen_link_artikel['href'] if elemen_link_artikel else ""

                elemen_kelas = article_soup.find('div', class_='article__subtitle article__subtitle--inline')
                kelas = elemen_kelas.text.strip() if elemen_kelas else ""

                konten = ambil_artikel_kompas(url_artikel)

                data.append({
                    'Date': tgl_jam,
                    'Title': judul,
                    'URL': link_artikel,
                    'Content': konten,
                    'Class': kelas
                })

            current_date += timedelta(days=1)
        else:
            print(f"Gagal mengambil data untuk {current_date.strftime('%d-%m-%Y')}")

    return data

# Streamlit app starts here
st.title('Kompas.com Web Crawler')

# Category selection
kategori = st.selectbox('Pilih Kategori', ['Sports', 'Health', 'Edukasi', 'Travel', 'Otomotif', 'Food', 'Sains'])

# Date selection
tanggal_mulai = st.date_input('Tanggal Mulai', date(2024, 3, 1))
tanggal_selesai = st.date_input('Tanggal Selesai', date(2024, 3, 2))

# Define base URL based on selected category
base_urls = {
    'Sports': "https://www.kompas.com/sports/search/{}-{}-{}",
    'Health': "https://health.kompas.com/search/{}-{}-{}",
    'Edukasi': "https://edukasi.kompas.com/search/{}-{}-{}",
    'Travel': "https://travel.kompas.com/search/{}-{}-{}",
    'Otomotif' : "https://otomotif.kompas.com/search/{}-{}-{}",
    'Food' : "https://www.kompas.com/food/search/{}-{}-{}",
    'Sains' : "https://www.kompas.com/sains/search/{}-{}-{}"
}

base_url = base_urls[kategori]

# Button to trigger crawling
if st.button('Scrape'):
    with st.spinner('Scraping dalam proses...'):
        # Scrape data
        data = scrape_news_data(base_url, tanggal_mulai, tanggal_selesai)

        # Display data
        df = pd.DataFrame(data)
        st.write(df)

        # Download button
        if not df.empty:
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()  # Encode CSV data
            href = f'<a href="data:file/csv;base64,{b64}" download="scraped_data.csv">Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)

