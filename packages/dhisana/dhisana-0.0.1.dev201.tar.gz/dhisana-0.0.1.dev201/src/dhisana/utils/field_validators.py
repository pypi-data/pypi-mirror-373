import logging
from urllib.parse import urlparse
import urllib.parse
import re

from email_validator import validate_email, EmailNotValidError
from fqdn import FQDN

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------------------
# Utility sets and patterns
# -------------------------------------------------------------------------------------
PLACEHOLDER_EMAILS = {
    "test@example.com",
    "test@test.com",
    "test@domain.com",
    "user@domain.com",
    "user@example.com",
    "user@yourdomain.com",
    "no-reply@example.com",
    "no-reply@domain.com",
    "no-reply@yourdomain.com",
    "admin@domain.com",
    "contact@domain.com",
    "info@domain.com",
    "none@none.com",
    "none@domain.com",
    "noemail@noemail.com",
    "test@fake.com",
    "test@demo.com",
    "test@testing.com",
    "test@local.com",
    "fake@fake.com",
    "email@email.com",
    "asdf@asdf.com",
    "qwerty@qwerty.com",
    "xxx@xxx.com",
    "aaaa@aaaa.com",
    "nomail@nomail.com",
    "dontreply@dontreply.com",
    "asdasd@asdasd.com",
    "abcdefg@abcdefg.com",
    "123@123.com",
    "test123@test.com",
}

DISPOSABLE_DOMAINS = {
    "mailinator.com",
    "10minutemail.com",
    "yopmail.com",
    "guerrillamail.com",
    "tempmail.com",
    "fakemailgenerator.com",
    "mytrashmail.com",
    "getnada.com",
    "throwawaymail.com",
    "sharklasers.com",
    "maildrop.cc",
    "discard.email",
    "temporaryemail.com",
    "trashmail.com",
    "mohmal.com",
    "mail.tm",
    "mailsac.com",
    "mailcatch.com",
    "temp-mail.org",
    "emailondeck.com",
    "mailinabox.email",
    "spambog.com",
    "mintemail.com",
    "spam4.me",
    "spambox.us",
    "edumail.rocks",
    "getairmail.com",
    "mailnesia.com",
    "spoofmail.de",
    "dropmail.me",
    "tempmailaddress.com",
    "33mail.com",
    "incognitomail.com",
    "tempemail.co",
    "trbvm.com",
    "online.ms",
    "20mail.in",
    "wavee.net",
    "ephemeral.email",
    "bccto.me",
    "cuvox.de",
    "dispostable.com",
    "easytrashmail.com",
    "email-fake.org",
    "emailtemporario.com.br",
    "fleckens.hu",
    "lroid.com",
    "mail-temporaire.fr",
    "mailate.com",
    "mailfever.com",
    "mailforspam.com",
    "mailfreeonline.com",
    "mailhazard.com",
    "mailimate.com",
    "mailin8r.com",
    "mailincubator.com",
    "mailmoat.com",
    "mailzilla.org",
    "notsharingmy.info",
    "objectmail.com",
    "proxymail.eu",
    "spamdecoy.net",
    "spamfree24.org",
    "spamgourmet.com",
    "spamify.com",
    "spamomatic.com",
    "spamspot.com",
    "superrito.com",
    "teleworm.us",
    "trash-amil.com",
    "trashmail.me",
    "trashmail.net",
    "wegwerfemail.de",
    "wh4f.org",
    "zmail.ru",
    # Add more as needed
}

SPAMMY_PATTERN = re.compile(r"(.)\1{3,}")  # e.g., 4+ repeated characters

