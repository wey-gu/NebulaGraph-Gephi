# **Nebula**Grahp **Gephi** Exchange

[![for NebulaGraph](https://img.shields.io/badge/Toolchain-NebulaGraph-blue)](https://github.com/vesoft-inc/nebula) [![Gephi](https://img.shields.io/badge/Gephi-Supported-brightgreen)](https://github.com/gephi/gephi-lite/) [![Docker Image](https://img.shields.io/docker/v/weygu/nebulagraph-gephi-exchange?label=Image&logo=docker)](https://hub.docker.com/r/weygu/nebulagraph-gephi-exchange) [![Docker Extension](https://img.shields.io/badge/Docker-Extension-blue?logo=docker)](https://hub.docker.com/extensions/weygu/nebulagraph-dd-ext) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/wey-gu/NebulaGraph-Gephi?label=Version)](https://github.com/wey-gu/NebulaGraph-Gephi/releases) [![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg?)](https://nebulagraph-gephi.streamlit.app/) 

[![Docker Image CI](https://github.com/wey-gu/NebulaGraph-Gephi/actions/workflows/docker-image.yml/badge.svg)](https://github.com/wey-gu/NebulaGraph-Gephi/actions/workflows/docker-image.yml)

Gephi is an Awesome Graph Algo and Vis tool! If you would like to visualize your data on NebulaGraph with it, this is the way to go.

https://github.com/siwei-io/talks/assets/1651790/c036a229-c71e-4344-93d4-720657f2ba90

Features:

- Query NebulaGraph
- Render results
- Export result to a [gexf file](https://raw.githubusercontent.com/wey-gu/NebulaGraph-Gephi/main/example/nebulagraph_export.gexf) for Gephi
- Download the [HTML file](https://raw.githubusercontent.com/wey-gu/NebulaGraph-Gephi/main/example/nebulagraph_export.html) for any renderable graph
- Download [CSV results](https://raw.githubusercontent.com/wey-gu/NebulaGraph-Gephi/main/example/nebulagraph_export.csv) for any query(or Multiple Queries)
- Graph Algorithm and Visualization with [Gephi-Lite](https://github.com/gephi/gephi-lite/)

### 💻 How to use

> Render Multiple Queries, and export `GEXF`, `HTML,` or `CSV` files.

<p align="center">
  <a href="https://www.siwei.io/demo-dumps/adhoc-graphs/nebulagraph_export_supply_chain.html">
    <img width="650" alt="graph_supply_chain" src="https://github.com/wey-gu/NebulaGraph-Gephi/assets/1651790/00524169-70ee-469b-9408-92fd58840b37">
  </a>
  <br>
  <small>
    <i>Connect to NebulaGraph, then make queries, multiple queries will be merged in one Graph, we could download single </i>
    <a href="https://raw.githubusercontent.com/wey-gu/NebulaGraph-Gephi/main/example/nebulagraph_export.html">
      .html
    </a>
    <i>files to embed in your blog, or webpage. Rendered like </i>
    <a href="https://www.siwei.io/demo-dumps/adhoc-graphs/nebulagraph_export_supply_chain.html">
      this
    </a>.
  </small>
</p>

> Embed the rendered graph in your blog:

```html
<iframe
   src="https://www.siwei.io/demo-dumps/adhoc-graphs/nebulagraph_export_supply_chain.html"
   width="100%"
   height="500px"
></iframe>
```

> Load into Gephi-Lite!

<p align="center">
  <a href="https://www.siwei.io/demo-dumps/adhoc-graphs/nebulagraph_export_supply_chain.html">
    <img width="650" alt="graph_supply_chain" src="https://github.com/wey-gu/NebulaGraph-Gephi/assets/1651790/63894390-824c-4b98-bb1d-769c88ef23a9">
  </a>
  <br>
  <small>
    <i>Gephi-Lite Graph, imported from </i>
    <a href="https://raw.githubusercontent.com/wey-gu/NebulaGraph-Gephi/main/example/nebulagraph_export.gexf">
      .gexf file
    </a>
     <i> exported from the query.</i>
  </small>
</p>


## 🚀 How to Install

> Installation

```bash
git clone https://github.com/wey-gu/NebulaGraph-Gephi.git && cd NebulaGraph-Gephi
python3 -m pip install -r requirements.txt
```

> Run

```bash
streamlit run nebulagraph-gephi-exchange.py
```

> Optionally, with the docker

```
docker-compose up -d
```

> Or, if you are using the NebulaGraph Docker extension, it's already been included since 0.4.12

Go to [here](https://hub.docker.com/extensions/weygu/nebulagraph-dd-ext) and one click to try it!



## ♥️ Thanks to

- [Gephi/Gephi-Lite](Gephi/Gephi-Lite), the amazing open-source project makes Graph Analytics in the Browser so very easy and elegant!
- [Streamlit](https://streamlit.io/), the best lib& community makes py-script boy like me to create decent data & GUI-ish things.
- [PyVis](https://github.com/WestHealth/pyvis), the best lib makes graph rendering so very smoothly in pure Python.
