from dataclasses import dataclass

from enum import Enum
from typing import List, Literal, Optional, Union


from selectolax.lexbor import LexborHTMLParser, LexborNode


# copy

Element = Union[
    "Anchor",
    "Image",
    "Text",
    "Button",
    "Heading",
    "Paragraph",
    "TextInput",
    "UrlInput",
    "CheckboxInput",
    "RadioInput",
    "Label",
    "Select",
    "Option",
    "Details",
    "Summary",
]


class AsMethods:
    # generated:

    def as_anchor(self) -> Optional["Anchor"]:
        return self if self.__class__.__name__ == "Anchor" else None  # type: ignore

    def as_image(self) -> Optional["Image"]:
        return self if self.__class__.__name__ == "Image" else None  # type: ignore

    def as_text(self) -> Optional["Text"]:
        return self if self.__class__.__name__ == "Text" else None  # type: ignore

    def as_button(self) -> Optional["Button"]:
        return self if self.__class__.__name__ == "Button" else None  # type: ignore

    def as_heading(self) -> Optional["Heading"]:
        return self if self.__class__.__name__ == "Heading" else None  # type: ignore

    def as_paragraph(self) -> Optional["Paragraph"]:
        return self if self.__class__.__name__ == "Paragraph" else None  # type: ignore

    def as_text_input(self) -> Optional["TextInput"]:
        return self if self.__class__.__name__ == "TextInput" else None  # type: ignore

    def as_url_input(self) -> Optional["UrlInput"]:
        return self if self.__class__.__name__ == "UrlInput" else None  # type: ignore

    def as_checkbox_input(self) -> Optional["CheckboxInput"]:
        return self if self.__class__.__name__ == "CheckboxInput" else None  # type: ignore

    def as_radio_input(self) -> Optional["RadioInput"]:
        return self if self.__class__.__name__ == "RadioInput" else None  # type: ignore

    def as_label(self) -> Optional["Label"]:
        return self if self.__class__.__name__ == "Label" else None  # type: ignore

    def as_select(self) -> Optional["Select"]:
        return self if self.__class__.__name__ == "Select" else None  # type: ignore

    def as_option(self) -> Optional["Option"]:
        return self if self.__class__.__name__ == "Option" else None  # type: ignore

    def as_details(self) -> Optional["Details"]:
        return self if self.__class__.__name__ == "Details" else None  # type: ignore

    def as_summary(self) -> Optional["Summary"]:
        return self if self.__class__.__name__ == "Summary" else None  # type: ignore


@dataclass
class Anchor(AsMethods):
    href: str

    inner: List[Element]


@dataclass
class Image(AsMethods):
    src: str

    alt: Optional[str]


@dataclass
class Text(AsMethods):
    content: str


@dataclass
class Button(AsMethods):
    id: int

    inner: List[Element]


@dataclass
class Heading(AsMethods):
    level: int

    inner: List[Element]


@dataclass
class Paragraph(AsMethods):
    inner: List[Element]


@dataclass
class TextInput(AsMethods):
    id: int

    placeholder: Optional[str]


@dataclass
class UrlInput(AsMethods):
    id: int

    placeholder: Optional[str]


@dataclass
class CheckboxInput(AsMethods):
    id: int

    checked: bool


@dataclass
class RadioInput(AsMethods):
    id: int

    checked: bool


@dataclass
class Label(AsMethods):
    inner: List[Element]


@dataclass
class Select(AsMethods):
    inner: List[Element]

    multiple: bool


@dataclass
class Option(AsMethods):
    text: str


@dataclass
class Details(AsMethods):
    inner: List[Element]


@dataclass
class Summary(AsMethods):
    inner: List[Element]


