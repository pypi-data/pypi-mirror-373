# A set of domains that should be excluded because they are social or bio/link aggregator services.
import tldextract


EXCLUDED_LINK_DOMAINS = [
    "beacon.ai",
    "tap.bio",
    "campsite.bio",
    "shor.by",
    "milkshake.app",
    "lnk.bio",
    "carrd.co",
    "bio.fm",
    "withkoji.com",
    "flowcode.com",
    "biolinky.co",
    "contactinbio.com",
    "linktr.ee",
    "linkedin.com",
    "facebook.com",
    "youtube.com",
]

def get_domain_from_website(website: str) -> str:
    """
    Extracts the domain from a given website URL using tldextract.
    Returns an empty string if no website is provided.

    :param website: The full URL from which to extract the domain.
    :return: Extracted domain in the form 'example.com', or '' if none.
    """
    if not website:
        return ""
    extracted = tldextract.extract(website)
    return f"{extracted.domain}.{extracted.suffix}"


def is_excluded_domain(domain: str) -> bool:
    """
    Checks if the domain is in the EXCLUDED_LINK_DOMAINS list.

    :param domain: The domain (without protocol) to be checked.
    :return: True if the domain is excluded, False otherwise.
    """
    return domain.lower() in EXCLUDED_LINK_DOMAINS