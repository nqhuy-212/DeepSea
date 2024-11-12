import streamlit as st 
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go 
from datetime import date,datetime
from load_data import get_data

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
nha_may = st.sidebar.selectbox("Chọn nhà máy",options=fty,index=fty.index(st.session_state.factory))
reports = ['Tổng hợp','Công nhân Cắt','Công nhân may','Công nhân QC1','Công nhân Là','Công nhân QC2','Công nhân đóng gói','Công nhân NDC','Công nhân phụ','Quản lý']
bao_cao = st.sidebar.selectbox("Chọn báo cáo",options= reports,index=2)

st.markdown(f'<h1 class="centered-title">BÁO CÁO THƯỞNG NĂNG SUẤT ({bao_cao})</h1>', unsafe_allow_html=True)
if bao_cao == 'Công nhân may':
    df_cn_may = get_data(DB='INCENTIVE',query=f"SELECT * FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_CN_MAY WHERE NHA_MAY = '{nha_may}' ORDER BY CHUYEN")
    df_cn_may['XUONG'] = df_cn_may['CHUYEN'].str[0:1] + 'P0' + df_cn_may['CHUYEN'].str[1:2]
    df_cn_may['SAH'] = df_cn_may['EFF_TB']*df_cn_may['TONG_TGLV']
    df_cn_may_selected = df_cn_may.query('NHA_MAY == @nha_may')
    df_cn_may_selected = df_cn_may_selected[~df_cn_may_selected['CHUYEN'].str.contains('TNC')]
    xuong = st.sidebar.multiselect("Chọn xưởng",options=df_cn_may_selected['XUONG'].unique(),default=df_cn_may_selected['XUONG'].unique())
    df_cn_may_selected= df_cn_may_selected[df_cn_may_selected['XUONG'].isin(xuong)]
    ###
    cols = st.columns([1,1,12])
    with cols[0]:
        nam_opt = df_cn_may_selected['NAM'].sort_values(ascending=False).unique()
        nam = st.selectbox("Chọn năm",options=nam_opt)
    with cols[1]:   
        df_cn_may_selected = df_cn_may_selected.query('NAM == @nam')
        thang_opt = df_cn_may_selected['THANG'].sort_values(ascending=False).unique()
        thang = st.selectbox("Chọn tháng",options=thang_opt)
    with cols[2]:  
        df_cn_may_selected = df_cn_may_selected.query('NAM == @nam and THANG == @thang')
        chuyen = st.multiselect("Chọn chuyền",options= df_cn_may_selected['CHUYEN'].unique(),default=df_cn_may_selected['CHUYEN'].unique())
    df_cn_may_selected = df_cn_may_selected[df_cn_may_selected['CHUYEN'].isin(chuyen)]
    df_cn_may_selected['Hiệu suất'] = df_cn_may_selected['EFF_TB'].apply(lambda x: f"{x:.0%}")
    df_cn_may_selected['Tiền thưởng'] = df_cn_may_selected['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
    ###
    so_ngay_min = df_cn_may_selected['SO_NGAY'].min()
    so_ngay_max = df_cn_may_selected['SO_NGAY'].max()
    so_ngay_from,so_ngay_to = st.sidebar.slider("Chọn số ngày làm việc",min_value= so_ngay_min,max_value=so_ngay_max,value=[so_ngay_min,so_ngay_max])
    df_cn_may_selected = df_cn_may_selected.query('SO_NGAY >= @so_ngay_from and SO_NGAY <=@so_ngay_to')
    ###
    cols = st.columns([1,4,2])
    with cols[0]:
        so_cn = df_cn_may_selected['MST'].count()
        Eff_tb = df_cn_may_selected['SAH'].sum()/df_cn_may_selected['TONG_TGLV'].sum()
        Incentive_tb = df_cn_may_selected['TONG_THUONG'].mean()
        so_ngay_tb = df_cn_may_selected['SO_NGAY'].mean()
        st.info("Tổng quan")
        st.metric(label="Số ngày làm việc trung bình",value= f"{so_ngay_tb:,.0f}")
        st.metric(label="Số công nhân",value= f"{so_cn:,.0f}")
        st.metric(label="Hiệu suất trung bình",value= f"{Eff_tb:,.0%}")
        st.metric(label="Tiền thưởng trung bình",value= f"{Incentive_tb:,.0f}")
    with cols[1]:   
        SCP_order = ['U','N','S','M']
        fig = px.scatter(
            df_cn_may_selected,
            x= "EFF_TB",
            y= "TONG_THUONG",
            color= "SCP",
            color_discrete_map={
                'U' : 'red',
                'N' : 'blue',
                'S' : 'green',
                'M' : 'purple'
            },
            size= "TONG_TGLV",
            hover_data={
                'MST':True,
                'HO_TEN' : True,
                'CHUYEN' : True,
                'EFF_TB' : False,
                'TONG_THUONG' : False,
                'Hiệu suất' : True,
                'Tiền thưởng' : True,
                'SCP' : False
            },
            category_orders= {'SCP' : SCP_order},
            # symbol='XUONG',
            size_max= 10
        )
        fig.update_layout(
            xaxis_title = 'Hiệu suất trung bình',
            yaxis_title = "Tổng thưởng (VNĐ)",
            title = "Phân bổ tiền thưởng theo hiệu suất"
        )
        fig.update_xaxes(
            tickformat = '.0%',
        )
        fig.update_traces(
            marker = dict(line = dict(width = 1,color = 'white')),
        )
        st.plotly_chart(fig,use_container_width=True)
        # st.dataframe(df_cn_may_selected)
    with cols[2]:
        SCP_order = ['U','N','S','M']
        fig = px.pie(
            df_cn_may_selected[df_cn_may_selected['SCP'].isin(SCP_order)],
            color="SCP",
            names="SCP",
            category_orders={"SCP" : SCP_order},
            color_discrete_map={
                'U' : 'red',
                'N' : 'blue',
                'S' : 'green',
                'M' : 'purple'
            }
        )
        fig.update_layout(
            title = "Tỉ lệ công nhân theo SCP"
        )
        fig.update_traces(
            textinfo = 'percent+label',
            textposition = 'inside',
            textfont = dict(size = 14)
        )
        st.plotly_chart(fig,use_container_width=True)
    cols = st.columns(3)
    with cols[0]:
        fig = px.histogram(
            df_cn_may_selected,
            x= "EFF_TB",
            text_auto= True
        )
        fig.update_layout(
            title = "Phân bổ công nhân theo hiệu suất",
            xaxis_title = "Hiệu suất",
            yaxis_title = "Số công nhân"
        )
        fig.update_xaxes(
            tickformat = ".0%"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        st.plotly_chart(fig,use_container_width=True)
    with cols[1]:
        SCP_order = ['U','N','S','M']
        fig = px.box(
            df_cn_may_selected,
            x= "SCP",
            y= "TONG_THUONG",
            color="SCP",
            category_orders= {"SCP" : SCP_order},
            color_discrete_map={
                'U' : 'red',
                'N' : 'blue',
                'S' : 'green',
                'M' : 'purple'
            }
        )
        fig.update_layout(
            title = "Phân bổ tiền thưởng theo bậc kỹ năng",
            yaxis_title = "Tiền thưởng"
        )
        st.plotly_chart(fig,use_container_width=True)
    with cols[2]:
        df_cn_may_selected_SCP = df_cn_may_selected.groupby(by="SCP").agg({"TONG_THUONG" : 'mean'}).reset_index()
        df_cn_may_selected_SCP['Tổng thưởng'] = df_cn_may_selected_SCP['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
        SCP_order = ['U','N','S','M']
        fig = px.bar(
            df_cn_may_selected_SCP,
            x='SCP',
            y= "TONG_THUONG",
            text= 'Tổng thưởng',
            color="SCP",
            color_discrete_map={
                'U' : 'red',
                'N' : 'blue',
                'S' : 'green',
                'M' : 'purple'
            },
            category_orders={"SCP" : SCP_order}
        )
        fig.update_traces(
            textposition = 'outside'
        )
        fig.update_layout(
            title = 'Tiền thưởng trung bình theo bậc kỹ năng',
            yaxis_title = 'Tiền thưởng'
        )
        st.plotly_chart(fig,use_container_width=True)
if bao_cao == 'Tổng hợp':
    df_nhom_may = get_data(DB='INCENTIVE',query=f"SELECT * FROM THUONG_NHOM_MAY_HANG_NGAY WHERE 'NT' + LEFT(LINE,1) = '{nha_may}'")
    df_nhom_may['Month'] = df_nhom_may['WorkDate'].str[5:7]
    df_nhom_may['Year'] = df_nhom_may['WorkDate'].str[:4]
    years = df_nhom_may['Year'].sort_values(ascending=False).unique()
    sel_year = st.sidebar.selectbox("Chọn năm",options=years)
    months = df_nhom_may[df_nhom_may['Year']==sel_year]['Month'].sort_values(ascending = False).unique()
    sel_month = st.sidebar.selectbox("Chọn tháng",months)
    df_nhom_may = df_nhom_may.query("Month == @sel_month and Year == @sel_year")
    # st.dataframe(df_nhom_may)
    df_nhom_cat = get_data(DB='INCENTIVE',query=f"SELECT * FROM THUONG_NHOM_CAT_HANG_NGAY WHERE NHA_MAY = '{nha_may}' AND NHOM NOT LIKE '%C99'")
    df_nhom_cat['THANG']= df_nhom_cat['NGAY'].str[5:7]
    df_nhom_cat['NAM']= df_nhom_cat['NGAY'].str[:4]
    df_nhom_cat = df_nhom_cat.query("NAM == @sel_year and THANG == @sel_month")
    # st.dataframe(df_nhom_cat)
    df_nhom_qc1 = get_data(DB='INCENTIVE',query=f"SELECT * FROM THUONG_NHOM_QC1_HANG_NGAY WHERE NHA_MAY = '{nha_may}' AND NHOM NOT LIKE '%QC199'")
    df_nhom_qc1['THANG']= df_nhom_qc1['NGAY'].str[5:7]
    df_nhom_qc1['NAM']= df_nhom_qc1['NGAY'].str[:4]
    df_nhom_qc1 = df_nhom_qc1.query("NAM == @sel_year and THANG == @sel_month")
    # st.dataframe(df_nhom_qc1)
    df_nhom_la = get_data(DB='INCENTIVE',query=f"SELECT * FROM THUONG_NHOM_LA_HANG_NGAY WHERE NHA_MAY = '{nha_may}' AND CHUYEN NOT LIKE '%I99'")
    df_nhom_la['THANG']= df_nhom_la['NGAY'].str[5:7]
    df_nhom_la['NAM']= df_nhom_la['NGAY'].str[:4]
    df_nhom_la = df_nhom_la.query("NAM == @sel_year and THANG == @sel_month")
    # st.dataframe(df_nhom_la)
    df_nhom_qc2 = get_data(DB='INCENTIVE',query=f"SELECT * FROM THUONG_NHOM_QC2_HANG_NGAY WHERE NHA_MAY = '{nha_may}' AND NHOM NOT LIKE '%QC299'")
    df_nhom_qc2['THANG']= df_nhom_qc2['NGAY'].str[5:7]
    df_nhom_qc2['NAM']= df_nhom_qc2['NGAY'].str[:4]
    df_nhom_qc2 = df_nhom_qc2.query("NAM == @sel_year and THANG == @sel_month")
    # st.dataframe(df_nhom_qc2)
    df_nhom_hoan_thien = get_data(DB='INCENTIVE',query=f"SELECT * FROM THUONG_NHOM_DONG_GOI_HANG_NGAY WHERE NHA_MAY = '{nha_may}' AND NHOM NOT LIKE '%F99'")
    df_nhom_hoan_thien['THANG']= df_nhom_hoan_thien['NGAY'].str[5:7]
    df_nhom_hoan_thien['NAM']= df_nhom_hoan_thien['NGAY'].str[:4]
    df_nhom_hoan_thien = df_nhom_hoan_thien.query("NAM == @sel_year and THANG == @sel_month")
    # st.dataframe(df_nhom_hoan_thien)
    df_nhom_ndc = get_data(DB='INCENTIVE',query=f"SELECT * FROM THUONG_NHOM_NDC_HANG_NGAY WHERE NHA_MAY = '{nha_may}' AND NHOM NOT LIKE '%NDC99'")
    df_nhom_ndc['THANG']= df_nhom_ndc['NGAY'].str[5:7]
    df_nhom_ndc['NAM']= df_nhom_ndc['NGAY'].str[:4]
    df_nhom_ndc = df_nhom_ndc.query("NAM == @sel_year and THANG == @sel_month")
    # st.dataframe(df_nhom_ndc)
    df_quan_ly = get_data(DB='INCENTIVE',query=f"SELECT * FROM INCENTIVE_QUANLY_HANG_NGAY WHERE 'NT'+LEFT(CHUYEN,1) = '{nha_may}'")
    df_quan_ly['THANG']= df_quan_ly['NGAY'].str[5:7]
    df_quan_ly['NAM']= df_quan_ly['NGAY'].str[:4]
    df_quan_ly = df_quan_ly.query("NAM == @sel_year and THANG == @sel_month")
    # st.dataframe(df_quan_ly)
    df_cn_phu = get_data(DB='INCENTIVE',query=f"SELECT * FROM INCENTIVE_CN_PHU_HANG_NGAY WHERE 'NT'+LEFT(CHUYEN,1) = '{nha_may}'")
    df_cn_phu['THANG']= df_cn_phu['NGAY'].str[5:7]
    df_cn_phu['NAM']= df_cn_phu['NGAY'].str[:4]
    df_cn_phu = df_cn_phu.query("NAM == @sel_year and THANG == @sel_month")
    # st.dataframe(df_cn_phu)
    st.info("Tổng tiền thưởng Incentive")
    cols = st.columns(4)
    with cols[0]:
        tong_thuong_cat = df_nhom_cat['TONG_THUONG_NHOM'].sum()
        st.metric("Nhóm Cắt",value=f"{tong_thuong_cat:,.0f} VNĐ")
        ###
        tong_thuong_qc2 = df_nhom_qc2['TONG_THUONG_NHOM'].sum()
        st.metric("Nhóm QC2",value=f"{tong_thuong_qc2:,.0f} VNĐ")
    with cols[1]:
        tong_thuong_may = df_nhom_may['TONG_THUONG'].sum()
        st.metric("Nhóm May",value=f"{tong_thuong_may:,.0f} VNĐ")
        ###
        tong_thuong_hoan_thien = df_nhom_hoan_thien['TONG_THUONG_NHOM'].sum()
        st.metric("Nhóm Hoàn thiện",value=f"{tong_thuong_hoan_thien:,.0f} VNĐ")
    with cols[2]:
        tong_thuong_qc1 = df_nhom_qc1['TONG_THUONG_NHOM'].sum()
        st.metric("Nhóm QC1",value=f"{tong_thuong_qc1:,.0f} VNĐ")
        ###
        tong_thuong_NDC= df_nhom_ndc['THUONG_NHOM'].sum()
        st.metric("Nhóm Dò kim",value=f"{tong_thuong_NDC:,.0f} VNĐ")
    with cols[3]:
        tong_thuong_la = df_nhom_la['TONG_THUONG_NHOM'].sum()
        st.metric("Nhóm Là",value=f"{tong_thuong_la:,.0f} VNĐ")
         ###
        tong_thuong_quan_ly= df_quan_ly['THUONG_CA_NHAN'].sum()
        tong_thuong_cn_phu= df_cn_phu['THUONG_CA_NHAN'].sum()
        st.metric("Nhóm Quản lý",value=f"{tong_thuong_quan_ly:,.0f} VNĐ")
        st.metric("Nhóm công nhân phụ",value=f"{tong_thuong_cn_phu:,.0f} VNĐ")