from os import scandir
from os.path import splitext
from pathlib import Path
from typing import (
    Any,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    Union,
)

from rdflib import Graph, URIRef
from rdflib.namespace import NamespaceManager
from rdflib.plugins.sparql.sparql import Query


class TemplateQueryCollection:
    def __init__(
        self, queries: Optional[dict] = None, initNs: Optional[Mapping[str, Any]] = None
    ):
        self.queries = queries or {}
        self.namespaceManager = NamespaceManager(Graph())
        if initNs:
            for prefix, ns in initNs.items():
                self.namespaceManager.bind(prefix, ns)

    def get(self, key):
        query_object = self.queries.get(key)
        if not query_object:
            return None
        if not isinstance(query_object, TemplateQuery):
            return TemplateQuery(query_object=query_object, collection=self)
        else:
            return query_object

    @property
    def namespaces(self) -> Iterable[Tuple[str, URIRef]]:
        return self.namespaceManager.namespaces()

    def set(self, key, val):
        self.queries[key] = val

    def loadFromDirectory(self, directory: Path):
        """Load a set of queries from .rq files in the given directory."""
        any(
            self.loadFromFile(path)
            for path in scandir(directory)
            if path.is_file() and splitext(path)[1] == ".rq"
        )

    def loadFromFile(self, filename: Path):
        """Load a queriy from an .rq file."""
        with open(filename, "r") as fileobject:
            self.set(splitext(filename.name)[0], fileobject.read())


class TemplateQuery:
    def __init__(
        self,
        query_object: Union[str, Query],
        collection: Optional[TemplateQueryCollection] = None,
    ):
        self.query_object = query_object
        self.collection = collection

    def prepare(self, **initBindings):
        # Setting use_store_provided is a hack, since the SPARQLStore of rdflib does not handle initBindings correctly:
        # cf. https://github.com/RDFLib/rdflib/issues/1772
        # alternatively in this prepare query, the initBindings could be injected directly into the query, while it would also be nice
        # if someone implements it here, to provide a pull request to the rdflib

        # something like, the following would be nice, but translateAlgebra() currently also replaces Functions with placeholders.
        #
        # from loguru import logger
        # from rdflib.plugins.sparql.algebra import translateQuery, translateAlgebra, Values, Join, pprintAlgebra
        # from rdflib.plugins.sparql.parser import parseQuery
        # query_object = translateQuery(parseQuery(query), queryGraph, initNs)
        # values = Values(res=[{Variable(x): initBindings[x] for x in v}])
        # cur = query_object.algebra.p
        # assert cur.name == "Project"
        # cur = cur.p
        # if cur.name == "Filter":
        #     cur = cur.p
        # if cur.p.name == "BGP":
        #     cur.p = Join(p1=values, p2=cur.p)
        # logger.debug(values)
        # logger.debug(query_object.algebra.p)
        # logger.debug(pprintAlgebra(query_object))
        # query = translateAlgebra(query_object)
        # logger.debug(query)

        initNs = None
        if self.collection:
            initNs = dict(self.collection.namespaces)

        if initBindings:
            return {
                "query_object": self.query_object,
                "initNs": initNs,
                "initBindings": initBindings,
                "use_store_provided": False,
            }
        else:
            return {
                "query_object": self.query_object,
                "initNs": initNs,
            }

    p = prepare
