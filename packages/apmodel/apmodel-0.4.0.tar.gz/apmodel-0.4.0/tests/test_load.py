import json
from apmodel.loader import load
from apmodel.vocab.activity.add import Add
from apmodel.vocab.article import Article
from apmodel.vocab.actor import Person
from apmodel.core.link import Link
from apmodel.core.collection import Collection
from apmodel.vocab.note import Note

def test_load_complex_add_activity():
    data = '''{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Martin added an article to his blog",
        "type": "Add",
        "published": "2015-02-10T15:04:55Z",
        "actor": {
            "type": "Person",
            "id": "http://www.test.example/martin",
            "name": "Martin Smith",
            "url": "http://example.org/martin",
            "image": {
                "type": "Link",
                "href": "http://example.org/martin/profile.jpg",
                "mediaType": "image/jpeg"
            }
        },
        "object": {
            "type": "Article",
            "name": "My First Article",
            "content": "<p>This is the content of my first article.</p>",
            "attributedTo": "http://www.test.example/martin"
        },
        "target": {
            "type": "Collection",
            "name": "Martin's Blog",
            "url": "http://example.org/martin/blog"
        }
    }'''
    loaded = load(json.loads(data))
    assert isinstance(loaded, Add)
    assert loaded.summary == "Martin added an article to his blog"
    assert isinstance(loaded.actor, Person)
    assert loaded.actor.name == "Martin Smith"
    assert isinstance(loaded.actor.image, Link)
    assert loaded.actor.image.href == "http://example.org/martin/profile.jpg"
    assert isinstance(loaded.object, Article)
    assert loaded.object.name == "My First Article"
    assert isinstance(loaded.target, Collection)
    assert loaded.target.name == "Martin's Blog"

def test_load_unknown_type():
    data = '''{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "UnknownType",
        "summary": "This is an unknown type"
    }'''
    loaded = load(json.loads(data))
    assert isinstance(loaded, dict)
    assert loaded["summary"] == "This is an unknown type"

def test_load_extra_fields():
    data = '''{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Note",
        "content": "This is a note",
        "extraField": "This is an extra field"
    }'''
    loaded = load(json.loads(data))
    assert isinstance(loaded, Note)
    assert hasattr(loaded, "_extra")
    assert loaded._extra["extraField"] == "This is an extra field"