"""A Link represents the predicate-object portion of a triple."""
from typing import Any, Dict, Type

from rdflib import BNode, Graph, Literal, Namespace, RDF, XSD

from altimeter.core.graph.exceptions import LinkParseException
from altimeter.core.graph.link.base import Link
from altimeter.core.graph.node_cache import NodeCache


class SimpleLink(Link):
    """A SimpleLink represents a scalar value. In RDF terms a SimpleLink creates a Literal
    in the graph."""

    field_type = "simple"

    def to_rdf(
        self, subj: BNode, namespace: Namespace, graph: Graph, node_cache: NodeCache
    ) -> None:
        """Graph this link on a BNode in a Graph using a given Namespace to create the full
        predicate.

        Args:
             subj: subject portion of triple - graph this link's pred, obj against it.
             namespace: RDF namespace to use for this triple's predicate
             graph: RDF graph
             node_cache: NodeCache to use to find cached nodes.
        """
        datatype = None
        if isinstance(self.obj, int):
            if self.obj > 2147483647:
                datatype = XSD.nonNegativeInteger
        literal = Literal(self.obj, datatype=datatype)
        graph.add((subj, getattr(namespace, self.pred), literal))


class MultiLink(Link):
    """Represents a named set of sublinks.  For example an 'EBSVolumeAttachemnt'
    MultiLink could exist which specifies sublinks Volume, AttachTime"""

    field_type = "multi"

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of this Link

        Returns:
            Dict representation of this Link
        """
        return {
            "pred": self.pred,
            "obj": [field.to_dict() for field in self.obj],
            "type": self.field_type,
        }

    def to_rdf(
        self, subj: BNode, namespace: Namespace, graph: Graph, node_cache: NodeCache
    ) -> None:
        """Graph this link on a BNode in a Graph using a given Namespace to create the full
        predicate.

        Args:
             subj: subject portion of triple - graph this link's pred, obj against it.
             namespace: RDF namespace to use for this triple's predicate
             graph: RDF graph
             node_cache: NodeCache to use to find cached nodes.
        """
        map_node = BNode()
        graph.add((map_node, RDF.type, getattr(namespace, f"{self.pred}")))
        for field in self.obj:
            field.to_rdf(map_node, namespace, graph, node_cache)
        graph.add((subj, getattr(namespace, self.pred), map_node))

    @classmethod
    def from_dict(cls: Type["MultiLink"], pred: str, obj: Any) -> "MultiLink":
        """Create a MultiLink object from a dict

        Args:
            pred: Link predicate
            obj: Link object, in the case of a MultiLink this is a list of Fields

        Returns:
            Link subclass object
        """
        fields = [link_from_dict(field) for field in obj]
        return cls(pred=pred, obj=fields)


class ResourceLinkLink(Link):
    """Represents a link to another resource which must exist in the graph."""

    field_type = "resource_link"

    def to_rdf(
        self, subj: BNode, namespace: Namespace, graph: Graph, node_cache: NodeCache
    ) -> None:
        """Graph this link on a BNode in a Graph using a given Namespace to create the full
        predicate.

        Args:
             subj: subject portion of triple - graph this link's pred, obj against it.
             namespace: RDF namespace to use for this triple's predicate
             graph: RDF graph
             node_cache: NodeCache to use to find cached nodes.
        """
        link_node = node_cache.setdefault(self.obj, BNode())
        graph.add((subj, getattr(namespace, self.pred), link_node))


class TransientResourceLinkLink(Link):
    """Represents a link to another resource which may or may not exist in the graph."""

    field_type = "transient_resource_link"

    def to_rdf(
        self, subj: BNode, namespace: Namespace, graph: Graph, node_cache: NodeCache
    ) -> None:
        """Graph this link on a BNode in a Graph using a given Namespace to create the full
        predicate.

        Args:
             subj: subject portion of triple - graph this link's pred, obj against it.
             namespace: RDF namespace to use for this triple's predicate
             graph: RDF graph
             node_cache: NodeCache to use to find cached nodes.
        """
        link_node = node_cache.setdefault(self.obj, BNode())
        graph.add((subj, getattr(namespace, self.pred), link_node))


class TagLink(Link):
    """Represents a AWS-style Tag attached to a node."""

    field_type = "tag"

    def to_rdf(
        self, subj: BNode, namespace: Namespace, graph: Graph, node_cache: NodeCache
    ) -> None:
        """Graph this link on a BNode in a Graph using a given Namespace to create the full
        predicate.

        Args:
             subj: subject portion of triple - graph this link's pred, obj against it.
             namespace: RDF namespace to use for this triple's predicate
             graph: RDF graph
             node_cache: NodeCache to use to find cached nodes.
        """
        tag_id = f"{self.pred}:{self.obj}"
        tag_node = node_cache.get(tag_id)
        if tag_node is None:
            tag_node = BNode()
            graph.add((tag_node, namespace.key, Literal(self.pred)))
            graph.add((tag_node, namespace.value, Literal(self.obj)))
            graph.add((tag_node, RDF.type, getattr(namespace, "tag")))
            node_cache[tag_id] = tag_node
        graph.add((subj, getattr(namespace, "tag"), tag_node))


def link_from_dict(data: Dict[str, Any]) -> Link:
    """Create and return a Link subclass object from dict data.

    Args:
        data: data to generate a Link from

    Returns:
        object of the appropriate Link subclass
    """
    field_type = data.get("type")
    if field_type is None:
        raise LinkParseException(f"key 'type' not found in {data}")
    pred = data.get("pred")
    if pred is None:
        raise LinkParseException(f"key 'pred' not found in {data}")
    obj = data.get("obj")
    if field_type == "transient_resource_link":
        return TransientResourceLinkLink.from_dict(pred, obj)
    if obj is None:
        raise LinkParseException(f"key 'obj' not found in {data}")
    if field_type == "simple":
        return SimpleLink.from_dict(pred, obj)
    if field_type == "multi":
        return MultiLink.from_dict(pred, obj)
    if field_type == "resource_link":
        return ResourceLinkLink.from_dict(pred, obj)
    if field_type == "tag":
        return TagLink.from_dict(pred, obj)
    raise LinkParseException(f"Unknown field type '{field_type}")
