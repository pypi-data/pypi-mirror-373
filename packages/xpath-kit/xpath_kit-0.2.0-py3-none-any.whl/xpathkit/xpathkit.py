from typing import Any, Callable, Dict, Iterable, List, Optional, Union

import lxml
import lxml.etree

from .exceptions import XPathError, XPathModificationError, XPathSelectionError
from .expressions import el


class XPathElement:
    """
    A wrapper for lxml.etree._Element, providing convenient XPath and DOM-like operations.
    """

    def __init__(
        self,
        element: lxml.etree._Element,
    ):
        """Initialize a XPathElement with a lxml.etree._Element."""
        self._ele = element

    @staticmethod
    def create(
        tag: str,
        attr: Optional[Dict[str, str]] = None,
        text: Optional[str] = None,
    ) -> "XPathElement":
        element = lxml.etree.Element(tag, attrib=attr or {})
        element.text = text
        return XPathElement(element)

    @property
    def tag(self) -> str:
        """Return the tag name of the element."""
        return self._ele.tag

    @property
    def attr(self) -> Dict[str, str]:
        """Return the attribute dictionary of the element."""
        return self._ele.attrib

    @property
    def start(
        self,
    ) -> str:
        ret = f"<{self.tag}"
        attr = " ".join(f'{k}="{v.strip()}"' for k, v in self.attr.items())
        if attr:
            ret += f" {attr}"
        ret += ">"
        return ret

    @property
    def end(
        self,
    ) -> str:
        return f"</{self.tag}>"

    def __str__(
        self,
    ):
        """Return the start tag as string representation."""
        return self.start

    def tostring(
        self,
    ) -> str:
        """Return the string serialization of the element."""
        return lxml.etree.tostring(
            self._ele,
            encoding="unicode",
        )

    def text(
        self,
    ) -> List[str]:
        """Return a list of direct text nodes under this element."""
        return self._ele.xpath("./text()")

    def string(
        self,
    ) -> str:
        """Return the string value of this element and all its descendants."""
        return self._ele.xpath("string(.)")

    def children(
        self,
        element: Union[str, el],
    ) -> "XPathElementList":
        """Return all direct child elements matching the given tag/expression."""
        if isinstance(element, str):
            element = el(element)
        return XPathElementList(self._ele.xpath(f"./{element}"))

    def child(
        self,
        element: Union[str, el],
    ) -> "XPathElement":
        """Return the first direct child element matching the given tag/expression."""
        return self.children(element).one()

    def descendants(
        self,
        element: Union[str, el],
    ) -> "XPathElementList":
        """Return all descendant elements matching the given tag/expression."""
        if isinstance(element, str):
            element = el(element)
        return XPathElementList(self._ele.xpath(f".//{element}"))

    def descendant(
        self,
        element: Union[str, el],
    ) -> "XPathElement":
        """Return the first descendant element matching the given tag/expression."""
        return self.descendants(element).one()

    def xpath(
        self,
        string: str,
    ) -> "XPathElementList":
        """Run an arbitrary XPath query and return the results as XPathElementList."""
        return XPathElementList(self._ele.xpath(string))

    def parent(
        self,
    ) -> "XPathElement":
        """Return the parent element as XPathElement."""
        return self.xpath("..").one()

    def next_sibling(
        self,
    ) -> Optional["XPathElement"]:
        """Return the next sibling element, or None if not found."""
        sibs = self._ele.itersiblings()
        for sib in sibs:
            return XPathElement(sib)
        return None

    def prev_sibling(
        self,
    ) -> Optional["XPathElement"]:
        """Return the previous sibling element, or None if not found."""
        sibs = self._ele.itersiblings(preceding=True)
        for sib in sibs:
            return XPathElement(sib)
        return None

    def __contains__(
        self,
        key: str,
    ) -> bool:
        """Check if the element has the given attribute."""
        return key in self._ele.attrib

    def __getitem__(
        self,
        key: str,
    ) -> Optional[str]:
        """Get the value of the given attribute, or None if not present."""
        return self._ele.attrib.get(key)

    def __setitem__(
        self,
        key: str,
        val: str,
    ) -> None:
        self._ele.attrib[key] = val

    def remove(
        self,
        child: "XPathElement",
    ) -> None:
        """Remove the given child element from this element."""
        try:
            self._ele.remove(child._ele)
        except ValueError as e:
            raise XPathModificationError(
                "Element is not a child of this element"
            ) from e

    def clear(
        self,
    ):
        """Remove all child elements and text from this element."""
        self._ele.clear()

    def append(
        self,
        child: "XPathElement",
    ) -> None:
        """Append a child element to this element."""
        self._ele.append(child._ele)

    def insert(
        self,
        index: int,
        child: "XPathElement",
    ) -> None:
        """Insert a child element at the given position."""
        self._ele.insert(index, child._ele)


class XPathElementList:
    """
    A list-like wrapper for multiple XPathElement objects, supporting batch operations.
    """

    def __init__(
        self,
        elements: Iterable[lxml.etree._Element],
    ):
        """Initialize a list of XPathElement objects from an iterable of lxml elements."""
        self._eles = [XPathElement(e) for e in elements]

    def __str__(
        self,
    ):
        """Return string representation of the list of elements."""
        return str([str(e) for e in self._eles])

    def __len__(
        self,
    ) -> int:
        """Return the number of elements in the list."""
        return len(self._eles)

    def len(
        self,
    ) -> int:
        return len(self._eles)

    def empty(
        self,
    ) -> bool:
        """Return True if the list is empty, else False."""
        return len(self) == 0

    def one(
        self,
    ) -> XPathElement:
        if self.empty():
            raise XPathSelectionError("No elements in group")
        if self.len() != 1:
            raise XPathSelectionError(
                "Element list does not contain exactly one element"
            )
        return self._eles[0]

    def first(
        self,
    ) -> XPathElement:
        if self.empty():
            raise XPathSelectionError("No elements in group")
        return self._eles[0]

    def last(
        self,
    ) -> XPathElement:
        if self.empty():
            raise XPathError("No elements in group")
        return self._eles[-1]

    def __getitem__(
        self,
        index: int,
    ) -> XPathElement:
        """Get the element at the specified index."""
        return self._eles[index]

    def filter(
        self,
        func: Callable[[XPathElement], bool],
    ) -> "XPathElementList":
        """Return a new XPathElementList filtered by the given function."""
        return XPathElementList([e._ele for e in self._eles if func(e)])

    def map(
        self,
        func: Callable[[XPathElement], Any],
    ) -> List[Any]:
        """Apply a function to each element and return a list of results."""
        return [func(e) for e in self._eles]

    def for_each(
        self,
        func: Callable[[XPathElement], None],
    ) -> None:
        """Apply a function to each element (no return)."""
        for e in self._eles:
            func(e)

    def to_list(
        self,
    ) -> List[XPathElement]:
        """Return the underlying list of XPathElement objects."""
        return self._eles


def html(
    content: Optional[Union[str, bytes]] = None,
    path: Optional[str] = None,
    encoding: str = "utf-8",
) -> XPathElement:
    """Parse HTML content and return the root XPathElement."""
    if not content and not path:
        raise ValueError("Either content or path must be provided")
    if content and path:
        raise ValueError("Only one of content or path must be provided")
    if not content:
        with open(path, "rb") as f:
            content = f.read()
    parser = lxml.etree.HTMLParser(encoding=encoding)
    tree = lxml.etree.HTML(content, parser=parser)
    return XPathElement(tree)
