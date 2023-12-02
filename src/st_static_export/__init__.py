from bs4 import BeautifulSoup
from typing import  Literal
import pandas as pd
import re
import altair as alt
from textwrap import dedent

class StreamlitStaticExportException(Exception):
    def __init__(self, m):
        self.message = m
    def __str__(self):
        return self.message


class StreamlitStaticExport:
    header_size = Literal["H1", "H2", "H3", "H4"]
    return_type = Literal["String", "Bytes"]
    """Initializes a HTML object. CSS can be assigned as part of initialization."""
    def __init__(self, css:str = str())->None:
        self.css = css
        self.report_body = {}
        
       
    def add_header(self, id:str, text :str, size:header_size , header_class:str = None) -> None:
        class_def = f'class="{header_class}"' if header_class else str()
        header_html = f'''<{size} {class_def}>{text}</{size}>'''
        self.report_body[id] = header_html

    def export_dataframe(self, id:str, dataframe:pd.DataFrame, table_class:str = None, inside_expandable:bool = False) -> None:
        if inside_expandable:
            self.css += dedent("""
                         details {
                        user-select: all;
                               
                        }

                        details>summary span.icon {
                        width: 24px;
                        height: 24px;
                        transition: all 0.3s;
                        margin-left: auto;
                        }

                        details[open] summary span.icon {
                        transform: rotate(180deg);
                        transform-origin:center center;
                        }

                        summary {
                        display: flex;
                        background-color:#D3D3D3;
                        padding:1rem;
                        border-radius:.5rem;
                        cursor: pointer;
                        margin-bottom:1rem;
                       
                        }

                        summary::-webkit-details-marker {
                        display: none;
                        
                        }
                                        """)
            collapsible_button = '<button class="collapsible">Expand</button>'
            
            html_table = re.sub("class=\"dataframe\"", f"class = \"{table_class}\"", dataframe.to_html()) if table_class else dataframe.to_html()
            html_table = html_table.replace("\\n","<br/>")
            collapsible_div = f'<details><summary><span class="icon">⬇️</span></summary>{html_table}</details>'
            self.report_body[id] = collapsible_div
        else:
            html_table = re.sub("class=\"dataframe\"", f"class = \"{table_class}\"", dataframe.to_html()) if table_class else dataframe.to_html()
            html_table = html_table.replace("\\n","<br/>")
            self.report_body[id] = html_table

    def add_text(self, id:str, text :str, text_class:str = None) -> None:
        class_def = f'class="{text_class}"' if text_class else str()
        text = text.replace("\n","<br/>")
        text_html = f'''<p {class_def}>{text}</p>'''
        self.report_body[id] = text_html

    def export_altair_graph(self, id:str, graph:alt.Chart, graph_class:str = None) -> None:
        if graph.data.shape[0] >5000:
            raise StreamlitStaticExportException("Altair graph data cannot be longer than 5000 rows.")
        else:
            soup = BeautifulSoup(graph.to_html(output_div=id, fullhtml=True),"html.parser")
            body = soup.find("body")
            graphs = body.find("script")
            graphs = str(graphs).replace('{"mode": "vega-lite"}','{ "actions": false }') 
            class_def = f'class="{graph_class}"' if graph_class else str()
            visual_html = f'<div{class_def}><div id="{id}"></div>{graphs}</div>'
            self.report_body[id] = visual_html

    def create_html(self,return_type:return_type = "String") -> [str,bytes]:
        if return_type not in ["String", "Bytes"]:
            raise("Invalid return_type for function create_html()")
        else:
            output=str()
            header = f"""
            <head>
            <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega@5"></script>
                <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-lite@5.16.3"></script>
                <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
                <style>{dedent(self.css)}</style>
            </head>
            """
            output += header
            for k,v in self.report_body.items():
                output += f'{v}\n\n'
            
            if return_type == "String":
                return output 
            if return_type == "Bytes":
                return bytes(output, encoding='utf-8')
            


              
            