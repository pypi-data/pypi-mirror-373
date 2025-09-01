import h2j

def test_class_to_selector():
    html = '<div class="a b c"></div>'
    out = h2j.convert(html, capture_element_attributes=True)
    cls = out["div"][0]["_attrs"]["class"]
    assert cls == "a.b.c"

def test_single_text_value():
    html = "<p>Hello</p>"
    out = h2j.convert(html)
    assert out["p"][0]["_val"] == "Hello"

def test_nested_text():
    html = "<p>Hello <b>World</b></p>"
    out = h2j.convert(html)
    assert out["p"][0]["_val"] == "Hello "
    assert out["p"][0]["b"][0]["_val"] == "World"

def test_multiple_text_values():
    html = "<p>Hello <i>dear</i> world</p>"
    out = h2j.convert(html)
    # p krijgt meerdere tekstsegmenten → _vals
    assert "_vals" in out["p"][0]
    vals = out["p"][0]["_vals"]
    assert "Hello " in vals
    assert " world" in vals
