import pytest
import os
import jsonlines
from pprint import pprint
import json
from rara_tools.elastic import KataElastic
from rara_linker.linkers.linker import Linker
from rara_linker.linkers.keyword_linker import KeywordLinker
from rara_linker.linkers.meta_linker import MetaLinker
from rara_linker.config import EntityType
from rara_linker.exceptions import InvalidInputError
from time import sleep
from typing import List

ES_DATA_DIR = os.path.join("tests", "test_data", "es_data")
KEYWORD_DATA_DIR = os.path.join("tests", "test_data", "keywords")
META_DATA_DIR = os.path.join("tests", "test_data", "meta")

EMS_TEST_FILE = os.path.join(ES_DATA_DIR, "ems_es_test.jl")
PER_TEST_FILE = os.path.join(ES_DATA_DIR, "persons_es_test.jl")
ORG_TEST_FILE = os.path.join(ES_DATA_DIR, "organizations_es_test.jl")
LOC_TEST_FILE = os.path.join(ES_DATA_DIR, "locations_es_test.jl")
TITLE_TEST_FILE = os.path.join(ES_DATA_DIR, "titles_es_test.jl")

KEYWORDS_TEST_FILE = os.path.join(KEYWORD_DATA_DIR, "keywords_test.json")


PER_TEST_INDEX = "per_test_linker"
ORG_TEST_INDEX = "org_test_linker"
LOC_TEST_INDEX = "loc_test_linker"
EMS_TEST_INDEX = "ems_test_linker"
TITLE_TEST_INDEX = "title_test_linker"

ES_URL = os.getenv("ELASTIC_TEST_URL", "http://localhost:9200")
ELASTIC = KataElastic(ES_URL)

VECTORIZER_DATA_DIR = os.path.join("tests", "vectorizer_data")


LINKER = Linker(
    add_viaf_info=False,
    vectorizer_or_dir_path=VECTORIZER_DATA_DIR,
    per_config = {"es_host": ES_URL, "es_index": PER_TEST_INDEX},
    org_config = {"es_host": ES_URL, "es_index": ORG_TEST_INDEX},
    loc_config = {"es_host": ES_URL, "es_index": LOC_TEST_INDEX},
    ems_config = {"es_host": ES_URL, "es_index": EMS_TEST_INDEX},
    title_config = {"es_host": ES_URL, "es_index": TITLE_TEST_INDEX}
)

LINKER_WITH_VIAF = Linker(
    add_viaf_info=True,
    vectorizer_or_dir_path=VECTORIZER_DATA_DIR,
    per_config = {"es_host": ES_URL, "es_index": PER_TEST_INDEX},
    org_config = {"es_host": ES_URL, "es_index": ORG_TEST_INDEX},
    loc_config = {"es_host": ES_URL, "es_index": LOC_TEST_INDEX},
    ems_config = {"es_host": ES_URL, "es_index": EMS_TEST_INDEX},
    title_config = {"es_host": ES_URL, "es_index": TITLE_TEST_INDEX}
)

KEYWORD_LINKER = KeywordLinker(
    add_viaf_info=True,
    vectorizer_or_dir_path=VECTORIZER_DATA_DIR,
    per_config = {"es_host": ES_URL, "es_index": PER_TEST_INDEX},
    org_config = {"es_host": ES_URL, "es_index": ORG_TEST_INDEX},
    loc_config = {"es_host": ES_URL, "es_index": LOC_TEST_INDEX},
    ems_config = {"es_host": ES_URL, "es_index": EMS_TEST_INDEX},
    title_config = {"es_host": ES_URL, "es_index": TITLE_TEST_INDEX}
)

