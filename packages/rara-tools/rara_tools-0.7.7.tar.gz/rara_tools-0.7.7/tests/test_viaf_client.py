from rara_tools.normalizers.viaf import VIAFRecord, VIAFClient


def test_fetch_clusters_by_id_list():
    viaf_ids = ["7432247", "456"]
    client = VIAFClient()

    results = client.fetch_viaf_clusters(viaf_ids)
    assert len(results) == 2
    assert results["456"] == {}
    assert len(results["7432247"]) > 0


def test_fetch_viaf_results_for_normalizer():
    viaf_ids = ["7432247", "456"]
    client = VIAFClient()

    results = client.get_normalized_data_by_ids(viaf_ids)
    assert len(results) == 2

def test_get_normalized_data_by_search_term():
    client = VIAFClient()
    entity = "Kaja Kallas"

    # Test without verification
    record = client.get_normalized_data_by_search_term(
        search_term=entity,
        verify=False
    )
    assert record.name == "Kallas, Siim"

    record = client.get_normalized_data_by_search_term(
        search_term=entity,
        verify=True
    )
    assert record.name == "Kallas, Kaja"

    record = client.get_normalized_data_by_search_term(
        search_term = "ahsjhajhsjh",
        verify=True,
        max_records=5
    )
    assert record == None

def test_viaf_search_term_query_working():
    client = VIAFClient()
    assert client.check_search_term_query()

def test_viaf_id_query_working():
    client = VIAFClient()
    assert client.check_id_query()


def test_subfield_based_main_field_extraction():
    """ VIAFRecod.name should be retrieved from
    subfield (a) for persons, corporations etc, but
    from field (t) for titles.
    """
    client = VIAFClient()
    record = client.get_normalized_data_by_search_term(
        search_term="Kevade",
        field="local.uniformTitleWorks",
        verify=True
    )
    assert record.name == "Kevade"

    record = client.get_normalized_data_by_search_term(
        search_term="Oskar Luts",
        verify=True
    )
    assert record.name == "Luts, Oskar"

def test_changing_allowed_sources():
    client = VIAFClient(allowed_viaf_sources=["PLWABN"])
    record = client.get_normalized_data_by_search_term(
        search_term="Anora",
        field="local.uniformTitleWorks",
        verify=False
    )
    assert record.name == "Anora (film)"

    client = VIAFClient(allowed_viaf_sources=["LC"])
    record = client.get_normalized_data_by_search_term(
        search_term="Anora",
        field="local.uniformTitleWorks",
        verify=False
    )
    assert record.name == "Anora (Motion picture)"