class Parser:
    """Represents a parser for (interactivity-content-balanced) structured HTML.


    Creating this class is a cheap operation.

    There's no need to consider the performance cost by keeping this constructed.
    """

    __slots__ = ("id",)

    id: int

    def __init__(self):
        self.id = 0

    def fetch_advance_id(self) -> int:
        """(internal) Advance the ID counting, and return the previous value."""
        p = self.id

        self.id += 1
        return p

    def parse(self, html: str) -> List[Element]:
        """Parse from HTML.


        Returns:

            list[Element]: A list of elements, structured.
        """

        parser = LexborHTMLParser(html)

        body = parser.body

        if not body:
            return []

        return self.parse_children(body)

    def parse_children(self, root: LexborNode) -> List[Element]:
        """(internal) Parse the children.


        Args:

            root (LexborNode): The root to iterate from.
        """

        elements: List[Element] = []

        for node in root.iter(include_text=True):
            if not node.tag or node.tag == "-text":
                # "None" is possibly a text node

                text = node.text(strip=True)

                if text:
                    elements.append(Text(text))

            elif node.tag == "a":
                href = node.attributes.get("href", None)
                if not href:
                    continue

                children = self.parse_children(node)
                if not children:
                    continue

                elements.append(Anchor(href=href, inner=children))

            elif node.tag == "img":
                src = node.attributes.get("src", None)
                if not src:
                    continue

                alt = node.attributes.get("alt", None)

                elements.append(Image(src=src, alt=alt))

            elif node.tag == "button":
                children = self.parse_children(node)
                if not children:
                    continue

                elements.append(Button(id=self.fetch_advance_id(), inner=children))

            elif (
                len(node.tag) == 2
                and node.tag.startswith("h")
                and node.tag[-1].isdigit()
            ):
                children = self.parse_children(node)
                if not children:
                    continue

                elements.append(Heading(level=int(node.tag[1:]), inner=children))

            elif node.tag == "p":
                children = self.parse_children(node)
                if not children:
                    continue

                elements.append(Paragraph(children))

            elif node.tag == "input":
                type_ = node.attributes.get("type", "text")

                if type_ == "text":
                    placeholder = node.attributes.get("placeholder", None)
                    elements.append(
                        TextInput(id=self.fetch_advance_id(), placeholder=placeholder)
                    )

                elif type_ == "url":
                    placeholder = node.attributes.get("placeholder", None)
                    elements.append(
                        UrlInput(id=self.fetch_advance_id(), placeholder=placeholder)
                    )

                elif type_ == "checkbox":
                    attributes = node.attributes

                    if "checked" in attributes:
                        if attributes["checked"] == "true" or not attributes["checked"]:
                            checked = True
                        else:
                            checked = False
                    else:
                        checked = False

                    elements.append(
                        CheckboxInput(
                            id=self.fetch_advance_id(),
                            checked=checked,
                        )
                    )

                elif type_ == "radio":
                    attributes = node.attributes

                    if "checked" in attributes:
                        if attributes["checked"] == "true" or not attributes["checked"]:
                            checked = True
                        else:
                            checked = False
                    else:
                        checked = False

                    elements.append(
                        RadioInput(
                            id=self.fetch_advance_id(),
                            checked=checked,
                        )
                    )

            elif node.tag == "select":
                children = self.parse_children(node)
                if children:
                    attributes = node.attributes

                    if "multiple" in attributes:
                        if (
                            attributes["multiple"] == "true"
                            or not attributes["multiple"]
                        ):
                            multiple = True
                        else:
                            multiple = False
                    else:
                        multiple = False

                    elements.append(
                        Select(
                            children,
                            multiple=multiple,
                        )
                    )

            elif node.tag == "option":
                text = node.text(strip=True)

                if text:
                    elements.append(Option(text))

            elif node.tag == "label":
                children = self.parse_children(node)
                if children:
                    elements.append(Label(children))

            elif node.tag == "details":
                children = self.parse_children(node)
                if children:
                    elements.append(Details(children))

            elif node.tag == "summary":
                children = self.parse_children(node)
                if children:
                    elements.append(Summary(children))

            elif node.tag in ("script", "style"):
                continue

            else:
                # treat as fragments
                children = self.parse_children(node)
                if children:
                    elements.extend(children)

        return elements


class Indentation(Enum):
    Indent = 0
    Outdent = 1


