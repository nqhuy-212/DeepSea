import streamlit as st 
from load_data import get_data

st.set_page_config(layout= 'wide',page_title="DeepSea",page_icon="logo_blue.png",)
st.logo("logo_white.png",size= 'large')
st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        margin-top: 200 px;
        color: 'rgb(255,255,255)';
        font-size : 68px;
    }
    div.block-container{padding-top:1.5rem};
    </style>
    """,
    unsafe_allow_html=True
)

#---PAGE SETUP---

rank_page = st.Page(
    page="views/rank.py",
    title= "Bảng xếp hạng",
    icon= ':material/emoji_events:',
)

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

hourly_page = st.Page(
    page="views/hourly.py",
    title= "Báo cáo dập thẻ hàng giờ",
    icon= ':material/timer:'
)

QCO_page = st.Page(
    page="views/QCO.py",
    title= "Báo cáo QCO",
    icon= ':material/fast_forward:'
)

map_page = st.Page(
    page="views/map.py",
    title= "Bản đồ - CCTV",
    icon= ':material/public:'
)

chat_page = st.Page(
    page="views/chatbot.py",
    title= "Chatbot nội bộ",
    icon= ':material/chat:'
)

ppc_page = st.Page(
    page="views/PPC.py",
    title= "Báo cáo PPC",
    icon= ':material/target:'
)

OQL_page = st.Page(
    page="views/OQL.py",
    title= "Tỉ lệ lỗi",
    icon= ':material/sentiment_dissatisfied:'
)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown(f'<h1 class="centered-title"> &nbsp D e e p  S e a</h1>', unsafe_allow_html=True)
    cols = st.columns(3)
    with cols[1]:
        
        cols = st.columns(3)
        with cols[1]:
            st.image("logo_white.png",use_container_width=True)
        with st.form("Đăng nhập"):
            factory = st.selectbox("Chọn nhà máy",options=['NT1','NT2'])
            username = st.text_input("Tài khoản", placeholder="Nhập vào mã chấm công")
            password = st.text_input("Mật khẩu", placeholder="Nhập vào mật khẩu", type='password')
            
            # Form submission button
            submit_button = st.form_submit_button("Đăng nhập",use_container_width=True)

            # Perform actions after form submission
            if submit_button:
                df_login = get_data("HR",f"SELECT * FROM Nhanvien WHERE macongty = '{factory}' AND masothe = '{username}' AND matkhau = '{password}' AND deepsea = 'x'")
                if df_login.shape[0] > 0:
                    st.session_state.logged_in = True
                    st.session_state.factory = factory
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("Tên tài khoản hoặc mật khẩu không đúng. Vui lòng thử lại.")
else:
    # if st.sidebar.button("Làm mới dữ liệu"):
    #     st.rerun()
    pg = st.navigation(pages={
    'Chọn trang' :[sumary_page,hr_page,incentive_page,hourly_page,ppc_page,OQL_page,salary_page,QCO_page,map_page,rank_page]})   
    pg.run()




