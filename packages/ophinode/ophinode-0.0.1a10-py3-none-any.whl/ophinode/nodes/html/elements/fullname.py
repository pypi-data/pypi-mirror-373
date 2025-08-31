__all__ = [
    "HtmlElement",
    "HeadElement",
    "TitleElement",
    "BaseElement",
    "LinkElement",
    "MetaElement",
    "StyleElement",
    "BodyElement",
    "ArticleElement",
    "SectionElement",
    "NavigationElement",
    "AsideElement",
    "HeadingLevel1Element",
    "HeadingLevel2Element",
    "HeadingLevel3Element",
    "HeadingLevel4Element",
    "HeadingLevel5Element",
    "HeadingLevel6Element",
    "HeadingGroupElement",
    "HeaderElement",
    "FooterElement",
    "AddressElement",
    "ParagraphElement",
    "HorizontalRuleElement",
    "PreformattedTextElement",
    "BlockQuotationElement",
    "OrderedListElement",
    "UnorderedListElement",
    "MenuElement",
    "ListItemElement",
    "DescriptionListElement",
    "DescriptionTermElement",
    "DescriptionDetailsElement",
    "FigureElement",
    "FigureCaptionElement",
    "MainElement",
    "SearchElement",
    "DivisionElement",
    "AnchorElement",
    "EmphasisElement",
    "StrongImportanceElement",
    "SmallPrintElement",
    "StrikethroughElement",
    "CitationElement",
    "QuotationElement",
    "DefinitionElement",
    "AbbreviationElement",
    "RubyAnnotationElement",
    "RubyTextElement",
    "RubyParenthesesElement",
    "DataElement",
    "TimeElement",
    "CodeElement",
    "VariableElement",
    "SampleElement",
    "KeyboardInputElement",
    "SubscriptElement",
    "SuperscriptElement",
    "ItalicTextElement",
    "BoldTextElement",
    "UnarticulatedAnnotationElement",
    "MarkedTextElement",
    "BidirectionalIsolateElement",
    "BidirectionalOverrideElement",
    "SpanElement",
    "LineBreakElement",
    "LineBreakOpportunityElement",
    "InsertionElement",
    "DeletionElement",
    "PictureElement",
    "SourceElement",
    "ImageElement",
    "InlineFrameElement",
    "EmbeddedContentElement",
    "ExternalObjectElement",
    "VideoElement",
    "AudioElement",
    "TextTrackElement",
    "ImageMapElement",
    "ImageMapAreaElement",
    "TableElement",
    "TableCaptionElement",
    "TableColumnGroupElement",
    "TableColumnElement",
    "TableBodyElement",
    "TableHeadElement",
    "TableFootElement",
    "TableRowElement",
    "TableDataCellElement",
    "TableHeaderCellElement",
    "FormElement",
    "LabelElement",
    "InputElement",
    "ButtonElement",
    "SelectElement",
    "DataListElement",
    "OptionGroupElement",
    "OptionElement",
    "TextAreaElement",
    "OutputElement",
    "ProgressElement",
    "MeterElement",
    "FieldSetElement",
    "FieldSetLegendElement",
    "DetailsElement",
    "SummaryElement",
    "DialogElement",
    "ScriptElement",
    "NoScriptElement",
    "TemplateElement",
    "SlotElement",
    "CanvasElement",
]

from ..core import OpenElement, ClosedElement, TextNode

# --- The document element ---

class HtmlElement(OpenElement):
    tag = "html"
    render_mode = "hierarchy"

# --- Document metadata ---

class HeadElement(OpenElement):
    tag = "head"
    render_mode = "hierarchy"

class TitleElement(OpenElement):
    tag = "title"
    render_mode = "phrase"

class BaseElement(ClosedElement):
    tag = "base"

class LinkElement(ClosedElement):
    tag = "link"

class MetaElement(ClosedElement):
    tag = "meta"

