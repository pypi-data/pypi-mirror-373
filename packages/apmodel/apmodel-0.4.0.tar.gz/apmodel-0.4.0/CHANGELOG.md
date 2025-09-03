## [unreleased]

### 🚀 Features

- Implement core models
- Add test
- Nodeinfo parser
- Extra models
- Context parser
- Hashtag type
- Automatically add the URL to the context based on the value
- LCContext test
- Test cid
- Enforce keyword-only arguments for NodeinfoServices
- Add support for extra types
- Ruff rule
- Autochange version with vcs

### 🐛 Bug Fixes

- Setup uv before setup python
- Incorrect Link values
- Type hint
- Fix the code error causing the TypeError and use `ctx.full_context` instead of `ctx.json`.
- Use rmdir in windows
- Changes from gemini code assist's suggestions
- Check if the expected keys are a subset of the data's keys
- *(actor)* Resolve side effects and context handling in Actor.to_json
- *(link)* Fix context aggregation in Link.to_json
- *(question)* Prevent side effects in Question.to_json
- *(tombstone)* Prevent side effects in Tombstone.to_json
- Use `ctx.full_context` instead of `ctx.json`
- Initialize aggregated_context as a new LDContext instance, copied from self._context
- Use PrivateFormat.PKCS1 instead of PrivateFormat.Raw in rsa-priv
- *(cid)* Handle 'Z' timezone in DataIntegrityProof
- Fixes for violation of the Liskov Substitution Principle
- Use is instead of isinstance
- Use InvalidField instead of Exception
- *(cid)* Import InvalidField from exceptions.py
- *(cid)* Remove type: ignore
- Replace +00:00 with Z
- Use fromisoformat
- Include timezone information
- Use InvalidField instead of Exception
- Use InvalidField instead of Exception
- Use InvalidField instead of Exception
- Add Z in text end
- *(ci)* Set checkout branch
- *(ci)* Run in release branch

### 🚜 Refactor

- *(loader)* Refactor Nodeinfo detection logic
- Centralize JSON serialization logic
- *(cid)* Use central serializer for CID models
- Remove unused imports
- Remove whitespace in __init__.py
- Remove whitespace in __init__.py

### ⚙️ Miscellaneous Tasks

- Use context parser
- Context parser
- Context parser
- Styleguide
- Instructions for code review (likely, gemini code assist).
- Edit style guide
- Ignore git_commit_msg_tmp.txt
- Add classifiers
- Add dataclass decorator in ActivityPubModel
- Add styleguide
- Changelog auto generate
- Update changelog [skip ci]
- Update changelog [skip ci]
## [0.3.1](https://github.com/fedi-libs/apmodel/releases/tag/0.3.1) - 2025-03-16

### 🐛 Bug Fixes

- Correct version to write to
## [0.3.0](https://github.com/fedi-libs/apmodel/releases/tag/0.3.0) - 2025-03-16

### 🚀 Features

- Docstring
- `Activity.accept()` can now generate an Accept activity for the activity and `Activity.reject()` can generate a Reject activity for the activity
- Auto publish
- Use scm for version

### 🐛 Bug Fixes

- Typehint
- Note is not included in the default import
- Incorrect version

### ⚙️ Miscellaneous Tasks

- Update Dependencies
- Add social link
## [0.2.4](https://github.com/fedi-libs/apmodel/releases/tag/0.2.4) - 2025-02-27

### 🚀 Features

- 0.1.2
- Actor-related objects should inherit from Actor
- Multikey support
- 0.2.0
- Add fep-8b32 support
- 0.2.1
- 0.2.2

### 🐛 Bug Fixes

- Import __init__
- Add Organization, Application, Service, Group
- Fix missing arguments
- 2
- Many fixes

### 💼 Other

- Attachment is list

### ⚙️ Miscellaneous Tasks

- Initial commit
- Format
