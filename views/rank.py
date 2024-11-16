import streamlit as st 
from load_data import get_data
import pandas as pd
import plotly.express as px

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
    div.block-container{padding-top:2rem};
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(f'<h1 class="centered-title">BẢNG XẾP HẠNG</h1>', unsafe_allow_html=True)
# st.markdown("---")
rp_type = st.sidebar.radio("Xếp hạng theo",options=['Hiệu suất','Tiền thưởng'])
chuyen_cong_nhan = st.sidebar.radio("Chuyền/Công nhân",options=['Chuyền','Công nhân'])
ds_nha_may = ['NT1','NT2']
nha_may = st.sidebar.multiselect("Chọn nhà máy",options=ds_nha_may,default=ds_nha_may)
### Lấy dữ liệu từ SQL
df_chuyen = get_data("INCENTIVE","""
                     SELECT 'NT' + LEFT(Line,1) as NHA_MAY,WorkDate as NGAY,Line as CHUYEN,
                     SAH,Total_hours as TGLV,TONG_THUONG
                     FROM THUONG_NHOM_MAY_HANG_NGAY ORDER BY WORKDATE,LINE
                     """)
df_chuyen['NAM'] = df_chuyen['NGAY'].str[:4]
df_chuyen['THANG'] = df_chuyen['NGAY'].str[5:7]
df_chuyen['NGAY'] = pd.to_datetime(df_chuyen['NGAY'],format="%Y-%m-%d")
ds_nam = sorted(df_chuyen['NAM'].unique(),reverse =True)
nam = st.sidebar.selectbox("Chọn năm",options=ds_nam)
ds_thang = sorted(df_chuyen[df_chuyen['NAM'] == nam]['THANG'].unique(),reverse=True)
thang = st.sidebar.selectbox("Chọn tháng",options=ds_thang)
ngay_min = df_chuyen[(df_chuyen['NAM'] == nam) & (df_chuyen['THANG'] == thang)]['NGAY'].min()
ngay_max = df_chuyen[(df_chuyen['NAM'] == nam) & (df_chuyen['THANG'] == thang)]['NGAY'].max()
tu_ngay = st.sidebar.date_input("Từ ngày",value=ngay_min)
den_ngay = st.sidebar.date_input("Đến ngày",value=ngay_max)
df_ten_chuyen = pd.DataFrame({'CHUYEN' : ['11S01','11S03','11S05','11S07','11S09','11S11','11S13', \
                                        '12S01','12S03','12S05','12S07','12S09','12S11','12S13', \
                                        '21S01','21S03','21S05','21S07','21S09','21S11','21S13', \
                                        '22S01','22S03','22S05','22S07','22S09','22S11','22S13', \
                                        '23S01','23S03','23S05','23S07','23S09','23S11','23S13', \
                                        '24S01','24S03','24S05','24S07','24S09','24S11','24S13', \
                                        '25S01','25S03','25S05','25S07','25S09','25S11','25S13'],\
                'TEN' : ['🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    ]})
# st.dataframe(df_ten_chuyen)
df_chuyen = df_chuyen.merge(df_ten_chuyen,on='CHUYEN',how='left')
df_chuyen = df_chuyen.query("NAM == @nam and THANG == @thang and NGAY >= @tu_ngay and NGAY <= @den_ngay")
df_chuyen = df_chuyen[df_chuyen['NHA_MAY'].isin(nha_may)]
df_chuyen[['SAH lũy kế','TGLV lũy kế','Thưởng lũy kế']] = (df_chuyen.groupby('CHUYEN')[['SAH','TGLV','TONG_THUONG']].cumsum())
# st.dataframe(df_chuyen)
###
df_cong_nhan = get_data("INCENTIVE","""
                        SELECT MST,HO_TEN,CHUYEN,NGAY,SAH,SO_GIO as TGLV,THUONG_CA_NHAN
                        FROM INCENTIVE_CN_MAY_HANG_NGAY WHERE THUONG_CA_NHAN >0
                        ORDER BY NGAY,CHUYEN
                        """)
df_cong_nhan['NHA_MAY'] = 'NT' + df_cong_nhan['CHUYEN'].str[:1]
df_cong_nhan['NAM'] = df_cong_nhan['NGAY'].str[:4]
df_cong_nhan['THANG'] = df_cong_nhan['NGAY'].str[5:7]
df_cong_nhan['NGAY'] = pd.to_datetime(df_cong_nhan['NGAY'])
df_cong_nhan = df_cong_nhan.query("NAM == @nam and THANG == @thang and NGAY >= @tu_ngay and NGAY <=@den_ngay")
df_cong_nhan = df_cong_nhan[df_cong_nhan['NHA_MAY'].isin(nha_may)]
###
if chuyen_cong_nhan == "Chuyền":
    st.info("🏆 Bảng xếp hạng chuyền ")
    df_chuyen_groupby = df_chuyen.groupby(by=["TEN",'CHUYEN']).agg({'SAH' : 'sum','TGLV' : 'sum','TONG_THUONG' : 'sum'}).reset_index()
    df_chuyen_groupby['EFF'] = df_chuyen_groupby['SAH']/df_chuyen_groupby['TGLV']
    df_chuyen_groupby['Hiệu suất'] = df_chuyen_groupby['EFF'].apply(lambda x: f"{x:,.1%}")
    df_chuyen_groupby['Tổng thưởng'] = df_chuyen_groupby['TONG_THUONG'].apply(lambda x: f"{x/1_000_000:,.1f} triệu")
    df_chuyen_groupby['TEN_CHUYEN'] = df_chuyen_groupby['TEN'] + '-' + df_chuyen_groupby['CHUYEN']
    if rp_type == "Hiệu suất":
        col1,col2,col3 = st.columns(3)
        with col2:
            chuyen_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,0]
            # hieu_suat_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,5]
            st.metric("Chuyền vô địch",value= f"{chuyen_num_1}🥇")
            # st.metric("Hiệu suất", value= f"{hieu_suat_num_1}")
        with col1:
            st.metric("",value="")
            chuyen_num_2 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[1,0]
            st.metric("Chuyền Á quân",value= f"{chuyen_num_2}🥈")
        with col3:
            st.metric("",value="")
            st.metric("",value="")
            chuyen_num_3 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[2,0]
            st.metric("Chuyền hạng 3",value= f"{chuyen_num_3}🥉")
        st.markdown("---")

        fig = px.bar(
        df_chuyen_groupby.sort_values('EFF',ascending=True).iloc[-10:],
        x="EFF",
        y='TEN_CHUYEN',
        text="Hiệu suất"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        max_eff = df_chuyen_groupby['EFF'].max()*1.2
        fig.update_xaxes(
            tickformat = ",.0%",
            range = [0,max_eff]
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        fig.update_layout(
            title = "Top 10 chuyền có hiệu suất cao nhất",
            xaxis_title = 'Hiệu suất chuyền',
            yaxis_title = 'Chuyền'
        )
        st.plotly_chart(fig,use_container_width=True)
        ###
        with st.expander("Dữ liệu chi tiết"):
            st.dataframe(df_chuyen_groupby.sort_values("EFF",ascending=False))
    if rp_type == "Tiền thưởng":
        col1,col2,col3 = st.columns(3)
        with col2:
            chuyen_num_1 = df_chuyen_groupby.sort_values('TONG_THUONG',ascending=False).iloc[0,0]
            # hieu_suat_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,5]
            st.metric("Chuyền vô địch",value= f"{chuyen_num_1}🥇")
            # st.metric("Hiệu suất", value= f"{hieu_suat_num_1}")
        with col1:
            st.metric("",value="")
            chuyen_num_2 = df_chuyen_groupby.sort_values('TONG_THUONG',ascending=False).iloc[1,0]
            st.metric("Chuyền Á quân",value= f"{chuyen_num_2}🥈")
        with col3:
            st.metric("",value="")
            st.metric("",value="")
            chuyen_num_3 = df_chuyen_groupby.sort_values('TONG_THUONG',ascending=False).iloc[2,0]
            st.metric("Chuyền hạng 3",value= f"{chuyen_num_3}🥉")
        st.markdown("---")
        fig = px.bar(
            df_chuyen_groupby.sort_values('TONG_THUONG',ascending=True).iloc[-10:],
            x="TONG_THUONG",
            y='TEN_CHUYEN',
            text="Tổng thưởng"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        fig.update_layout(
            title = "Top 10 chuyền có tiền thưởng cao nhất",
            xaxis_title = 'Tiền thưởng',
            yaxis_title = 'Chuyền'
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        max_tien_thuong = df_chuyen_groupby['TONG_THUONG'].max()*1.2
        fig.update_xaxes(
            range=[0,max_tien_thuong]
        )
        st.plotly_chart(fig,use_container_width=True)
        ###
        with st.expander("Dữ liệu chi tiết"):
            st.dataframe(df_chuyen_groupby.sort_values("TONG_THUONG",ascending=False))
if chuyen_cong_nhan == "Công nhân":
    st.info("🥇 Bảng xếp hạng công nhân may")
    df_cong_nhan_groupby = df_cong_nhan.groupby(by=['NHA_MAY','MST','HO_TEN']).agg({'SAH' : 'sum','TGLV' : 'sum','THUONG_CA_NHAN' :'sum'}).reset_index()
    df_cong_nhan_groupby['EFF'] = df_cong_nhan_groupby['SAH']/df_cong_nhan_groupby['TGLV']
    df_cong_nhan_groupby['Hiệu suất'] = df_cong_nhan_groupby['EFF'].apply(lambda x: f"{x:,.1%}")
    df_cong_nhan_groupby['Tiền thưởng'] = df_cong_nhan_groupby['THUONG_CA_NHAN'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    df_cong_nhan_groupby['MST_HO_TEN'] = df_cong_nhan_groupby['NHA_MAY'] + '-' + df_cong_nhan_groupby['MST'] + '-' + df_cong_nhan_groupby['HO_TEN']
    if rp_type == "Hiệu suất":
        col1,col2,col3 = st.columns(3)
        with col2:
            cn_num_1 = df_cong_nhan_groupby.sort_values('EFF',ascending=False).iloc[0,2]
            # hieu_suat_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,5]
            st.metric("Hạng nhất",value= f"{cn_num_1}🥇")
            # st.metric("Hiệu suất", value= f"{hieu_suat_num_1}")
        with col1:
            st.metric("",value="")
            cn_num_2 = df_cong_nhan_groupby.sort_values('EFF',ascending=False).iloc[1,2]
            st.metric("Hạng nhì",value= f"{cn_num_2}🥈")
        with col3:
            st.metric("",value="")
            st.metric("",value="")
            cn_num_3 = df_cong_nhan_groupby.sort_values('EFF',ascending=False).iloc[2,2]
            st.metric("Hạng ba",value= f"{cn_num_3}🥉")
        st.markdown("---")
        fig = px.bar(
            df_cong_nhan_groupby.sort_values('EFF',ascending=True).iloc[-10:],
            x="EFF",
            y='MST_HO_TEN',
            text="Hiệu suất"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        max_eff = df_cong_nhan_groupby['EFF'].max()*1.2
        fig.update_xaxes(
            tickformat = ",.0%",
            range = [0,max_eff]
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        fig.update_layout(
            title = "Top 10 công nhân có hiệu suất cao nhất",
            xaxis_title = 'Hiệu suất cá nhân',
            yaxis_title = 'MST - Họ tên'
        )
        st.plotly_chart(fig,use_container_width=True,key='bar_cn1')
        ###
        with st.expander("Dữ liệu chi tiết"):
            st.dataframe(df_cong_nhan_groupby.sort_values("EFF",ascending=False))
    if rp_type == "Tiền thưởng":
        col1,col2,col3 = st.columns(3)
        with col2:
            cn_num_1 = df_cong_nhan_groupby.sort_values('THUONG_CA_NHAN',ascending=False).iloc[0,2]
            # hieu_suat_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,5]
            st.metric("Hạng nhất",value= f"{cn_num_1}🥇")
            # st.metric("Hiệu suất", value= f"{hieu_suat_num_1}")
        with col1:
            st.metric("",value="")
            cn_num_2 = df_cong_nhan_groupby.sort_values('THUONG_CA_NHAN',ascending=False).iloc[1,2]
            st.metric("Hạng hai",value= f"{cn_num_2}🥈")
        with col3:
            st.metric("",value="")
            st.metric("",value="")
            cn_num_3 = df_cong_nhan_groupby.sort_values('THUONG_CA_NHAN',ascending=False).iloc[2,2]
            st.metric("Hạng 3",value= f"{cn_num_3}🥉")
        st.markdown("---")
        fig = px.bar(
            df_cong_nhan_groupby.sort_values('THUONG_CA_NHAN',ascending=True).iloc[-10:],
            x="THUONG_CA_NHAN",
            y='MST_HO_TEN',
            text="Tiền thưởng"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        fig.update_layout(
            title = "Top 10 công nhân đạt tiền thưởng cao nhất",
            xaxis_title = 'Tiền thưởng',
            yaxis_title = 'MST - Họ tên'
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        max_tien_thuong = df_cong_nhan_groupby['THUONG_CA_NHAN'].max()*1.2
        fig.update_xaxes(
            range=[0,max_tien_thuong]
        )
        st.plotly_chart(fig,use_container_width=True,key='bar_cn2')
        ###
        with st.expander("Dữ liệu chi tiết"):
            st.dataframe(df_cong_nhan_groupby.sort_values('THUONG_CA_NHAN',ascending=False))