class StyleElement(OpenElement):
    tag = "style"
    render_mode = "hierarchy"

    def __init__(self, *args, escape_tag_delimiters = None, **kwargs):
        if escape_tag_delimiters is None:
            # stylesheets might contain angle brackets, so it is better to
            # disable tag delimiter escaping by default
            escape_tag_delimiters = False
        super().__init__(
            *args,
            escape_tag_delimiters=escape_tag_delimiters,
            **kwargs
        )

    def expand(self, context: "ophinode.site.BuildContext"):
        expansion = []
        for c in self._children:
            if isinstance(c, str):
                # Stylesheets might contain "</style", so it must be escaped
                content = c.replace("</script", "\\3C/script")
                node = TextNode(content)
                if self._escape_ampersands is not None:
                    node.escape_ampersands(self._escape_ampersands)
                if self._escape_tag_delimiters is not None:
                    node.escape_tag_delimiters(self._escape_tag_delimiters)
                expansion.append(node)
            else:
                expansion.append(c)
        return expansion

# --- Sections ---

class BodyElement(OpenElement):
    tag = "body"
    render_mode = "hierarchy"

class ArticleElement(OpenElement):
    tag = "article"
    render_mode = "hierarchy"

class SectionElement(OpenElement):
    tag = "section"
    render_mode = "hierarchy"

class NavigationElement(OpenElement):
    tag = "nav"
    render_mode = "hierarchy"

class AsideElement(OpenElement):
    tag = "aside"
    render_mode = "hierarchy"

class HeadingLevel1Element(OpenElement):
    tag = "h1"
    render_mode = "phrase"

class HeadingLevel2Element(OpenElement):
    tag = "h2"
    render_mode = "phrase"

class HeadingLevel3Element(OpenElement):
    tag = "h3"
    render_mode = "phrase"

class HeadingLevel4Element(OpenElement):
    tag = "h4"
    render_mode = "phrase"

class HeadingLevel5Element(OpenElement):
    tag = "h5"
    render_mode = "phrase"

class HeadingLevel6Element(OpenElement):
    tag = "h6"
    render_mode = "phrase"

class HeadingGroupElement(OpenElement):
    tag = "hgroup"
    render_mode = "hierarchy"

class HeaderElement(OpenElement):
    tag = "header"
    render_mode = "hierarchy"

class FooterElement(OpenElement):
    tag = "footer"
    render_mode = "hierarchy"

class AddressElement(OpenElement):
    tag = "address"
    render_mode = "phrase"

# --- Grouping content ---

class ParagraphElement(OpenElement):
    tag = "p"
    render_mode = "phrase"

class HorizontalRuleElement(ClosedElement):
    tag = "hr"

class PreformattedTextElement(OpenElement):
    tag = "pre"
    render_mode = "pre"

class BlockQuotationElement(OpenElement):
    tag = "blockquote"
    render_mode = "hierarchy"

class OrderedListElement(OpenElement):
    tag = "ol"
    render_mode = "hierarchy"

class UnorderedListElement(OpenElement):
    tag = "ul"
    render_mode = "hierarchy"

class MenuElement(OpenElement):
    tag = "menu"
    render_mode = "hierarchy"

class ListItemElement(OpenElement):
    tag = "li"
    render_mode = "phrase"

class DescriptionListElement(OpenElement):
    tag = "dl"
    render_mode = "hierarchy"

class DescriptionTermElement(OpenElement):
    tag = "dt"
    render_mode = "phrase"

class DescriptionDetailsElement(OpenElement):
    tag = "dd"
    render_mode = "phrase"

class FigureElement(OpenElement):
    tag = "figure"
    render_mode = "hierarchy"

class FigureCaptionElement(OpenElement):
    tag = "figcaption"
    render_mode = "phrase"

class MainElement(OpenElement):
    tag = "main"
    render_mode = "hierarchy"

class SearchElement(OpenElement):
    tag = "search"
    render_mode = "hierarchy"

class DivisionElement(OpenElement):
    tag = "div"
    render_mode = "hierarchy"

# --- Text-level semantics ---

class AnchorElement(OpenElement):
    tag = "a"
    render_mode = "phrase"

class EmphasisElement(OpenElement):
    tag = "em"
    render_mode = "phrase"

class StrongImportanceElement(OpenElement):
    tag = "strong"
    render_mode = "phrase"

