# **Nebula**Grahp **Gephi** Exchange

[![for NebulaGraph](https://img.shields.io/badge/Toolchain-NebulaGraph-blue)](https://github.com/vesoft-inc/nebula) [![Gephi](https://img.shields.io/badge/Gephi-Supported-brightgreen)](https://github.com/gephi/gephi-lite/) [![Docker Image](https://img.shields.io/docker/v/weygu/nebulagraph-gephi-exchange?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/weygu/nebulagraph-gephi-exchange) [![Docker Extension](https://img.shields.io/badge/Docker-Extension-blue?logo=dockert)](https://hub.docker.com/extensions/weygu/nebulagraph-dd-ex) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/wey-gu/NebulaGraph-Gephi)](https://github.com/wey-gu/NebulaGraph-Gephi/releases) [![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg?)](https://nebulagraph-gephi.streamlit.app/) 

Gephi is an Awesome Graph Algo and Vis tool! If you would like to visualize your data on NebulaGraph with it, this is the way to go.

https://github.com/siwei-io/talks/assets/1651790/c036a229-c71e-4344-93d4-720657f2ba90

Features:

- Query NebulaGraph
- Render results
- Export result to a [gexf file](https://raw.githubusercontent.com/wey-gu/NebulaGraph-Gephi/main/example/nebulagraph_export.gexf) for Gephi
- Graph Algorithm and Visualization with [Gephi-Lite](https://github.com/gephi/gephi-lite/)

TODO

- [ ] Download as HTML
- [ ] Download the result as a CSV

## 🚀 How to

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
