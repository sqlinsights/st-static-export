import streamlit as st
import st_static_export as sse
from vega_datasets import local_data
import altair as alt



css_text = """
table, th, td {
  border: 1px solid black;
  border-collapse: collapse;
}
tr:nth-child(even) {background-color: #f2f2f2;}
.table{
    width:100%;
}
.footn{
color:#c0c0c0;
}
"""

html = sse.StreamlitStaticExport(css=css_text)

html.add_header(id="title",text="Seattle Weather", size="H1" )
html.add_header(id="subtitle",text="Dataset from Vegas", size="H3" )
st.title("Seattle Weather")
html.add_text(id="explanation", text="""This is a brief explanation of \n how Seattle weather behaves""", text_class='footn')
df = local_data.seattle_weather()


st.dataframe(df)
html.export_dataframe(id="df", dataframe=df.head(5),inside_expandable=True, table_class='table')

base = alt.Chart(df).mark_bar().encode(
    x=alt.X('date', type='temporal'),
    y=alt.Y('precipitation', type='quantitative'),
    color = alt.Color('weather', type ='nominal')
)


st.altair_chart(base, use_container_width=True)

html.export_altair_graph(id="chart",html_content=base.properties(width=900))

dumps = html.create_html(return_type="String")
with open('sample.html', 'w') as b: 
    b.write(dumps)

dumpb = html.create_html(return_type="Bytes")
with open('sample_bytes.html', 'wb') as b: 
    b.write(dumpb)