BLOCKED_DOMAINS = {
    # URL shorteners and link forwarders
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "ow.ly",
    "is.gd",
    "cutt.ly",
    "bit.do",
    "buff.ly",
    "rebrand.ly",
    "rebrandly.com",
    "snip.ly",
    "shorte.st",
    "soo.gd",
    "shorturl.at",
    "adf.ly",
    # Bio / profile link aggregators
    "linktr.ee",
    "linktree.com",
    "linkin.bio",
    "campsite.bio",
    "bio.link",
    "bio.site",
    "bio.fm",
    "milkshake.app",
    "lnk.bio",
    "withkoji.com",
    "about.me",
    "carrd.co",
    # Large social platforms (block if used as “organization domain”)
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "youtube.com",
    "yelp.com",
    "twitter.com",
    "tiktok.com",
    "pinterest.com",
    "reddit.com",
    "snapchat.com",
    "tumblr.com",
    "vimeo.com",
    "flickr.com",
    "wechat.com",
    "qq.com",
}


# -------------------------------------------------------------------------------------
# Helper: Check FQDN validity
# -------------------------------------------------------------------------------------
def is_valid_fqdn(domain: str) -> bool:
    """
    Returns True if `domain` is a syntactically valid Fully Qualified Domain Name.
    """
    try:
        if not domain or not isinstance(domain, str):
            return False
        fqdn_obj = FQDN(domain)
        return fqdn_obj.is_valid
    except Exception:
        return False


# -------------------------------------------------------------------------------------
# Domain validation for organizations
# -------------------------------------------------------------------------------------
def validation_organization_domain(domain: str) -> str:
    """
    1. Lowercases/strips the input domain string.
    2. Checks if the domain is in (or a subdomain of) a blocked set.
    3. Checks if the domain is a valid FQDN.
    4. Returns '' if blocked or invalid, otherwise returns the normalized domain.
    """
    if not domain or not isinstance(domain, str):
        return ""

    domain = domain.strip().lower()
    # If domain exactly matches OR is a subdomain of any blocked domain
    if any(domain == blocked or domain.endswith(f".{blocked}") for blocked in BLOCKED_DOMAINS):
        return ""

    # Otherwise, confirm valid FQDN
    return domain if is_valid_fqdn(domain) else ""


# -------------------------------------------------------------------------------------
# Email validation & cleaning
# -------------------------------------------------------------------------------------
def validate_and_clean_email(email: str) -> str:
    """
    Return a validated, normalized email string or '' if invalid/unwanted.
    Checks:
      1. Syntax / deliverability via email_validator
      2. Against placeholder/fake emails
      3. Against disposable email domains
      4. Spammy repeated character patterns
    """
    if not email or not isinstance(email, str):
        return ""

    try:
        v = validate_email(email, check_deliverability=True)
        normalized_email = v["email"]  # canonical form
        local_part, domain_part = normalized_email.rsplit("@", 1)

        # 1. Check entire address in placeholder set
        if normalized_email.lower() in PLACEHOLDER_EMAILS:
            return ""

        # 2. Check domain in disposable set
        if domain_part.lower() in DISPOSABLE_DOMAINS:
            return ""

        # 3. Check repeated/spammy pattern
        if SPAMMY_PATTERN.search(normalized_email):
            return ""

        return normalized_email
    except EmailNotValidError:
        return ""


# -------------------------------------------------------------------------------------
# Website URL validation
# -------------------------------------------------------------------------------------
def validate_website_url(raw_url: str) -> str:
    """
    Validate a website URL (must be http/https or a raw domain).
    If no scheme is provided but the input is a valid FQDN-like string
    (e.g. www.google.com), automatically prefix https://.
    Return the normalized URL without query/fragment, or '' if invalid.
    """
    if not raw_url or not isinstance(raw_url, str):
        return ""

    # Clean input
    raw_url = raw_url.strip().lower()
    
    try:
        parsed = urllib.parse.urlparse(raw_url)
        
        # If there's no scheme, try prefixing https://
        if not parsed.scheme:
            # Example: "www.google.com" => "https://www.google.com"
            potential_url = f"https://{raw_url}"
            test_parsed = urllib.parse.urlparse(potential_url)
            
            # If that yields a valid scheme and netloc, use it
            if test_parsed.scheme in ["http", "https"] and test_parsed.netloc:
                parsed = test_parsed
            else:
                return ""
        
        # Check we now have a valid scheme and netloc
        if parsed.scheme not in ["http", "https"] or not parsed.netloc:
            return ""
        
        # Normalize by removing query and fragment parts
        normalized = urllib.parse.urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path, "", "", "")
        )
        return normalized
    
    except Exception:
        return ""


