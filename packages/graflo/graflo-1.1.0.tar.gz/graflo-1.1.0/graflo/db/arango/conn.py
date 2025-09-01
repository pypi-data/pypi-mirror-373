"""ArangoDB connection implementation for graph database operations.

This module implements the Connection interface for ArangoDB, providing
specific functionality for graph operations in ArangoDB. It handles:
- Graph and collection management
- Document and edge operations
- Index creation and management
- AQL query execution
- Batch operations with upsert support

Key Features:
    - Graph-based document organization
    - Edge collection management
    - Persistent, hash, skiplist, and fulltext indices
    - Batch document and edge operations
    - AQL query generation and execution

Example:
    >>> conn = ArangoConnection(config)
    >>> conn.init_db(schema, clean_start=True)
    >>> conn.upsert_docs_batch(docs, "users", match_keys=["email"])
"""

import json
import logging
from typing import Optional

from arango import ArangoClient
from suthing import ArangoConnectionConfig

from graflo.architecture.edge import Edge
from graflo.architecture.onto import (
    Index,
    IndexType,
)
from graflo.architecture.schema import Schema
from graflo.architecture.vertex import VertexConfig
from graflo.db.arango.query import fetch_fields_query
from graflo.db.arango.util import render_filters
from graflo.db.connection import Connection
from graflo.db.util import get_data_from_cursor
from graflo.filter.onto import Clause
from graflo.onto import AggregationType, DBFlavor
from graflo.util.transform import pick_unique_dict

logger = logging.getLogger(__name__)


