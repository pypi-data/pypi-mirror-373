import pytest
from apmodel.loader import load
from apmodel.vocab.activity import Create
from apmodel.vocab import Note
from apmodel import LDContext

def test_nested_object_context_is_merged():
    """
    Tests that a nested object's @context is merged into the parent's
    @context during serialization, and not included in the nested object itself.
    """
    # 1. Define two different contexts
    activity_context = LDContext(["https://www.w3.org/ns/activitystreams"])
    
    object_specific_context_url = "https://example.com/custom/terms#"
    object_context_data = ["https://www.w3.org/ns/activitystreams", object_specific_context_url]
    object_context = LDContext(object_context_data)

    # 2. Create an activity and a nested object with their respective contexts
    note = Note(
        _context=object_context,
        id="http://example.org/note/1",
        content="This is a note with a custom context"
    )

    create_activity = Create(
        _context=activity_context,
        id="http://example.org/activity/1",
        actor="http://example.org/actor/1",
        object=note
    )

    # 3. Serialize the top-level activity to JSON
    json_output = create_activity.to_json()

    # 4. Assertions
    
    # a) Check that the top-level @context exists and is correctly merged.
    # The custom context URL should have been merged with the base one.
    assert "@context" in json_output
    expected_context = ["https://www.w3.org/ns/activitystreams", object_specific_context_url]
    # The actual order might vary, so we check for content equivalence
    assert isinstance(json_output["@context"], list)
    assert len(json_output["@context"]) == len(expected_context)
    assert all(item in json_output["@context"] for item in expected_context)

    # b) Check that the nested object *does not* have its own @context key.
    assert "object" in json_output
    nested_object_json = json_output["object"]
    assert isinstance(nested_object_json, dict)
    assert "@context" not in nested_object_json

    # c) Verify other properties of the nested object are still present.
    assert nested_object_json.get("id") == "http://example.org/note/1"
    assert nested_object_json.get("type") == "Note"
