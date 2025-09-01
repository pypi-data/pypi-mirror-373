import re
def normalize_company_name(name: str) -> str:
    """
    Normalize a company name while preserving the original letter case of
    alphanumeric characters. Returns '' if the name is invalid, a common placeholder,
    or contains disallowed keywords.

    Steps:
      1) Reject if name is None, not a string, or in typical placeholder words (e.g. 'none', 'na', etc.).
      2) If 'freelance', 'consulting', 'startup', etc. appear anywhere (case-insensitive), return ''.
      3) Remove parentheses and their contents.
      4) Remove anything after the first '|'.
      5) Strip out non-alphanumeric characters (but preserve the case of letters that remain).
      6) Trim whitespace. Return the result.
    """

    # 1. Quick checks for invalid inputs
    if not name or not isinstance(name, str):
        return ""

    # Convert to lowercase for checks while keeping original in `name`
    lower_str = name.strip().lower()
    invalid_placeholders = {
        "null", "none", "na", "n.a", "notfound", "error", 
        "notavilable", "notavailable", ""
    }
    if lower_str in invalid_placeholders:
        return ""

    # 2. Disallowed keywords => entire name is made empty
    #    (Case-insensitive substring check)
    disallowed_keywords = [
        "freelance",
        "freelancer",
        "consulting",
        "not working",
        "taking break",
        "startup",
        "stealth startup",
        "sealth startup",
    ]
    for keyword in disallowed_keywords:
        if keyword in lower_str:
            return ""

    # 3. Remove parentheses and their contents
    no_paren = re.sub(r"\(.*?\)", "", name)

    # 4. Remove content after '|'
    #    Splits on the first '|'; keeps only the left side
    no_pipe = no_paren.split("|", 1)[0]

    # 5. Strip out non-alphanumeric chars (preserve letters' original case)
    #    Keep letters (a-z, A-Z), digits, and whitespace
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", no_pipe)

    # 6. Final trim
    final_str = cleaned.strip()

    return final_str
