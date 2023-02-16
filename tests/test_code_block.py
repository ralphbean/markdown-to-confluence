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
        '<ac:parameter ac:name="language">py</ac:parameter>'
        "<ac:plain-text-body><![CDATA["
        "m = {}\n"
        'm["x"] = 1\n'
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


def test_code_block_avoid_escape(script):
    """
    Avoid escaping code.
    """
    script.set_content(
        dedent(
            """
                ```yaml
                'test': '<[{}]>'

                ```
            """
        )
    )
    assert (
        '<ac:structured-macro ac:name="code" ac:schema-version="1">'
        '<ac:parameter ac:name="language">yml</ac:parameter>'
        "<ac:plain-text-body><![CDATA["
        "'test': '<[{}]>'\n"
        "]]></ac:plain-text-body>"
        "</ac:structured-macro>"
    ) in script.run()


def test_code_block_escape(script):
    """
    If code contains "]]>" (CDATA end), split it into multiple CDATA sections.
    """
    script.set_content(
        dedent(
            """
                ```xml
                <![CDATA[TEST]]>

                ```
            """
        )
    )
    assert (
        '<ac:structured-macro ac:name="code" ac:schema-version="1">'
        '<ac:parameter ac:name="language">xml</ac:parameter>'
        "<ac:plain-text-body><![CDATA[<![CDATA[TEST]]>]]&gt;<![CDATA[\n]]></ac:plain-text-body>"
        "</ac:structured-macro>"
    ) in script.run()


def test_code_block_for_unsuported_syntax(script):
    """
    Test code block for an unsupported syntax.
    """
    script.set_content(
        dedent(
            """
                ```Dockerfile
                FROM postgres:latest

                ```
            """
        )
    )
    assert (
        '<ac:structured-macro ac:name="code" ac:schema-version="1">'
        "<ac:plain-text-body><![CDATA[FROM postgres:latest\n]]></ac:plain-text-body>"
        "</ac:structured-macro>"
    ) in script.run()


def test_code_block_language_name_mapping(script):
    """
    Test code block language name mapping ("YAML" to "yml").
    """
    script.set_content(
        dedent(
            """
                ```YAML
                - test

                ```
            """
        )
    )
    assert (
        '<ac:structured-macro ac:name="code" ac:schema-version="1">'
        '<ac:parameter ac:name="language">yml</ac:parameter>'
        "<ac:plain-text-body><![CDATA[- test\n]]></ac:plain-text-body>"
        "</ac:structured-macro>"
    ) in script.run()
