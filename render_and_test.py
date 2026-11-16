#!/usr/bin/env python3
"""
Automated Playwright Test & Screenshot Capture Script
for Make.fun Bring the Humans Entry (bring-humans-second-design-private-20261115)

Tests:
- Desktop 1280px & Mobile 375px rendering
- Zero horizontal overflow
- Zero console/page errors
- Bilingual EN/ID language switcher and DOM updates
- Referral link and code validation
- Social composer URL encoding
- Clipboard actions and toast alerts
- Keyboard focus and accessibility controls
- Generates root ad.png with scale factor 2
"""

import os
import sys
import json
import urllib.parse
from playwright.sync_api import sync_playwright

REPO_DIR = "/workspace/bring-humans-second-design-private-20261115"
HTML_PATH = f"file://{REPO_DIR}/index.html"
OUT_TEST_DIR = "/workspace/bring-humans-second-antigravity-20261116"
ROOT_AD_PNG = f"{REPO_DIR}/ad.png"
CHROME_PATH = "/usr/bin/chromium"

os.makedirs(OUT_TEST_DIR, exist_ok=True)

test_results = {
    "console_errors": [],
    "page_errors": [],
    "checks_passed": 0,
    "checks_failed": 0
}

def log_check(name, passed, details=""):
    status = "PASS" if passed else "FAIL"
    if passed:
        test_results["checks_passed"] += 1
    else:
        test_results["checks_failed"] += 1
    print(f"[{status}] {name} - {details}")