class ArangoConnection(Connection):
    """ArangoDB-specific implementation of the Connection interface.

    This class provides ArangoDB-specific implementations for all database
    operations, including graph management, document operations, and query
    execution. It uses the ArangoDB Python driver for all operations.

    Attributes:
        conn: ArangoDB database connection instance
    """

    def __init__(self, config: ArangoConnectionConfig):
        """Initialize ArangoDB connection.

        Args:
            config: ArangoDB connection configuration containing URL, credentials,
                and database name
        """
        super().__init__()
        client = ArangoClient(hosts=config.url, request_timeout=config.request_timeout)

        self.conn = client.db(
            config.database,
            username=config.username,
            password=config.password,
        )

    def create_database(self, name: str):
        """Create a new ArangoDB database.

        Args:
            name: Name of the database to create
        """
        if not self.conn.has_database(name):
            self.conn.create_database(name)

    def delete_database(self, name: str):
        """Delete an ArangoDB database.

        Args:
            name: Name of the database to delete
        """
        if not self.conn.has_database(name):
            self.conn.delete_database(name)

    def execute(self, query, **kwargs):
        """Execute an AQL query.

        Args:
            query: AQL query string to execute
            **kwargs: Additional query parameters

        Returns:
            Cursor: ArangoDB cursor for the query results
        """
        cursor = self.conn.aql.execute(query)
        return cursor

    def close(self):
        """Close the ArangoDB connection."""
        # self.conn.close()
        pass

    def init_db(self, schema: Schema, clean_start):
        """Initialize ArangoDB with the given schema.

        Args:
            schema: Schema containing graph structure definitions
            clean_start: If True, delete all existing collections before initialization
        """
        if clean_start:
            self.delete_collections([], [], delete_all=True)
        self.define_collections(schema)
        self.define_indexes(schema)

    def define_collections(self, schema: Schema):
        """Define ArangoDB collections based on schema.

        Args:
            schema: Schema containing collection definitions
        """
        self.define_vertex_collections(schema)
        self.define_edge_collections(schema.edge_config.edges_list(include_aux=True))

    def define_vertex_collections(self, schema: Schema):
        """Define vertex collections in ArangoDB.

        Creates vertex collections for both connected and disconnected vertices,
        organizing them into appropriate graphs.

        Args:
            schema: Schema containing vertex definitions
        """
        vertex_config = schema.vertex_config
        disconnected_vertex_collections = (
            set(vertex_config.vertex_set) - schema.edge_config.vertices
        )
        for item in schema.edge_config.edges_list():
            u, v = item.source, item.target
            gname = item.graph_name
            logger.info(f"{item.source}, {item.target}, {gname}")
            if self.conn.has_graph(gname):
                g = self.conn.graph(gname)
            else:
                g = self.conn.create_graph(gname)  # type: ignore

            _ = self.create_collection(
                vertex_config.vertex_dbname(u), vertex_config.index(u), g
            )

            _ = self.create_collection(
                vertex_config.vertex_dbname(v), vertex_config.index(v), g
            )
        for v in disconnected_vertex_collections:
            _ = self.create_collection(
                vertex_config.vertex_dbname(v), vertex_config.index(v), None
            )

    def define_edge_collections(self, edges: list[Edge]):
        """Define edge collections in ArangoDB.

        Creates edge collections and their definitions in the appropriate graphs.

        Args:
            edges: List of edge configurations to create
        """
        for item in edges:
            gname = item.graph_name
            if self.conn.has_graph(gname):
                g = self.conn.graph(gname)
            else:
                g = self.conn.create_graph(gname)  # type: ignore
            if not g.has_edge_definition(item.collection_name):
                _ = g.create_edge_definition(
                    edge_collection=item.collection_name,
                    from_vertex_collections=[item._source_collection],
                    to_vertex_collections=[item._target_collection],
                )

    def _add_index(self, general_collection, index: Index):
        """Add an index to an ArangoDB collection.

        Supports persistent, hash, skiplist, and fulltext indices.

        Args:
            general_collection: ArangoDB collection to add index to
            index: Index configuration to create

        Returns:
            IndexHandle: Handle to the created index
        """
        data = index.db_form(DBFlavor.ARANGO)
        if index.type == IndexType.PERSISTENT:
            ih = general_collection.add_index(data)
        if index.type == IndexType.HASH:
            ih = general_collection.add_index(data)
        elif index.type == IndexType.SKIPLIST:
            ih = general_collection.add_skiplist_index(
                fields=index.fields, unique=index.unique
            )
        elif index.type == IndexType.FULLTEXT:
            ih = general_collection.add_index(
                data={"fields": index.fields, "type": "fulltext"}
            )
        else:
            ih = None
        return ih

    def define_vertex_indices(self, vertex_config: VertexConfig):
        """Define indices for vertex collections.

        Creates indices for each vertex collection based on the configuration.

        Args:
            vertex_config: Vertex configuration containing index definitions
        """
        for c in vertex_config.vertex_set:
            general_collection = self.conn.collection(vertex_config.vertex_dbname(c))
            ixs = general_collection.indexes()
            field_combinations = [tuple(ix["fields"]) for ix in ixs]
            for index_obj in vertex_config.indexes(c):
                if tuple(index_obj.fields) not in field_combinations:
                    self._add_index(general_collection, index_obj)

    def define_edge_indices(self, edges: list[Edge]):
        """Define indices for edge collections.

        Creates indices for each edge collection based on the configuration.

        Args:
            edges: List of edge configurations containing index definitions
        """
        for edge in edges:
            general_collection = self.conn.collection(edge.collection_name)
            for index_obj in edge.indexes:
                self._add_index(general_collection, index_obj)

    def fetch_indexes(self, db_class_name: Optional[str] = None):
        """Fetch all indices from the database.

        Args:
            db_class_name: Optional collection name to fetch indices for

        Returns:
            dict: Mapping of collection names to their indices
        """
        if db_class_name is None:
            classes = self.conn.collections()
        elif self.conn.has_collection(db_class_name):
            classes = [self.conn.collection(db_class_name)]
        else:
            classes = []

        r = {}
        for cname in classes:
            assert isinstance(cname["name"], str)
            c = self.conn.collection(cname["name"])
            r[cname["name"]] = c.indexes()
        return r

    def create_collection(self, db_class_name, index: None | Index = None, g=None):
        """Create a new ArangoDB collection.

        Args:
            db_class_name: Name of the collection to create
            index: Optional index to create on the collection
            g: Optional graph to create the collection in

        Returns:
            IndexHandle: Handle to the created index if one was created
        """
        if not self.conn.has_collection(db_class_name):
            if g is not None:
                _ = g.create_vertex_collection(db_class_name)
            else:
                self.conn.create_collection(db_class_name)
            general_collection = self.conn.collection(db_class_name)
            if index is not None and index.fields != ["_key"]:
                ih = self._add_index(general_collection, index)
                return ih
            else:
                return None

    def delete_collections(self, cnames=(), gnames=(), delete_all=False):
        """Delete collections and graphs from ArangoDB.

        Args:
            cnames: Collection names to delete
            gnames: Graph names to delete
            delete_all: If True, delete all non-system collections and graphs
        """
        logger.info("collections (non system):")
        logger.info([c for c in self.conn.collections() if c["name"][0] != "_"])

        if delete_all:
            cnames = [c["name"] for c in self.conn.collections() if c["name"][0] != "_"]
            gnames = [g["name"] for g in self.conn.graphs()]

        for gn in gnames:
            if self.conn.has_graph(gn):
                self.conn.delete_graph(gn)

        logger.info("graphs (after delete operation):")
        logger.info(self.conn.graphs())

        for cn in cnames:
            if self.conn.has_collection(cn):
                self.conn.delete_collection(cn)

        logger.info("collections (after delete operation):")
        logger.info([c for c in self.conn.collections() if c["name"][0] != "_"])

        logger.info("graphs:")
        logger.info(self.conn.graphs())

    def get_collections(self):
        """Get all collections in the database.

        Returns:
            list: List of collection information dictionaries
        """
        return self.conn.collections()

    def upsert_docs_batch(
        self,
        docs,
        class_name,
        match_keys: list[str] | None = None,
        **kwargs,
    ):
        """Upsert a batch of documents using AQL.

        Performs an upsert operation on a batch of documents, using the specified
        match keys to determine whether to update existing documents or insert new ones.

        Args:
            docs: List of documents to upsert
            class_name: Collection name to upsert into
            match_keys: Keys to match for upsert operation
            **kwargs: Additional options:
                - dry: If True, don't execute the query
                - update_keys: Keys to update on match
                - filter_uniques: If True, filter duplicate documents
        """
        dry = kwargs.pop("dry", False)
        update_keys = kwargs.pop("update_keys", None)
        filter_uniques = kwargs.pop("filter_uniques", True)

        if isinstance(docs, list):
            if filter_uniques:
                docs = pick_unique_dict(docs)
            docs = json.dumps(docs)
        if match_keys is None:
            upsert_clause = ""
            update_clause = ""
        else:
            upsert_clause = ", ".join([f'"{k}": doc.{k}' for k in match_keys])
            upsert_clause = f"UPSERT {{{upsert_clause}}}"

            if isinstance(update_keys, list):
                update_clause = ", ".join([f'"{k}": doc.{k}' for k in update_keys])
                update_clause = f"{{{update_clause}}}"
            elif update_keys == "doc":
                update_clause = "doc"
            else:
                update_clause = "{}"
            update_clause = f"UPDATE {update_clause}"

        options = "OPTIONS {exclusive: true, ignoreErrors: true}"

        q_update = f"""FOR doc in {docs}
                            {upsert_clause}
                            INSERT doc
                            {update_clause} 
                                IN {class_name} {options}"""
        if not dry:
            self.execute(q_update)

    def insert_edges_batch(
        self,
        docs_edges,
        source_class,
        target_class,
        relation_name=None,
        collection_name=None,
        match_keys_source=("_key",),
        match_keys_target=("_key",),
        filter_uniques=True,
        uniq_weight_fields=None,
        uniq_weight_collections=None,
        upsert_option=False,
        head=None,
        **kwargs,
    ):
        """Insert a batch of edges using AQL.

        Creates edges between source and target vertices, with support for
        weight fields and unique constraints.

        Args:
            docs_edges: List of edge documents in format [{_source_aux: source_doc, _target_aux: target_doc}]
            source_class: Source vertex collection name
            target_class: Target vertex collection name
            relation_name: Optional relation name for the edges
            collection_name: Edge collection name
            match_keys_source: Keys to match source vertices
            match_keys_target: Keys to match target vertices
            filter_uniques: If True, filter duplicate edges
            uniq_weight_fields: Fields to consider for uniqueness
            uniq_weight_collections: Collections to consider for uniqueness
            upsert_option: If True, use upsert instead of insert
            head: Optional limit on number of edges to insert
            **kwargs: Additional options:
                - dry: If True, don't execute the query
        """
        dry = kwargs.pop("dry", False)

        if isinstance(docs_edges, list):
            if docs_edges:
                logger.debug(f" docs_edges[0] = {docs_edges[0]}")
            if head is not None:
                docs_edges = docs_edges[:head]
            if filter_uniques:
                docs_edges = pick_unique_dict(docs_edges)
            docs_edges_str = json.dumps(docs_edges)
        else:
            return ""

        if match_keys_source[0] == "_key":
            result_from = f'CONCAT("{source_class}/", edge[0]._key)'
            source_filter = ""
        else:
            result_from = "sources[0]._id"
            filter_source = " && ".join(
                [f"v.{k} == edge[0].{k}" for k in match_keys_source]
            )
            source_filter = (
                f"LET sources = (FOR v IN {source_class} FILTER"
                f" {filter_source} LIMIT 1 RETURN v)"
            )

        if match_keys_target[0] == "_key":
            result_to = f'CONCAT("{target_class}/", edge[1]._key)'
            target_filter = ""
        else:
            result_to = "targets[0]._id"
            filter_target = " && ".join(
                [f"v.{k} == edge[1].{k}" for k in match_keys_target]
            )
            target_filter = (
                f"LET targets = (FOR v IN {target_class} FILTER"
                f" {filter_target} LIMIT 1 RETURN v)"
            )

        doc_definition = f"MERGE({{_from : {result_from}, _to : {result_to}}}, edge[2])"

        logger.debug(f" source_filter = {source_filter}")
        logger.debug(f" target_filter = {target_filter}")
        logger.debug(f" doc = {doc_definition}")

        if upsert_option:
            ups_from = result_from if source_filter else "doc._from"
            ups_to = result_to if target_filter else "doc._to"

            weight_fs = []
            if uniq_weight_fields is not None:
                weight_fs += uniq_weight_fields
            if uniq_weight_collections is not None:
                weight_fs += uniq_weight_collections
            if relation_name is not None:
                weight_fs += ["relation"]

            if weight_fs:
                weights_clause = ", " + ", ".join(
                    [f"'{x}' : edge.{x}" for x in weight_fs]
                )
            else:
                weights_clause = ""

            upsert = f"{{'_from': {ups_from}, '_to': {ups_to}" + weights_clause + "}"
            logger.debug(f" upsert clause: {upsert}")
            clauses = f"UPSERT {upsert} INSERT doc UPDATE {{}}"
            options = "OPTIONS {exclusive: true}"
        else:
            if relation_name is None:
                doc_clause = "doc"
            else:
                doc_clause = f"MERGE(doc, {{'relation': '{relation_name}' }})"
            clauses = f"INSERT {doc_clause}"
            options = "OPTIONS {exclusive: true, ignoreErrors: true}"

        q_update = f"""
            FOR edge in {docs_edges_str} {source_filter} {target_filter}
                LET doc = {doc_definition}
                {clauses}
                in {collection_name} {options}"""
        if not dry:
            self.execute(q_update)

    def insert_return_batch(self, docs, class_name):
        """Insert documents and return their keys.

        Args:
            docs: Documents to insert
            class_name: Collection to insert into

        Returns:
            str: AQL query string for the operation
        """
        docs = json.dumps(docs)
        query0 = f"""FOR doc in {docs}
              INSERT doc
              INTO {class_name}
              LET inserted = NEW
              RETURN {{_key: inserted._key}}
        """
        return query0

    def fetch_present_documents(
        self,
        batch,
        class_name,
        match_keys,
        keep_keys,
        flatten=False,
        filters: None | Clause | list | dict = None,
    ) -> list | dict:
        """Fetch documents that exist in the database.

        Args:
            batch: Batch of documents to check
            class_name: Collection to check in
            match_keys: Keys to match documents
            keep_keys: Keys to keep in result
            flatten: If True, flatten the result into a list
            filters: Additional query filters

        Returns:
            Union[list, dict]: Documents that exist in the database, either as a
                flat list or a dictionary mapping batch indices to documents
        """
        q0 = fetch_fields_query(
            collection_name=class_name,
            docs=batch,
            match_keys=match_keys,
            keep_keys=keep_keys,
            filters=filters,
        )
        # {"__i": i, "_group": [doc]}
        cursor = self.execute(q0)

        if flatten:
            rdata = []
            for item in get_data_from_cursor(cursor):
                group = item.pop("_group", [])
                rdata += [sub_item for sub_item in group]
            return rdata
        else:
            rdata_dict = {}
            for item in get_data_from_cursor(cursor):
                __i = item.pop("__i")
                group = item.pop("_group")
                rdata_dict[__i] = group
            return rdata_dict

    def fetch_docs(
        self,
        class_name,
        filters: None | Clause | list | dict = None,
        limit: int | None = None,
        return_keys: list | None = None,
        unset_keys: list | None = None,
    ):
        """Fetch documents from a collection.

        Args:
            class_name: Collection to fetch from
            filters: Query filters
            limit: Maximum number of documents to return
            return_keys: Keys to return
            unset_keys: Keys to unset

        Returns:
            list: Fetched documents
        """
        filter_clause = render_filters(filters, doc_name="d")

        if return_keys is None:
            if unset_keys is None:
                return_clause = "d"
            else:
                tmp_clause = ", ".join([f'"{item}"' for item in unset_keys])
                return_clause = f"UNSET(d, {tmp_clause})"
        else:
            if unset_keys is None:
                tmp_clause = ", ".join([f'"{item}"' for item in return_keys])
                return_clause = f"KEEP(d, {tmp_clause})"
            else:
                raise ValueError("both return_keys and unset_keys are set")

        if limit is not None and isinstance(limit, int):
            limit_clause = f"LIMIT {limit}"
        else:
            limit_clause = ""

        q = (
            f"FOR d in {class_name}"
            f"  {filter_clause}"
            f"  {limit_clause}"
            f"  RETURN {return_clause}"
        )
        cursor = self.execute(q)
        return get_data_from_cursor(cursor)

    def aggregate(
        self,
        class_name,
        aggregation_function: AggregationType,
        discriminant: str | None = None,
        aggregated_field: str | None = None,
        filters: None | Clause | list | dict = None,
    ):
        """Perform aggregation on a collection.

        Args:
            class_name: Collection to aggregate
            aggregation_function: Type of aggregation to perform
            discriminant: Field to group by
            aggregated_field: Field to aggregate
            filters: Query filters

        Returns:
            list: Aggregation results
        """
        filter_clause = render_filters(filters, doc_name="doc")

        if (
            aggregated_field is not None
            and aggregation_function != AggregationType.COUNT
        ):
            group_unit = f"g[*].doc.{aggregated_field}"
        else:
            group_unit = "g"

        if discriminant is not None:
            collect_clause = f"COLLECT value = doc['{discriminant}'] INTO g"
            return_clause = f"""{{ '{discriminant}' : value, '_value': {aggregation_function}({group_unit})}}"""
        else:
            if (
                aggregated_field is None
                and aggregation_function == AggregationType.COUNT
            ):
                collect_clause = (
                    f"COLLECT AGGREGATE value =  {aggregation_function} (doc)"
                )
            else:
                collect_clause = (
                    "COLLECT AGGREGATE value ="
                    f" {aggregation_function}(doc['{aggregated_field}'])"
                )
            return_clause = """{ '_value' : value }"""

        q = f"""FOR doc IN {class_name} 
                    {filter_clause}
                    {collect_clause}
                    RETURN {return_clause}"""

        cursor = self.execute(q)
        data = get_data_from_cursor(cursor)
        return data

    def keep_absent_documents(
        self,
        batch,
        class_name,
        match_keys,
        keep_keys,
        filters: None | Clause | list | dict = None,
    ):
        """Keep documents that don't exist in the database.

        Args:
            batch: Batch of documents to check
            class_name: Collection to check in
            match_keys: Keys to match documents
            keep_keys: Keys to keep in result
            filters: Additional query filters

        Returns:
            list: Documents that don't exist in the database
        """
        present_docs_keys = self.fetch_present_documents(
            batch=batch,
            class_name=class_name,
            match_keys=match_keys,
            keep_keys=keep_keys,
            flatten=False,
            filters=filters,
        )

        assert isinstance(present_docs_keys, dict)

        if any([len(v) > 1 for v in present_docs_keys.values()]):
            logger.warning(
                "fetch_present_documents returned multiple docs per filtering condition"
            )

        absent_indices = sorted(set(range(len(batch))) - set(present_docs_keys.keys()))
        batch_absent = [batch[j] for j in absent_indices]
        return batch_absent

    def update_to_numeric(self, collection_name, field):
        """Update a field to numeric type in all documents.

        Args:
            collection_name: Collection to update
            field: Field to convert to numeric

        Returns:
            str: AQL query string for the operation
        """
        s1 = f"FOR p IN {collection_name} FILTER p.{field} update p with {{"
        s2 = f"{field}: TO_NUMBER(p.{field}) "
        s3 = f"}} in {collection_name}"
        q0 = s1 + s2 + s3
        return q0
