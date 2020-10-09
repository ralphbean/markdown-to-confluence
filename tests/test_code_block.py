from textwrap import dedent


def test_code_block(script):
    """
    Test code block.
    """
    script.set_content(
        dedent(
            """
                ```python
                m = {}
                m["x"] = 1
                ```
            """
        )
    )
    assert (
        '<ac:structured-macro ac:name="code" ac:schema-version="1">'
        '<ac:parameter ac:name="language">python</ac:parameter>'
        "<ac:plain-text-body><![CDATA["
        "m = {}\n"
        'm["x"\\] = 1\n'
        "]]></ac:plain-text-body>"
        "</ac:structured-macro>"
    ) in script.run()


def test_code_block_default_language(script):
    """
    Test code block with a default language.
    """
    script.set_content(
        dedent(
            """
                ```
                cd $HOME
                ```
            """
        )
    )
    assert (
        '<ac:structured-macro ac:name="code" ac:schema-version="1">'
        '<ac:parameter ac:name="language">bash</ac:parameter>'
        "<ac:plain-text-body><![CDATA["
        "cd $HOME\n"
        "]]></ac:plain-text-body>"
        "</ac:structured-macro>"
    ) in script.run()
