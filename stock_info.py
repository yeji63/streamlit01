import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import datetime
import matplotlib.pyplot as plt
import matplotlib 
from io import BytesIO
import plotly.graph_objects as go
import pandas as pd


today = datetime.datetime.now()

with st.sidebar:
    stock_name = st.text_input("회사 이름", "삼성전자")
    add_datebox = st.sidebar.date_input(
    "시작일-종료일",
    (datetime.date(2019, 1, 1), today),
    format="YYYY.MM.DD")
    btn = st.button("주가데이터확인")

    # st.write(add_datebox)
    # st.write(add_radio)

# caching
# 인자가 바뀌지 않는 함수 실행 결과를 저장 후 크롬의 임시 저장 폴더에 저장 후 재사용
@st.cache_data
def get_stock_info():
    base_url =  "http://kind.krx.co.kr/corpgeneral/corpList.do"    
    method = "download"
    url = "{0}?method={1}".format(base_url, method)   
    df = pd.read_html(url, header=0, encoding='cp949')[0]
    df['종목코드']= df['종목코드'].apply(lambda x: f"{x:06d}")     
    df = df[['회사명','종목코드']]
    return df

def get_ticker_symbol(company_name):     
    df = get_stock_info()
    code = df[df['회사명']==company_name]['종목코드'].values    
    ticker_symbol = code[0]
    return ticker_symbol

if btn:
    # 코드 조각 추가
    st.write(stock_name)
    
    start_p = add_datebox[0]               
    end_p = add_datebox[1] + datetime.timedelta(days=1) 

    ticker_symbol = get_ticker_symbol(stock_name)
    df = fdr.DataReader(f'KRX:{ticker_symbol}', start_p, end_p)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Change']]
    df.index = df.index.date
    st.subheader(f"[{stock_name}] 주가 데이터")
    st.dataframe(df.tail(7))

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
            )
        ]
    )
    st.plotly_chart(fig, use_container_width=True)

    excel_data = BytesIO()      
    df.to_excel(excel_data)

    st.download_button(
        label="CSV파일 다운로드",
        data=df.to_csv(),
        file_name="df.csv",
        mime="text/csv")
    
    # excel 파일 바이너리 파일
    st.download_button("엑셀 파일 다운로드", 
            excel_data, file_name='stock_data.xlsx')