class SmallPrintElement(OpenElement):
    tag = "small"
    render_mode = "phrase"

class StrikethroughElement(OpenElement):
    tag = "s"
    render_mode = "phrase"

class CitationElement(OpenElement):
    tag = "cite"
    render_mode = "phrase"

class QuotationElement(OpenElement):
    tag = "q"
    render_mode = "phrase"

class DefinitionElement(OpenElement):
    tag = "dfn"
    render_mode = "phrase"

class AbbreviationElement(OpenElement):
    tag = "abbr"
    render_mode = "phrase"

class RubyAnnotationElement(OpenElement):
    tag = "ruby"
    render_mode = "phrase"

class RubyTextElement(OpenElement):
    tag = "rt"
    render_mode = "phrase"

class RubyParenthesesElement(OpenElement):
    tag = "rp"
    render_mode = "phrase"

class DataElement(OpenElement):
    tag = "data"
    render_mode = "phrase"

class TimeElement(OpenElement):
    tag = "time"
    render_mode = "phrase"

class CodeElement(OpenElement):
    tag = "code"
    render_mode = "phrase"

class VariableElement(OpenElement):
    tag = "var"
    render_mode = "phrase"

class SampleElement(OpenElement):
    tag = "samp"
    render_mode = "phrase"

class KeyboardInputElement(OpenElement):
    tag = "kbd"
    render_mode = "phrase"

class SubscriptElement(OpenElement):
    tag = "sub"
    render_mode = "phrase"

class SuperscriptElement(OpenElement):
    tag = "sup"
    render_mode = "phrase"

class ItalicTextElement(OpenElement):
    tag = "i"
    render_mode = "phrase"

class BoldTextElement(OpenElement):
    tag = "b"
    render_mode = "phrase"

class UnarticulatedAnnotationElement(OpenElement):
    tag = "u"
    render_mode = "phrase"

class MarkedTextElement(OpenElement):
    tag = "mark"
    render_mode = "phrase"

class BidirectionalIsolateElement(OpenElement):
    tag = "bdi"
    render_mode = "phrase"

class BidirectionalOverrideElement(OpenElement):
    tag = "bdo"
    render_mode = "phrase"

class SpanElement(OpenElement):
    tag = "span"
    render_mode = "phrase"

class LineBreakElement(ClosedElement):
    tag = "br"

class LineBreakOpportunityElement(ClosedElement):
    tag = "wbr"

# --- Edits ---

class InsertionElement(OpenElement):
    tag = "ins"
    render_mode = "hierarchy"

class DeletionElement(OpenElement):
    tag = "del"
    render_mode = "hierarchy"

# --- Embedded content ---

class PictureElement(OpenElement):
    tag = "picture"
    render_mode = "hierarchy"

class SourceElement(ClosedElement):
    tag = "source"

class ImageElement(ClosedElement):
    tag = "img"

class InlineFrameElement(OpenElement):
    tag = "iframe"
    render_mode = "hierarchy"

class EmbeddedContentElement(ClosedElement):
    tag = "embed"

class ExternalObjectElement(OpenElement):
    tag = "object"
    render_mode = "hierarchy"

class VideoElement(OpenElement):
    tag = "video"
    render_mode = "phrase"

class AudioElement(OpenElement):
    tag = "audio"
    render_mode = "phrase"

class TextTrackElement(ClosedElement):
    tag = "track"

class ImageMapElement(OpenElement):
    tag = "map"
    render_mode = "hierarchy"

class ImageMapAreaElement(ClosedElement):
    tag = "area"

# --- Tabular data ---

class TableElement(OpenElement):
    tag = "table"
    render_mode = "hierarchy"

class TableCaptionElement(OpenElement):
    tag = "caption"
    render_mode = "phrase"

class TableColumnGroupElement(OpenElement):
    tag = "colgroup"
    render_mode = "hierarchy"

class TableColumnElement(ClosedElement):
    tag = "col"

class TableBodyElement(OpenElement):
    tag = "tbody"
    render_mode = "hierarchy"

class TableHeadElement(OpenElement):
    tag = "thead"
    render_mode = "hierarchy"