META_LINKER = MetaLinker(
    add_viaf_info=True,
    vectorizer_or_dir_path=VECTORIZER_DATA_DIR,
    per_config = {"es_host": ES_URL, "es_index": PER_TEST_INDEX},
    org_config = {"es_host": ES_URL, "es_index": ORG_TEST_INDEX},
    loc_config = {"es_host": ES_URL, "es_index": LOC_TEST_INDEX},
    ems_config = {"es_host": ES_URL, "es_index": EMS_TEST_INDEX},
    title_config = {"es_host": ES_URL, "es_index": TITLE_TEST_INDEX}
)

def load_jl(file_path: str):
    data = []
    with jsonlines.open(file_path, "r") as f:
        for doc in f:
            data.append(doc)
    return data

def jl_iterator(file_path: str):
    with jsonlines.open(file_path, "r") as f:
        for doc in f:
            yield doc

def load_json(file_path: str):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data



def upload_test_documents(
        elastic: KataElastic,
        data_file: str,
        test_index_name: str,
        vector_field: str = ""
    ):

    data = load_jl(data_file)
    # Create test index
    created = elastic.create_index(test_index_name)

    # If vector field is specified, add vector mapping
    if vector_field:
        result = elastic.add_vector_mapping(
            index_name=test_index_name,
            field=vector_field
        )
    sleep(1)
    for document in data:
        indexed = elastic.index_document(test_index_name, document)
    return indexed

@pytest.mark.order(1)
def test_index_upload():
    # Upload EMS test index
    indexed = upload_test_documents(
        elastic=ELASTIC,
        data_file=EMS_TEST_FILE,
        test_index_name=EMS_TEST_INDEX
    )
    assert indexed["result"] == "created"

    # Upload LOC test index
    indexed = upload_test_documents(
        elastic=ELASTIC,
        data_file=LOC_TEST_FILE,
        test_index_name=LOC_TEST_INDEX
    )
    assert indexed["result"] == "created"

    # Upload PER test index
    indexed = upload_test_documents(
        elastic=ELASTIC,
        data_file=PER_TEST_FILE,
        test_index_name=PER_TEST_INDEX,
        vector_field="vector"
    )
    assert indexed["result"] == "created"

    # Upload ORG test index
    indexed = upload_test_documents(
        elastic=ELASTIC,
        data_file=ORG_TEST_FILE,
        test_index_name=ORG_TEST_INDEX,
        vector_field="vector"
    )
    assert indexed["result"] == "created"

    # Upload TITLE test index
    indexed = upload_test_documents(
        elastic=ELASTIC,
        data_file=TITLE_TEST_FILE,
        test_index_name=TITLE_TEST_INDEX
    )
    assert indexed["result"] == "created"

@pytest.mark.order(2)
def test_per_linking_exact():
    linked = LINKER.link(entity="Paul Keres")
    print(linked)
    #pprint(linked.to_dict)
    assert linked.n_linked == 2
    assert linked.entity_type == EntityType.PER


@pytest.mark.order(3)
def test_per_linking_fuzzy():
    linked = LINKER.link(entity="Paul Keers")
    assert linked.n_linked == 3
    assert linked.entity_type == EntityType.PER

@pytest.mark.order(4)
def test_per_linking_fuzzy_with_vector_search():
    context = "Selgusid 53. maleturniiri võitjad"
    linked = LINKER.link(entity="Paul Keers", context=context)

    expected_description = "Eesti maletaja ja maleteoreetik"
    assert linked.n_linked == 1
    assert linked.linked_info[0].elastic["description"] == expected_description
    assert linked.entity_type == EntityType.PER

@pytest.mark.order(5)
def test_org_linking_fuzzy():
    linked = LINKER.link(entity="Gustav Adolfi Gümnasium")
    assert linked.n_linked == 1
    assert linked.entity_type == EntityType.ORG

@pytest.mark.order(6)
def test_org_acronym_linking():
    linked = LINKER.link(entity="EKI")
    assert linked.n_linked == 3
    assert linked.entity_type == EntityType.ORG


