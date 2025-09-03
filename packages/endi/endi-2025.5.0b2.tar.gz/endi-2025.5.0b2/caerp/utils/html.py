import nh3
import lxml.html
import lxml.etree
from copy import deepcopy


ALLOWED_HTML_TAGS = nh3.ALLOWED_TAGS.union({"font"})

ALLOWED_HTML_ATTRS = deepcopy(nh3.ALLOWED_ATTRIBUTES)
ALLOWED_HTML_ATTRS["font"] = {"color"}
ALLOWED_HTML_ATTRS["*"] = {"class", "style"}
ALLOWED_HTML_ATTRS["a"].union({"href", "target", "download"})

ALLOWED_CSS_STYLES = {
    "text-align",
    "font-weight",
    "font-family",
    "text-decoration",
    "padding",
    "padding-left",
    "color",
    "background-color",
    "line-height",
}


VOID_TAGS = (
    "<br />",
    "<br/>",
)
TAGS_TO_CHECK = (
    ("<p>", "</p>"),
    ("<div>", "</div>"),
)


def clean_style_attribute(tagname: str, attribute: str, value: str) -> str:
    """Remove unwanted css styles from the style attribute"""
    if attribute == "style":
        styles = [val.strip() for val in value.split(";") if ":" in val]

        key_values = [val.split(":") for val in styles]
        value = ";".join(
            [
                ":".join([key, value])
                for key, value in key_values
                if key in ALLOWED_CSS_STYLES
            ]
        )
    return value


def remove_tag(text, tag):
    """
    Remove the tag from the beginning of the given text

    :param str text: The text with the tag
    :param str tag: The tag to remove
    :rtype: str
    """
    return text[0 : -1 * len(tag)].strip()


def strip_whitespace(value):
    """
    Strip whitespace and tabs at the beginning/end of a string

    :param str value: The value to clean
    :rtype: str
    """
    if hasattr(value, "strip"):
        value = value.strip(" \t")
        if value.endswith("&nbsp;"):
            value = value[:-6]  # remove &nbsp;
            value = value.strip(" \t")
    return value


def strip_linebreaks(value):
    """
    Strip linebreaks

    :param str value: The value to clean
    :rtype: str
    """
    # we don't use rstrip since it's used for character stripping
    # (not chain)
    if hasattr(value, "strip"):
        value = value.strip("\n\r")
        for tag in "<br />", "<br>", "<br/>":
            if value.endswith(tag):
                value = remove_tag(value, tag)
                return strip_linebreaks(value)

    return value


def strip_void_lines(value):
    """
    RStrip value ending with void html tags

    :param str value: The value to clean
    :rtype: str
    """
    if hasattr(value, "strip"):
        for tag, close_tag in TAGS_TO_CHECK:
            if value.endswith(close_tag):
                prec_value = remove_tag(value, close_tag)
                prec_value = strip_whitespace(prec_value)
                prec_value = strip_linebreaks(prec_value)
                if prec_value.endswith(tag):
                    value = remove_tag(prec_value, tag)
                    value = strip_whitespace(value)
                    value = strip_linebreaks(value)
                    return strip_void_lines(value)

    return value


def strip_html(value):
    """
    Strip html void lines
    """
    value = strip_whitespace(value)
    value = strip_linebreaks(value)
    return strip_void_lines(value)


def strip_html_tags(text: str) -> str:
    """Remove Html tags from text"""
    if text:
        return nh3.clean(text, tags=set())
    else:
        return text


def clean_html(text):
    """
    Return a sanitized version of an html code keeping essential html tags
    and allowing only a few attributes
    """
    if text:
        text = strip_html(text)
        return nh3.clean(
            text,
            tags=ALLOWED_HTML_TAGS,
            attributes=ALLOWED_HTML_ATTRS,
            attribute_filter=clean_style_attribute,
        )
    else:
        return text


def split_rich_text_in_blocks(html_text: str):
    """
    Split the html text around the first level occurences of tagname

    >>> split_by_first_level_tag("<p>text <p>Texte</p></p><p>Texte2</p>texte en dehors"
    ['<p>text <p>Texte</p></p>', '<p>Texte2</p>', 'text en dehors]
    """
    if html_text is None:
        return [""]

    html_text = clean_html(html_text)

    try:
        # on a une balise parente
        lxml.html.fragment_fromstring(html_text)
        single = True
    except lxml.etree.ParserError:
        # On a pas de balise parent, on subdivise
        # PLusieurs résultats
        surrounding = lxml.html.fragment_fromstring(html_text, create_parent="div")
        single = False

    # On a une balise html au niveau du dessus, on ne peut pas splitter
    if single:
        return [html_text]
    elif len(surrounding.getchildren()) <= 1:
        return [html_text]
    else:
        # le résultat c'est les balises de premier niveau et d'éventuel textes
        # placés au premier niveau également
        result = []
        children = surrounding.getchildren()
        for child in children:
            result.append(lxml.etree.tostring(child).decode("utf-8"))
        return result
