import streamlit as st 
from load_data import get_data
from collections import defaultdict
import re

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

fty = ['NT1','NT2']
nha_may = st.sidebar.selectbox("Chọn nhà máy",options= fty, index= fty.index(st.session_state.factory))

queries = {
    "kho": f"""SELECT Section_code, line, count(*) as so_luong
              FROM Danh_sach_CBCNV
              WHERE Trang_thai_lam_viec = N'Đang làm việc'
                AND Factory = '{nha_may}'
                AND Department LIKE '%WHS%'
                AND Line NOT LIKE '%FAB%'
              GROUP BY Trang_thai_lam_viec, Department, Factory, Line, Section_code""",

    "xa_vai": f"""SELECT Section_code, line, count(*) as so_luong
                 FROM Danh_sach_CBCNV
                 WHERE Trang_thai_lam_viec = N'Đang làm việc'
                   AND Factory = '{nha_may}'
                   AND Department LIKE '%WHS%'
                   AND Line LIKE '%FAB%'
                 GROUP BY Trang_thai_lam_viec, Department, Factory, Line, Section_code""",

    "trai_vai": f"""SELECT Section_code, line, count(*) as so_luong
                   FROM Danh_sach_CBCNV
                   WHERE Trang_thai_lam_viec = N'Đang làm việc'
                     AND Factory = '{nha_may}'
                     AND Section_description LIKE '%CUT%'
                     AND Job_title_VN LIKE N'%trải vải%'
                     AND Line NOT LIKE '%99'
                     AND Line NOT LIKE '%00'
                   GROUP BY Trang_thai_lam_viec, Department, Factory, Line, Section_code""",

    "cat": f"""SELECT Section_code, line, count(*) as so_luong
              FROM Danh_sach_CBCNV
              WHERE Trang_thai_lam_viec = N'Đang làm việc'
                AND Factory = '{nha_may}'
                AND Section_description LIKE '%CUT%'
                AND Job_title_VN NOT LIKE N'%trải vải%'
                AND Job_title_VN NOT LIKE N'%công nhân phụ cắt%'
                AND Chuc_vu NOT LIKE N'%Nhân viên%'
                AND Line NOT LIKE '%99'
                AND Line NOT LIKE '%00'
              GROUP BY Trang_thai_lam_viec, Department, Factory, Line, Section_code""",

    "cpi": f"""SELECT Section_code, line, count(*) as so_luong
              FROM Danh_sach_CBCNV
              WHERE Trang_thai_lam_viec = N'Đang làm việc'
                AND Factory = '{nha_may}'
                AND Section_description LIKE '%CUT%'
                AND Job_title_VN LIKE N'%công nhân phụ cắt%'
                AND Line NOT LIKE '%99'
                AND Line NOT LIKE '%00'
              GROUP BY Trang_thai_lam_viec, Department, Factory, Line, Section_code""",

    "may": f"""SELECT Section_code, line, count(*) as so_luong
              FROM Danh_sach_CBCNV
              WHERE Trang_thai_lam_viec = N'Đang làm việc'
                AND Factory = '{nha_may}'
                AND Section_description LIKE '%SEW%'
                AND Line NOT LIKE '%99'
                AND Line NOT LIKE '%00'
                AND LINE NOT LIKE '20%'
              GROUP BY Trang_thai_lam_viec, Department, Factory, Line, Section_code""",

    "qc1": f"""SELECT Section_code, line, count(*) as so_luong
              FROM Danh_sach_CBCNV
              WHERE Trang_thai_lam_viec = N'Đang làm việc'
                AND Factory = '{nha_may}'
                AND Section_description LIKE '%QC1%'
                AND Line NOT LIKE '%99'
                AND Line NOT LIKE '%00'
              GROUP BY Trang_thai_lam_viec, Department, Factory, Line, Section_code""",

    "la": f"""SELECT Section_code, line, count(*) as so_luong
             FROM Danh_sach_CBCNV
             WHERE Trang_thai_lam_viec = N'Đang làm việc'
               AND Factory = '{nha_may}'
               AND Section_description LIKE '%FNS%'
               AND Job_title_VN LIKE N'%là%'
               AND Line NOT LIKE '%99'
               AND Line NOT LIKE '%00'
             GROUP BY Trang_thai_lam_viec, Department, Factory, Line, Section_code""",

    "qc2": f"""SELECT Section_code, line, count(*) as so_luong
              FROM Danh_sach_CBCNV
              WHERE Trang_thai_lam_viec = N'Đang làm việc'
                AND Factory = '{nha_may}'
                AND Section_description LIKE '%QC2%'
                AND Line NOT LIKE '%99'
                AND Line NOT LIKE '%00'
              GROUP BY Trang_thai_lam_viec, Department, Factory, Line, Section_code""",

    "dong_goi": f"""SELECT Section_code, line, count(*) as so_luong
                   FROM Danh_sach_CBCNV
                   WHERE Trang_thai_lam_viec = N'Đang làm việc'
                     AND Factory = '{nha_may}'
                     AND Section_description LIKE '%FNS%'
                     AND Job_title_VN LIKE N'%đóng gói%'
                     AND Line NOT LIKE '%99'
                     AND Line NOT LIKE '%00'
                   GROUP BY Trang_thai_lam_viec, Department, Factory, Line, Section_code""",

    "dong_thung": f"""SELECT Section_code, line, count(*) as so_luong
                     FROM Danh_sach_CBCNV
                     WHERE Trang_thai_lam_viec = N'Đang làm việc'
                       AND Factory = '{nha_may}'
                       AND Section_description LIKE '%FNS%'
                       AND Job_title_VN LIKE N'%đóng thùng%'
                       AND Line NOT LIKE '%99'
                       AND Line NOT LIKE '%00'
                     GROUP BY Trang_thai_lam_viec, Department, Factory, Line, Section_code"""
}

