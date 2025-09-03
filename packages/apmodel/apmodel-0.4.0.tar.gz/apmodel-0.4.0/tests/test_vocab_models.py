import pytest
from apmodel.loader import load
from apmodel.vocab import Article, Person, Event, Note, Profile
from apmodel.core import Object

# --- Test Data ---

ARTICLE_JSON = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "Article",
    "name": "What a Crazy Day!",
    "content": "<div>... you will not believe ...</div>",
    "attributedTo": "http://example.org/martin"
}

PERSON_JSON = {
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Person",
  "id": "http://example.org/alice",
  "name": "Alice",
  "preferredUsername": "alice",
  "summary": "A test user"
}

# A Profile is a specialized Object, often used with `describes`
PROFILE_JSON = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "Profile",
    "describes": {
        "type": "Person",
        "name": "Sally"
    },
    "summary": "Sally's profile"
}

# --- Tests ---

def test_load_article():
    """Tests loading an Article object."""
    article = load(ARTICLE_JSON)
    
    assert isinstance(article, Article)
    assert isinstance(article, Object) # Verify base class
    assert article.type == "Article"
    assert article.name == "What a Crazy Day!"
    assert article.content == "<div>... you will not believe ...</div>"
    assert article.attributedTo == "http://example.org/martin"

def test_load_person():
    """Tests loading a Person object."""
    person = load(PERSON_JSON)

    assert isinstance(person, Person)
    assert isinstance(person, Object) # Verify base class
    assert person.type == "Person"
    assert person.id == "http://example.org/alice"
    assert person.name == "Alice"
    # Check a property specific to Actor types like Person
    assert person.preferredUsername == "alice"
    assert person.summary == "A test user"

def test_load_profile():
    """Tests loading a Profile object with a nested object."""
    profile = load(PROFILE_JSON)

    assert isinstance(profile, Profile)
    assert profile.type == "Profile"
    assert profile.summary == "Sally's profile"
    
    # Test the nested 'describes' object
    assert isinstance(profile.describes, Person)
    assert profile.describes.name == "Sally"
