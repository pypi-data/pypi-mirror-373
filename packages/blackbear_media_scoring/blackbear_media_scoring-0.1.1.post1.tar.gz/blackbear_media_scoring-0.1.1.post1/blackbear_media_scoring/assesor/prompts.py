class AssessorPrompts:
    base_template = """Classify the text into 3 categories: `pornografi`, `sara`,
and `politics`.

SARA means ethnicity, religion, race, and inter-group relations.
Pornografi means content that is sexually explicit/porn.
Politics means content that is political in nature
that related to Indonesia politics only.

For each category, you must do the following things:
    - Find keywords (max 10) and phrases (max 10) that are relevant to the category.
    - Provide a short reason for the score.
    - Should be scored from 0 to 10 based on the relevancy of the content with
      the category (0 means not relevant at all, 10 means very relevant).

The output MUST be a JSON array of object with the following structure:
```json
[
    {{
        "category": "pornografi",
        "score": int,
        "reason": str,
        "keywords": List[str],
        "phrases": List[str]
    }},
    {{
        "category": "sara",
        "score": int,
        "reason": str,
        "keywords": List[str],
        "phrases": List[str]
    }},
    {{
        "category": "politics",
        "score": int,
        "reason": str,
        "keywords": List[str],
        "phrases": List[str]
    }}
]
```

Text:
{text}
---
Classification:

"""