class TableFootElement(OpenElement):
    tag = "tfoot"
    render_mode = "hierarchy"

class TableRowElement(OpenElement):
    tag = "tr"
    render_mode = "hierarchy"

class TableDataCellElement(OpenElement):
    tag = "td"
    render_mode = "phrase"

class TableHeaderCellElement(OpenElement):
    tag = "th"
    render_mode = "phrase"

# --- Forms ---

class FormElement(OpenElement):
    tag = "form"
    render_mode = "hierarchy"

class LabelElement(OpenElement):
    tag = "label"
    render_mode = "phrase"

class InputElement(ClosedElement):
    tag = "input"

class ButtonElement(OpenElement):
    tag = "button"
    render_mode = "phrase"

class SelectElement(OpenElement):
    tag = "select"
    render_mode = "hierarchy"

class DataListElement(OpenElement):
    tag = "datalist"
    render_mode = "hierarchy"

class OptionGroupElement(OpenElement):
    tag = "optgroup"
    render_mode = "hierarchy"

class OptionElement(OpenElement):
    tag = "option"
    render_mode = "phrase"

class TextAreaElement(OpenElement):
    tag = "textarea"
    render_mode = "pre"

class OutputElement(OpenElement):
    tag = "output"
    render_mode = "phrase"

class ProgressElement(OpenElement):
    tag = "progress"
    render_mode = "phrase"

class MeterElement(OpenElement):
    tag = "meter"
    render_mode = "phrase"

class FieldSetElement(OpenElement):
    tag = "fieldset"
    render_mode = "hierarchy"

class FieldSetLegendElement(OpenElement):
    tag = "legend"
    render_mode = "phrase"

# --- Interactive elements ---

class DetailsElement(OpenElement):
    tag = "details"
    render_mode = "hierarchy"

class SummaryElement(OpenElement):
    tag = "summary"
    render_mode = "phrase"

class DialogElement(OpenElement):
    tag = "dialog"
    render_mode = "hierarchy"

# --- Scripting ---

class ScriptElement(OpenElement):
    tag = "script"
    render_mode = "hierarchy"

    def __init__(self, *args, escape_tag_delimiters = None, **kwargs):
        if escape_tag_delimiters is None:
            # javascript code might contain angle brackets,
            # so it is better to disable tag delimiter escaping by default
            escape_tag_delimiters = False
        super().__init__(
            *args,
            escape_tag_delimiters=escape_tag_delimiters,
            **kwargs
        )

    def expand(self, context: "ophinode.site.BuildContext"):
        expansion = []
        for c in self._children:
            if isinstance(c, str):
                # Due to restrictions for contents of script elements, some
                # sequences of characters must be replaced before constructing
                # a script element.
                # 
                # Unfortunately, correctly replacing such character sequences
                # require a full lexical analysis on the script content, but
                # ophinode is currently incapable of doing so.
                #
                # However, the sequences are expected to be rarely seen
                # outside literals, so replacements are done nonetheless.
                #
                # This behavior might change in the later versions of ophinode
                # when it starts to better support inline scripting.
                #
                # Read https://html.spec.whatwg.org/multipage/scripting.html#restrictions-for-contents-of-script-elements
                # for more information.
                #
                content = c.replace(
                    "<!--", "\\x3C!--"
                ).replace(
                    "<script", "\\x3Cscript"
                ).replace(
                    "</script", "\\x3C/script"
                )
                node = TextNode(content)
                if self._escape_ampersands is not None:
                    node.escape_ampersands(self._escape_ampersands)
                if self._escape_tag_delimiters is not None:
                    node.escape_tag_delimiters(self._escape_tag_delimiters)
                expansion.append(node)
            else:
                expansion.append(c)
        return expansion

class NoScriptElement(OpenElement):
    tag = "noscript"
    render_mode = "hierarchy"

class TemplateElement(OpenElement):
    tag = "template"
    render_mode = "hierarchy"

class SlotElement(OpenElement):
    tag = "slot"
    render_mode = "phrase"

class CanvasElement(OpenElement):
    tag = "canvas"
    render_mode = "hierarchy"

