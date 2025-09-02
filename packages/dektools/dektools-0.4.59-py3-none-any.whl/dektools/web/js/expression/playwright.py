import threading
from playwright.sync_api import sync_playwright


def exec_js(s, codes=None, contents=None, paths=None, browser=None):
    with sync_playwright() as p:
        b = getattr(p, browser or 'chromium').launch(headless=True)
        context = b.new_context()
        page = context.new_page()
        if codes:
            for code in codes:
                page.add_init_script(script=code)
        if contents:
            for content in contents:
                page.add_script_tag(content=content)
        if paths:
            for path in paths:
                page.add_script_tag(path=path)
        result = page.evaluate("async () => {%s}" % s)
        context.close()
        b.close()
        return result


def exec_js_safe(*args, **kwargs):
    def target():
        nonlocal result
        result = exec_js(*args, **kwargs)
        lock.release()

    lock = threading.Lock()
    lock.acquire()
    result = None
    threading.Thread(target=target).start()
    with lock:
        return result
