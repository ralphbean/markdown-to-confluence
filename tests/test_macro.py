def test_html_macro(script):
    """
    Test that we can use raw HTML enclosed in div elements.
    """
    script.set_content(
        "<div>"
        '<ac:structured-macro ac:name="jiraissues">'
        '<ac:parameter ac:name="jqlQuery">filter=666 ORDER BY updated DESC</ac:parameter>'
        '<ac:parameter ac:name="columns">a,b,c</ac:parameter>'
        "</ac:structured-macro>"
        "</div>"
    )
    assert (
        "<div>"
        '<ac:structured-macro ac:name="jiraissues">'
        '<ac:parameter ac:name="jqlQuery">filter=666 ORDER BY updated DESC</ac:parameter>'
        '<ac:parameter ac:name="columns">a,b,c</ac:parameter>'
        "</ac:structured-macro>"
        "</div>"
    ) in script.run()