@pytest.mark.order(7)
def test_org_acronym_linking_with_vector_search():
    context = "Tavast: keelemudeli arendajad ei soovi eesti keele korpust isegi tasuta"
    linked = LINKER.link(entity="EKI", context=context)
    assert linked.n_linked == 1
    assert linked.entity_type == EntityType.ORG
    assert linked.linked_info[0].linked_entity == "Eesti Keele Instituut"

@pytest.mark.order(8)
def test_loc_linking():
    linked = LINKER.link(entity="Reval")
    assert linked.n_linked == 1
    assert linked.linked_info[0].linked_entity == "Tallinn"
    assert linked.entity_type == EntityType.LOC

@pytest.mark.order(9)
def test_ems_en_keyword_linking():
    linked = LINKER.link(entity="cinematography")
    assert linked.n_linked == 1
    assert linked.linked_info[0].linked_entity == "filmikunst"
    assert linked.entity_type == EntityType.KEYWORD

@pytest.mark.order(10)
def test_ems_et_keyword_linking():
    linked = LINKER.link(entity="harimatu")
    assert linked.n_linked == 1
    assert linked.linked_info[0].linked_entity == "harimatus"
    assert linked.entity_type == EntityType.KEYWORD

@pytest.mark.order(11)
def test_entity_type_param():
    linked = LINKER.link(entity="feline")
    assert linked.n_linked == 1
    assert linked.linked_info[0].linked_entity == "Viljandi"
    assert linked.entity_type == EntityType.LOC

    linked = LINKER.link(entity="feline", entity_type="EMS_KEYWORD")
    assert linked.n_linked == 1
    assert linked.linked_info[0].linked_entity == "kaslased"
    assert linked.entity_type == EntityType.KEYWORD

@pytest.mark.order(12)
def test_prefix_length_param():
    linked = LINKER.link(entity="Raul Keres")
    assert linked.n_linked == 0
    assert linked.entity_type == EntityType.UNK

    linked = LINKER.link(entity="Raul Keres", prefix_length=0)
    assert linked.n_linked == 2
    assert linked.entity_type == EntityType.PER

@pytest.mark.order(13)
def test_fuzziness_param():
    linked = LINKER.link(entity="Heino Barrik")
    assert linked.n_linked == 1
    assert linked.entity_type == EntityType.PER

    linked = LINKER.link(entity="Heino Barrik", fuzziness=0)
    assert linked.n_linked == 0
    assert linked.entity_type == EntityType.UNK


@pytest.mark.order(14)
def test_output_has_required_fields():
    linked = LINKER_WITH_VIAF.link(entity="Jarmo Kauge")
    assert linked.n_linked == 1
    assert linked.entity_type == EntityType.PER
    assert linked.original_entity == "Jarmo Kauge"
    assert linked.similarity_score == 1.0
    assert linked.linking_config

    linked_doc = linked.linked_info[0]
    assert linked_doc.to_dict()
    assert linked_doc.elastic
    assert linked_doc.json
    assert linked_doc.marc
    assert linked_doc.linked_entity
    assert linked_doc.viaf

@pytest.mark.order(15)
def test_per_stage_name_linking():
    # Should return matches
    linked = LINKER.link(entity="Shakira")
    assert linked.n_linked == 1
    assert linked.entity_type == EntityType.PER


@pytest.mark.order(16)
def test_per_single_surname_linking():
    # Should NOT return matches
    linked = LINKER.link(entity="Snicket")
    assert linked.n_linked == 0
    assert linked.entity_type == EntityType.UNK

    linked = LINKER.link(entity="Lemony Snicket")
    assert linked.n_linked == 1
    assert linked.entity_type == EntityType.PER

@pytest.mark.order(17)
def test_title_linking():
    linked = LINKER.link(entity="Kevade")
    assert linked.entity_type == EntityType.TITLE
    assert linked.n_linked == 1
    assert linked.linked_info[0].elastic.get("author_name", "") == "Luts, Oskar"