# -------------------------------------------------------------------------------------
# LinkedIn URL Normalizers
# -------------------------------------------------------------------------------------
def normalize_linkedin_url(raw_url: str) -> str:
    """
    Normalize a personal LinkedIn URL to the form: https://www.linkedin.com/in/<something>
    Must contain '/in/'. Otherwise, return ''.
    """
    if not raw_url or not isinstance(raw_url, str):
        return ""

    try:
        raw_url = raw_url.strip()
        parsed = urlparse(raw_url)

        if not parsed.scheme or not parsed.netloc:
            return ""

        if "linkedin.com" not in parsed.netloc.lower():
            return ""

        url = raw_url.rstrip("/")
        parsed = urlparse(url)

        if "/in/" not in parsed.path.lower():
            return ""

        path = parsed.path.lstrip("/")
        return f"https://www.linkedin.com/{path}".rstrip("/")
    except Exception:
        return ""


def normalize_linkedin_company_url(raw_url: str) -> str:
    """
    Normalize a company LinkedIn URL to the form: https://www.linkedin.com/company/<something>
    Must contain '/company/'. Otherwise, return ''.
    """
    if not raw_url or not isinstance(raw_url, str):
        return ""

    try:
        raw_url = raw_url.strip()
        parsed = urlparse(raw_url)

        if not parsed.scheme or not parsed.netloc:
            return ""

        if "linkedin.com" not in parsed.netloc.lower():
            return ""

        url = raw_url.rstrip("/")
        parsed = urlparse(url)

        if "/company/" not in parsed.path.lower():
            return ""

        path = parsed.path.lstrip("/")
        return f"https://www.linkedin.com/{path}".rstrip("/")
    except Exception:
        return ""


def normalize_linkedin_company_salesnav_url(raw_url: str) -> str:
    """
    Normalize a company Sales Navigator URL to: https://www.linkedin.com/sales/company/<something>
    Must contain '/sales/company/'. Otherwise, return ''.
    """
    if not raw_url or not isinstance(raw_url, str):
        return ""

    try:
        raw_url = raw_url.strip()
        parsed = urlparse(raw_url)

        if not parsed.scheme or not parsed.netloc:
            return ""

        if "linkedin.com" not in parsed.netloc.lower():
            return ""

        url = raw_url.rstrip("/")
        parsed = urlparse(url)

        if "/sales/company/" not in parsed.path.lower():
            return ""

        path = parsed.path.lstrip("/")
        return f"https://www.linkedin.com/{path}".rstrip("/")
    except Exception:
        return ""


def normalize_salesnav_url(raw_url: str) -> str:
    """
    Normalize a Sales Navigator URL to: https://www.linkedin.com/sales/lead/<something>
    Must contain '/sales/lead/'. Otherwise, return ''.
    Strips anything after a comma in the URL.
    """
    if not raw_url or not isinstance(raw_url, str):
        return ""

    try:
        raw_url = raw_url.strip()
        parsed_initial = urlparse(raw_url)

        if not parsed_initial.scheme or not parsed_initial.netloc:
            return ""

        if "linkedin.com" not in parsed_initial.netloc.lower():
            return ""

        # Remove trailing slash
        url = raw_url.rstrip("/")

        # Strip anything after the first comma
        comma_idx = url.find(",")
        if comma_idx != -1:
            url = url[:comma_idx]

        parsed = urlparse(url)

        if "/sales/lead/" not in parsed.path.lower():
            return ""

        path = parsed.path.lstrip("/")
        return f"https://www.linkedin.com/{path}".rstrip("/")
    except Exception:
        return ""
