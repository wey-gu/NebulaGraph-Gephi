import math
import sys
from typing import List, Dict

import networkx as nx
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from nebula3.Config import Config
from nebula3.data.DataObject import Node, PathWrapper, Relationship, GeographyWrapper
from nebula3.data.ResultSet import ResultSet
from nebula3.gclient.net import ConnectionPool
from pyvis.network import Network
from streamlit import session_state as _state
from streamlit_ace import st_ace

sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")

_PERSIST_STATE_KEY = f"{__name__}_PERSIST"


INIT_QUERY = """\
MATCH p=()-[]->() RETURN p LIMIT 30;

GET SUBGRAPH WITH PROP 2 STEPS FROM "player100"
    YIELD VERTICES AS nodes,
          EDGES AS relationships;

FIND SHORTEST PATH FROM "player102" TO "team204" OVER *
    YIELD path AS shortest_path;
"""


# for session_state
def persist(key: str) -> str:
    """Mark widget state as persistent."""
    if _PERSIST_STATE_KEY not in _state:
        _state[_PERSIST_STATE_KEY] = set()

    _state[_PERSIST_STATE_KEY].add(key)

    return key


def load_widget_state() -> None:
    """Load persistent widget state."""
    if _PERSIST_STATE_KEY in _state:
        _state.update(
            {
                key: value
                for key, value in _state.items()
                if key in _state[_PERSIST_STATE_KEY]
            }
        )


# end for session_state

# for nebulagraph
from nebula3.data.DataObject import Node, PathWrapper, Relationship, GeographyWrapper
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from nebula3.data.ResultSet import ResultSet


def result_to_df(result) -> Dict[str, list]:
    if result is None:
        return None

    columns = result.keys()
    d: Dict[str, list] = {}
    for col_num in range(result.col_size()):
        col_name = columns[col_num]
        col_list = result.column_values(col_name)
        d[col_name] = [x.cast() for x in col_list]
    return pd.DataFrame(d)


# COLORS = ["#E2DBBE", "#D5D6AA", "#9DBBAE", "#769FB6", "#188FA7"]
# solarized dark
COLORS = [
    "#93A1A1",
    "#B58900",
    "#CB4B16",
    "#DC322F",
    "#D33682",
    "#6C71C4",
    "#268BD2",
    "#2AA198",
    "#859900",
]


def truncate(string: str, length: int = 10) -> str:
    if len(string) > length:
        return string[:length] + ".."
    else:
        return string


def get_color(input_str: str) -> str:
    hash_val = 0
    for char in input_str:
        hash_val = (hash_val * 31 + ord(char)) & 0xFFFFFFFF
    return COLORS[hash_val % len(COLORS)]


def render_pd_item(g, g_nx, item):
    # g is pyvis graph
    # g_nx is networkx graph

    if isinstance(item, Node):
        node_id = str(item.get_id().cast())
        tags = item.tags()  # list of strings
        props_raw = dict()
        for tag in tags:
            props_raw.update(item.properties(tag))
        props = {
            k: str(v.cast()) if hasattr(v, "cast") else str(v)
            for k, v in props_raw.items()
        }

        if "name" in props:
            label = props["name"]
        else:
            label = f"tag: {tags}, id: {node_id}"
            for k in props:
                if "name" in str(k).lower():
                    label = props[k]
                    break
        if "id" not in props:
            props["id"] = node_id

        g.add_node(node_id, label=label, title=str(props), color=get_color(node_id))

        # networkx
        if len(tags) > 1:
            g_nx.add_node(node_id, type=tags[0], **props)
        else:
            g_nx.add_node(node_id, **props)
    elif isinstance(item, Relationship):
        src_id = str(item.start_vertex_id().cast())
        dst_id = str(item.end_vertex_id().cast())
        edge_name = item.edge_name()
        props_raw = item.properties()
        props = {
            k: str(v.cast()) if hasattr(v, "cast") else str(v)
            for k, v in props_raw.items()
        }
        # ensure start and end vertex exist in graph
        if not src_id in g.node_ids:
            g.add_node(
                src_id,
                label=str(src_id),
                title=str(src_id),
                color=get_color(src_id),
            )
        if not dst_id in g.node_ids:
            g.add_node(
                dst_id,
                label=str(dst_id),
                title=str(dst_id),
                color=get_color(dst_id),
            )
        props_str_list: List[str] = []
        for k in props:
            if len(props_str_list) >= 1:
                break
            props_str_list.append(f"{truncate(k, 7)}: {truncate(str(props[k]), 8)}")
        props_str = "\n".join(props_str_list)

        label = f"{props_str}\n{edge_name}" if props else edge_name
        g.add_edge(src_id, dst_id, label=label, title=str(props))
        # networkx
        props["edge_type"] = edge_name
        g_nx.add_edge(src_id, dst_id, **props)
    elif isinstance(item, PathWrapper):
        for node in item.nodes():
            render_pd_item(g, g_nx, node)
        for edge in item.relationships():
            render_pd_item(g, g_nx, edge)
    elif isinstance(item, list):
        for it in item:
            render_pd_item(g, g_nx, it)


