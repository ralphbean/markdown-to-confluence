def test_image(script):
    """
    Test image.
    """
    script.set_content("![The Image](images/example.png)")
    assert (
        '<p><ac:image ac:thumbnail="true" ac:title="The Image" ac:alt="The Image">'
        '<ri:attachment ri:filename="example.png"/>'
        "</ac:image></p>"
    ) in script.run()


def test_image_html(script):
    """
    Test image.
    """
    script.set_content(
        '<img src="images/example.png" alt="The Image" style="width:200px;"/>'
    )
    assert (
        '<img src="images/example.png" alt="The Image" style="width:200px;"/>'
    ) in script.run()
