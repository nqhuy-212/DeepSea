import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from datetime import datetime
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from pathlib import Path
import os

st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        margin-top: 0 px;
        color: 'rgb(255,255,255)';
        font-size : 48px;
    }
    div.block-container{padding-top:1.5rem};
    </style>
    """,
    unsafe_allow_html=True
)

BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR / ".env"
load_dotenv(env_file)

def get_data(DB,query):
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        f'SERVER={os.getenv("SERVER")};'
        f'DATABASE={DB};'
        f'UID={os.getenv("UID")};'
        f'PWD={os.getenv("PASSWORD")}'
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df1 = get_data('DW','SELECT * FROM ETS_5 WHERE WORKDATE < CAST(GETDATE() AS DATE)')
df1= df1.groupby(by=['WorkDate','Line']).agg({
    'Total_Qty':'sum',
    'SAH_A' : 'sum'
})
df2 = get_data('DW','SELECT * FROM PPC')
#st.dataframe(df2)
df3 = get_data('DW',"SELECT * FROM HR WHERE (KOIS = 'K' OR (KOIS = 'I' AND LINE LIKE '_TNC01')) AND WORKDATE >= '2024-09-01'")
#st.dataframe(df3)

#ghép các bảng với nhau
df = pd.merge(df1,df2, on = ['WorkDate','Line'], how= 'left')
df = pd.merge(df,df3, on=['WorkDate','Line'], how= 'left')
#di chuyển cột
move_col = df.pop('Fty')
df.insert(0,'Fty',move_col)
move_col = df.pop('Unit')
df.insert(1,'Unit',move_col)
move_col = df.pop('Line')
df.insert(2,'Line',move_col)
move_col = df.pop('Style_P')
df.insert(2,'Style_P',move_col)
df.rename(columns={'Total_Qty':'Qty_A'}, inplace= True)
df.dropna(subset=['Fty'])
df = df[df['Fty'] != 'nan']
#chuyển cột WorkDate về dạng date
df['WorkDate'] = pd.to_datetime(df['WorkDate'], format='%Y-%m-%d')
df['WorkDate'] = df['WorkDate'].dt.date
df['Attn_P'] = df.apply(lambda row: 0.93 if row['Fty'] == 'NT2' else 0.9,axis=1)
df['Total_hours_P'] = df['Hours_P'] * df['Worker_P'] * df['Attn_P']
df['WS*Hours_A'] = df['Worker_A']*df['Hours_A']

###########################
fty = ['NT1','NT2']
sel_fty = st.sidebar.selectbox("Chọn nhà máy:",options = fty,index=0)

unit = df[df['Fty'] == sel_fty]['Unit'].unique()
unit_sorted = sorted(unit, reverse= False)
sel_unit = st.sidebar.multiselect("Chọn xưởng:", options= unit, default= unit_sorted)

min_date = df['WorkDate'].min()
today = date.today()
first_day_of_month =  today.replace(day=1)
start_date = st.sidebar.date_input(label="Từ ngày:",value= first_day_of_month)

max_date = df['WorkDate'].max()
end_date = st.sidebar.date_input(label="Đến ngày:", value= max_date)

st.markdown(f'<h1 class="centered-title">BÁO CÁO TỔNG HỢP {sel_fty}</h1>', unsafe_allow_html=True)
df4 = df[
(df['Unit'].isin(sel_unit)) & 
(df['WorkDate'] >= start_date) & 
(df['WorkDate'] <= end_date)]

Qty_A = df4['Qty_A'].sum()
Qty_P = df4['Qty_P'].sum()
SAH_A = df4['SAH_A'].sum()
SAH_P = df4['SAH_P'].sum()
Total_hours_A = df4['Total_hours_A'].sum()
Total_hours_P = df4['Total_hours_P'].sum()
Eff_A = SAH_A/Total_hours_A
Eff_P = SAH_P/Total_hours_P
Attn_A = df4['Total_hours_A'].sum()/(df4['WS*Hours_A']).sum()
Attn_P = df4['Attn_P'].mean()
Worker_A = df4[df4['WorkDate'] == end_date]['Worker_A'].sum()
Worker_P = df4[df4['WorkDate'] == end_date]['Worker_P'].sum()
Hour_A = df4['Total_hours_A'].sum()/df4['Worker_A'].sum()
Hour_P = df4['Total_hours_P'].sum()/df4['Worker_P'].sum()
SAH_CN_A = df4['SAH_A'].sum()/df4['Worker_A'].sum()
SAH_CN_P = df4['SAH_P'].sum()/df4['Worker_P'].sum()

cols = st.columns(4, gap= 'large')
with cols[0]:
    st.info('Sản lượng',icon= "👕" )
    st.metric(label= 'Mục tiêu',value= f'{Qty_P:,.0f}')
    st.metric(label= 'Thực tế',value= f'{Qty_A:,.0f}',delta= f'{(Qty_A-Qty_P):,.0f}')
    
    st.info('Tổng CN May',icon="👩‍💼")
    st.metric(label='Mục tiêu', value= f'{Worker_P:,.0f}')
    st.metric(label='Thực tế', value= f'{Worker_A:,.0f}',delta=f'{(Worker_A-Worker_P):,.0f}')
with cols[1]:
    st.info('Tổng SAH',icon= "💰" )
    st.metric(label= 'Mục tiêu',value= f'{SAH_P:,.0f}')
    st.metric(label= 'Thực tế',value= f'{SAH_A:,.0f}',delta= f'{(SAH_A-SAH_P):,.0f}')
    
    st.info('Tỉ lệ đi làm',icon="🏃")
    st.metric(label='Mục tiêu', value= f'{Attn_P:,.0%}')
    st.metric(label='Thực tế', value= f'{Attn_A:,.1%}',delta=f'{(Attn_A-Attn_P):,.1%}')
with cols[2]:
    st.info('Tổng TGLV',icon= "🕗" )
    st.metric(label= 'Mục tiêu',value= f'{Total_hours_P:,.0f}')
    st.metric(label= 'Thực tế',value= f'{Total_hours_A:,.0f}',delta=f'{(Total_hours_A-Total_hours_P):,.0f}')
    
    st.info('Số giờ làm việc',icon= "🕗" )
    st.metric(label= 'Mục tiêu',value= f'{Hour_P:,.1f}')
    st.metric(label= 'Thực tế',value= f'{Hour_A:,.1f}',delta=f'{(Hour_A-Hour_P):,.1f}')
with cols[3]:
    st.info('Hiệu suất',icon= "📈" )
    st.metric(label= 'Mục tiêu',value= f'{Eff_P:,.1%}')
    st.metric(label= 'Thực tế',value= f'{Eff_A:,.1%}',delta=f'{(Eff_A-Eff_P):,.1%}')
    
    st.info('SAH/CN/Ngày',icon= "💰" )
    st.metric(label= 'Mục tiêu',value= f'{SAH_CN_P:,.1f}')
    st.metric(label= 'Thực tế',value= f'{SAH_CN_A:,.1f}',delta=f'{(SAH_CN_A-SAH_CN_P):,.1f}')
# df5 = nhóm theo ngày    
st.markdown("---")
df5 = df4.groupby(by=df4['WorkDate']).agg({
'Qty_A' : 'sum',
'Qty_P' : 'sum',
'SAH_A' : 'sum',
'SAH_P' : 'sum',
'Total_hours_A' : 'sum',
'Total_hours_P' : 'sum'
    }).reset_index()

df5['SAH_A_formated']= df5['SAH_A'].apply(lambda x: f"{x:,.0f}")
df5 = df5.sort_values('WorkDate')

df6 = pd.melt(df5,id_vars= 'WorkDate',value_vars=['SAH_A','SAH_P'])
df6 = df6.sort_values('WorkDate')
df6 = df6.rename(columns={'value' : 'SAH','variable' : 'Chỉ số'})
df6 = df6.replace({'Chỉ số': {'SAH_A' : 'SAH thực tế','SAH_P' : 'SAH mục tiêu'}})
df6['SAH_formated'] = df6['SAH'].apply(lambda x: f"{x:,.0f}")
# st.dataframe(df6)
fig = px.line(df6,
                x= df6['WorkDate'],
                y= df6['SAH'],
                color=df6['Chỉ số'],
                color_discrete_map={
                    'SAH thực tế' : 'blue',
                    'SAH mục tiêu' : 'red'
                },
                text= df6['SAH_formated']
                )
fig.update_xaxes(
    dtick = 'D1',
    tickangle = 45,
    tickformat = "%d/%m"
)
fig.update_layout(
    xaxis_title = 'Ngày',
    yaxis_title = 'Tổng SAH',
    title = "Tổng SAH theo ngày"
)
fig.update_traces(
    textposition = 'top center',
    textfont = dict(size = 14),
)
st.plotly_chart(fig,use_container_width=True)
#########
df5['Eff_A'] = df5['SAH_A']/df5['Total_hours_A']
df5['Eff_P'] = df5['SAH_P']/df5['Total_hours_P']
# st.dataframe(df5)
df6 = pd.melt(df5,id_vars= 'WorkDate',value_vars=['Eff_A','Eff_P'])
df6 = df6.sort_values('WorkDate')
df6 = df6.rename(columns={'value' : 'Hiệu suất','variable' : 'Chỉ số'})
df6 = df6.replace({'Chỉ số': {'Eff_A' : 'Hiệu suất thực tế','Eff_P' : 'Hiệu suất mục tiêu'}})
df6['Eff_formated'] = df6['Hiệu suất'].apply(lambda x: f"{x:,.1%}")
# st.dataframe(df6)
fig = px.line(df6,
                x= df6['WorkDate'],
                y= df6['Hiệu suất'],
                color=df6['Chỉ số'],
                text= df6['Eff_formated'],
                color_discrete_map={
                    'Hiệu suất thực tế' : 'blue',
                    'Hiệu suất mục tiêu' : 'red'
                }
                )
fig.update_xaxes(
    dtick = 'D1',
    tickangle = 45,
    tickformat = "%d/%m"
)
fig.update_layout(
    xaxis_title = 'Ngày',
    yaxis_title = 'Tổng SAH',
    title = "Hiệu suất trung bình theo ngày"
)
fig.update_traces(
    textposition = 'top center',
    textfont = dict(size = 14),
)

st.plotly_chart(fig,use_container_width=True)

st.markdown("---")
# tính toán SAH, Eff theo xưởng
df_unit_eff = df4.groupby(by = ['Unit']).agg({
    'SAH_A' : 'sum',
    'Total_hours_A' : 'sum',
    'SAH_P' : 'sum',
    'Total_hours_P' : 'sum'
},axis = 1).reset_index()
df_unit_eff['Eff_A'] = (df_unit_eff['SAH_A']/df_unit_eff['Total_hours_A'])
df_unit_eff['Eff_A_formated'] = df_unit_eff['Eff_A'].apply(lambda x: f"{x:.1%}")
df_unit_eff['Eff_P'] = (df_unit_eff['SAH_P']/df_unit_eff['Total_hours_P'])
df_unit_eff['Eff_P_formated'] = df_unit_eff['Eff_P'].apply(lambda x: f"{x:.1%}")
df_unit_eff['SAH_A_formated'] = df_unit_eff['SAH_A'].apply(lambda x: f"{x:,.0f}")
df_unit_eff['SAH_P_formated']= df_unit_eff['SAH_P'].apply(lambda x: f"{x:,.0f}")
cols = st.columns(2)
with cols[0]:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x= df_unit_eff['Unit'],
        y = df_unit_eff['SAH_A'],
        text = df_unit_eff['SAH_A_formated'],
        textposition= 'outside',
        marker=dict(color = 'blue'),
        name = "Thực tế"
    ))
    fig.add_trace(go.Bar(
        x= df_unit_eff['Unit'],
        y = df_unit_eff['SAH_P'],
        text = df_unit_eff['SAH_P_formated'],
        textposition= 'outside',
        marker= dict(color = 'red'),
        name="Mục tiêu"
    ))
    
    fig.update_layout(
        title="Tổng SAH theo xưởng",
        xaxis_title="Xưởng", 
        yaxis_title="Tổng SAH" 
    )

    max_SAH = max(df_unit_eff['SAH_A'].max(),df_unit_eff['SAH_P'].max()) * 1.2
    fig.update_yaxes(
        range = [0,max_SAH],
        # showticklabels = False
    )  
    st.plotly_chart(fig,use_container_width=True)
## hiệu suất theo xưởng
with cols[1]:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x= df_unit_eff['Unit'],
        y = df_unit_eff['Eff_A'],
        text = df_unit_eff['Eff_A_formated'],
        textposition= 'outside',
        marker=dict(color = 'blue'),
        name = "Thực tế"
    ))
    fig.add_trace(go.Bar(
        x= df_unit_eff['Unit'],
        y = df_unit_eff['Eff_P'],
        text = df_unit_eff['Eff_P_formated'],
        textposition= 'outside',
        marker= dict(color = 'red'),
        name="Mục tiêu"
    ))
    
    fig.update_layout(
        title="Hiệu suất theo xưởng",
        xaxis_title="Xưởng", 
        yaxis_title="Hiệu suất trung bình" 
    )
    max_SAH = max(df_unit_eff['Eff_A'].max(),df_unit_eff['Eff_P'].max()) * 1.2
    fig.update_yaxes(
        range = [0,max_SAH],
        # showticklabels = False
    )
    st.plotly_chart(fig,use_container_width=True,key='fig2')

st.markdown("---")
## Heatmap theo chuyền , ngày
df_line_eff = df4.groupby(by = ['WorkDate','Line']).agg({
    'SAH_A' : 'sum',
    'Total_hours_A' : 'sum'
},axis = 1).reset_index()

df_line_eff['Eff_A'] = df_line_eff['SAH_A']/df_line_eff['Total_hours_A']

df_line_eff_pivot = pd.pivot_table(data=df_line_eff,index='Line',columns='WorkDate',values='Eff_A')

fig = px.imshow(
    df_line_eff_pivot,
    color_continuous_scale= "RdYlGn",
    # color_continuous_midpoint=0.5,
    text_auto= True)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
num_row = df_line_eff_pivot.shape[0]
row_hight = 35
fig.update_layout(
    title = "Biểu đồ nhiệt - Hiệu suất chuyền theo ngày",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = num_row * row_hight
)
fig.update_traces(
    texttemplate='%{z:.1%}',
    textfont = dict(size = 14),
    zmin = 0,
    zmax = 1
)

st.plotly_chart(fig,use_container_width=True)






