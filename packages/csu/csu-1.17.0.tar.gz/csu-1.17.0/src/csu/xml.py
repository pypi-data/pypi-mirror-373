from collections.abc import Callable
from collections.abc import Iterator
from functools import reduce
from typing import T
from xml.etree import ElementTree
from xml.etree.ElementTree import Comment as ElementTreeComment
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ProcessingInstruction as ElementTreeProcessingInstruction
from xml.etree.ElementTree import QName as ElementTreeQName
from xml.etree.ElementTree import _escape_attrib as ElementTree_escape_attrib
from xml.etree.ElementTree import _escape_cdata as ElementTree_escape_cdata

from defusedxml.ElementTree import fromstring

try:
    from typing import Self
except ImportError:
    from typing import Self


class XMLParseError(Exception):
    pass


def serialize_xml(write: Callable[[str], None], elem: ElementTree.Element, qnames, namespaces, indent="\n") -> None:
    """
    Patched up version of etree.ElementTree._serialize_xml that produces well-indented output.
    """
    tag = elem.tag
    text = elem.text
    if text:
        text = text.strip()
    if tag is ElementTreeComment:
        write(f"{indent}<!--{text}-->")
    elif tag is ElementTreeProcessingInstruction:
        write(f"{indent}<?{text}?>")
    else:
        tag = qnames[tag]
        next_indent = f"{indent}  "
        if tag is None:
            if text:
                write(indent)
                write(ElementTree_escape_cdata(text))
            for e in elem:
                serialize_xml(write, e, qnames, None, next_indent)
        else:
            write(f"{indent}<{tag}")
            items = list(elem.items())
            if items or namespaces:
                if namespaces:
                    for v, k in sorted(namespaces.items(), key=lambda x: x[1]):  # sort on prefix
                        if k:
                            k = ":" + k
                        write(f' xmlns{k}="{ElementTree_escape_attrib(v)}"')
                for k, v in items:
                    if isinstance(k, ElementTreeQName):
                        k = k.text
                    v = qnames[v.text] if isinstance(v, ElementTreeQName) else ElementTree_escape_attrib(v)
                    write(f' {qnames[k]}="{v}"')
            children = len(elem)
            if text or children:
                write(">")
                if text:
                    if children:
                        write(next_indent)
                    write(ElementTree_escape_cdata(text))
                for e in elem:
                    serialize_xml(write, e, qnames, None, next_indent)
                if children:
                    write(indent)
                if text:
                    write(f"</{tag}>")
                else:
                    write(f"</{tag}>")
            else:
                write(" />")

    tail = elem.tail
    if tail:
        tail = tail.strip()
    if tail:
        write(indent)
        write(ElementTree_escape_cdata(tail))


def replace_ns(value: str, replacement: tuple[str, str]) -> str:
    alias, ns = replacement
    return value.replace(ns, f"{{{alias}}}")


class XML:
    element: Element

    def __init__(self, element, namespaces: None | dict = None):
        assert isinstance(element, Element), "Expected an Element instance. Perhaps you wanted to use XML.fromstring?"
        self.element = element
        self.namespaces = namespaces or {}

    @classmethod
    def fromstring(cls, xml: str, namespaces: None | dict = None) -> Self:
        try:
            return cls(
                fromstring(xml, forbid_dtd=True, forbid_entities=True, forbid_external=True),
                namespaces=namespaces,
            )
        except Exception as exc:
            raise XMLParseError(exc) from exc

    def __repr__(self):
        return ElementTree.tostring(self.element, encoding="unicode")

    def __str__(self):
        output = []
        serialize_xml(output.append, self.element, *ElementTree._namespaces(self.element))
        return "".join(output).strip()

    def __iter__(self) -> Iterator[Self]:
        return (XML(el) for el in self.element)

    @property
    def tag(self) -> str:
        return reduce(replace_ns, self.namespaces.items(), self.element.tag)

    @property
    def text(self) -> str:
        text = self.element.text
        return text.strip() if text else ""

    def find(self, tag, *, strict=True) -> Self | None:
        # noinspection StrFormat
        tag = tag.format(**self.namespaces)
        if self.element.tag == tag:
            element = self.element
        else:
            element = self.element.find(tag)

        if element is None:
            if strict:
                children = ",".join(f"<{element.tag}>" for element in self.element)
                raise XMLParseError(f"Failed to find <{tag}> element. Element list was: {children}. Parent: {self.element}")
        else:
            return self.__class__(element, self.namespaces)

    def findall(self, tag, *, strict=True) -> list[Self]:
        # noinspection StrFormat
        tag = tag.format(**self.namespaces)
        if self.element.tag == tag:
            return [self]
        else:
            elements = self.element.findall(tag)

        return [self.__class__(element, self.namespaces) for element in elements]

    def findtext(self, tag=None, strict=True, cast: type[T] | None = None) -> str | T:
        value = None
        if tag:
            xml = self.find(tag, strict=strict)
            if xml:
                value = xml.findtext()
        elif self.element.text:
            value = self.element.text.strip()

        if cast is str:
            return value or ""
        elif cast and (value or strict):
            try:
                return cast(value)
            except Exception as exc:
                raise XMLParseError(f"Failed casting <{tag}>{value!r} to {cast}", exc) from exc
        else:
            return value

    def getattr(self, attr, strict=True, cast: type[T] | None = None) -> str | T:
        # noinspection StrFormat
        attr = attr.format(**self.namespaces)
        attrs = self.element.attrib
        if attr in attrs:
            value = attrs[attr]
        elif strict:
            raise XMLParseError(f"Failed to find attribute {attr!r} in element {self.element.tag} with attributes {attrs}.")
        else:
            value = None

        if cast is str:
            return value or ""
        elif cast and (value or strict):
            try:
                return cast(value)
            except Exception as exc:
                raise XMLParseError(f"Failed casting {attr}={value!r} to {cast}", exc) from exc
        else:
            return value