class TextTransformer:
    __slots__ = ("elements", "texts")

    elements: List[Element]
    texts: List[Union[str, Literal[Indentation.Indent, Indentation.Outdent]]]

    def __init__(self, elements: List[Element]):
        self.elements = elements
        self.texts = []

    def indent(self):
        self.texts.append(Indentation.Indent)

    def outdent(self):
        self.texts.append(Indentation.Outdent)

    def add(self, t: str, /):
        self.texts.append(t)

    def add_body_prompt(self):
        self.add("- body:")

    def add_id_prompt(self, id: int, /):
        self.add("- id: " + str(id))

    def transform_inner(self, elements: List[Element]):
        """(internal) Transform inner elements."""

        for element in elements:
            anchor = element.as_anchor()
            if anchor:
                href = anchor.href
                inner = anchor.inner

                self.add("Anchor")
                self.indent()

                self.add("- " + href)

                self.add_body_prompt()
                self.indent()
                self.transform_inner(inner)
                self.outdent()
                self.outdent()

            button = element.as_button()

            if button:
                id = button.id

                inner = button.inner

                self.add("Button")
                self.indent()
                self.add_id_prompt(id)

                self.add_body_prompt()
                self.indent()
                self.transform_inner(inner)
                self.outdent()
                self.outdent()

            checkbox = element.as_checkbox_input()

            if checkbox:
                id = checkbox.id

                checked = checkbox.checked

                self.add("Checkbox")
                self.indent()
                self.add_id_prompt(id)

                self.add("- checked: " + str(checked))
                self.outdent()

            details = element.as_details()
            if details:
                inner = details.inner

                self.add("Details")
                self.indent()

                self.add_body_prompt()
                self.indent()
                self.transform_inner(inner)
                self.outdent()
                self.outdent()

            heading = element.as_heading()

            if heading:
                level = heading.level

                inner = heading.inner

                self.add("Heading" + str(level))
                self.indent()

                self.add_body_prompt()
                self.indent()
                self.transform_inner(inner)
                self.outdent()
                self.outdent()

            image = element.as_image()

            if image:
                src = image.src

                alt = image.alt

                self.add("Image")
                self.indent()

                self.add("- " + src)
                if alt:
                    self.add("- alt: " + alt)

                self.outdent()

            label = element.as_label()

            if label:
                inner = label.inner

                self.add("Label")
                self.indent()

                self.add_body_prompt()
                self.indent()
                self.transform_inner(inner)
                self.outdent()
                self.outdent()

            option = element.as_option()
            if option:
                text = option.text

                self.add("Option: " + text)

            paragraph = element.as_paragraph()
            if paragraph:
                inner = paragraph.inner

                self.add("Paragraph")
                self.indent()
                self.add_body_prompt()
                self.indent()
                self.transform_inner(inner)
                self.outdent()
                self.outdent()

            radio = element.as_radio_input()
            if radio:
                id = radio.id

                checked = radio.checked

                self.add("Radio")
                self.indent()
                self.add_id_prompt(id)

                self.add("- checked: " + str(checked))
                self.outdent()

            select = element.as_select()
            if select:
                inner = select.inner

                self.add("Select")
                self.indent()

                self.add_body_prompt()
                self.indent()
                self.transform_inner(inner)
                self.outdent()
                self.outdent()

            summary = element.as_summary()

            if summary:
                inner = summary.inner

                self.add("Summary")
                self.indent()

                self.add_body_prompt()
                self.indent()
                self.transform_inner(inner)
                self.outdent()
                self.outdent()

            text = element.as_text()

            if text:
                content = text.content
                self.add(content)

            text_input = element.as_text_input()

            if text_input:
                id = text_input.id

                placeholder = text_input.placeholder

                self.add("TextInput")
                self.indent()
                self.add_id_prompt(id)
                if placeholder:
                    self.add("- placeholder: " + placeholder)

                self.outdent()

            url_input = element.as_url_input()
            if url_input:
                id = url_input.id
                placeholder = url_input.placeholder

                self.add("UrlInput")
                self.indent()
                self.add_id_prompt(id)
                if placeholder:
                    self.add("- placeholder: " + placeholder)

                self.outdent()

    def transform(self) -> None:
        """Transform the page (all elements).
        
        Does not return anything.
        """
        self.transform_inner(self.elements)

    def text(self) -> str:
        """Once `transform()` is used, use this to generate text, if any.

        Alternatively, just use this function to automatically transform.
        """
        if not self.texts:
            self.transform()

        result = ""
        indents = 0

        for piece in self.texts:
            if piece == Indentation.Indent:
                indents += 1

            elif piece == Indentation.Outdent:
                indents -= 1

            else:
                result += "\n" + " " * (indents * 2) + piece

        return result