def create_graph(result_df, g: Network = None, g_nx: nx.MultiDiGraph = None):
    if g is None:
        g = Network(
            notebook=True,
            directed=True,
            cdn_resources="in_line",
            height="600px",
            width="100%",
            bgcolor="#002B36",
            font_color="#93A1A1",
            neighborhood_highlight=True,
            # select_menu=True,
            filter_menu=True,
        )
    if g_nx is None:
        g_nx = nx.MultiDiGraph()
    for _, row in result_df.iterrows():
        for item in row:
            render_pd_item(g, g_nx, item)
    # configure pyvis Network node size based on node degree
    for node_id in g.get_nodes():
        if node_id in g_nx.nodes:
            node_degree = g_nx.degree(node_id)

            g.get_node(node_id)["size"] = math.log(node_degree + 2) * 10

    g.repulsion(
        node_distance=90,
        central_gravity=0.2,
        spring_length=200,
        spring_strength=0.05,
        damping=0.09,
    )

    # g.hrepulsion(
    #     node_distance=100,
    #     central_gravity=0.2,
    #     spring_length=200,
    #     spring_strength=0.05,
    #     damping=0.09,
    # )
    # g.force_atlas_2based(
    # )
    return g, g_nx


def query_nebulagraph(
    query: str,
    space_name: str,
    address: str,
    port: int,
    user: str = "root",
    password: str = "nebula",
) -> List[ResultSet]:
    # define a config
    config: Config = Config()
    config.max_connection_pool_size: int = 10
    # init connection pool
    connection_pool: ConnectionPool = ConnectionPool()
    results: List[ResultSet] = []
    queries: str = query.strip().split(";")
    queries = [q.strip() for q in queries if q]
    st.session_state.queries = queries

    try:
        connection_pool.init([(address, port)], config)
        for query in queries:
            with connection_pool.session_context(
                user,
                password,
            ) as session:
                if space_name:
                    session.execute("USE {}".format(space_name))
                result: ResultSet = session.execute(query)
            results.append(result)
        connection_pool.close()
    except Exception as e:
        st.warning(e)
        return None
    return results


# end for nebulagraph


# get gephi graph from networkx graph
def get_gephi_graph(g) -> None:
    nx.write_gexf(g, "nebulagraph_export.gexf")


# streamlit app

