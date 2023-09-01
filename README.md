# NebulaGrahp Gephi Exchange

https://github.com/siwei-io/talks/assets/1651790/c036a229-c71e-4344-93d4-720657f2ba90

Features:

- Query NebulaGraph
- Render results
- Export result to a [gexf file](https://raw.githubusercontent.com/wey-gu/NebulaGraph-Gephi/main/example/nebulagraph_export.gexf) for Gephi
- Graph Algorithm and Visualization with [Gephi-Lite](https://github.com/gephi/gephi-lite/)

TODO

- [ ] Download as HTML
- [ ] Download the result as a CSV

## How to

> Installation

```bash
git clone https://github.com/wey-gu/NebulaGraph-Gephi.git && cd NebulaGraph-Gephi
python3 -m pip install -r requirements.txt
```

> Run

```bash
streamlit run nebulagraph-gephi-exchange.py
```

> Optionally, with docker

```
docker-compose up -d
```