data = defaultdict(lambda: defaultdict(list))

for column_name, sql in queries.items():
    rows = get_data(DB='HR', query=sql)

    for _, row in rows.iterrows():
        section = row["Section_code"]
        line = row["line"]
        so_luong = row["so_luong"] or 0

        # Tìm số xưởng sau "P0", ví dụ P01, P02...
        match = re.search(r"P0(\d+)", section)
        if not match:
            section = "Khác"

        # Thêm vào cấu trúc data
        data[section][column_name].append({
            "line": line,
            "so_luong": so_luong
        })
     
# Tạo bảng HTML
columns = ["kho", "xa_vai", "trai_vai", "cat", "cpi", "may", "qc1", "la", "qc2", "dong_goi", "dong_thung"]

html = """
<style>
    table {
        border: 1px solid black;
        border-collapse: collapse;
        width: 100%;
    }
    thead th {
        position: sticky;
        top: 60px;
        z-index: 1;
        background-color: #031b52;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 6px;
        text-align: center !important;
        vertical-align: middle !important;
    }
    .workshop {
        font-weight: bold;
    }
</style>
<table>
    <thead>
        <tr>
            <th>Xưởng</th>
            <th>Chuyền</th>
            <th>Kho</th>
            <th>Xả vải</th>
            <th>Trải vải</th>
            <th>Cắt</th>
            <th>CPI</th>
            <th>May</th>
            <th>QC1</th>
            <th>Là</th>
            <th>QC2</th>
            <th>Đóng gói</th>
            <th>Đóng thùng</th>
        </tr>
    </thead>
<tbody>
"""

for workshop, steps in data.items():
    # gom line -> {line: {step: so_luong}}
    line_data = {}
    for step, items in steps.items():
        for item in items:
            line = item["line"]
            so_luong = item["so_luong"]
            if line not in line_data:
                line_data[line] = {}
            line_data[line][step] = so_luong

    lines = list(line_data.items())
    rowspan = len(lines)

    for i, (line, step_values) in enumerate(lines):
        html += "<tr>"
        if i == 0:
            html += f"<td class='workshop' rowspan='{rowspan}'>{workshop}</td>"
        html += f"<td>{line}</td>"

        for col in columns:
            val = step_values.get(col, "")
            html += f"<td>{val}</td>"
        html += "</tr>\n"

html += "</tbody></table>"
# Hiển thị bảng
st.markdown(html, unsafe_allow_html=True)  