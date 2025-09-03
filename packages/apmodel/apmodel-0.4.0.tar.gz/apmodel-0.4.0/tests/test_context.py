import pytest
from apmodel import LDContext

# Sample data for tests
CTX_URL_1 = "https://www.w3.org/ns/activitystreams"
CTX_URL_2 = "https://w3id.org/security/v1"
CTX_DEF_1 = {"sensitive": "as:sensitive", "Hashtag": "as:Hashtag"}
CTX_DEF_2 = {"quoteUrl": "as:quoteUrl", "sensitive": "as:overwritten"}

INITIAL_CONTEXT = [CTX_URL_1, CTX_DEF_1]

def test_initialization_and_properties():
    """Tests basic initialization and property correctness."""
    ctx = LDContext(INITIAL_CONTEXT)
    
    assert ctx.urls == [CTX_URL_1]
    assert ctx.json == CTX_DEF_1
    assert ctx.full_context == [CTX_URL_1, CTX_DEF_1]

def test_add_and_deduplication():
    """Tests adding items, including duplicates."""
    ctx = LDContext(INITIAL_CONTEXT)
    
    # Add a duplicate URL (should be ignored)
    ctx.add(CTX_URL_1)
    assert ctx.urls.count(CTX_URL_1) == 1
    
    # Add a new URL
    ctx.add(CTX_URL_2)
    assert ctx.urls == [CTX_URL_1, CTX_URL_2]
    
    # Add a dictionary with a new key and an overwriting key
    ctx.add(CTX_DEF_2)
    expected_json = {
        "sensitive": "as:overwritten", # Overwritten
        "Hashtag": "as:Hashtag",       # Original
        "quoteUrl": "as:quoteUrl"      # New
    }
    assert ctx.json == expected_json
    assert ctx.full_context == [CTX_URL_1, CTX_URL_2, expected_json]

def test_remove_items():
    """Tests removing items from the context."""
    ctx = LDContext(INITIAL_CONTEXT)
    ctx.add(CTX_URL_2)
    
    # Remove a URL
    ctx.remove(CTX_URL_1)
    assert CTX_URL_1 not in ctx.urls
    assert ctx.full_context == [CTX_URL_2, CTX_DEF_1]
    
    # Remove a definition by key
    ctx.remove({"sensitive": "as:sensitive"})
    assert "sensitive" not in ctx.json
    assert ctx.json == {"Hashtag": "as:Hashtag"}

def test_list_like_behavior():
    """Tests the list-like interface (len, iter, getitem)."""
    ctx = LDContext(INITIAL_CONTEXT)
    assert len(ctx) == 2
    assert ctx[0] == CTX_URL_1
    assert ctx[1] == CTX_DEF_1
    assert [item for item in ctx] == [CTX_URL_1, CTX_DEF_1]

def test_merge_parsers():
    """Tests merging two LDContext instances with __add__."""
    ctx1 = LDContext(INITIAL_CONTEXT)
    
    other_context_data = [CTX_URL_2, CTX_DEF_2]
    ctx2 = LDContext(other_context_data)
    
    merged_ctx = ctx1 + ctx2
    
    # Check merged URLs (deduplicated)
    assert merged_ctx.urls == [CTX_URL_1, CTX_URL_2]
    
    # Check merged definitions (key from ctx2 overwrites ctx1)
    expected_json = {
        "sensitive": "as:overwritten",
        "Hashtag": "as:Hashtag",
        "quoteUrl": "as:quoteUrl"
    }
    assert merged_ctx.json == expected_json
    
    # Ensure original parsers are not modified
    assert ctx1.full_context == INITIAL_CONTEXT
    assert ctx2.full_context == other_context_data
