from playwright.async_api import Page
import logging

logger = logging.getLogger(__name__)


async def inject_script(page: Page):
    try:
        await page.evaluate(
            """
            () => {
                // Stable hash function
                const getStringHash = (str) => {
                    let hash = 0;
                    for (let i = 0; i < str.length; i++) {
                        const char = str.charCodeAt(i);
                        hash = ((hash << 5) - hash) + char;
                        hash = hash & hash; // 32-bit integer
                    }
                    return Math.abs(hash);
                };

                // Generate ID from combined seed (URL + element path)
                const generateId = (seed) => {
                    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
                    let id = '';
                    let state = seed;
                    for (let i = 0; i < 5; i++) {
                        state = (state * 16807) % 2147483647;
                        const idx = Math.floor((state / 2147483646) * chars.length);
                        id += chars[idx % chars.length];
                    }
                    return id;
                };

                // Get DOM path as indices (e.g., "0,2,1")
                const getElementPath = (el) => {
                    const path = [];
                    let current = el;
                    while (current.parentNode && current.parentNode !== document) {
                        const children = Array.from(current.parentNode.children);
                        const index = children.indexOf(current);
                        path.unshift(index);
                        current = current.parentNode;
                    }
                    return path.join(',');
                };

                const assignId = (el) => {
                    if (el.hasAttribute('element_id')) return;
                    
                    const url = window.location.href;
                    const path = getElementPath(el);
                    const seed = getStringHash(url + path);
                    const newId = generateId(seed);
                    
                    el.setAttribute('element_id', newId);
                };

                // MAIN EXECUTION ===============================
                const initializeObserver = () => {
                    // Assign to all existing elements
                    const allElements = document.querySelectorAll('*');
                    for (const el of allElements) assignId(el);

                    // MutationObserver for new elements
                    const observer = new MutationObserver(mutations => {
                        for (const mutation of mutations) {
                            for (const node of mutation.addedNodes) {
                                if (node.nodeType === Node.ELEMENT_NODE) {
                                    assignId(node);
                                    // Process children if added via innerHTML
                                    node.querySelectorAll('*').forEach(assignId);
                                }
                            }
                        }
                    });
                    
                    // SAFE OBSERVER START ======================
                    if (document.body) {
                        observer.observe(document.body, { childList: true, subtree: true });
                    } else {
                        // Wait for body to be available
                        document.addEventListener('DOMContentLoaded', () => {
                            observer.observe(document.body, { childList: true, subtree: true });
                        });
                    }
                };

                // Start initialization when DOM is ready
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', initializeObserver);
                } else {
                    initializeObserver();  // DOM already loaded
                }
            }
            """
        )
    except Exception as e:
        logger.error(f"Error injecting script: {e}")


async def handle_frame_navigated(frame):
    logger.info(f"Frame navigated: {frame.url}")
    if frame == frame.page.main_frame:  # Only process main frame
        await inject_script(frame.page)


async def inject_element_ids_into_page(page: Page):
    await inject_script(page)
    page.on("framenavigated", lambda frame: handle_frame_navigated(frame))
