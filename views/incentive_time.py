import streamlit as st 
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go 
from datetime import date,datetime
from load_data import get_data
import math
import numpy as np

st.logo("logo_white.png",size= 'large')
st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        margin-top: 200 px;
        color: 'rgb(255,255,255)';
        font-size : 48px;
    }
    div.block-container{padding-top:1.5rem};
    </style>
    """,
    unsafe_allow_html=True
)
fty =['NT1','NT2']
nha_may = st.sidebar.multiselect("Chọn nhà máy",options=fty,default=fty)
reports = ['Công nhân Cắt','Công nhân may','Công nhân QC1','Công nhân Là','Công nhân QC2','Công nhân đóng gói','Công nhân NDC','Công nhân phụ','Quản lý']
bao_cao = st.sidebar.selectbox("Chọn báo cáo",options= reports,index=0)

st.markdown(f'<h1 class="centered-title">BÁO CÁO THƯỞNG NĂNG SUẤT THEO CÁC THÁNG ({bao_cao})</h1>', unsafe_allow_html=True)
#Config chung cho plotly chart
config = {
    'displayModeBar': True,  # Hiển thị/thêm thanh công cụ
    'modeBarButtonsToRemove': ['zoom', 'select', 'lasso2d', 'resetScale', 'toImage'],  # Ẩn nút
    'displaylogo': False,  # Ẩn logo Plotly
    'modeBarButtonsToAdd': []  # Đảm bảo không thêm bất kỳ nút nào khác
}

if bao_cao == 'Công nhân Cắt':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV as TONG_TGLV,TONG_THUONG,SO_NGAY,N'Cắt' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_CAT WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    
    df['XUONG'] = df['CHUYEN'].apply(lambda x: (x[:1] + 'NDC') if 'NDC' in x \
        else (x[:1] + 'TNC') if 'TNC' in x \
        else (x[:1] + 'P0' + x[1:2]))
    
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    df = df.query("NAM == @sel_nam")
    
    df 
    df_list = [df[df['NHA_MAY'] == fac] for fac in nha_may]
    cols = st.columns(len(nha_may))
    
    max_thang = max(df["THANG"].max() for df in df_list)
    min_thang = max(df["THANG"].min() for df in df_list)
    
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            
            df_tb_thuong = df_fac.groupby(by=['THANG']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            
            fig = px.line(df_tb_thuong, x="THANG", y="TONG_THUONG")
            
            fig.update_layout(
                title = f'Trung bình tiền thưởng nhóm cắt theo tháng {fac}',
                xaxis_title = 'Tháng',
                yaxis_title = 'Trung bình tiền thưởng'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_xaxes(
                range=[min_thang, max_thang]
            )
            fig.update_layout(dragmode="pan")
            
            st.plotly_chart(fig,use_container_width=True,key=f'line2{fac}',config = config)