@pytest.mark.order(18)
def test_title_linking_with_author_filter():
    linked = LINKER.link(
        entity="Kevade", author="Kenneth Sammal",
        entity_type=EntityType.TITLE
    )
    assert linked.n_linked == 0

    linked = LINKER.link(
        entity="Kevade", author="Oskar Luts",
        entity_type=EntityType.TITLE
    )
    assert linked.n_linked > 0

    linked = LINKER.link(
        entity="Kevade", author="Luts, Oskar",
        entity_type=EntityType.TITLE
    )
    assert linked.n_linked > 0

@pytest.mark.order(19)
def test_title_linking_with_year_filter():
    linked = LINKER.link(
        entity="Kevade", min_year=1900,
        entity_type=EntityType.TITLE
    )
    assert linked.n_linked > 0

    linked = LINKER.link(
        entity="Kevade", min_year=1900, max_year=1950,
        entity_type=EntityType.TITLE
    )
    assert linked.n_linked > 0

    linked = LINKER.link(
        entity="Kevade", max_year=700,
        entity_type=EntityType.TITLE
    )
    assert linked.n_linked == 0


@pytest.mark.order(20)
def test_title_linking_with_author_and_year_filter():
    linked = LINKER.link(
        entity="Kevade", min_year=2000, author="Oskar Luts",
        entity_type=EntityType.TITLE
    )
    assert linked.n_linked == 0

    linked = LINKER.link(
        entity="Kevade", min_year=1900, max_year=1950, author="Erki Nool",
        entity_type=EntityType.TITLE
    )
    assert linked.n_linked == 0

    linked = LINKER.link(
        entity="Kevade", min_year=1900, max_year=1950, author="Oskar Luts",
        entity_type=EntityType.TITLE
    )
    assert linked.n_linked == 1

@pytest.mark.order(21)
def test_per_linking_with_year_filter():
    linked = LINKER.link(entity="Paul Keres")
    assert linked.n_linked == 2

    linked = LINKER.link(entity="Paul Keres", min_year=1950)
    assert linked.n_linked == 1

    linked = LINKER.link(entity="Paul Keres", max_year=1782)
    assert linked.n_linked == 0

    linked = LINKER.link(entity="Paul Keres", min_year=1800, max_year=1950)
    assert linked.n_linked == 1

@pytest.mark.order(22)
def test_keyword_linker():
    keywords = load_json(KEYWORDS_TEST_FILE)

    linked_keywords = KEYWORD_LINKER.link_keywords(
        keywords=keywords, use_viaf=True
    )

    assert linked_keywords

@pytest.mark.order(23)
def test_meta_linker():
    # Test epub, mets_alto and pdf
    # meta-extractor outputs
    meta_dicts = [
        load_json(os.path.join(META_DATA_DIR, fn))
        for fn in os.listdir(META_DATA_DIR)
    ]
    for meta_dict in meta_dicts:
        linked_meta = META_LINKER.link_meta(
            meta=meta_dict, use_viaf=True
        )
        assert linked_meta

@pytest.mark.order(24)
def test_linking_empty_entity_raises_exception():
    # Should NOT return matches
    with pytest.raises(InvalidInputError) as e:
        linked = LINKER.link(entity="")


@pytest.mark.order(25)
def test_linking_nonstring_entity_raises_exception():
    # Should NOT return matches
    with pytest.raises(InvalidInputError) as e:
        linked = LINKER.link(entity=200)

@pytest.mark.order(26)
def test_index_deleting():
    """
    Tests deleting index. We delete the test index now.
    """
    indices = [PER_TEST_INDEX, ORG_TEST_INDEX, LOC_TEST_INDEX, EMS_TEST_INDEX, TITLE_TEST_INDEX]
    for index in indices:
        deleted = ELASTIC.delete_index(index)
        sleep(1)
        assert deleted["acknowledged"] is True
