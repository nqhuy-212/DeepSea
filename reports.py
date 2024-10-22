import streamlit as st 

st.set_page_config(layout= 'wide')
st.logo("logo_white.png",size= 'large')

#---PAGE SETUP---
sumary_page = st.Page(
    page="views/summary.py",
    title= "Báo cáo tổng hợp",
    icon= ':material/bar_chart:',
    default= True
)

incentive_page = st.Page(
    page="views/incentive.py",
    title= "Báo cáo thưởng năng suất",
    icon= ':material/attach_money:'
)

hr_page = st.Page(
    page="views/hr.py",
    title= "Báo cáo nhân sự",
    icon= ':material/group:'
)

tnc_page = st.Page(
    page="views/tnc.py",
    title= "Báo cáo công nhân TNC",
    icon= ':material/child_friendly:'
)

salary_page = st.Page(
    page="views/salary.py",
    title= "Báo cáo lương",
    icon= ':material/credit_card:'
)

pg = st.navigation(pages={
    'Chọn trang' :[sumary_page,incentive_page,hr_page,tnc_page,salary_page]})
pg.run()


