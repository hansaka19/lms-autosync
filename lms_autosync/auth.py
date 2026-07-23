from . import config

# Moodle login page එකේ SSO button එක හොයන්න try කරන selectors
# (LMS UI updates වලදී order එකෙන් try වෙනවා)
SSO_BUTTON_SELECTORS = [
    "a.login-identityprovider-btn",          # පරණ Moodle theme එක
    "a[href*='auth/oauth2/login.php']",      # අලුත් OAuth2 flow එක
    "a:has-text('IAM')",                     # "IAM OUSL LMS USER" text button
]

# Keycloak error message selectors (පරණ + අලුත් 'ousl' theme)
KC_ERROR_SELECTORS = (
    "#input-error, .kc-feedback-text, .alert-error, "
    ".ousl-error, .ousl-alert, [class*='ousl'][class*='error']"
)


_BLOCKED_RESOURCE_TYPES = {"image", "media", "font", "stylesheet"}


def _block_heavy_resources(context):
    """Scraper එකට ඕන HTML/DOM විතරයි. Images, fonts, CSS, video වගේ බර
    resources block කරලා page loads ගොඩක් වේගවත් කරනවා — විශේෂයෙන් slow
    (0.1 CPU) instance එකක. Scripts/XHR/fetch block කරන්නේ නෑ (course cards
    AJAX වලින් load වෙන නිසා)."""
    def _route(route):
        if route.request.resource_type in _BLOCKED_RESOURCE_TYPES:
            try:
                route.abort()
                return
            except Exception:
                pass
        route.continue_()
    context.route("**/*", _route)


def login(playwright, username=None, password=None):
    browser = playwright.chromium.launch(headless=config.HEADLESS)
    context = browser.new_context()
    _block_heavy_resources(context)
    page = context.new_page()

    # Credentials parameter එකෙන් ආවේ නැත්නම් local keyring vault එකෙන් ගන්නවා
    if username is None or password is None:
        from .vault import get_credentials
        username, password = get_credentials()

    def fail(prefix, detail):
        current_url = page.url
        try:
            page.screenshot(path="debug_login_page.png")
        except Exception:
            pass
        browser.close()
        raise RuntimeError(f"{prefix}: {detail} [page: {current_url}]")

    # 1. Native Moodle login page එකට යනවා
    page.goto(config.LMS_BASE_URL + config.LMS_LOGIN_PATH,
              wait_until="domcontentloaded", timeout=60000)

    # 2. Keycloak එකට යනවා — කෙලින්ම redirect උනේ නැත්නම් SSO button එක click කරනවා
    if "iam.ou.ac.lk" not in page.url:
        clicked = False
        for sel in SSO_BUTTON_SELECTORS:
            try:
                btn = page.locator(sel).first
                btn.wait_for(state="visible", timeout=5000)
                btn.click()
                clicked = True
                break
            except Exception:
                continue
        if not clicked:
            fail("SSO_BUTTON_NOT_FOUND",
                 "Moodle login page එකේ SSO/IAM button එක හම්බුනේ නෑ — "
                 "LMS UI එක වෙනස් වෙලා ඇති, debug_login_page.png බලන්න")

    # 3. Keycloak login form එක එනකම් බලනවා — URL එක check කරන්නේ නෑ,
    #    form එකම (#username) එනකම් බලනවා (page load stalls වලට resistant)
    #    #username / #password / #kc-login — පරණ + අලුත් UI දෙකේම එකයි
    try:
        page.wait_for_selector("#username", state="visible", timeout=30000)
    except Exception:
        fail("KEYCLOAK_FORM_NOT_FOUND",
             "Login form එක (username field) load උනේ නෑ")

    page.fill("#username", username)
    page.fill("#password", password)

    try:
        page.wait_for_selector("#kc-login", state="visible", timeout=15000)
        page.click("#kc-login")
    except Exception:
        fail("LOGIN_BUTTON_FAILED", "Sign in button එක click කරන්න බැරි උනා")

    # 4. Keycloak එකෙන් ආපහු oulms.ou.ac.lk එකට redirect වෙනකම් බලනවා
    #    (glob pattern වෙනුවට predicate function — load stalls වලට resistant)
    try:
        page.wait_for_url(lambda url: "oulms.ou.ac.lk" in url,
                          wait_until="domcontentloaded", timeout=45000)
    except Exception:
        # තාම Keycloak එකේ නම් — error message එකක් පෙනෙනවාද බලනවා
        err_text = ""
        try:
            err_loc = page.locator(KC_ERROR_SELECTORS).first
            if err_loc.count() > 0:
                err_text = (err_loc.inner_text() or "").strip()
        except Exception:
            pass
        if err_text:
            fail("LOGIN_INVALID", err_text)
        fail("LOGIN_TIMEOUT",
             "redirect back to LMS never happened (debug_login_page.png බලන්න)")

    return browser, context, page
