import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from datetime import datetime
from datetime import date,timedelta
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from load_data import get_data
import time
import numpy as np

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

df1 = get_data('DW','SELECT * FROM ETS_5 WHERE WORKDATE < CAST(GETDATE() AS DATE)')
df1= df1.groupby(by=['WorkDate','Line']).agg({
    'Total_Qty':'sum',
    'SAH_A' : 'sum'
})

df2 = get_data('DW','SELECT * FROM PPC')
#st.dataframe(df2)
df3 = get_data('DW',"SELECT * FROM HR_INCLUDE_TNC WHERE KOIS = 'K'  AND WORKDATE >= '2024-09-01'")
# st.dataframe(df3)

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
sel_fty = st.sidebar.selectbox("Chọn nhà máy:",options = fty,index=fty.index(st.session_state.factory))
unit = df[df['Fty'] == sel_fty]['Unit'].unique()
unit_sorted = sorted(unit, reverse= False)
sel_unit = st.sidebar.multiselect("Chọn xưởng:", options= unit, default= unit_sorted)

min_date = df['WorkDate'].min()
today = date.today() if date.today().day >1 else date.today() - timedelta(days=1)
first_day_of_month =  today.replace(day=1)
start_date = st.sidebar.date_input(label="Từ ngày:",value= first_day_of_month)

max_date = df['WorkDate'].max()
end_date = st.sidebar.date_input(label="Đến ngày:", value= max_date)

styles = df[
(df['Unit'].isin(sel_unit)) & 
(df['WorkDate'] >= start_date) & 
(df['WorkDate'] <= end_date)]['Style_P'].unique()
sel_style = st.sidebar.multiselect("Chọn Style:",options=styles,default=styles)

st.markdown(f'<h1 class="centered-title">BÁO CÁO TỔNG HỢP {sel_fty}</h1>', unsafe_allow_html=True)
df4 = df[
(df['Unit'].isin(sel_unit)) & 
(df['WorkDate'] >= start_date) & 
(df['WorkDate'] <= end_date) &
(df['Style_P'].isin(sel_style))]

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
## Heatmap hiệu suất theo chuyền , ngày
df_line_eff = df4.groupby(by = ['WorkDate','Line']).agg({
    'SAH_A' : 'sum',
    'Total_hours_A' : 'sum'
},axis = 1).reset_index()

df_line_eff['Eff_A'] = df_line_eff['SAH_A']/df_line_eff['Total_hours_A']

df_line_eff_pivot = pd.pivot_table(data=df_line_eff,index='Line',columns='WorkDate',values='Eff_A')
df4['Style_P_short'] = df4['Style_P'].str[-4:]
df_line_style = pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='Style_P')
df_line_short_style = pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='Style_P_short')
df_line_SAH = pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='SAH_A')

df4['Link_anh'] = 'http://localhost:100/sketch/' + df4['Style_P'] + '.png'
df_line_link_anh = pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='Link_anh')

customdata = np.dstack([df_line_style.values, df_line_SAH.values,df_line_link_anh.values])

#Vẽ biểu đồ nhiệt theo Eff
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
    height = num_row * row_hight,
)
fig.update_traces(
    customdata=customdata,
    texttemplate='%{z:.0%}',
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
    hovertemplate=(
        "Style: %{customdata[0]}<br>"
        "SAH: %{customdata[1]:.0f}<br>"
        # "<img src='%{customdata[2]}' style='width:100px;height:100px;'>"
    )
)
st.plotly_chart(fig,use_container_width=True,key='heatmap0')
#Vẽ biểu đồ nhiệt theo short style
fig = px.imshow(
    df_line_eff_pivot,
    color_continuous_scale= "RdYlGn",
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
    title = "Style_P",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = num_row * row_hight
)
fig.update_traces(
    customdata = customdata,
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
    hovertemplate=(
        "Hiệu suất: %{z:.1%}<br>"
        "SAH: %{customdata[1]:.0f}"
    ),
    text=df_line_short_style.values, 
    texttemplate="%{text}"
)
st.plotly_chart(fig,use_container_width=True,key='heatmap1')
#Vẽ biểu đồ nhiệt theo SAH
fig = px.imshow(
    df_line_eff_pivot,
    color_continuous_scale= "RdYlGn",
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
    title = "SAH",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = num_row * row_hight
)
fig.update_traces(
    customdata = customdata,
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
    hovertemplate=(
        "Hiệu suất: %{z:.1%}<br>"
        "Style: %{customdata[0]}"
    ),
    text=df_line_SAH.values, 
    texttemplate="%{text:.0f}"
)
st.plotly_chart(fig,use_container_width=True,key='heatmap2')
# #Vẽ biểu đồ nhiệt theo Eff - Style - SAH
# df4['Eff_formated'] = (df4['SAH_A']/df4['Total_hours_A']).apply(lambda x: f"{x:.0%}")
# df4['SAH_A_formated'] = df4['SAH_A'].apply(lambda x: f"{x:.0f}")
# df_line_eff_formated = pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='Eff_formated')
# df_line_SAH_formated= pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='SAH_A_formated')

# text_data = df_line_short_style + "<br>" + df_line_eff_formated + "<br>" + df_line_SAH_formated
# fig = px.imshow(
#     df_line_eff_pivot,
#     color_continuous_scale= "RdYlGn",
#     text_auto= True)
# fig.update_xaxes(
#     dtick = 'D1',
#     tickformat = '%d/%m',
#     tickfont = dict(size = 12)
# )
# fig.update_yaxes(
#     tickfont = dict(size = 14),
#     dtick = 'D1'
# )
# num_row = df_line_eff_pivot.shape[0]
# row_hight = 70
# fig.update_layout(
#     title = "SAH",
#     xaxis_title = "Ngày",
#     yaxis_title = "Chuyền",
#     height = num_row * row_hight
# )
# fig.update_traces(
#     customdata = customdata,
#     textfont=dict(size=14),
#     zmin=0,
#     zmax=1,
#     hovertemplate=(
#         "Hiệu suất: %{z:.1%}<br>"
#         "Style: %{customdata[0]}"
#     ),
#     text=text_data.values, 
#     texttemplate="%{text}"
# )
# st.plotly_chart(fig,use_container_width=True,key='heatmap3')

## Heatmap style theo chuyền , ngày

fig = px.density_heatmap(
    df_line_style,
    color_continuous_scale= "Blues",
    text_auto=True)
fig.update_layout(
    title = 'Phân bổ đơn hàng theo chuyền',
    xaxis_title = 'Chuyền',
    yaxis_title = 'Style',
    coloraxis_colorbar_title='Số ngày'
)
fig.update_xaxes(
    tickfont = dict(size = 14)
)
fig.update_yaxes(
    tickfont = dict(size = 14)
)
fig.update_traces(
    textfont = dict(size = 14)
)
st.plotly_chart(fig,use_container_width=True)
# st.dataframe(df_line_style)
with st.expander("Dữ liệu chi tiết"):
    st.dataframe(df4,hide_index=True)

# while True:
#     time.sleep(30)
#     st.rerun()









