from kurra import sparql
from httpx import Client
from rdflib import Graph, Dataset

assert sparql.query("http://localhost:3030/demods", "DROP ALL", Client(auth=("admin", "admin"))) == ""

# g = Dataset()
# g.parse("tests/test_sparql/vocab.nq")
# print(len(g))
# g.update("DROP ALL")
# print(len(g))