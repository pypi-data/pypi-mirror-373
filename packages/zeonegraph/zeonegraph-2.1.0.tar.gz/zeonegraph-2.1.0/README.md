# ZeoneGraph Python Driver

ZeoneGraph Python Driver allows Python programs to connect to an ZeoneGraph database. Since it is [Psycopg2](http://initd.org/psycopg/) type extension module for ZeoneGraph, it supports additional data types such as `Vertex`, `Edge`, and `Path` to represent graph data.

## Features
- Cypher query support for Psycopg2 PostgreSQL Python driver (enables cypher queries directly)
- Deserialize ZeoneGraph results (AGType) to Vertex, Edge, Path

## Build From Source

```sh
git clone http://192.168.1.111:9980/zeonegraph/zeonegraph-python
cd zeonegraph-python
python setup.py install
```

## Example

```python
import psycopg2
import zeonegraph

conn = psycopg2.connect("dbname=test host=127.0.0.1 user=postgres")
cur = conn.cursor()
cur.execute("DROP GRAPH IF EXISTS t CASCADE")
cur.execute("CREATE GRAPH t")
cur.execute("SET graph_path = t")

cur.execute("CREATE (:v {name: 'ZeoneGraph'})")
conn.commit()

cur.execute("MATCH (n) RETURN n")
v = cur.fetchone()[0]
print(v.props['name'])
```

## Test

You may run the following command to test ZeoneGraph Python Driver.

```sh
pip install pytest
pytest
```

Before running the command, set the following environment variables to specify which database you will use for the test.

Variable Name                | Meaning
---------------------------- | ---------------------------
`ZEONEGRAPH_TESTDB`          | database name to connect to
`ZEONEGRAPH_TESTDB_HOST`     | database server host
`ZEONEGRAPH_TESTDB_PORT`     | database server port
`ZEONEGRAPH_TESTDB_USER`     | database user name
`ZEONEGRAPH_TESTDB_PASSWORD` | user password
