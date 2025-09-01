#!/usr/bin/env python
"""Convert HTML to JSON (h2j: light & fast)."""

import bs4

def _record_element_value(element, json_output):
    # Bewaar originele spacing; negeer pure whitespace (zoals indents/newlines)
    if element == '\n' or element.strip() == '':
        return

    if json_output.get('_val'):
        json_output['_vals'] = [json_output['_val']]
        json_output['_vals'].append(element)  # bewaar exact zoals gezien
        del json_output['_val']
    elif json_output.get('_vals'):
        json_output['_vals'].append(element)
    else:
        json_output['_val'] = element


def _to_class_selector(value):
    tokens = []
    if isinstance(value, (list, tuple)):
        for item in value:
            if item is None:
                continue
            tokens.extend(str(item).split())
    elif isinstance(value, str):
        tokens = value.split()
    elif value is not None:
        tokens = str(value).split()
    return ".".join(tokens) if tokens else ""

def _normalize_attributes(attrs):
    if not attrs:
        return {}
    norm = {}
    for k, v in attrs.items():
        if k == "class":
            norm["class"] = _to_class_selector(v)
        else:
            norm[k] = v
    return norm

def _iterate(
    html_section,
    json_output,
    capture_element_values,
    capture_element_attributes,
):
    for part in html_section:
        if not isinstance(part, str):
            if not json_output.get(part.name):
                json_output[part.name] = list()
            new_json_output_for_subparts = {}
            if part.attrs and capture_element_attributes:
                new_json_output_for_subparts = {"_attrs": _normalize_attributes(part.attrs)}
            json_output[part.name].append(
                _iterate(
                    part,
                    new_json_output_for_subparts,
                    capture_element_values=capture_element_values,
                    capture_element_attributes=capture_element_attributes,
                )
            )
        else:
            if capture_element_values:
                _record_element_value(part, json_output)
    return json_output

def convert(
    html_string,
    capture_element_values=True,
    capture_element_attributes=True,
):
    """Convert the HTML string to JSON (dict)."""
    soup = bs4.BeautifulSoup(html_string, "html.parser")
    children = [child for child in soup.contents]
    return _iterate(
        children,
        {},
        capture_element_values=capture_element_values,
        capture_element_attributes=capture_element_attributes,
    )
