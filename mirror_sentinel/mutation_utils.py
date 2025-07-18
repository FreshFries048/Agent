import random
import re

# Predefined synonyms for key words used in outreach templates
SYNONYMS = {
    "noticed": ["observed", "seen"],
    "interesting": ["noteworthy", "compelling"],
    "work": ["efforts", "projects"],
    "industry": ["sector", "domain"],
    "share": ["provide", "deliver"],
    "resources": ["materials", "guides"],
    "insights": ["information", "tips"],
    "secure": ["protect", "safeguard"],
    "data": ["information", "records"],
    "scaling": ["growing", "expanding"],
    "marketing": ["promotion", "outreach"],
    "customers": ["clients", "buyers"]
}

def mutate_phrase(phrase: str, synonyms: dict = SYNONYMS) -> str:
    """
    Mutate a phrase by replacing words with random synonyms defined in SYNONYMS.
    Placeholders wrapped in curly braces (e.g., {name}) are left unchanged.
    Punctuation attached to words is preserved.
    """
    tokens = []
    for word in phrase.split():
        # Skip placeholders like {name} or {company}
        if word.startswith("{") and word.endswith("}"):
            tokens.append(word)
            continue
        # Separate punctuation from the core word
        match = re.match(r"(^\\W*)(\\w+)(\\W*$)", word)
        if match:
            prefix, core, suffix = match.groups()
        else:
            prefix, core, suffix = "", word, ""
        key = core.lower()
        if key in synonyms:
            options = synonyms[key]
            replacement = random.choice(options)
            # Preserve case
            if core[0].isupper():
                replacement = replacement.capitalize()
            core = replacement
        tokens.append(prefix + core + suffix)
    return " ".join(tokens)

def mutate_template(template: str, synonyms: dict = SYNONYMS) -> str:
    """
    Mutate an entire multi-line template by mutating each line individually.
    """
    mutated_lines = []
    for line in template.split("\n"):
        mutated_lines.append(mutate_phrase(line, synonyms))
    return "\n".join(mutated_lines)
