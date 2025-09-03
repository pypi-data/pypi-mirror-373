import pytest

from rudi_node_read.rudi_node_reader import RudiNodeReader

rudi_node_info = RudiNodeReader("https://bacasable.fenix.rudi-univ-rennes1.fr")


@pytest.fixture
def rudi_node():
    assert rudi_node_info is not None
    return rudi_node_info


def test_metadata_count(rudi_node):
    assert rudi_node.metadata_count > 0


def test_metadata_list(rudi_node):
    assert len(rudi_node.metadata_list) == rudi_node.metadata_count


def test_organization_list(rudi_node):
    assert len(rudi_node.organization_list) > 0


def test_organization_names(rudi_node):
    assert len(rudi_node.organization_names) == len(rudi_node.organization_list)


def test_contact_list(rudi_node):
    assert len(rudi_node.contact_list) > 0


def test_contact_names(rudi_node):
    assert len(rudi_node.contact_names) == len(rudi_node.contact_list)


def test_themes(rudi_node):
    assert len(rudi_node.themes) > 0


def test_keywords(rudi_node):
    assert len(rudi_node.keywords) > 0


def test_filter_metadata(rudi_node):
    meta1_id = rudi_node.metadata_list[0]["global_id"]
    assert len(rudi_node.filter_metadata({"global_id": meta1_id})) == 1


def test_get_metadata_with_producer(rudi_node):
    producer_name = rudi_node.metadata_list[0]["producer"]["organization_name"]
    assert len(rudi_node.get_metadata_with_producer(producer_name)) > 0


def test_get_metadata_with_contact(rudi_node):
    contact_name = rudi_node.metadata_list[0]["contacts"][0]["contact_name"]
    assert len(rudi_node.get_metadata_with_contact(contact_name)) > 0


def test_get_metadata_with_theme(rudi_node):
    theme = rudi_node.metadata_list[0]["theme"]
    assert len(rudi_node.get_metadata_with_theme(theme)) > 0


def test_get_metadata_with_keywords(rudi_node):
    keywords = rudi_node.metadata_list[0]["keywords"]
    assert len(rudi_node.get_metadata_with_keywords([keywords])) > 0


def test_find_metadata_with_uuid(rudi_node):
    meta1_id = rudi_node.metadata_list[0]["global_id"]
    assert rudi_node.find_metadata_with_uuid(meta1_id)["global_id"] == meta1_id


def test_find_metadata_with_title(rudi_node):
    meta1_title = rudi_node.metadata_list[0]["resource_title"]
    assert bool(meta1_title)
    meta1 = rudi_node.find_metadata_with_title(meta1_title)
    assert bool(meta1)
    assert meta1["resource_title"] == meta1_title


def test_metadata_with_available_media(rudi_node):
    meta_list = rudi_node.metadata_with_available_media
    assert len(meta_list) > 0
    media_list = meta_list[0]["available_formats"]
    an_available_media_was_found = False
    for media in media_list:
        if media["media_type"] == "FILE" and media["file_storage_status"] == "available":
            an_available_media_was_found = True
    assert an_available_media_was_found


def test_find_metadata_with_media_name(rudi_node):
    media_name = rudi_node.metadata_list[0]["available_formats"][0]["media_name"]
    assert len(rudi_node.find_metadata_with_media_name(media_name)) > 0


def test_find_metadata_with_media_name(rudi_node):
    media_uuid = rudi_node.metadata_list[0]["available_formats"][0]["media_id"]
    assert len(rudi_node.find_metadata_with_media_uuid(media_uuid)) > 0
