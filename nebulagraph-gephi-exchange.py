import sys


import streamlit as st
import streamlit.components.v1 as components

sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")


from streamlit import session_state as _state

_PERSIST_STATE_KEY = f"{__name__}_PERSIST"


# for session_state
def persist(key: str) -> str:
    """Mark widget state as persistent."""
    if _PERSIST_STATE_KEY not in _state:
        _state[_PERSIST_STATE_KEY] = set()

    _state[_PERSIST_STATE_KEY].add(key)

    return key


def load_widget_state():
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


def result_to_df(result):
    if result is None:
        return None
    from typing import Dict

    import pandas as pd

    columns = result.keys()
    d: Dict[str, list] = {}
    for col_num in range(result.col_size()):
        col_name = columns[col_num]
        col_list = result.column_values(col_name)
        d[col_name] = [x.cast() for x in col_list]
    return pd.DataFrame(d)


COLORS = ["#E2DBBE", "#D5D6AA", "#9DBBAE", "#769FB6", "#188FA7"]


def get_color(input_str):
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
            k: str(v.cast()) if isinstance(v.cast(), GeographyWrapper) else v.cast()
            for k, v in props_raw.items()
        }
        # print types of all props
        for k, v in props.items():
            print(f"{k}: {type(v)}")
        print(f"props: {props}")

        g.add_node(node_id, label=node_id, title=str(props), color=get_color(node_id))

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
            k: str(v.cast()) if isinstance(v.cast(), GeographyWrapper) else v.cast()
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
        label = f"{props}\n{edge_name}" if props else edge_name
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


def create_graph(result_df):
    from pyvis.network import Network

    g = Network(
        notebook=True,
        directed=True,
        cdn_resources="in_line",
        height="500px",
        width="100%",
    )
    g_nx = nx.MultiDiGraph()
    for _, row in result_df.iterrows():
        for item in row:
            render_pd_item(g, g_nx, item)
    g.repulsion(
        node_distance=100,
        central_gravity=0.2,
        spring_length=200,
        spring_strength=0.05,
        damping=0.09,
    )
    return g, g_nx


def query_nebulagraph(
    query,
    space_name,
    address,
    port,
    user="root",
    password="nebula",
):
    # from nebula3.Config import SessionPoolConfig
    # from nebula3.gclient.net.SessionPool import SessionPool

    from nebula3.gclient.net import ConnectionPool
    from nebula3.Config import Config

    # define a config
    config = Config()
    config.max_connection_pool_size = 10
    # init connection pool
    connection_pool = ConnectionPool()
    try:
        connection_pool.init([(address, port)], config)
        with connection_pool.session_context(
            user,
            password,
        ) as session:
            if space_name:
                session.execute("USE {}".format(space_name))
            result = session.execute(query)
            print(result)
        connection_pool.close()
    except Exception as e:
        st.warning(e)
        return None
    return result


# end for nebulagraph

# nebulagraph to networkx to gephi
# from ng_nx import NebulaReader
# from ng_nx.utils import NebulaGraphConfig
import networkx as nx


def get_gephi_graph(g):
    nx.write_gexf(g, "nebulagraph_export.gexf")