def run_tests():
    print("Starting Playwright automation test suite using", CHROME_PATH)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        
        # -------------------------------------------------------------
        # 1. Desktop 1280px Tests
        # -------------------------------------------------------------
        print("\n--- 1. Testing Desktop 1280x800 ---")
        context_desktop = browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=2,
            color_scheme="light"
        )
        page_d = context_desktop.new_page()

        page_d.on("console", lambda msg: test_results["console_errors"].append(msg.text) if msg.type == "error" else None)
        page_d.on("pageerror", lambda err: test_results["page_errors"].append(str(err)))

        page_d.goto(HTML_PATH)
        page_d.wait_for_load_state("networkidle")

        # Zero console/page errors
        log_check("No console errors on load", len(test_results["console_errors"]) == 0, f"Errors: {test_results['console_errors']}")
        log_check("No page errors on load", len(test_results["page_errors"]) == 0, f"Page errors: {test_results['page_errors']}")

        # Horizontal overflow check
        scroll_w = page_d.evaluate("document.documentElement.scrollWidth")
        client_w = page_d.evaluate("document.documentElement.clientWidth")
        log_check("Desktop 1280px overflow check", scroll_w <= client_w, f"scrollWidth={scroll_w}, clientWidth={client_w}")

        # Referral code & URLs
        code_text = page_d.locator("#referralCode").inner_text().strip()
        log_check("Referral code is 75pngn23", code_text == "75pngn23", f"Found: '{code_text}'")

        direct_link_href = page_d.locator("#directReferralLink").get_attribute("href")
        log_check("Direct link href is exact", direct_link_href == "https://make.fun/r/75pngn23", f"Found: {direct_link_href}")

        join_btn_href = page_d.locator("#joinBtn").get_attribute("href")
        log_check("Join CTA href is exact", join_btn_href == "https://make.fun/r/75pngn23", f"Found: {join_btn_href}")

        # Social composer encoding checks
        wa_href = page_d.locator("#waShareLink").get_attribute("href")
        log_check("WhatsApp share link valid", "wa.me" in wa_href and "75pngn23" in wa_href, f"URL: {wa_href[:65]}...")

        tg_href = page_d.locator("#tgShareLink").get_attribute("href")
        log_check("Telegram share link valid", "t.me/share/url" in tg_href and "75pngn23" in tg_href, f"URL: {tg_href[:65]}...")

        x_href = page_d.locator("#xShareLink").get_attribute("href")
        log_check("X share link valid", "twitter.com/intent/tweet" in x_href and "75pngn23" in x_href, f"URL: {x_href[:65]}...")

        # Keyboard accessibility: test skip link focus
        page_d.keyboard.press("Tab")
        active_tag = page_d.evaluate("document.activeElement.tagName")
        active_class = page_d.evaluate("document.activeElement.className")
        log_check("Keyboard skip link focused on initial Tab", "skip-link" in active_class, f"tag={active_tag}, class={active_class}")

        # Test EN -> ID language toggle
        page_d.locator("#langIdBtn").click()
        page_d.wait_for_timeout(200)

        lang_id = page_d.evaluate("document.documentElement.lang")
        headline_id = page_d.locator("#pageHeadline").inner_text()
        cta_id = page_d.locator("#joinBtn").inner_text()
        log_check("Language attribute switched to ID", lang_id == "id", f"lang={lang_id}")
        log_check("Headline translated to Indonesian", "agen AI" in headline_id and "sayembara" in headline_id.lower(), f"Headline: {headline_id}")
        log_check("Join CTA translated to Indonesian", "gabung" in cta_id.lower(), f"CTA: {cta_id}")

        # Save ID screenshot to outside test folder
        page_d.screenshot(path=f"{OUT_TEST_DIR}/desktop_1280_id.png")
        print(f"Saved Indonesian screenshot: {OUT_TEST_DIR}/desktop_1280_id.png")

        # Test ID -> EN language toggle back
        page_d.locator("#langEnBtn").click()
        page_d.wait_for_timeout(200)
        lang_en = page_d.evaluate("document.documentElement.lang")
        headline_en = page_d.locator("#pageHeadline").inner_text()
        log_check("Language attribute switched back to EN", lang_en == "en", f"lang={lang_en}")
        log_check("Headline restored to English", "Build software" in headline_en, f"Headline: {headline_en}")

        # Test copy buttons & toast feedback
        page_d.locator("#copyCodeBtn").click()
        page_d.wait_for_timeout(250)
        toast_show = page_d.locator("#toastNotice").evaluate("el => el.classList.contains('show')")
        toast_msg = page_d.locator("#toastMessage").inner_text()
        log_check("Copy Code triggers visible toast", toast_show, f"Toast: '{toast_msg}'")

        page_d.locator("#copyLinkBtn").click()
        page_d.wait_for_timeout(250)
        toast_msg_link = page_d.locator("#toastMessage").inner_text()
        log_check("Copy Link updates toast message", "link" in toast_msg_link.lower() or "tautan" in toast_msg_link.lower(), f"Toast: '{toast_msg_link}'")

        # Save EN screenshot to outside test folder
        page_d.screenshot(path=f"{OUT_TEST_DIR}/desktop_1280_en.png")
        print(f"Saved English screenshot: {OUT_TEST_DIR}/desktop_1280_en.png")

        # -------------------------------------------------------------
        # 2. Capture Final Root ad.png (scale factor 2, 1280x800)
        # -------------------------------------------------------------
        print("\n--- 2. Generating Final Root ad.png ---")
        # Ensure fresh clean view without toast
        page_d.reload()
        page_d.wait_for_load_state("networkidle")
        page_d.wait_for_timeout(500)

        # Capture viewport 1280x800 hero screenshot with scale factor 2
        page_d.screenshot(path=ROOT_AD_PNG, clip={"x": 0, "y": 0, "width": 1280, "height": 800})
        ad_size = os.path.getsize(ROOT_AD_PNG)
        log_check("Generated root ad.png", os.path.exists(ROOT_AD_PNG), f"File size: {ad_size} bytes ({ad_size / 1024:.1f} KB)")

        context_desktop.close()

        # -------------------------------------------------------------
        # 3. Mobile 375px Tests
        # -------------------------------------------------------------
        print("\n--- 3. Testing Mobile 375px (iPhone SE viewport) ---")
        context_mobile = browser.new_context(
            viewport={"width": 375, "height": 667},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
            color_scheme="light"
        )
        page_m = context_mobile.new_page()
        page_m.goto(HTML_PATH)
        page_m.wait_for_load_state("networkidle")

        mobile_scroll_w = page_m.evaluate("document.documentElement.scrollWidth")
        mobile_client_w = page_m.evaluate("document.documentElement.clientWidth")
        log_check("Mobile 375px zero horizontal overflow", mobile_scroll_w <= mobile_client_w, f"scrollWidth={mobile_scroll_w}, clientWidth={mobile_client_w}")

        # Check mobile button visibility
        join_m_visible = page_m.locator("#joinBtn").is_visible()
        log_check("Join CTA visible on mobile", join_m_visible)

        # Check mobile screenshot
        page_m.screenshot(path=f"{OUT_TEST_DIR}/mobile_375.png")
        print(f"Saved mobile screenshot: {OUT_TEST_DIR}/mobile_375.png")

        context_mobile.close()
        browser.close()

    print("\n==========================================")
    print(f"Test Suite Finished: {test_results['checks_passed']} Passed, {test_results['checks_failed']} Failed")
    print("==========================================")
    if test_results["checks_failed"] > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