st.set_page_config(
    page_title="NebulaGraph Gephi Exchange",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

load_widget_state()

with st.sidebar:
    st.markdown(
        """
<div style="display:flex; align-items:center;">
        <a href="https://github.com/wey-gu/NebulaGraph-Gephi">
        <img src="https://raw.githubusercontent.com/nebula-contrib/nebulagraph-docker-ext/main/nebulagraph.svg"
            style="margin-right:10px; height:50px; width:auto;">
        </a>
        <h4>NebulaGraph Gephi</h4>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    graphd_host = st.sidebar.text_input(
        "graphd host", value="graphd", key="graphd_host", label_visibility="collapsed"
    )
    graphd_port = st.sidebar.number_input(
        "graphd port", value=9669, key="graphd_port", label_visibility="collapsed"
    )
    user = st.sidebar.text_input(
        "user", value="root", key="user", label_visibility="collapsed"
    )
    password = st.sidebar.text_input(
        "passwore",
        value="nebula",
        type="password",
        key="password",
        label_visibility="collapsed",
    )
    if "space_name_list" not in st.session_state:
        space_name_list = persist("space_name_list")
        st.session_state.space_name_list = []
    if "rendered_graph" not in st.session_state:
        rendered_graph = persist("rendered_graph")
        st.session_state.rendered_graph = None
    if "g" not in st.session_state:
        g = persist("g")
        st.session_state.g = None
    if "results" not in st.session_state:
        results = persist("results")
        st.session_state.results = None
    if "result_dfs" not in st.session_state:
        result_dfs = persist("result_dfs")
        st.session_state.result_df = None
    if "excuted_clicked" not in st.session_state:
        excuted_clicked = persist("excuted_clicked")
        st.session_state.excuted_clicked = False
    if "raw_pyvis_html" not in st.session_state:
        raw_pyvis_html = persist("raw_pyvis_html")
        st.session_state.raw_pyvis_html = ""
    if "queries" not in st.session_state:
        queries = persist("queries")
        st.session_state.queries = []

    st.sidebar.markdown("---")

    if st.sidebar.button("🔗　Connect", type="secondary"):
        results = query_nebulagraph(
            "SHOW SPACES;", None, graphd_host, graphd_port, user, password
        )
        if results is None or len(results) == 0:
            st.warning("connect failed")
            st.stop()
        result: ResultSet = results[0]
        spaces_df = result_to_df(result)
        st.session_state.space_name_list = spaces_df["Name"].tolist()
        # st.sidebar.dataframe(st.session_state.space_name_list)
        persist("space_name")
        # clear all results
        st.session_state.results = None
        st.session_state.result_dfs = None
        st.session_state.g = None
        st.session_state.excuted_clicked = False

# main page

# two tabs
(
    tab_query,
    tab_gephi,
) = st.tabs(
    [
        "Query NebulaGraph",
        "Gephi",
    ]
)

with tab_query:
    if len(st.session_state.space_name_list) == 0:
        # floating window before login
        st.markdown(
            """
            <style>
                .floating-window {
                    position: absolute;
                    z-index: 1;
                    left: -20px;
                    top: -10px;
                    right: -20px;
                    bottom: 0.1px;
                    background-color: rgba(25, 49, 75, 0.30);
                    padding: 10px;
                    border: 1px solid #48494D;
                    border-radius: 10px;
                    min-height: 720px;
                    backdrop-filter: blur(5px);
                }
                .text-container {
                    position: absolute;
                    z-index: 1;
                    left: 300px;
                    top: 300px;
                    right: 300px;
                    bottom: 300px;
                    background-color: #0E1118;
                    padding: 10px;
                    border: 0px solid #48494D;
                    border-radius: 10px;
                    min-height: 20px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
                }
            </style>
            <div class="floating-window">
                <div class="text-container">
                    <p style=
                    "position: absolute;
                    top: 50%; left: 50%;
                    transform: translate(-50%, -50%);
                    color: #FAFAFA;
                    ">
                        🔗　 Connect to <span> </span>
                        <img src="https://raw.githubusercontent.com/nebula-contrib/nebulagraph-docker-ext/main/nebulagraph.svg" alt=" " style="height: 16px; width: auto;">
                        <span style="color: #009EFF;"><strong>Nebula</strong></span>Graph first.                        
                    </p>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.info(
        "Query NebulaGraph then Download and put the `GEXF` file to"
        " [Gephi](https://gephi.org/gephi-lite/) "
        "for more analysis and visualization. ",
        icon="🧙‍♂️",
    )

    with st.expander("▷ Console", expanded=True):
        # to column, query field and query button
        input_field, buttons = st.columns([8, 1.3])
        with input_field:
            query = st_ace(
                value=INIT_QUERY,
                height=170,
                annotations="""# Query SUBGRAPH, PATH, \
NODES AND EDGES to enable visualization.
            MATCH p=(v)-[]->()
            WHERE id(v) == "player100"
            RETURN p LIMIT 50;
            # or
            GET SUBGRAPH WITH PROP 2 STEPS FROM "player100"
            YIELD VERTICES AS NODES, EDGES AS RELATIONSHIPS;
            # or
            FIND PATH FROM "player102" TO "team204" OVER * YIELD path AS p;
            """,
                language="pgsql",
                theme="solarized_dark",
                auto_update=True,
            )

        with buttons:
            space_name = st.selectbox(
                "Graph Space",
                st.session_state.space_name_list,
                key="space_name",
            )

            if st.button(
                "Execute",
                use_container_width=True,
                type="secondary",
                disabled=not bool(st.session_state.space_name),
            ):
                results = query_nebulagraph(
                    query,
                    st.session_state.space_name,
                    st.session_state.graphd_host,
                    st.session_state.graphd_port,
                    st.session_state.user,
                    st.session_state.password,
                )

                if results is None or len(results) == 0:
                    st.warning("query failed")
                    st.stop()
                st.session_state.results = results

                result_dfs = []
                st.session_state.g = None
                g, g_nx = None, None

                for result in results:
                    if result is not None and result.error_code() == 0:
                        result_df = result_to_df(result)
                        result_dfs.append(result_df)
                        # create pyvis graph
                        g, g_nx = create_graph(result_df, g, g_nx)

                st.session_state.g = g
                get_gephi_graph(g_nx)
                with open("nebulagraph_export.gexf", "rb") as f:
                    st.download_button(
                        label="GEXF File",
                        use_container_width=True,
                        data=f.read(),
                        type="primary",
                        file_name="nebulagraph_export.gexf",
                        mime="application/xml",
                    )
                st.session_state.result_dfs = result_dfs
                st.session_state.excuted_clicked = True

        if st.session_state.results is not None:
            for result in st.session_state.results:
                if result.error_code() != 0:
                    st.markdown("---")
                    st.warning(result.error_msg())
                    st.stop()

        if st.session_state.excuted_clicked:
            st.warning(
                "Hint: Ensure to download files from a browser. "
                "If you're using the `Docker Extension` embed window, "
                "just click [http://127.0.0.1:17005](http://127.0.0.1:17005)"
                " and visit from browser instead 😄.",
                icon="💡",
            )

    if st.session_state.g is not None:
        g = st.session_state.g
        g_is_renderable = g.get_nodes() and g.get_edges()

        if g_is_renderable:
            # render with random file name
            graph_html = g.generate_html()
            graph_html.replace(
                "height: 600px", "height: 720px"
            )
            components.html(graph_html, height=720, scrolling=False)

        for index in range(len(st.session_state.result_dfs)):
            # check all value to see whether there is any nested raw data, in case yes
            # then we'll cast all values to string
            raw_data = False
            result_df = st.session_state.result_dfs[index]
            df_is_empty = result_df.empty
            for _, row in result_df.iterrows():
                for item in row:
                    if type(item) in [
                        PathWrapper,
                        GeographyWrapper,
                        Node,
                        Relationship,
                        list,
                    ]:
                        raw_data = True
                        break

            if not raw_data:
                csv_df = result_df

            else:
                # format result_df to string values
                csv_df = result_df.applymap(lambda x: str(x))

            # download buttons
            # two col in one row
            col0, col1, col2 = st.columns(
                [2, 8, 2],
                gap="small",
            )
            with col1:
                pass
            with col0:
                if g_is_renderable:
                    g.filter_menu = False
                    st.session_state.raw_pyvis_html = g.generate_html().replace(
                        "height: 600px", "height: 1080px"
                    )
                    if st.session_state.raw_pyvis_html != "" and index == 0:
                        st.download_button(
                            label="⬇　 HTML File",
                            data=st.session_state.raw_pyvis_html,
                            type="secondary",
                            file_name="nebulagraph_export.html",
                            mime="text/html",
                            use_container_width=True,
                        )
            with col2:
                if not df_is_empty:
                    # button to download csv
                    st.download_button(
                        label=f"⬇　.CSV File {index + 1}",
                        data=csv_df.to_csv(index=False),
                        type="secondary",
                        file_name="nebulagraph_export.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
            # download buttons end

            # df table
            st.markdown("---")
            if len(st.session_state.queries) >= index + 1:
                st.markdown(
                    f"""
```cypher
-- Query {index + 1}
{st.session_state.queries[index]}
```
    """
                )
            try:
                st.dataframe(
                    csv_df,
                    use_container_width=True,
                    hide_index=True,
                )
            except Exception as e:
                st.warning(e)
            # df table end


with tab_gephi:
    # iframe of https://gephi.org/gephi-lite/
    # when click this tab, hide the sidebar

    components.iframe(
        src="https://gephi.org/gephi-lite/",
        height=800,
        scrolling=True,
    )
