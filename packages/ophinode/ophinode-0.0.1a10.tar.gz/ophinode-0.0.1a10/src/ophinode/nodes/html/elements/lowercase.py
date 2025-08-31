__all__ = [
    "html",
    "head",
    "title",
    "base",
    "link",
    "meta",
    "style",
    "body",
    "article",
    "section",
    "nav",
    "aside",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hgroup",
    "header",
    "footer",
    "address",
    "p",
    "hr",
    "pre",
    "blockquote",
    "ol",
    "ul",
    "menu",
    "li",
    "dl",
    "dt",
    "dd",
    "figure",
    "figcaption",
    "main",
    "search",
    "div",
    "a",
    "em",
    "strong",
    "small",
    "s",
    "cite",
    "q",
    "dfn",
    "abbr",
    "ruby",
    "rt",
    "rp",
    "data",
    "time",
    "code",
    "var",
    "samp",
    "kbd",
    "sub",
    "sup",
    "i",
    "b",
    "u",
    "mark",
    "bdi",
    "bdo",
    "span",
    "br",
    "wbr",
    "ins",
    "del_",
    "picture",
    "source",
    "img",
    "iframe",
    "embed",
    "object_",
    "video",
    "audio",
    "track",
    "map",
    "area",
    "table",
    "caption",
    "colgroup",
    "column",
    "tbody",
    "thead",
    "tfoot",
    "tr",
    "td",
    "th",
    "form",
    "label",
    "input",
    "button",
    "select",
    "datalist",
    "optgroup",
    "option",
    "textarea",
    "output",
    "progress",
    "meter",
    "fieldset",
    "legend",
    "details",
    "summary",
    "dialog",
    "script",
    "noscript",
    "template",
    "slot",
    "canvas",
]

from .fullname import (
    HtmlElement,
    HeadElement,
    TitleElement,
    BaseElement,
    LinkElement,
    MetaElement,
    StyleElement,
    BodyElement,
    ArticleElement,
    SectionElement,
    NavigationElement,
    AsideElement,
    HeadingLevel1Element,
    HeadingLevel2Element,
    HeadingLevel3Element,
    HeadingLevel4Element,
    HeadingLevel5Element,
    HeadingLevel6Element,
    HeadingGroupElement,
    HeaderElement,
    FooterElement,
    AddressElement,
    ParagraphElement,
    HorizontalRuleElement,
    PreformattedTextElement,
    BlockQuotationElement,
    OrderedListElement,
    UnorderedListElement,
    MenuElement,
    ListItemElement,
    DescriptionListElement,
    DescriptionTermElement,
    DescriptionDetailsElement,
    FigureElement,
    FigureCaptionElement,
    MainElement,
    SearchElement,
    DivisionElement,
    AnchorElement,
    EmphasisElement,
    StrongImportanceElement,
    SmallPrintElement,
    StrikethroughElement,
    CitationElement,
    QuotationElement,
    DefinitionElement,
    AbbreviationElement,
    RubyAnnotationElement,
    RubyTextElement,
    RubyParenthesesElement,
    DataElement,
    TimeElement,
    CodeElement,
    VariableElement,
    SampleElement,
    KeyboardInputElement,
    SubscriptElement,
    SuperscriptElement,
    ItalicTextElement,
    BoldTextElement,
    UnarticulatedAnnotationElement,
    MarkedTextElement,
    BidirectionalIsolateElement,
    BidirectionalOverrideElement,
    SpanElement,
    LineBreakElement,
    LineBreakOpportunityElement,
    InsertionElement,
    DeletionElement,
    PictureElement,
    SourceElement,
    ImageElement,
    InlineFrameElement,
    EmbeddedContentElement,
    ExternalObjectElement,
    VideoElement,
    AudioElement,
    TextTrackElement,
    ImageMapElement,
    ImageMapAreaElement,
    TableElement,
    TableCaptionElement,
    TableColumnGroupElement,
    TableColumnElement,
    TableBodyElement,
    TableHeadElement,
    TableFootElement,
    TableRowElement,
    TableDataCellElement,
    TableHeaderCellElement,
    FormElement,
    LabelElement,
    InputElement,
    ButtonElement,
    SelectElement,
    DataListElement,
    OptionGroupElement,
    OptionElement,
    TextAreaElement,
    OutputElement,
    ProgressElement,
    MeterElement,
    FieldSetElement,
    FieldSetLegendElement,
    DetailsElement,
    SummaryElement,
    DialogElement,
    ScriptElement,
    NoScriptElement,
    TemplateElement,
    SlotElement,
    CanvasElement,
)

html = HtmlElement
head = HeadElement
title = TitleElement
base = BaseElement
link = LinkElement
meta = MetaElement
style = StyleElement
body = BodyElement
article = ArticleElement
section = SectionElement
nav = NavigationElement
aside = AsideElement
h1 = HeadingLevel1Element
h2 = HeadingLevel2Element
h3 = HeadingLevel3Element
h4 = HeadingLevel4Element
h5 = HeadingLevel5Element
h6 = HeadingLevel6Element
hgroup = HeadingGroupElement
header = HeaderElement
footer = FooterElement
address = AddressElement
p = ParagraphElement
hr = HorizontalRuleElement
pre = PreformattedTextElement
blockquote = BlockQuotationElement
ol = OrderedListElement
ul = UnorderedListElement
menu = MenuElement
li = ListItemElement
dl = DescriptionListElement
dt = DescriptionTermElement
dd = DescriptionDetailsElement
figure = FigureElement
figcaption = FigureCaptionElement
main = MainElement
search = SearchElement
div = DivisionElement
a = AnchorElement
em = EmphasisElement
strong = StrongImportanceElement
small = SmallPrintElement
s = StrikethroughElement
cite = CitationElement
q = QuotationElement
dfn = DefinitionElement
abbr = AbbreviationElement
ruby = RubyAnnotationElement
rt = RubyTextElement
rp = RubyParenthesesElement
data = DataElement
time = TimeElement
code = CodeElement
var = VariableElement
samp = SampleElement
kbd = KeyboardInputElement
sub = SubscriptElement
sup = SuperscriptElement
i = ItalicTextElement
b = BoldTextElement
u = UnarticulatedAnnotationElement
mark = MarkedTextElement
bdi = BidirectionalIsolateElement
bdo = BidirectionalOverrideElement
span = SpanElement
br = LineBreakElement
wbr = LineBreakOpportunityElement
ins = InsertionElement
del_ = DeletionElement
picture = PictureElement
source = SourceElement
img = ImageElement
iframe = InlineFrameElement
embed = EmbeddedContentElement
object_ = ExternalObjectElement
video = VideoElement
audio = AudioElement
track = TextTrackElement
map = ImageMapElement
area = ImageMapAreaElement
table = TableElement
caption = TableCaptionElement
colgroup = TableColumnGroupElement
column = TableColumnElement
tbody = TableBodyElement
thead = TableHeadElement
tfoot = TableFootElement
tr = TableRowElement
td = TableDataCellElement
th = TableHeaderCellElement
form = FormElement
label = LabelElement
input = InputElement
button = ButtonElement
select = SelectElement
datalist = DataListElement
optgroup = OptionGroupElement
option = OptionElement
textarea = TextAreaElement
output = OutputElement
progress = ProgressElement
meter = MeterElement
fieldset = FieldSetElement
legend = FieldSetLegendElement
details = DetailsElement
summary = SummaryElement
dialog = DialogElement
script = ScriptElement
noscript = NoScriptElement
template = TemplateElement
slot = SlotElement
canvas = CanvasElement

