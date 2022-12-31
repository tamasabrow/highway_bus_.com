import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from time import sleep
import pandas as pd
import datetime
import os

st.title('高速バスドットコム  空席状況取得')
st.text('ver 1.0')

# １．今日の年月日を自動取得

# １-① 曜日を検索する辞書
d_week = {'Sun': '日', 'Mon': '月', 'Tue': '火', 'Wed': '水', 'Thu': '木', 'Fri': '金', 'Sat': '土'}
# １-② 本日の年月日を自動取得
now = datetime.date.today()
# １-③ %aで曜日を取得し、keyに代入
key = now.strftime('%a')
# １-④ d_weekからkeyに該当する値を取得し、wに代入
w = d_week[key]
today = now.strftime('%Y%m%d')
# １-⑤ タイトルの下に今日の年月日を表示させる
st_today = now.strftime('%Y年%m月%d日') + f'（{w}）'
st.write(st_today)



# ２．乗降地リスト
city_lists = {
  '東  京':'13', 
  '横  浜':'14', 
  '名古屋':'23', 
  '大  阪':'27', 
  '神  戸':'28', 
  '徳  島':'36', 
  '松  山':'38'
  }

# ２-① 乗車地リストから地名のリストを作成
depCity_list = [k for k, v in city_lists.items()]
# ２-② 地名リストのセレクトボックスを表示させる
depCity_name = st.selectbox('乗降地を選択してください', depCity_list)
# ２-③ 選択した地名から出発地の値を乗降地リストから取得し、頭に0を3つ付け足して6桁のコードにし、depCity変数に代入
depCity_num = '000' + city_lists[depCity_name]

# ３-① 乗降地リストから地名リストを作成
destCity_list = [k for k ,v in city_lists.items()]
# ３-② 地名リストのセレクトボックスを表示させる
destCity_name = st.selectbox('目的地を選択してください', destCity_list)
# ３-③ 選択した地名から目的地の値を乗降地リストから取得し、頭に0を3つ付け足して6桁のコードにし、destCity変数に代入
destCity_num = '000' + city_lists[destCity_name]


# ４．出発年月日を選択
dep_date = st.date_input('検索を開始する年月日を選択してください')
# ４-① 取得した出発年月日を、年（dep_Y）、月（dep_M）、日（dep_D）ｎ変数に分割
dep_Y = dep_date.year
dep_M = dep_date.month
dep_D = dep_date.day

# ５．検索期間の入力
how_many_day = st.date_input('検索したい期間の年月日を選択してください')

dt_seach = how_many_day.day - dep_date.day + 1
serch_Y = how_many_day.year
serch_M = how_many_day.month
serch_D = how_many_day.day

submit_btn = st.button('検索')

if submit_btn:

  st.write(f'区    間：{depCity_name} ➡ {destCity_name}')
  st.write(f'検索期間：{dep_Y}年{dep_M}月{dep_D}日 ~ {serch_Y}年{serch_M}月{serch_D}日  （{dt_seach}日間）')
  st.write('検索を開始します')


  for i in range(0, dt_seach):
    dt_next = dep_date + datetime.timedelta(days=i)
    dt_next_year = str(dt_next.year)
    dt_next_month = str(dt_next.month)
    if len(dt_next_month) == 1:
      dt_next_month = '0' + dt_next_month
    dt_next_day = str(dt_next.day)
    if len(dt_next_day) == 1:
      dt_next_day = '0' + dt_next_day
    depYM = dt_next_year + dt_next_month
    depD = dt_next_day
    depYMD = depYM + depD
    
    url = (f'https://www.kosokubus.com/?page=bus_list&sMode=1&pageNum=0'
              f'&depCity=&destCity=&depPreflog=&destPreflog={destCity_num}&depT=&arrT=&depPref={depCity_num}'
              f'&depCity=&destPref={destCity_num}&destCity=&depYM={depYM}&depD={depD}&numMan=1&numWoman=0&DepFrom=noselected&DepTo=noselected&DestFrom=noselected&DestTo=noselected')    
      
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')

    pageNum = soup.find('div', id='pagernum').text
    pageNum = int(pageNum[-2:]) # 検索するページ数を取得
    num = soup.find('span', class_='num').text # 検索件数を取得

    st.write(f'検索年月日：{dt_next_year}年{dt_next_month}月{dt_next_day}日')  
    st.write(f'検索結果：{num}件')
      
    d_list = []

    for i in range(0, pageNum):
          
          url = (f'https://www.kosokubus.com/?page=bus_list&sMode=1&pageNum={i}\&depCity=&destCity=&depPreflog=&destPreflog=&depT=&arrT=&depPref='
              f'{depCity_num}&depCity=&destPref={destCity_num}&destCity=&depYM={depYM}&depD={depD}&numMan=1&numWoman=0&DepFrom=noselected&DepTo=noselected&DestFrom=noselected&DestTo=noselected')
          r = requests.get(url)
          st.write(url)
          soup = BeautifulSoup(r.content, 'html.parser')

          sleep(1)

          contents = soup.find_all('div', class_='scheduleBox')

          for content in contents: 
              title = content.find('a').text
              name = content.find('div', class_='name')
              company = name.find('a').text
              daynight = content.find('p', class_='daynight').text
              stools = name.find_all('p')
              stools = stools[2].text.split('：')
              stools = stools[1]
              price = content.find('span', class_='tRed').text
              seats = content.find('table', class_='section')
              seats = seats.find_all('td')
              seats = int(seats[1].text)

              d = {
                  '便名': title,
                  '運行会社': company,
                  '便コード': stools,
                  '料金': price,
                  '空席': seats,
                  '時間帯':daynight
              }

              d_list.append(d)

          df = pd.DataFrame(d_list)
          df = df[['時間帯', '運行会社', '便コード', '料金', '空席', '便名']]
          

    filename = f'{today}_{depYMD}{depCity_name}→{destCity_name} 空席状況.csv'
    df.to_csv(filename, encoding='utf_8_sig')
    df = pd.read_csv(filename)
    st.dataframe(df)
  
  st.write('処理が完了しました') 












