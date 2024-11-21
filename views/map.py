import streamlit as st 
import streamlit.components.v1 as components
from load_data import get_data
import time
import pandas as pd 
import leafmap.foliumap as leafmap
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from branca.colormap import linear
import json
import geopandas as gpd

st.logo("logo_white.png",size= 'large')
st.markdown(
    """
    <style>pip install folium

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
# st.markdown(f'<h1 class="centered-title">Phân bổ công nhân theo vị trí địa lý</h1>', unsafe_allow_html=True)
###
nha_may = st.sidebar.radio("Chọn nhà máy",options=['NT1','NT2'])
#####

#####
# Nhúng trang web vào ứng dụng Streamlit
st.header("CCTV")
if nha_may == 'NT1':
    st.write("[CCTV NT1](http://namthuan.dssddns.net/)")
else:
    st.write("[CCTV NT2 - Block1](http://namthuan.smartddns.tv/)")
    st.write("[CCTV NT2 - Block2](http://namthuan2.smartddns.tv:81/)")
st.markdown("---")
# st.dataframe(df_loction)
df_hr = get_data("HR",f"""SELECT Ltrim(Rtrim(Tinh_TP)) as Tinh_TP,Ltrim(Rtrim(Quan_huyen)) as Quan_huyen,
                 Ltrim(Rtrim(Phuong_xa)) as Phuong_xa,Count(*) as HC 
                 FROM DANH_SACH_CBCNV 
                 WHERE TRANG_THAI_LAM_VIEC = N'ĐANG LÀM VIỆC' AND FACTORY = '{nha_may}'
                 Group by Ltrim(Rtrim(Tinh_TP)),Ltrim(Rtrim(Quan_huyen)),Ltrim(Rtrim(Phuong_xa))
                 """)
# st.dataframe(df_hr)
df_hr['NAME_1'] = df_hr['Tinh_TP'].str.replace(' ','',regex=True)
df_hr['NAME_2'] = df_hr['Quan_huyen'].str.replace(' ','',regex=True)
df_hr['NAME_3'] = df_hr['Phuong_xa'].str.replace(' ','',regex=True)

if nha_may == 'NT1':
    center = (20.92329180823736, 106.6506876954207)
else:
    center = (19.07221942023573, 105.61020468188303)
    
### phương án 1
geo_data = gpd.read_file("gadm41_VNM_3.json")
# geo_data
geo_data['NAME_1'] = geo_data['NAME_1'].replace({'Thuỷ': 'Thủy', 'Hoà': 'Hòa'}, regex=True)
geo_data['NAME_2'] = geo_data['NAME_2'].replace({'Thuỷ': 'Thủy', 'Hoà': 'Hòa'}, regex=True)
geo_data['NAME_3'] = geo_data['NAME_3'].replace({'Thuỷ': 'Thủy', 'Hoà': 'Hòa'}, regex=True)
df = pd.merge(geo_data,df_hr,on=['NAME_1','NAME_2','NAME_3'],how='inner')
# df
m = folium.Map(location=center, zoom_start=10)
folium.Choropleth(
    geo_data=df,
    data=df,
    columns=["NAME_3", "HC"],  
    key_on="feature.properties.NAME_3",  
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Số công nhân"
).add_to(m)
tooltip = folium.GeoJson(
    df,
    style_function=lambda feature: {
        "fillColor": "transparent",
        "color": "transparent",
        "weight": 0,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["NAME_1","NAME_2","NAME_3", "HC"],  # Các cột để hiển thị
        aliases=["Tỉnh:","Huyện:","Xã:", "Số CN:"],  # Nhãn hiển thị trong tooltip
        localize=True,
    ),
)
tooltip.add_to(m)
folium.Marker(
    location=center,
    tooltip= "Nam Thuận",
    icon=folium.Icon(color="red", icon="home", prefix="fa")
    ).add_to(m)

st.header("Bản đồ phân bổ công nhân")
st_folium(m,width='1500',height='600')

## phuong an 2
# df_loction = pd.read_csv("location.csv",encoding="utf-8")
# df = pd.merge(df_hr,df_loction,on=['Tinh_TP','Quan_huyen','Phuong_xa'],how='left')
# # st.dataframe(df)
# df = df[~df['Vi_do'].isnull()]
# map = folium.Map(location=center,zoom_start=12)
# for index,row in df.iterrows():  
#     location = (row['Vi_do'],row['Kinh_do'])
#     folium.Marker(
#                 location=location,
#                   popup=row['Phuong_xa'],
#                   icon=folium.Icon(color="blue", icon="user"),
#                   tooltip=f"Tỉnh: {row["Tinh_TP"]}<br>Huyện: {row["Quan_huyen"]}<br>Xã: {row["Phuong_xa"]}<br>Số công nhân: {row["HC"]}"
#                   ).add_to(map)
# folium.Marker(
#     location=center,
#     tooltip= "Nam Thuận",
#     icon=folium.Icon(color="red", icon="home", prefix="fa")
#     ).add_to(map)
# heat_data = df[['Vi_do','Kinh_do','HC']]
# HeatMap(heat_data, radius=50).add_to(map)
# geo_data = json.load(open("gadm41_VNM_3.json", 'r', encoding="utf-8"))

# st.header("Bản đồ")
# st_folium(map,width='1500',height='600')
###
# ###
# st.markdown("---")
# url = "https://app.powerbi.com/view?r=eyJrIjoiYzI1MjVmNzgtYzJhZC00OGUwLWFlZGYtYTc4M2U4ZTBjMGVhIiwidCI6Ijg5MGRiNGExLWNkNDAtNDZlMS04ZTNhLWIzNmE5N2Q4OGY3ZCIsImMiOjEwfQ%3D%3D"  # Thay bằng URL trang web bạn muốn nhúng
# iframe = f"""
#     <iframe src="{url}" width="100%" height="700" style="border-radius:10px;"></iframe>
# """
# components.html(iframe, height=800)
# ###




    

    



