# GEDCOM-X Python Toolkit (gedcom-x beta 0.5.5)

A lightweight, class-based Python implementation of the [GEDCOM-X data model](https://github.com/FamilySearch/gedcomx).  

## ⚠️ Project Status

This project is currently in **beta**.  
While the core GEDCOM-X classes and serialization are functional, some features may not be fully implemented or may not behave exactly as expected.  

- Certain GEDCOM 7 tags are not yet mapped  
- Some classes may be missing methods or fields  
- Error handling and validation are still evolving  
- Backward compatibility is **not guaranteed** until the first stable release  

### ✅ What You Can Do
- Create and manipulate GEDCOM-X objects in Python  
- Serialize and deserialize data to/from JSON  
- Experimentally convert GEDCOM 5x & 7 files into GEDCOM-X JSON  
- Extend the classes to handle new GEDCOM tags or custom attributes  
- Use the library as a foundation for genealogy-related tooling or RAG pipelines  

### ❌ What You Can’t Do (Yet)
- Rely on complete coverage of all GEDCOM 7 tags  
- Expect perfect compliance with the GEDCOM-X specification  
- Assume strong validation or error recovery on malformed input  
- Use it as a drop-in replacement for production genealogy software  
- Write GEDCOM-X to GEDCOM 5x / 7
- Create Graphs from Genealogies

Contributors and testers are welcome — feedback will help stabilize the library!

---

This library aims to provide:

- Python classes for every GEDCOM-X type (Person, Fact, Source, etc.)
- Extensibility, with current GEDCOM RS etc, extension built in
- Serialization and Deserialization to/from GEDCOM-X JSON
- Utilities to convert GEDCOM 5x & 7 GEDCOM Files into GEDCOM-X and back
- Type-safe field definitions and extensibility hooks for future tags

---

## Features

- **Complete GEDCOM-X Class Coverage**  
  Each GEDCOM-X type is represented as a Python class with fields and types.

- **Serialization / Deserialization**  
  Every class can serialize to JSON and reconstruct from JSON via `_as_dict_()` and `_from_json()` methods.

- **Type Checking & Enum Validation**  
  Uses Python type hints and enums to ensure correct values (e.g. FactType, EventType, ConfidenceLevel).

- **Composable / Nestable Classes**  
  Nested objects (e.g. Person → Name → NameForm → TextValue) are constructed and validated recursively.

- **GEDCOM 7 → GEDCOM-X Conversion**  
  Experimental parser to read GEDCOM 7 files and convert them into structured GEDCOM-X JSON.

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/gedcom-x.git
cd gedcom-x
pip install -r requirements.txt
```
or
```
pip install gedcom-x
```
---

## Examples

<details>

<summary>Create a Person Gedcom-X Type</summary>

```python
import json
from gedcomx import Person, Name, NameForm, TextValue

person = Person(
    id="P-123",
    names=[Name(
        nameForms=[NameForm(
            fullText=TextValue(value="John Doe")
        )]
    )]
)

print(json.dumps(person._as_dict_,indent=4))
```
result
```text
{
    "id": "P-123",
    "lang": "en",
    "private": false,
    "living": false,
    "gender": {
        "lang": "en",
        "type": "http://gedcomx.org/Unknown"
    },
    "names": [
        {
            "lang": "en",
            "nameForms": [
                {
                    "lang": "en",
                    "fullText": {
                        "lang": "en",
                        "value": "John Doe"
                    }
                }
            ]
        }
    ]
}

</details>