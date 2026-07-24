from playwright.sync_api import sync_playwright
import sys

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # Collect console errors
    errors = []
    page.on('console', lambda msg: None)
    page.on('pageerror', lambda err: errors.append(str(err)))
    
    # Open the file
    page.goto('file:///C:/Users/lenovo/Documents/Codex/2026-07-24/she/work/gk-paper-generator/index.html')
    page.wait_for_timeout(2000)
    
    print('Page title:', page.title())
    print('JS errors:', errors if errors else 'None')
    
    # Try clicking the first tab button
    try:
        tabs = page.locator('.tb')
        count = tabs.count()
        print(f'Tab buttons found: {count}')
        
        if count > 0:
            # Click the second tab
            tabs.nth(1).click()
            page.wait_for_timeout(500)
            print('Clicked second tab - OK')
            
            # Check if the panel became active
            generate_panel = page.locator('#tab-generate')
            is_visible = generate_panel.is_visible()
            print(f'tab-generate visible: {is_visible}')
    except Exception as e:
        print(f'Click error: {e}')
    
    # Check if localStorage works by evaluating
    try:
        bank = page.evaluate('() => JSON.parse(localStorage.getItem("gk_question_bank"))')
        print(f'Bank questions: {len(bank) if bank else 0}')
    except Exception as e:
        print(f'localStorage error: {e}')
    
    browser.close()