# def get_networkx_graph(
#     graphd_host,
#     user,
#     password,
#     space,
#     edges,
#     properties,
#     limit=1000,
# ):
#     nebula_config = NebulaGraphConfig(
#         graphd_hosts=[graphd_host],
#         user=user,
#         password=password,
#         space=space,
#     )
#     nebula_reader = NebulaReader(
#         space=space,
#         edges=edges,
#         properties=properties,
#         nebula_config=nebula_config,
#         limit=limit,
#     )
#     return nebula_reader.read()


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
        f'<div style="display:flex; align-items:center;"><img src="https://raw.githubusercontent.com/nebula-contrib/nebulagraph-docker-ext/main/nebulagraph.svg" style="margin-right:10px; height:50px; width:auto;">'
        f"<h4>NebulaGraph Gephi</h4></div>",
        unsafe_allow_html=True,
    )
    # st.sidebar.markdown("---")

    graphd_host = st.sidebar.text_input("", value="graphd", key="graphd_host")
    graphd_port = st.sidebar.number_input("", value=9669, key="graphd_port")
    user = st.sidebar.text_input("", value="root", key="user")
    password = st.sidebar.text_input(
        "", value="nebula", type="password", key="password"
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
    if "g_nx" not in st.session_state:
        g_nx = persist("g_nx")
        st.session_state.g_nx = None

    st.sidebar.markdown("---")

    if st.sidebar.button("🔓　Connect", type="secondary"):
        result = query_nebulagraph(
            "SHOW SPACES;", None, graphd_host, graphd_port, user, password
        )
        if result is None:
            st.warning("connect failed")
            st.stop()
        spaces_df = result_to_df(result)
        st.session_state.space_name_list = spaces_df["Name"].tolist()
        # st.sidebar.dataframe(st.session_state.space_name_list)
        persist("space_name")

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
    st.info(
        "🧙‍♂️　Query NebulaGraph then Download and put the `GEXF` file to [Gephi](https://gephi.org/gephi-lite/) "
        "for more analysis and visualization."
    )

    with st.expander("", expanded=True):
        # to column, query field and query button
        input_field, buttons = st.columns([8, 1])
        with input_field:

            query = st.text_area(
                "Enter your query",
                height=190,
                value="MATCH p=()-[]->() \nRETURN p LIMIT 50;",
                key="query",
                label_visibility="collapsed",
                help="Query SUBGRAPH, PATH, NODES AND EDGES to enable visualization.",
                placeholder="""# Query SUBGRAPH, PATH, NODES AND EDGES to enable visualization.
            MATCH p=(v)-[]->()
            WHERE id(v) == "player100"
            RETURN p LIMIT 50;
            # or
            GET SUBGRAPH WITH PROP 2 STEPS FROM "player100"
            YIELD VERTICES AS NODES, EDGES AS RELATIONSHIPS;
            # or
            FIND PATH FROM "player102" TO "team204" OVER * YIELD path AS p;
            """,
            )
        with buttons:
            space_name = st.selectbox(
                "",
                st.session_state.space_name_list,
                key="space_name",
            )

            if st.button(
                "　Execute", type="secondary", disabled=not bool(st.session_state.space_name)
            ):
                
                result = query_nebulagraph(
                    query,
                    st.session_state.space_name,
                    st.session_state.graphd_host,
                    st.session_state.graphd_port,
                    st.session_state.user,
                    st.session_state.password,
                )

                if result is None:
                    st.warning("query failed")
                    st.stop()

                result_df = result_to_df(result)

                # create pyvis graph
                g, g_nx = create_graph(result_df)
                st.session_state.g = g
                get_gephi_graph(g_nx)
                with open("nebulagraph_export.gexf", "rb") as f:
                    st.download_button(
                        label="⬇️　.GEXF",
                        data=f.read(),
                        file_name="nebulagraph_export.gexf",
                        mime="application/xml",
                    )

    if st.session_state.g is not None:
        g = st.session_state.g
        # render with random file name
        graph_html = g.generate_html()

        components.html(graph_html, height=500, scrolling=True)

        # check all value to see whether there is a path or a GeographyWrapper
        path_or_geo = False
        for _, row in result_df.iterrows():
            for item in row:
                if isinstance(item, PathWrapper) or isinstance(item, GeographyWrapper):
                    path_or_geo = True
                    break

        if not path_or_geo:
            try:
                st.dataframe(result_df)
            except Exception as e:
                st.warning(e)
        else:
            # format result_df to string values
            result_df_str = result_df.applymap(lambda x: str(x))
            st.dataframe(
                result_df_str,
                width=1920,
            )
    # TODO:
    # - [ ] add a button to download the graph as html file
    # - [ ] add a button to download the result as csv file

with tab_gephi:
    # iframe of https://gephi.org/gephi-lite/
    # when click this tab, hide the sidebar

    components.iframe(
        src="https://gephi.org/gephi-lite/",
        height=1280,
        scrolling=True,
    )
