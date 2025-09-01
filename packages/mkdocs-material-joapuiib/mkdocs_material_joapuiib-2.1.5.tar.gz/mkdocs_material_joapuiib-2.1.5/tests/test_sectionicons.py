from material_joapuiib.plugins.sectionicons import extract_icon, remove_icon

def test_with_no_icon():
    section_title = "Section"

    icon = extract_icon(section_title)
    text = remove_icon(section_title)

    assert icon is None
    assert text == section_title

def test_with_icon():
    section_title = ":some/icon: Home"

    icon = extract_icon(section_title)
    text = remove_icon(section_title)

    assert icon == "some/icon"
    assert text == "Home"

def test_with_icon_and_spaces():
    section_title = ":some/icon: Home Page"

    icon = extract_icon(section_title)
    text = remove_icon(section_title)

    assert icon == "some/icon"
    assert text == "Home Page"

def test_with_icon_no_text():
    section_title = ":some/icon:"

    icon = extract_icon(section_title)
    text = remove_icon(section_title)

    assert icon == "some/icon"
    assert text == ""
