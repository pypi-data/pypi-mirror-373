from arkindex_cli.commands.export.utils import bounding_box, image_download


def test_image_download(responses, tmp_path, samples_dir):
    """
    Tests correct path is returned by image_download after redirecting input url
    with a response fixture
    """
    responses.add(
        responses.GET,
        url="http://www.google.fr/full/full/0/default.jpg",
        status=200,
        body=(samples_dir / "image.jpg").open("rb"),
    )

    assert (
        image_download("http://www.google.fr", "image", tmp_path)
        == tmp_path / "image.jpg"
    )


def test_bounding_box():
    """
    Tests correct starting coordinates, width and height is return from polygon
    coordinates
    """
    assert bounding_box(
        """[[538, 2307], [694, 2299], [767, 2316], [815, 2371], [1716, 2357],
        [2271, 2348], [2271, 1181], [1718, 1191], [902, 1171], [827, 1169],
        [788, 1192], [583, 1217], [538, 2307]]"""
    ) == (538, 2371, 1733, 1202)
