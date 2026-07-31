import streamlit as st
import plotly.express as px
import pandas as pd

st.title("🗺️ الخريطة الحرارية للسوق | Heatmap")

# Sample Data
data = pd.DataFrame({
    'Stock': ['أرامكو', "الراجحي", "الأهلي", "سابك", "STC", "معادن", "كهرباء السعودية"],
    'Sector': ['الطاقة', 'البنوك', 'البنوك', 'المواد الأساسية', 'الاتصالات', 'المواد الأساسية', 'المرافق'],
    'MarketCap': [2000, 300, 200, 150, 120, 110, 80],
    'Change': [1.5, 2.3, -1.1, 0.4, -0.5, 3.2, -0.2]
})

fig = px.treemap(
    data,
    path=['Sector', 'Stock'],
    values='MarketCap',
    color='Change',
    color_continuous_scale='RdYlGn',
    color_continuous_midpoint=0
)
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)
