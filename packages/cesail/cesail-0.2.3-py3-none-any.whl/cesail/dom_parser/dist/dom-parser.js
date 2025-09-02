(function () {
    'use strict';

    // Constants and configuration for DOM extractors

    // Pre-compile regex patterns
    const INTERACTIVE_TAGS = new Set([
        'a', 'button', 'input', 'select', 'textarea', 'video', 'audio',
        'summary', 'details', 'menu', 'menuitem'
    ]);

    const INTERACTIVE_ROLES = new Set([
        'button', 'link', 'checkbox', 'radio', 'textbox', 'combobox', 
        'listbox', 'menuitem', 'tab', 'switch', 'slider', 'option',
        'menuitemcheckbox', 'menuitemradio', 'treeitem'
    ]);

    const SENSITIVE_ATTRS = new Set(['password', 'credit-card', 'ssn', 'secret', 'token', 'key', 'auth']);
    const SENSITIVE_CLASSES = new Set(['password', 'secret', 'private', 'sensitive', 'auth', 'token', 'key']);

    // Attribute weights for scoring elements
    const ATTRIBUTE_WEIGHTS = {
        // 1) Unique locators (highest)
        id: 10,
        'data-testid': 9,
        'data-test-id': 9,
        'data-cid': 9,
        jsname: 8,
        jsaction: 8,

        // 2) ARIA & roles
        role: 9,
        'aria-label': 8,
        'aria-labelledby': 7,

        // 3) Navigation / resource URLs
        href: 8,
        src: 7,
        action: 7,

        // 4) Semantic behavior hooks
        onclick: 7,
        placeholder: 5,

        // 5) Accessibility semantics
        alt: 6,
        title: 5,

        // 6) Form state
        disabled: -5,   // less important if disabled
        checked: 4,
        selected: 4,
        hidden: -10,  // not visible → very low importance
        'aria-hidden': -10,  // ditto

        // 7) Styling / generic hooks
        class: 5,
        'data-action': 6,
        'data-toggle': 6,
        isContentEditable: 4,
    };

    // ARIA-specific weights for accessibility scoring
    const ARIA_WEIGHTS = {
        'aria-label': 9,   // explicit accessible name
        'aria-labelledby': 8,   // references one or more other elements' text
        'aria-describedby': 6    // supplemental description, less primary
    };

    // Style weights for scoring elements
    const STYLE_WEIGHTS = {
        // display
        display: {
            none: -20,   // not rendered
            hidden: -20,   // equivalent to none
            'inline': 2,   // small but visible
            'inline-block': 3,
            'block': 4,
            'flex': 5,
            'grid': 5,
            'table': 3,
            'table-row': 2,
            'table-cell': 2,
            // any other displays you care about  
        },

        // visibility
        visibility: {
            hidden: -20,   // present in flow but invisible
            collapse: -10,   // table rows/columns
            visible: 5     // fully visible
        },

        // zIndex: raw numeric value scaled/logged
        zIndex: {
            weightFactor: 0.1 // multiply zIndex by this (e.g. zIndex 50 → +5)
        }
    };

    // Instead, find and process all interactive elements directly
    const INTERACTIVE_SELECTORS = [
        // Interactive tags
        'button', 'a[href]', 'input', 'select', 'textarea', 'label', 'summary', 'details',
        
        // ARIA roles
        '[role="button"]', '[role="link"]', '[role="menuitem"]', '[role="checkbox"]', 
        '[role="radio"]', '[role="switch"]', '[role="tab"]', '[role="slider"]', 
        '[role="combobox"]', '[role="textbox"]', '[role="search"]', '[role="option"]',
        '[role="menuitemcheckbox"]', '[role="menuitemradio"]', '[role="treeitem"]',
        
        // Tabindex (including implicit tabindex)
        '[tabindex]',
        
        // Click handlers
        '[onclick]',
        
        // Interactive attributes
        '[href]', '[src]', '[action]', '[data-action]', '[data-toggle]',
        
        // Contenteditable
        '[contenteditable]',
        
        // Form controls
        'fieldset', 'legend',
        
        // Additional interactive elements
        'video', 'audio', 'canvas', 'svg', 'iframe', 'img[usemap]', 'area',
        'object', 'embed', 'applet', 'marquee', 'blink'
    ];

    // Cache management for DOM extractors

    // Cache for computed styles to avoid repeated calculations
    let styleCache = new Map();

    // Add global Set for top-level elements
    let topLevelElementsCache = new Map();

    // Add selector cache
    let selectorMap = new Map();

    // Add selector cache
    let selectorCache = new WeakMap();

    let nextSelectorId = 1;

    const clearStyleCache = () => {
        styleCache.clear();
    };

    function clearTopLevelElementsCache() {
        topLevelElementsCache.clear();
    }

    function clearSelectorMap() {
        selectorMap.clear();
        nextSelectorId = 1;
    }

    function clearSelectorCache() {
        selectorCache = new WeakMap();
    }

    function incrementSelectorId() {
        nextSelectorId++;
        return nextSelectorId;
    }

    function isInteractive(element) {
        const tag = element.tagName.toLowerCase();
        const role = element.getAttribute('role');

        if (tag === 'form') {
            return false;
        }
        
        // Check for interactive tags and roles
        if (INTERACTIVE_TAGS.has(tag)) return true;
        if (role && INTERACTIVE_ROLES.has(role.toLowerCase())) return true;
        
        // Check for tabindex (including implicit tabindex)
        if (element.hasAttribute('tabindex') || element.tabIndex >= 0) return true;
        
        // Check for click handlers
        if (element.onclick != null || element.getAttribute('onclick') != null) return true;
        
        // Check for common interactive attributes
        const interactiveAttrs = ['href', 'src', 'action', 'data-action', 'data-toggle'];
        if (interactiveAttrs.some(attr => element.hasAttribute(attr))) return true;
        
        // Check for form controls
        // if (element.form || element.tagName === 'LABEL') return true;
        
        // Check for contenteditable
        if (element.isContentEditable) return true;
        
        return false;
    }

    // Batch style reading for better performance
    function getComputedStyles(element) {
        if (styleCache.has(element)) {
            return styleCache.get(element);
        }
        
        const styles = window.getComputedStyle(element);
        const styleInfo = {
            display: styles.display,
            visibility: styles.visibility,
            opacity: parseFloat(styles.opacity),
            position: styles.position,
            zIndex: parseInt(styles.zIndex) || 0
        };
        
        styleCache.set(element, styleInfo);
        return styleInfo;
    }

    // Optimized visibility check with caching and early returns
    function isVisible(element) {
        const visibilityStartTime = performance.now();
        
        if (!element || !element.getBoundingClientRect) {
            // Store timing data for early return
            if (!window.visibilityTimings) {
                window.visibilityTimings = {
                    earlyReturn: [],
                    getBoundingClientRect: [],
                    getComputedStyles: [],
                    viewportCheck: [],
                    total: []
                };
            }
            window.visibilityTimings.earlyReturn.push(performance.now() - visibilityStartTime);
            window.visibilityTimings.total.push(performance.now() - visibilityStartTime);
            return false;
        }
        
        // Skip visibility check for the html element
        if (element.tagName.toLowerCase() === 'html') {
            if (!window.visibilityTimings) {
                window.visibilityTimings = {
                    earlyReturn: [],
                    getBoundingClientRect: [],
                    getComputedStyles: [],
                    viewportCheck: [],
                    total: []
                };
            }
            window.visibilityTimings.earlyReturn.push(performance.now() - visibilityStartTime);
            window.visibilityTimings.total.push(performance.now() - visibilityStartTime);
            return true;
        }
        
        const rectStart = performance.now();
        const rect = element.getBoundingClientRect();
        const rectTime = performance.now() - rectStart;
        
        const stylesStart = performance.now();
        const styles = getComputedStyles(element);
        const stylesTime = performance.now() - stylesStart;
        
        if (styles.display === 'none' || styles.visibility === 'hidden' || styles.opacity === 0) {
            // Store timing data for early return
            if (!window.visibilityTimings) {
                window.visibilityTimings = {
                    earlyReturn: [],
                    getBoundingClientRect: [],
                    getComputedStyles: [],
                    viewportCheck: [],
                    total: []
                };
            }
            window.visibilityTimings.getBoundingClientRect.push(rectTime);
            window.visibilityTimings.getComputedStyles.push(stylesTime);
            window.visibilityTimings.earlyReturn.push(performance.now() - visibilityStartTime);
            window.visibilityTimings.total.push(performance.now() - visibilityStartTime);
            return false;
        }
        
        const viewportStart = performance.now();
        // Check if element is in viewport
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        
        // Relax viewport check to include elements that might be scrolled into view
        const result = !(rect.bottom < -100 || rect.top > viewportHeight + 100 || 
                 rect.right < -100 || rect.left > viewportWidth + 100);
        const viewportTime = performance.now() - viewportStart;
        
        // Store timing data
        if (!window.visibilityTimings) {
            window.visibilityTimings = {
                earlyReturn: [],
                getBoundingClientRect: [],
                getComputedStyles: [],
                viewportCheck: [],
                total: []
            };
        }
        
        window.visibilityTimings.getBoundingClientRect.push(rectTime);
        window.visibilityTimings.getComputedStyles.push(stylesTime);
        window.visibilityTimings.viewportCheck.push(viewportTime);
        window.visibilityTimings.total.push(performance.now() - visibilityStartTime);
        
        return result;
    }

    // Optimized element type detection
    function getElementType(element) {
        const tag = element.tagName.toLowerCase();
        const role = element.getAttribute('role');
        const type = element.getAttribute('type');
        
        // Check role first (ARIA roles take precedence)
        if (role) {
            switch (role.toLowerCase()) {
                case 'button': return 'BUTTON';
                case 'link': return 'LINK';
                case 'checkbox': return 'CHECKBOX';
                case 'radio': return 'RADIO';
                case 'switch': return 'TOGGLE';
                case 'slider': return 'SLIDER';
                case 'textbox': return 'INPUT';
                case 'combobox': return 'SELECT';
                case 'tab': return 'TAB';
                case 'menuitem': return 'BUTTON';
                case 'listbox': return 'SELECT';
                case 'search': return 'FORM';
                case 'option': return 'BUTTON';
                case 'menuitemcheckbox': return 'CHECKBOX';
                case 'menuitemradio': return 'RADIO';
                case 'treeitem': return 'BUTTON';
            }
        }
        
        // Then check tag and type
        switch (tag) {
            case 'a': return 'LINK';
            case 'button': return 'BUTTON';
            case 'input':
                switch (type?.toLowerCase()) {
                    case 'checkbox': return 'CHECKBOX';
                    case 'radio': return 'RADIO';
                    case 'range': return 'SLIDER';
                    case 'date': return 'DATEPICKER';
                    case 'file': return 'FILE_INPUT';
                    case 'submit': return 'BUTTON';
                    case 'reset': return 'BUTTON';
                    case 'image': return 'BUTTON';
                    case 'search': return 'INPUT';
                    default: return 'INPUT';
                }
            case 'textarea': return 'TEXTAREA';
            case 'select': return 'SELECT';
            case 'video': return 'VIDEO';
            case 'audio': return 'AUDIO';
            case 'table': return 'TABLE';
            case 'tr': return 'TABLE_ROW';
            case 'td':
            case 'th': return 'TABLE_CELL';
            case 'form': return 'FORM';
            case 'svg': return 'SVG';
            case 'canvas': return 'CANVAS';
            case 'iframe': return 'IFRAME';
            case 'img': return 'IMAGE';
            case 'label': return 'LABEL';
            case 'summary': return 'SUMMARY';
            case 'details': return 'DETAILS';
            case 'menu': return 'MENU';
            case 'menuitem': return 'MENUITEM';
            default: 
                // Check if element has interactive attributes
                if (element.hasAttribute('href') || element.hasAttribute('src') || 
                    element.hasAttribute('action') || element.hasAttribute('data-action') || 
                    element.hasAttribute('data-toggle') || element.isContentEditable) {
                    return 'BUTTON';
                }
                return 'OTHER';
        }
    }

    // Optimized sensitivity check
    function isSensitive(element) {
        const attrs = element.attributes;
        for (let i = 0; i < attrs.length; i++) {
            const attr = attrs[i].name.toLowerCase();
            const value = attrs[i].value.toLowerCase();
            
            if (SENSITIVE_ATTRS.has(attr) || SENSITIVE_ATTRS.has(value)) {
                return true;
            }
        }
        
        // Handle both string and DOMTokenList cases for className
        let classes;
        if (typeof element.className === 'string') {
            classes = element.className.toLowerCase().split(' ');
        } else if (element.classList) {
            classes = Array.from(element.classList).map(c => c.toLowerCase());
        } else {
            classes = [];
        }
        
        return classes.some(cls => SENSITIVE_CLASSES.has(cls));
    }

    function convertPlaywrightSelectorToCSS(selector) {
        if (!selector || typeof selector !== 'string') {
            return null;
        }

        try {
            // Handle role-based selectors
            if (selector.startsWith('role=')) {
                const match = selector.match(/role=([^\[]+)(?:\[name="([^"]+)"\])?/);
                if (match) {
                    const role = match[1];
                    const name = match[2];
                    if (name) {
                        // Try multiple ARIA attribute combinations for the name
                        return `[role="${role}"][aria-label="${name}"], [role="${role}"][title="${name}"], [role="${role}"][alt="${name}"]`;
                    }
                    return `[role="${role}"]`;
                }
            }

            // Handle other Playwright selectors
            if (selector.includes('[') && selector.includes(']')) {
                // Convert Playwright attribute syntax to CSS
                return selector
                    .replace(/\[([^\]]+)\]/g, (match, attr) => {
                        if (attr.includes('=')) {
                            const [name, value] = attr.split('=');
                            return `[${name}="${value.replace(/"/g, '')}"]`;
                        }
                        return match;
                    });
            }

            return selector;
        } catch (e) {
            console.warn('Error converting selector:', selector, e);
            return null;
        }
    }

    // Batch process attributes
    function getAttributes(element) {
        const attrs = {};
        const attributes = element.attributes;
        for (let i = 0; i < attributes.length; i++) {
            const attr = attributes[i];
            attrs[attr.name] = attr.value;
        }
        return attrs;
    }

    function getShortestUniquePath(el) {
        const parts = [];
      
        while (el && el.nodeType === 1 && el.tagName.toLowerCase() !== 'html') {
          const tag = el.tagName.toLowerCase();
          const parent = el.parentNode;
      
          if (parent) {
            const siblings = Array.from(parent.children).filter(e => e.tagName === el.tagName);
            const index = siblings.indexOf(el) + 1;
            parts.unshift(`${tag}:nth-of-type(${index})`);
          } else {
            parts.unshift(tag);
          }
      
          el = parent;
        }
      
        return parts.join(' > ');
    }

    function getFastRobustSelector(el) {
        if (!(el instanceof Element)) return null;
        if (selectorCache.has(el)) return selectorCache.get(el);
      
        const selectorStartTime = performance.now();
        const selectorTimings = {};
      
        // 1) ID
        const idStart = performance.now();
        if (el.id) {
          const sel = `#${CSS.escape(el.id)}`;
          if (document.querySelectorAll(sel).length === 1) {
            selectorCache.set(el, sel);
            selectorTimings.id = performance.now() - idStart;
            return sel;
          }
        }
        selectorTimings.id = performance.now() - idStart;
      
        // 2) Custom test attributes
        const testAttrsStart = performance.now();
        const testAttrs = ['data-testid','data-test-id','data-cy','data-qa'];
        for (let attr of testAttrs) {
          const v = el.getAttribute(attr);
          if (v) {
            const sel = `[${attr}="${CSS.escape(v)}"]`;
            if (document.querySelectorAll(sel).length === 1) {
              selectorCache.set(el, sel);
              selectorTimings.testAttrs = performance.now() - testAttrsStart;
              return sel;
            }
          }
        }
        selectorTimings.testAttrs = performance.now() - testAttrsStart;
      
        // 4) ARIA role + name (only if aria-label exists)
        const ariaStart = performance.now();
        const role = el.getAttribute('role');
        const aria = el.getAttribute('aria-label');
        if (role && aria) {
          // Playwright‐style locator
          const safe = aria.replace(/(["\\])/g, '\\$1');
          const sel = `role=${role}[name="${safe}"]`;
          const sel2 = convertPlaywrightSelectorToCSS(sel);
          if (document.querySelectorAll(sel2).length === 1) {
            selectorCache.set(el, sel);
            selectorTimings.aria = performance.now() - ariaStart;
            return sel;
          }
        }
        selectorTimings.aria = performance.now() - ariaStart;
      
        // 5) Tag + unique class among siblings
        const classStart = performance.now();
        const tag = el.tagName.toLowerCase();
        for (let cls of el.classList) {
          // Check if this class is unique in the entire document
          const allElementsWithClass = document.querySelectorAll(`.${CSS.escape(cls)}`);
          if (allElementsWithClass.length === 1) {
            const sel = `${tag}.${CSS.escape(cls)}`;
            selectorCache.set(el, sel);
            selectorTimings.class = performance.now() - classStart;
            return sel;
          }
        }
        selectorTimings.class = performance.now() - classStart;
      
        // 6) Fallback: shortest unique CSS path (heaviest)
        const fallbackStart = performance.now();
        const sel = getShortestUniquePath(el);
        selectorCache.set(el, sel);
        selectorTimings.fallback = performance.now() - fallbackStart;
        
        const totalSelectorTime = performance.now() - selectorStartTime;
        
        // Store timing data for summary
        if (!window.selectorTimings) {
          window.selectorTimings = {
            id: [],
            testAttrs: [],
            aria: [],
            class: [],
            fallback: [],
            total: []
          };
        }
        
        window.selectorTimings.id.push(selectorTimings.id);
        window.selectorTimings.testAttrs.push(selectorTimings.testAttrs);
        window.selectorTimings.aria.push(selectorTimings.aria);
        window.selectorTimings.class.push(selectorTimings.class);
        window.selectorTimings.fallback.push(selectorTimings.fallback);
        window.selectorTimings.total.push(totalSelectorTime);
        
        return sel;
    }

    function getPlaywrightStyleSelector(element) {
        return getFastRobustSelector(element);
      }

    function extractActions() {

        const processElement = (element) => {
            if (!element || !element.tagName) return null;

            // Skip invisible elements early
            if (!isVisible(element)) return null;

            const tag = element.tagName.toLowerCase();
            const rect = element.getBoundingClientRect();
            
            // Batch DOM reads
            performance.now();
            const attributes = {};
            for (const attr of element.attributes) {
                attributes[attr.name] = attr.value;
            }

            const text = element.textContent?.trim() || '';

            // Check if element is interactive
            const interactive = isInteractive(element);
            const elementType = getElementType(element);
            const sensitive = isSensitive(element);

            // Generate Playwright-style selector
            let selector = null;
            try {
                selector = getPlaywrightStyleSelector(element);
            } catch (e) {
                selector = null;
            }

            const elementData = {
                tag,
                attributes,
                text,
                rect: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    left: rect.left,
                    bottom: rect.bottom,
                    right: rect.right
                },
                interactive,
                type: elementType,
                sensitive,
                role: element.getAttribute('role'),
                aria: {
                    label: element.getAttribute('aria-label'),
                    describedby: element.getAttribute('aria-describedby'),
                    labelledby: element.getAttribute('aria-labelledby')
                },
                computedStyle: {
                    display: window.getComputedStyle(element).display,
                    visibility: window.getComputedStyle(element).visibility,
                    zIndex: window.getComputedStyle(element).zIndex
                },
                selector,
                object: element
            };
            
            return elementData;
        };

        const foundElements = new Map();
        for (const selector of INTERACTIVE_SELECTORS) {
            const elements = document.querySelectorAll(selector);
            for (const element of elements) {
                if (isVisible(element) && isInteractive(element)) {
                    const processed = processElement(element);
                    if (processed) {
                        foundElements.set(element, processed);
                    }
                }
            }
        }

        return foundElements;
    }

    function extractMetaData() {
        return {
            url: window.location.href,
            canonical: document.querySelector('link[rel="canonical"]')?.href,
            title: document.title,
            meta: {
                description: document.querySelector('meta[name="description"]')?.content,
                keywords: document.querySelector('meta[name="keywords"]')?.content,
                viewport: document.querySelector('meta[name="viewport"]')?.content,
                og: {
                    title: document.querySelector('meta[property="og:title"]')?.content,
                    description: document.querySelector('meta[property="og:description"]')?.content,
                    image: document.querySelector('meta[property="og:image"]')?.content
                }
            },
            status: document.readyState
        };
    }

    function extractDocumentOutline() {
        const outline = [];
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        headings.forEach(heading => {
            outline.push({
                level: parseInt(heading.tagName[1]),
                text: heading.textContent.trim(),
                id: heading.id
            });
        });
        return outline;
    }

    function extractTextContent() {
        const textBlocks = [];
        const paragraphs = document.querySelectorAll('p, blockquote, pre');
        paragraphs.forEach(p => {
            if (isVisible(p)) {
                textBlocks.push({
                    type: p.tagName.toLowerCase(),
                    text: p.textContent.trim(),
                    id: p.id
                });
            }
        });
        return textBlocks;
    }

    function extractForms() {
        const forms = [];
        document.querySelectorAll('form').forEach(form => {
            const fields = [];
            form.querySelectorAll('input, select, textarea').forEach(field => {
                fields.push({
                    type: field.type || field.tagName.toLowerCase(),
                    name: field.name,
                    id: field.id,
                    placeholder: field.placeholder,
                    value: field.value,
                    required: field.required,
                    pattern: field.pattern,
                    min: field.min,
                    max: field.max,
                    options: field.tagName === 'SELECT' ? 
                        Array.from(field.options).map(opt => ({
                            value: opt.value,
                            text: opt.text
                        })) : undefined
                });
            });
            
            forms.push({
                id: form.id,
                action: form.action,
                method: form.method,
                fields
            });
        });
        return forms;
    }

    function extractMedia() {
        const media = [];
        
        // Images
        document.querySelectorAll('img, picture').forEach(img => {
            let rawSrc = img.src || '';
            rawSrc.length > 200
              ? rawSrc.slice(0, 200)  // take only the first 300 chars
              : rawSrc;
            media.push({
                type: 'image',
                src: img.src,
                alt: img.alt,
                width: img.width,
                height: img.height,
                loading: img.loading
            });
        });
        
        // Video/Audio
        document.querySelectorAll('video, audio').forEach(mediaEl => {
            let rawSrc = mediaEl.src || '';
            let src = rawSrc.length > 200
              ? rawSrc.slice(0, 200)  // take only the first 300 chars
              : rawSrc;
            media.push({
                type: mediaEl.tagName.toLowerCase(),
                src: src,
                controls: mediaEl.controls,
                autoplay: mediaEl.autoplay,
                loop: mediaEl.loop,
                muted: mediaEl.muted
            });
        });
        
        return media;
    }

    function extractLinks() {
        const links = [];
        document.querySelectorAll('a').forEach(link => {
            if (isVisible(link)) {
                links.push({
                    href: link.href,
                    text: link.textContent.trim(),
                    target: link.target,
                    rel: link.rel
                });
            }
        });
        return links;
    }

    function extractStructuredData() {
        const data = [];
        document.querySelectorAll('script[type="application/ld+json"]').forEach(script => {
            try {
                data.push(JSON.parse(script.textContent));
            } catch (e) {
                console.warn('Failed to parse JSON-LD:', e);
            }
        });
        return data;
    }

    function extractDynamicState() {
        return {
            modals: Array.from(document.querySelectorAll('[role="dialog"], [role="alertdialog"]'))
                .filter(isVisible)
                .map(modal => ({
                    id: modal.id,
                    role: modal.getAttribute('role'),
                    text: modal.textContent.trim()
                })),
            notifications: Array.from(document.querySelectorAll('[role="alert"], [role="status"]'))
                .filter(isVisible)
                .map(notif => ({
                    id: notif.id,
                    role: notif.getAttribute('role'),
                    text: notif.textContent.trim()
                })),
            loading: Array.from(document.querySelectorAll('[role="progressbar"], .loading, .spinner'))
                .filter(isVisible)
                .map(loader => ({
                    id: loader.id,
                    type: loader.getAttribute('role') || 'spinner'
                }))
        };
    }

    function extractLayoutInfo() {
        const layout = [];
        const sections = document.querySelectorAll('header, nav, main, footer, section, article, aside');
        sections.forEach(section => {
            if (isVisible(section)) {
                const rect = section.getBoundingClientRect();
                layout.push({
                    type: section.tagName.toLowerCase(),
                    id: section.id,
                    rect: {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    },
                    zIndex: window.getComputedStyle(section).zIndex
                });
            }
        });
        return layout;
    }

    function extractPaginationInfo() {
        const pagination = {
            next: document.querySelector('a[rel="next"]')?.href,
            prev: document.querySelector('a[rel="prev"]')?.href,
            pages: Array.from(document.querySelectorAll('.pagination a, [role="navigation"] a'))
                .filter(link => /^\d+$/.test(link.textContent.trim()))
                .map(link => ({
                    number: parseInt(link.textContent.trim()),
                    href: link.href
                }))
        };
        return pagination;
    }

    // Function to get all top-level elements
    function getTopLevelElements(dfsGroups) {
        try {
            const topLevelElements = [];
            for (const [key, element] of dfsGroups.entries()) {
                topLevelElements.push(scoreTopLevelElement(element));
            }
            return dfsGroups;
        } catch (e) {
            console.warn('Error in getTopLevelElements:', e);
            return [];
        }
    }

    // Function to score an element based on its ARIA attributes
    function scoreElementByAria(el) {
        let score = 0;
        for (const [attr, weight] of Object.entries(ARIA_WEIGHTS)) {
            if (el.hasAttribute(attr) && el.getAttribute(attr)?.trim()) {
                score += weight;
            }
        }

        // Normalize score to -1 to 1 range
        // The raw score typically ranges from 0 to 23 (sum of all ARIA_WEIGHTS)
        // Using a sigmoid-like function with a scaling factor of 10
        const normalizedScore = (2 / (1 + Math.exp(-score/10))) - 1;
        
        return normalizedScore;
    }

    // Function to score an element based on its computed styles
    function scoreElementByStyle(el) {
        const style = window.getComputedStyle(el);
        let score = 0;

        // 1) display
        const disp = style.display || 'block';
        score += STYLE_WEIGHTS.display[disp] ?? 0;

        // 2) visibility
        const vis = style.visibility || 'visible';
        score += STYLE_WEIGHTS.visibility[vis] ?? 0;

        // 3) z-index
        const zi = parseInt(style.zIndex, 10);
        if (!isNaN(zi)) {
            score += zi * STYLE_WEIGHTS.zIndex.weightFactor;
        }

        // Normalize score to -1 to 1 range
        // The raw score typically ranges from -20 to +25
        // Using a sigmoid-like function with a scaling factor of 20
        const normalizedScore = (2 / (1 + Math.exp(-score/20))) - 1;
        
        return normalizedScore;
    }

    // Function to score an element based on its attributes
    function scoreElementByAttributes(attributes) {
        let score = 0;
        
        // Score each attribute
        for (const [name, value] of Object.entries(attributes)) {
            if (name in ATTRIBUTE_WEIGHTS) {
                // Special handling for certain attributes
                if (name === 'tabindex' && value === '-1') {
                    score -= 5; // Penalize negative tabindex
                } else if (name === 'class') {
                    // Add points for each class (up to a limit)
                    const classCount = value.split(' ').length;
                    score += Math.min(classCount * 2, 10); // Cap at 10 points for classes
                } else {
                    score += ATTRIBUTE_WEIGHTS[name];
                }
            }
        }

        // Normalize score to -1 to 1 range
        // Using a sigmoid-like function with a scaling factor of 15
        // This gives a good spread for scores between -10 and +30
        const normalizedScore = (2 / (1 + Math.exp(-score/15))) - 1;
        
        return normalizedScore;
    }

    // Function to get inverse rank of element type (0 for highest importance, 28 for lowest)
    function getInverseElementRank(type) {
        const rankMap = {
            'BUTTON': 0,
            'LINK': 1,
            'SELECT': 2,
            'TEXTAREA': 3,
            'INPUT': 4,
            'CHECKBOX': 5,
            'RADIO': 6,
            'TOGGLE': 7,
            'SLIDER': 8,
            'DATEPICKER': 9,
            'FILE_INPUT': 10,
            'TAB': 11,
            'LABEL': 12,
            'IMAGE': 13,
            'VIDEO': 14,
            'AUDIO': 15,
            'SUMMARY': 16,
            'DETAILS': 17,
            'SVG': 18,
            'CANVAS': 19,
            'IFRAME': 20,
            'TABLE': 21,
            'TABLE_ROW': 22,
            'TABLE_CELL': 23,
            'FORM': 24,
            'MENU': 25,
            'MENUITEM': 26,
            'OTHER': 27
        };
        
        // Get the raw rank (0-27)
        const rawRank = rankMap[type] ?? 27;
        
        // Normalize to -1 to 1 range
        // Map 0 (highest importance) to 1, and 27 (lowest importance) to -1
        const normalizedRank = 1 - (rawRank / 27) * 2;
        
        return normalizedRank;
    }

    // Function to score an element based on its area
    function scoreElementByArea(element) {
        // Get element dimensions
        let width, height;
        
        if (element instanceof Element) {
            // If it's a DOM element, use getBoundingClientRect
            const rect = element.getBoundingClientRect();
            width = rect.width;
            height = rect.height;
        } else if (element && typeof element === 'object') {
            // If it's a plain object with width/height properties
            width = element.width;
            height = element.height;
        } else {
            // Invalid input, return neutral score
            return 0;
        }

        // Calculate viewport area
        const viewportArea = window.innerWidth * window.innerHeight;
        const ratio = (width * height) / viewportArea;

        // Shift sigmoid to center at 10% viewport area
        const threshold = 0.10;  // Center point (10% of viewport)
        const steepness = 50;    // Controls how quickly the score transitions
        const x = (ratio - threshold) * steepness;

        // Normalize to [-1, 1] range
        // This gives:
        // - ratio < 1% → score ≈ -1
        // - ratio ≈ 10% → score ≈ 0
        // - ratio > 10% → score ≈ +1
        const score = 2 / (1 + Math.exp(-x)) - 1;
        
        return score;
    }

    // Function to score a top-level element based on its actions
    function scoreTopLevelElement(element) {
        if (!element || !element.actions || !element.actions.length) {
            // Add default scores to the existing element
            element.scores = {
                elementRank: 0,
                attributes: 0,
                style: 0,
                aria: 0,
                semanticText: 0,
                area: 0,
                total: 0
            };
            return element;
        }

        // Initialize scores
        let elementRankScore = 0;
        let attributesScore = 0;
        let styleScore = 0;
        let ariaScore = 0;
        let semanticTextScore = 0;
        let areaScore = scoreElementByArea(element);

        // Score each action
        for (const action of element.actions) {
            try {            
                const actionEl = action.object;
                if (!actionEl) {
                    console.warn('Element not found for selector in scoring:', action.selector);
                    continue;
                }

                // Get element type and rank
                const type = getElementType(actionEl);
                elementRankScore = Math.max(elementRankScore, getInverseElementRank(type));

                // Get attribute score
                const attributes = getAttributes(actionEl);
                attributesScore = Math.max(attributesScore, scoreElementByAttributes(attributes));

                // Get style score
                styleScore = Math.max(styleScore, scoreElementByStyle(actionEl));

                // Get ARIA score
                ariaScore = Math.max(ariaScore, scoreElementByAria(actionEl));

                // Get semantic text score
                if (action.semanticTextScore !== undefined) {
                    semanticTextScore = Math.max(semanticTextScore, action.semanticTextScore);
                }
            } catch (e) {
                console.warn('Error scoring action:', action.selector, e);
            }
        }

        const totalScore = (
            elementRankScore    * 0.30 +   // 20%: type of element (button vs. link vs. form field)
            attributesScore     * 0.10 +   // 10%: IDs, data‑hooks, onclick, etc.
            styleScore          * 0.10 +   // 10%: display/visibility/z‑index
            ariaScore           * 0.10 +   // 10%: aria‑label, aria‑describedby, etc.
            semanticTextScore   * 0.20 +   // 20%: label richness & importantText
            areaScore           * 0.20     // 30%: on‑screen footprint
          );

        // Add scores directly to the existing element
        element.scores = {
            elementRank: elementRankScore,
            attributes: attributesScore,
            style: styleScore,
            aria: ariaScore,
            semanticText: semanticTextScore,
            area: areaScore,
            total: totalScore
        };

        return element;
    }

    function getLabelText(el) {
        if (!(el instanceof Element)) return '';
      
        const seen = new Set();
        const texts = [];
      
        // Skip hidden elements
        const isHidden = el => {
          const style = window.getComputedStyle(el);
          return (
            el.getAttribute('aria-hidden') === 'true' ||
            style.display === 'none' ||
            style.visibility === 'hidden'
          );
        };
      
        // Helper to extract visible trimmed text
        const getVisibleText = el => {
          return el.textContent?.trim() || '';
        };
      
        // Add only if not empty and not seen before
        const addText = t => {
          const text = t.trim();
          if (text && !seen.has(text)) {
            seen.add(text);
            texts.push(text);
          }
        };
      
        // 1. aria-label
        const ariaLabel = el.getAttribute('aria-label');
        if (ariaLabel) addText(ariaLabel);
      
        // 2. aria-labelledby
        const labelledBy = el.getAttribute('aria-labelledby');
        if (labelledBy) {
          labelledBy.split(/\s+/).forEach(id => {
            const ref = document.getElementById(id);
            if (ref && !isHidden(ref)) addText(getVisibleText(ref));
          });
        }
      
        // 3. alt (for <img>, <area>, etc.)
        if (el.hasAttribute('alt')) addText(el.getAttribute('alt'));
      
        // 4. placeholder (e.g., <input placeholder="Search">)
        if (el.hasAttribute('placeholder')) addText(el.getAttribute('placeholder'));
      
        // 5. title (tooltip text)
        if (el.hasAttribute('title')) addText(el.getAttribute('title'));
      
        // 6. button/input "value"
        if (el.tagName === 'INPUT' || el.tagName === 'BUTTON') {
          const type = el.getAttribute('type');
          if (type === 'submit' || type === 'reset' || type === 'button') {
            if (el.value) addText(el.value);
          }
        }
      
        // 7. Associated <label for="id">
        if (el.id) {
          const label = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
          if (label && !isHidden(label)) addText(getVisibleText(label));
        }
      
        // 8. Wrapping label (e.g. <label><input> Foo</label>)
        const wrappingLabel = el.closest('label');
        if (wrappingLabel && !isHidden(wrappingLabel)) addText(getVisibleText(wrappingLabel));
      
        // 9. <legend> inside fieldset
        const fieldset = el.closest('fieldset');
        if (fieldset) {
          const legend = fieldset.querySelector('legend');
          if (legend && !isHidden(legend)) addText(getVisibleText(legend));
        }
      
        // 10. Direct visible text content
        if (!isHidden(el)) addText(getVisibleText(el));
      
        return texts.join(' | ');
    }
      
    // Quickly gather label/text from descendants of an element
    function getDownstreamLabelText(rootEl, options = {}) {
        const { maxNodes = 50, maxChars = 300, includeSelf = false } = options;
        if (!rootEl || !(rootEl instanceof Element)) return '';

        const texts = [];
        const seen = new Set();

        const add = (t) => {
            const v = (t || '').trim();
            if (!v) return;
            if (seen.has(v)) return;
            seen.add(v);
            texts.push(v);
        };

        try {
            let scanned = 0;
            if (includeSelf) add(getLabelText(rootEl));

            // Use TreeWalker to efficiently traverse elements
            const walker = document.createTreeWalker(rootEl, NodeFilter.SHOW_ELEMENT);
            while (walker.nextNode()) {
                const el = walker.currentNode;
                add(getLabelText(el));
                scanned++;
                if (scanned >= maxNodes) break;
                if (texts.join(' | ').length >= maxChars) break;
            }
        } catch (_) {
            // Fallback: conservative empty string
        }

        let out = texts.join(' | ');
        if (out.length > maxChars) out = out.slice(0, maxChars);
        return out;
    }

    // New DFS-based functionality for computing counts and aggregating text
    function computeCountsAndText(root, actionableSet) {
        const infoMap = new WeakMap();

        function dfs(node) {
            if (!node || !node.children) {
                return { count: 0, text: '' };
            }
            
            let count = actionableSet.has(node) ? 1 : 0;
            let inActionableSet = false;
            if (count > 0) {
                inActionableSet = true;
            }
            // collect text only for actionable nodes (or you could collect all text)
            let text = getLabelText(node);

            let totalCount = 0;
            for (const child of node.children) {
                const { count: c2, text: t2 } = dfs(child);
                totalCount += c2;
                if (t2) text += (text ? ' ' : '') + t2;
            }

            count += totalCount;
            if (count > 1) {
                count = 1;
            }

            if (totalCount > 1) {
                infoMap.set(node, {count: 2, text, inActionableSet });
            } else {
                infoMap.set(node, {count, text, inActionableSet });
            }

            return { count, text };
        }

        dfs(root);
        return infoMap;
    }

    // Function to group actionable elements under their minimal containers using DFS approach
    function groupActionableElementsDFS(foundElements) {    
        // // 1) identify actionable elements
        // const actionableSet = new Map(); // element → actionData
        // for (const f of foundElements) {
        //     try {
        //         actionableSet.set(f.object, f);
        //     } catch (e) {
        //         console.warn('Error converting selector to element:', f.selector, e);
        //     }
        // }
        
        // 2) run the DFS
        const infoMap = computeCountsAndText(document.body, foundElements);


        const topLevelElementsCache = new Map();
        
        for (const [el, actionData] of foundElements) {
            let node = el;
            let elementActions = [];

            if (infoMap.get(node) && infoMap.get(node).count > 1){
                continue;
            }
            
            // climb until parent has count > 1 (so you stop at the smallest container that holds >1 action)
            while (node.parentElement && 
                   infoMap.has(node.parentElement) && 
                   infoMap.get(node.parentElement).count < 2) {
                // Collect action data from current node if it's in actionable set
                const nodeInfo = infoMap.get(node);
                if (nodeInfo && nodeInfo.inActionableSet) {
                    elementActions.push(foundElements.get(node));
                }
                node = node.parentElement;
            }
            
            // Collect action data from the final group root if it's in actionable set
            const rootInfo = infoMap.get(node);
            if (rootInfo && rootInfo.inActionableSet) {
                elementActions.push(foundElements.get(node));
            }
            
            // // Add to topLevelElementsCache as we find group roots
            const rect = node.getBoundingClientRect();
            // const nodeKey = `${rect.top},${rect.left},${rect.width},${rect.height}`;
            
            if (!topLevelElementsCache.has(node)) {
                const tmpElement = {
                    top: rect.top,
                    left: rect.left,
                    width: rect.width,
                    height: rect.height,
                    actions: elementActions || []
                };
                topLevelElementsCache.set(node, tmpElement);
            }
        }

        return topLevelElementsCache;
    }

    // Function to check if an element is truly clickable (not occluded)
    function isTrulyClickable(el) {
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return false;

        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        const topEl = document.elementFromPoint(centerX, centerY);
        return el.contains(topEl);
    }

    function filterOccludedElements(elements) {
        return elements.filter(element => {
            try {
                const el = element.object;
                
                if (!el) {
                    console.warn('Element not found for occlusion check:', element.selector);
                    return false;
                }
                
                return isTrulyClickable(el);
            } catch (e) {
                console.warn('Error checking occlusion for element:', element.selector, e);
                return false;
            }
        });
    }

    // Function to transform top-level elements into final structure
    function transformTopLevelElements(elements, config = null) {
        // Check if elements is null or undefined
        if (!elements) {
            console.warn('No elements provided to transformTopLevelElements');
            return [];
        }

        // Handle the new structure where elements is a Map with key-value pairs
        if (!(elements instanceof Map)) {
            console.warn('Expected elements to be a Map, got:', typeof elements);
            return [];
        }
        
        // Transform and score each element directly from the Map
        const transformedElements = Array.from(elements.entries()).map(([key, element]) => {
            if (!element) return null;

            // 1. Find the best type based on getInverseElementRank
            let bestType = null;
            let bestRank = Infinity;
            let bestAction = null;
            
            // Ensure actions is an array
            const actions = Array.isArray(element.actions) ? element.actions : [];
            
            for (const action of actions) {
                try {
                    // Use the DOM element directly from action.object
                    const actionEl = action.object;
                    if (!actionEl) {
                        console.warn('No DOM element found for action:', action.selector);
                        continue;
                    }
                    
                    const type = getElementType(actionEl);
                    const rank = getInverseElementRank(type);
                    
                    if (rank < bestRank) {
                        bestRank = rank;
                        bestType = type;
                        bestAction = action;
                    }
                } catch (e) {
                    console.warn('Error processing action:', action?.selector, e);
                }
            }

            // 2. Create normalized bounding box
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            const bbox = {
                x: (element.left || 0) / viewportWidth,
                y: (element.top || 0) / viewportHeight,
                w: (element.width || 0) / viewportWidth,
                h: (element.height || 0) / viewportHeight
            };

            // 3. Get selector from best action
            const selector = bestAction?.selector || '';

            // 4. Get attributes from best action
            const attributes = bestAction?.attributes || {};

            // 5. Combine text from all actions
            const text = actions
                .map(action => action.text?.trim())
                .filter(Boolean)
                .join(' | ');

            // 6. Build important text section
            let importantText = '';
            
            // First add text from high-priority attributes
            const highPriorityTexts = [];
            for (const action of actions) {
                try {
                    // Use the DOM element directly from action.object
                    const actionEl = action.object;
                    if (!actionEl) {
                        console.warn('No DOM element found for important text:', action.selector);
                        continue;
                    }

                    // Check ATTRIBUTE_WEIGHTS attributes
                    for (const [attr, weight] of Object.entries(ATTRIBUTE_WEIGHTS)) {
                        if (weight >= 7 && actionEl.hasAttribute(attr)) {
                            const value = actionEl.getAttribute(attr);
                            if (value) highPriorityTexts.push(value);
                        }
                    }

                    // Check ARIA_WEIGHTS attributes
                    for (const [attr, weight] of Object.entries(ARIA_WEIGHTS)) {
                        if (weight >= 7 && actionEl.hasAttribute(attr)) {
                            const value = actionEl.getAttribute(attr);
                            if (value) highPriorityTexts.push(value);
                        }
                    }
                } catch (e) {
                    console.warn('Error processing action for important text:', action?.selector, e);
                }
            }

            // Add high priority texts
            if (highPriorityTexts.length > 0) {
                importantText += highPriorityTexts.join(' | ');
            }

            // Then add importantText from actions
            const actionTexts = actions
                .map(action => action.importantText)
                .filter(Boolean)
                .flat()
                .filter(Boolean);

            if (actionTexts.length > 0) {
                if (importantText) importantText += ' | ';
                importantText += actionTexts.join(' | ');
            }

            // 7. Gather downstream label/text context under the chosen action element
            const labelContext = (bestAction && bestAction.object)
                ? getDownstreamLabelText(bestAction.object, { maxNodes: 50, maxChars: 300, includeSelf: false })
                : '';

            // Prepend a short version of labelContext (max 20 chars) to importantText
            const shortCtx = (labelContext || '').slice(0, 50);
            if (shortCtx) {
                importantText = importantText ? `${shortCtx} | ${importantText}` : shortCtx;
            }

            // Create the base action object
            const baseAction = {
                type: bestType || 'OTHER',
                bbox,
                selector,
                attributes,
                text,
                importantText,
                score: element.scores?.total || 0,
                object: key
            };

            return baseAction;
        }).filter(Boolean); // Remove any null elements

        return transformedElements.sort((a, b) => b.score - a.score);
    }

    function filterActionFields(action, config = null) {
        if (!config || !config.action_filters) {
            return action; // Return unchanged if no config
        }

        const filters = config.action_filters;
        const includeFields = filters.include_fields || [];
        const excludeFields = filters.exclude_fields || [];
        const importantTextMaxLength = filters.important_text_max_length || 250;
        const trimTextLength = filters.trim_text_to_length || 100;
        const filteredAction = {};

        // Process each field based on include/exclude rules
        for (const [key, value] of Object.entries(action)) {
            // Skip if field is explicitly excluded
            if (excludeFields.includes(key)) {
                continue;
            }

            // Include if no include_fields specified (include all) or if field is in include list
            if (includeFields.length === 0 || includeFields.includes(key)) {
                let processedValue = value;

                // Apply text length limits
                if (key === 'importantText' && typeof value === 'string') {
                    processedValue = value.slice(0, importantTextMaxLength);
                } else if (key === 'text' && typeof value === 'string') {
                    processedValue = value.slice(0, trimTextLength);
                }

                filteredAction[key] = processedValue;
            }
        }

        return filteredAction;
    }

    // perf.js - Chrome Tracing compatible performance tracking

    let perfEnabled = false;
    let traceEvents = [];
    let eventStack = [];
    let eventCounter = 0;

    function enablePerf() {
      perfEnabled = true;
      traceEvents = [];
      eventStack = [];
      eventCounter = 0;
      console.log("[PERF] Chrome tracing performance tracking ENABLED");
    }

    function perfStart(label, text) {
      if (!perfEnabled) return;
      
      const startTime = performance.now() * 1000; // Convert to microseconds for Chrome tracing
      const eventId = `event_${++eventCounter}`;
      const depth = eventStack.length; // Track nesting depth
      
      const event = {
        name: text,
        cat: label,
        ph: 'B', // Begin event
        ts: startTime,
        pid: 1,
        tid: depth, // Use depth as thread ID for visual hierarchy
        args: { 
          label, 
          text, 
          depth,
          timestamp: new Date().toISOString(),
          eventId
        }
      };
      
      traceEvents.push(event);
      eventStack.push({ 
        label, 
        eventId, 
        startTime, 
        depth,
        text 
      });
      
      console.log(`[PERF] 🟢 START: ${label} - ${text} (depth: ${depth})`);
    }

    function perfEnd(label) {
      if (!perfEnabled) return;
      
      const endTime = performance.now() * 1000; // Convert to microseconds
      const stackIndex = eventStack.findIndex(item => item.label === label);
      
      if (stackIndex === -1) {
        console.warn(`[PERF] ⚠️ No matching start event found for label: ${label}`);
        return;
      }
      
      const { startTime, depth, text } = eventStack[stackIndex];
      const duration = endTime - startTime;
      eventStack.splice(stackIndex, 1);
      
      const event = {
        name: text || label,
        cat: label,
        ph: 'E', // End event
        ts: endTime,
        pid: 1,
        tid: depth, // Use depth as thread ID for visual hierarchy
        args: {
          duration: `${duration.toFixed(2)}μs`,
          durationMs: `${(duration / 1000).toFixed(2)}ms`
        }
      };
      
      traceEvents.push(event);
      
      console.log(`[PERF] 🔴 END: ${label} - ${text || label} (duration: ${(duration / 1000).toFixed(2)}ms, depth: ${depth})`);
    }

    function getTraceData() {
      if (!perfEnabled) {
        console.log("[PERF] Performance tracking not enabled.");
        return null;
      }
      
      return {
        traceEvents: traceEvents,
        displayTimeUnit: 'ms',
        systemTraceEvents: 'systemTraceEvents',
        otherData: {
          totalEvents: traceEvents.length,
          maxDepth: Math.max(...eventStack.map(e => e.depth), 0),
          timestamp: new Date().toISOString()
        }
      };
    }

    function dumpTraceToFile(filename = 'performance-trace.json') {
      if (!perfEnabled) {
        console.log("[PERF] Performance tracking not enabled.");
        return;
      }
      
      const traceData = getTraceData();
      if (!traceData) return;
      
      const dataStr = JSON.stringify(traceData, null, 2);
      
      console.log(`[PERF] 📁 Trace data ready for saving as ${filename}`);
      console.log(`[PERF] 📊 Total events: ${traceData.otherData.totalEvents}`);
      console.log(`[PERF] 📊 Max depth: ${traceData.otherData.maxDepth}`);
      console.log(`[PERF] 📊 Data size: ${(dataStr.length / 1024).toFixed(2)} KB`);
      
      // Return the data to be saved by the caller (Python/Node.js)
      return {
        filename,
        data: dataStr,
        success: true,
        fileSize: dataStr.length,
        eventCount: traceData.otherData.totalEvents,
        traceData
      };
    }

    function printPerfSummary() {
      if (!perfEnabled) {
        console.log("[PERF] Performance tracking not enabled.");
        return;
      }

      console.log("========= 🕒 PERF SUMMARY =========");
      
      // Group events by category and calculate statistics
      const categories = {};
      const durations = [];
      
      for (const event of traceEvents) {
        if (event.ph === 'E') { // Only end events have duration
          const category = event.cat;
          if (!categories[category]) {
            categories[category] = { count: 0, totalDuration: 0, events: [] };
          }
          categories[category].count++;
          categories[category].events.push(event);
          
          // Calculate duration from matching start event
          const startEvent = traceEvents.find(e => 
            e.ph === 'B' && e.cat === category && e.name === event.name
          );
          if (startEvent) {
            const duration = event.ts - startEvent.ts;
            categories[category].totalDuration += duration;
            durations.push(duration);
          }
        }
      }
      
      // Print summary by category
      for (const [category, stats] of Object.entries(categories)) {
        const avgDuration = stats.totalDuration / stats.count;
        console.log(`📊 Category: ${category}`);
        console.log(`   Events: ${stats.count}`);
        console.log(`   Total Duration: ${(stats.totalDuration / 1000).toFixed(2)}ms`);
        console.log(`   Average Duration: ${(avgDuration / 1000).toFixed(2)}ms`);
        console.log('');
      }
      
      if (durations.length > 0) {
        const totalDuration = durations.reduce((sum, d) => sum + d, 0);
        const avgDuration = totalDuration / durations.length;
        const maxDuration = Math.max(...durations);
        const minDuration = Math.min(...durations);
        
        console.log(`📈 Overall Statistics:`);
        console.log(`   Total Events: ${traceEvents.length / 2}`); // Divide by 2 since each event has start+end
        console.log(`   Total Duration: ${(totalDuration / 1000).toFixed(2)}ms`);
        console.log(`   Average Duration: ${(avgDuration / 1000).toFixed(2)}ms`);
        console.log(`   Max Duration: ${(maxDuration / 1000).toFixed(2)}ms`);
        console.log(`   Min Duration: ${(minDuration / 1000).toFixed(2)}ms`);
        console.log(`   Max Depth: ${Math.max(...eventStack.map(e => e.depth), 0)}`);
      }
      
      console.log("===================================");
    }

    function clearPerf() {
      traceEvents = [];
      eventStack = [];
      eventCounter = 0;
    }

    // Function to create and position the canvas overlay
    function createCanvasOverlay() {
        const canvas = document.createElement('canvas');
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.pointerEvents = 'none'; // Allow clicking through the canvas
        canvas.style.zIndex = '9999';
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        document.body.appendChild(canvas);
        return canvas;
    }

    // Function to generate random color
    function getRandomColor() {
        const hue = Math.floor(Math.random() * 360); // Random hue
        return `hsla(${hue}, 70%, 50%, 0.8)`; // HSL with alpha for stroke
    }

    // Function to get lighter version of a color for fill
    function getLighterColor(color) {
        return color.replace('0.8', '0.1'); // Replace alpha for fill
    }

    // Function to draw bounding boxes
    function drawBoundingBoxes(elements) {
        // Create or get canvas
        let canvas = document.querySelector('#bounding-boxes-canvas');
        if (!canvas) {
            canvas = createCanvasOverlay();
            canvas.id = 'bounding-boxes-canvas';
        }

        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw each bounding box
        elements.forEach(element => {
            try {
                // Check if element has the expected structure
                if (!element || !element.bbox || typeof element.bbox.x === 'undefined') {
                    console.warn('Element missing bbox property:', element);
                    return; // Skip this element
                }

                const strokeColor = getRandomColor();
                const fillColor = getLighterColor(strokeColor);
                
                // Convert normalized bbox coordinates to pixel coordinates
                const x = element.bbox.x * canvas.width;
                const y = element.bbox.y * canvas.height;
                const width = element.bbox.w * canvas.width;
                const height = element.bbox.h * canvas.height;
                
                ctx.strokeStyle = strokeColor;
                ctx.lineWidth = 2;
                ctx.strokeRect(x, y, width, height);

                // Add a semi-transparent fill
                ctx.fillStyle = fillColor;
                ctx.fillRect(x, y, width, height);
                
                // Create label text
                const selector = element.selector || 'N/A';
                const label = `${selector}`;
                
                // Set font and measure text
                ctx.font = 'bold 18px Arial';
                ctx.textBaseline = 'middle';
                ctx.textAlign = 'center';
                const labelMetrics = ctx.measureText(label);
                const labelWidth = labelMetrics.width;
                const labelHeight = 20; // Approximate height for 18px font
                
                // Calculate center position of the element
                const centerX = x + width / 2;
                const centerY = y + height / 2;
                
                // Draw label background for better readability
                // ctx.fillStyle = 'rgba(255, 255, 255, 1.0)';
                // ctx.fillRect(centerX - labelWidth/2 - 4, centerY - labelHeight/2 - 2, labelWidth + 8, labelHeight + 4);
                
                // Draw text shadow/halo effect for better readability
                ctx.fillStyle = 'rgba(0, 0, 0, 0.8)'; // Black shadow
                ctx.fillText(label, centerX - 1, centerY - 1);
                ctx.fillText(label, centerX + 1, centerY - 1);
                ctx.fillText(label, centerX - 1, centerY + 1);
                ctx.fillText(label, centerX + 1, centerY + 1);
                
                // Draw main label text
                ctx.fillStyle = strokeColor;
                ctx.fillText(label, centerX, centerY);
                
                // Print selector to console
                console.log(`Element ${selector}`);
                
            } catch (error) {
                console.error('Error drawing bounding box for element:', element, error);
            }
        });
    }

    // Function to handle window resize
    function handleResize() {
        const canvas = document.querySelector('#bounding-boxes-canvas');
        if (canvas) {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            // Redraw boxes after resize
            try {
                const elements = window.getTopLevelElements ? window.getTopLevelElements() : [];
                if (elements && elements.length > 0) {
                    drawBoundingBoxes(elements);
                }
            } catch (error) {
                console.error('Error redrawing bounding boxes after resize:', error);
            }
        }
    }

    // Function to toggle visualization
    function toggleVisualization() {
        const canvas = document.querySelector('#bounding-boxes-canvas');
        if (canvas) {
            canvas.remove();
        } else {
            try {
                const elements = window.getTopLevelElements ? window.getTopLevelElements() : [];
                if (elements && elements.length > 0) {
                    drawBoundingBoxes(elements);
                } else {
                    console.warn('No elements found to visualize');
                }
            } catch (error) {
                console.error('Error toggling visualization:', error);
            }
        }
    }

    // Function to clear the canvas
    function clearCanvas() {
        const canvas = document.querySelector('#bounding-boxes-canvas');
        if (canvas) {
            canvas.remove();
            console.log('Canvas cleared');
        } else {
            console.log('No canvas found to clear');
        }
    }

    // Function to draw a dot at given coordinates
    function drawDot(x, y, color = 'red', size = 15) {
        // Create or get canvas
        let canvas = document.querySelector('#bounding-boxes-canvas');
        if (!canvas) {
            canvas = createCanvasOverlay();
            canvas.id = 'bounding-boxes-canvas';
        }

        const ctx = canvas.getContext('2d');
        
        // Save the current context state
        ctx.save();
        
        // Set the dot properties
        ctx.fillStyle = color;
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 2;
        
        // Draw the dot (circle)
        ctx.beginPath();
        ctx.arc(x, y, size, 0, 2 * Math.PI);
        ctx.fill();
        ctx.stroke();
        
        // Add a white center for better visibility
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(x, y, size * 0.6, 0, 2 * Math.PI);
        ctx.fill();
        
        // Restore the context state
        ctx.restore();
        
        console.log(`Drew ${color} dot at (${x}, ${y}) with size ${size}`);
    }

    // Function to draw a ruler with labels every 50px
    function drawRuler() {
        // Create or get canvas
        let canvas = document.querySelector('#bounding-boxes-canvas');
        if (!canvas) {
            canvas = createCanvasOverlay();
            canvas.id = 'bounding-boxes-canvas';
        }

        const ctx = canvas.getContext('2d');
        
        // Save the current context state
        ctx.save();
        
        const width = canvas.width;
        const height = canvas.height;
        
        // Set ruler properties (more transparent)
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.lineWidth = 1;
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Draw horizontal ruler (top)
        ctx.beginPath();
        ctx.moveTo(0, 20);
        ctx.lineTo(width, 20);
        ctx.stroke();
        
        // Draw vertical ruler (left)
        ctx.beginPath();
        ctx.moveTo(20, 0);
        ctx.lineTo(20, height);
        ctx.stroke();
        
        // Draw horizontal tick marks and labels (every 50px)
        for (let x = 0; x <= width; x += 50) {
            // Draw tick mark
            ctx.beginPath();
            ctx.moveTo(x, 15);
            ctx.lineTo(x, 25);
            ctx.stroke();
            
            // Draw label
            ctx.fillText(x.toString(), x, 8);
        }
        
        // Draw vertical tick marks and labels (every 50px)
        for (let y = 0; y <= height; y += 50) {
            // Draw tick mark
            ctx.beginPath();
            ctx.moveTo(15, y);
            ctx.lineTo(25, y);
            ctx.stroke();
            
            // Draw label (rotated for vertical ruler)
            ctx.save();
            ctx.translate(8, y);
            ctx.rotate(-Math.PI / 2);
            ctx.fillText(y.toString(), 0, 0);
            ctx.restore();
        }
        
        // Draw corner label (more transparent)
        ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
        ctx.fillRect(0, 0, 30, 30);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.font = 'bold 10px Arial';
        ctx.fillText('0,0', 15, 15);
        
        // Restore the context state
        ctx.restore();
        
        console.log(`Drew ruler for ${width}x${height} viewport`);
    }

    // Add event listeners
    window.addEventListener('resize', handleResize);

    // Export functions to global scope for compatibility
    window.drawBoundingBoxes = drawBoundingBoxes;
    window.toggleVisualization = toggleVisualization;
    window.clearCanvas = clearCanvas;
    window.drawDot = drawDot;
    window.drawRuler = drawRuler;

    // // Main entry point for DOM Parser - Public API
    // // This file serves as the main export for the library



    // Function to clean objects for JSON serialization
    function cleanForSerialization(obj) {
        if (obj === null || obj === undefined) {
            return obj;
        }
        
        if (typeof obj === 'object') {
            if (Array.isArray(obj)) {
                return obj.map(item => cleanForSerialization(item));
            } else {
                const cleaned = {};
                for (const [key, value] of Object.entries(obj)) {
                    // Skip DOM objects and functions
                    if (key === 'object' || key === 'element' || key === 'node' || 
                        typeof value === 'function' || 
                        (value && value.nodeType !== undefined)) {
                        continue;
                    }
                    cleaned[key] = cleanForSerialization(value);
                }
                return cleaned;
            }
        }
        
        return obj;
    }

    // Custom cleaning function for processing steps that preserves element data
    function cleanProcessingStep(obj) {
        if (obj === null || obj === undefined) {
            return obj;
        }
        
        if (typeof obj === 'object') {
            if (Array.isArray(obj)) {
                return obj.map(item => cleanProcessingStep(item));
            } else {
                const cleaned = {};
                for (const [key, value] of Object.entries(obj)) {
                    // For processing steps, we want to keep the element data but remove DOM objects
                    if (key === 'object' && value && value.nodeType !== undefined) {
                        // Skip DOM objects
                        continue;
                    } else if (key === 'element' && value && value.object) {
                        // Keep element data but remove the DOM object
                        const cleanedElement = { ...value };
                        delete cleanedElement.object;
                        cleaned[key] = cleanedElement;
                    } else if (typeof value === 'function' || 
                        (value && value.nodeType !== undefined)) {
                        // Skip functions and DOM objects
                        continue;
                    } else {
                        cleaned[key] = cleanProcessingStep(value);
                    }
                }
                return cleaned;
            }
        }
        
        return obj;
    }

    // Global storage for processing steps
    window.domParserProcessingSteps = {
        rawActions: null,
        groupedActions: null,
        scoredActions: null,
        transformedActions: null,
        filteredActions: null,
        mappedActions: null,
        fieldFilteredActions: null
    };

    // Helper functions to retrieve processing steps
    function getRawActions() {
        return window.domParserProcessingSteps.rawActions;
    }

    function getGroupedActions() {
        return window.domParserProcessingSteps.groupedActions;
    }

    function getScoredActions() {
        return window.domParserProcessingSteps.scoredActions;
    }

    function getTransformedActions() {
        return window.domParserProcessingSteps.transformedActions;
    }

    function getFilteredActions() {
        return window.domParserProcessingSteps.filteredActions;
    }

    function getMappedActions() {
        return window.domParserProcessingSteps.mappedActions;
    }

    function getFieldFilteredActions() {
        return window.domParserProcessingSteps.fieldFilteredActions;
    }

    // Main extraction function with optimizations
    function extractElements(config = null) {
        // Initialize result object
        perfStart('metadata-except-actions', 'Extract all metadata (forms, media, links, etc.) except actions');
        const result = {
            // Individual element extraction parameters
            meta: null,
            outline: null,
            text: null,
            forms: null,
            media: null,
            links: null,
            structuredData: null,
            dynamic: null,
            layout: null,
            pagination: null,
            
            // Only store mapped actions in result
            actions: []
        };

        perfEnd('metadata-except-actions');
        
        // Extract element extraction config
        const elementConfig = config?.element_extraction || {};
        const enableMapping = config?.element_extraction?.actions?.enable_mapping !== false; // Default to true
        const showBoundingBoxes = config?.element_extraction?.actions?.show_bounding_boxes ?? true; // Default to true
        
        // Helper function to check if extraction is enabled
        const shouldExtract = (key) => {
            if (!config) return true; // If no config, extract everything
            return elementConfig[key] !== false; // Default to true if not specified
        };
        
        // Conditionally extract elements based on config
        if (shouldExtract('extract_meta_data')) {
            result.meta = extractMetaData();
        }
        
        if (shouldExtract('extract_document_outline')) {
            result.outline = extractDocumentOutline();
        }
        
        if (shouldExtract('extract_text_content')) {
            result.text = extractTextContent();
        }
        
        if (shouldExtract('extract_forms')) {
            result.forms = extractForms();
        }
        
        if (shouldExtract('extract_media')) {
            result.media = extractMedia();
        }
        
        if (shouldExtract('extract_links')) {
            result.links = extractLinks();
        }
        
        if (shouldExtract('extract_structured_data')) {
            result.structuredData = extractStructuredData();
        }
        
        if (shouldExtract('extract_dynamic_state')) {
            result.dynamic = extractDynamicState();
        }
        
        if (shouldExtract('extract_layout_info')) {
            result.layout = extractLayoutInfo();
        }
        
        if (shouldExtract('extract_pagination_info')) {
            result.pagination = extractPaginationInfo();
        }
        
        // Initialize performance tracking and caches
        enablePerf();
        clearPerf();
        perfStart('extractElementsTotal', 'Perf for the entire extraction');

        // Clear selector mapping at the start of each extraction
        clearSelectorMap();
        clearTopLevelElementsCache();
        clearStyleCache();
        clearSelectorCache();

        // Store all interactive elements for priority filtering
        perfStart('interactiveElements', 'Process interactive elements');

        // Checkpoint 1: Raw actions
        const foundElements = extractActions();
        // Convert Map to array for storage
        const rawArray = Array.from(foundElements.entries()).map(([key, value]) => ({
            key: key,
            element: value
        }));
        
        window.domParserProcessingSteps.rawActions = cleanProcessingStep(rawArray);
        // Process found elements (debug logging removed for cleaner output)

        // Checkpoint 2: Grouped actions
        perfStart('dfsGrouping', 'Group actions using DFS');
        const dfsGroups = groupActionableElementsDFS(foundElements);
        // Convert Map to array for storage
        const groupedArray = Array.from(dfsGroups.entries()).map(([key, value]) => ({
            key: key,
            element: value
        }));
        window.domParserProcessingSteps.groupedActions = cleanProcessingStep(groupedArray);
        perfEnd('dfsGrouping');

        // Checkpoint 3: Scored actions
        perfStart('topLevelElements');
        const scoredElements = getTopLevelElements(dfsGroups);
        // Convert Map to array for storage
        const scoredArray = Array.from(scoredElements.entries()).map(([key, value]) => ({
            key: key,
            element: value
        }));
        window.domParserProcessingSteps.scoredActions = cleanProcessingStep(scoredArray);
        perfEnd('topLevelElements');

        // Checkpoint 4: Transformed actions
        perfStart('transform');
        const finalStructure = transformTopLevelElements(dfsGroups, config);
        window.domParserProcessingSteps.transformedActions = cleanForSerialization(finalStructure);
        perfEnd('transform');
        
        // Checkpoint 5: Filtered actions
        perfStart('occlusionFilter');
        const filteredStructure = filterOccludedElements(finalStructure);
        window.domParserProcessingSteps.filteredActions = cleanForSerialization(filteredStructure);
        perfEnd('occlusionFilter');

        // Checkpoint 6: Mapped actions (final output)
        perfStart('selectorMapping');
        let mappedStructure;
        if (enableMapping){
            mappedStructure = filteredStructure.map(element => {
                const selectorId = getSelectorId(element.selector);
                return {
                    ...element,
                    selector: selectorId
                };
            });
        } else {
            mappedStructure = filteredStructure;
        }

        window.domParserProcessingSteps.mappedActions = cleanForSerialization(mappedStructure);
        perfEnd('selectorMapping');
        
        // Draw bounding boxes for top-level elements (if enabled)
        if (showBoundingBoxes) {
            perfStart('drawBoundingBoxes');
            drawBoundingBoxes(cleanForSerialization(mappedStructure));
            perfEnd('drawBoundingBoxes');
        }

        // return result;
        // Apply action field filtering to filtered actions
        let fieldFilteredStructure = mappedStructure;
        if (elementConfig && elementConfig.actions && elementConfig.actions.action_filters) {
            fieldFilteredStructure = mappedStructure.map(action => filterActionFields(action, elementConfig.actions));
        }

        window.domParserProcessingSteps.fieldFilteredActions = cleanForSerialization(fieldFilteredStructure);

        result.actions = window.domParserProcessingSteps.fieldFilteredActions;

        perfEnd('extractElementsTotal');

        // Use mapped actions from global storage
        const cleanMappedStructure = window.domParserProcessingSteps.mappedActions || [];

        // Calculate and print the size in KB
        const jsonString = JSON.stringify(cleanMappedStructure);
        const sizeInBytes = new Blob([jsonString]).size;
        const sizeInKB = (sizeInBytes / 1024).toFixed(2);
        console.log(`\nFinal structure size: ${sizeInKB} KB (${sizeInBytes} bytes)`);
        console.log(`Number of elements: ${cleanMappedStructure.length}`);

        // Print all processing steps
        console.log('==========================================');
        console.log('ALL PROCESSING STEPS:');
        console.log('==========================================');
        console.log('Raw Actions Count:', window.domParserProcessingSteps.rawActions?.length || 0);
        console.log('Grouped Actions Count:', window.domParserProcessingSteps.groupedActions?.length || 0);
        console.log('Scored Actions Count:', window.domParserProcessingSteps.scoredActions?.length || 0);
        console.log('Transformed Actions Count:', window.domParserProcessingSteps.transformedActions?.length || 0);
        console.log('Filtered Actions Count:', window.domParserProcessingSteps.filteredActions?.length || 0);
        console.log('Mapped Actions Count:', window.domParserProcessingSteps.mappedActions?.length || 0);
        
        console.log('==========================================');
        console.log('RAW ACTIONS:');
        console.log('==========================================');
        console.log(JSON.stringify(window.domParserProcessingSteps.rawActions, null, 2));
        
        console.log('==========================================');
        console.log('GROUPED ACTIONS:');
        console.log('==========================================');
        console.log(JSON.stringify(window.domParserProcessingSteps.groupedActions, null, 2));
        
        console.log('==========================================');
        console.log('SCORED ACTIONS:');
        console.log('==========================================');
        console.log(JSON.stringify(window.domParserProcessingSteps.scoredActions, null, 2));
        
        console.log('==========================================');
        console.log('TRANSFORMED ACTIONS:');
        console.log('==========================================');
        console.log(JSON.stringify(window.domParserProcessingSteps.transformedActions, null, 2));
        
        console.log('==========================================');
        console.log('FILTERED ACTIONS:');
        console.log('==========================================');
        console.log(JSON.stringify(window.domParserProcessingSteps.filteredActions, null, 2));
        
        console.log('==========================================');
        console.log('MAPPED ACTIONS:');
        console.log('==========================================');
        console.log(JSON.stringify(window.domParserProcessingSteps.mappedActions, null, 2));

        console.log('==========================================');
        console.log('FIELD FILTERED ACTIONS:');
        console.log('==========================================');
        console.log(JSON.stringify(window.domParserProcessingSteps.fieldFilteredActions, null, 2));
        
        printPerfSummary();
        dumpTraceToFile("/tmp/trace.json");
        return result;
    }

    // // Function to clear the cache
    // function clearTopLevelElementsCache() {
    //     topLevelElementsCache.clear();
    // }

    // Global selector mapping
    // window.selectorMap = selectorMap;

    // Function to get or create selector ID
    function getSelectorId(selector) {
        if (!selectorMap.has(selector)) {
            selectorMap.set(selector, incrementSelectorId());
        }
        return String(selectorMap.get(selector));
    }

    // Function to get selector by ID
    function getSelectorById(id) {
        // Convert string ID to integer for comparison
        const numericId = parseInt(id, 10);
        
        for (const [selector, selectorId] of selectorMap) {
            if (selectorId === numericId) {
                return selector;
            }
        }
        return null;
    }

    // // Public API exports
    // export {
    //     // Main function
    //     extractElements,
    //     drawBoundingBoxes,
    //     toggleVisualization,
    //     clearCanvas,
    //     drawRuler,
    //     drawDot,
        
    //     // // Utility functions
    //     // clearTopLevelElementsCache,
    //     // transformTopLevelElements,
    //     // printProfilingSummary,
    //     // profilingData,
    //     // groupActionableElementsDFS,
    //     // // clearSelectorMapping,
    //     getSelectorId,
    //     getSelectorById,
        
    //     // // Element analysis
    //     // isVisible,
    //     // getElementType,
    //     // isInteractive,
    //     // getComputedStyles,
        
    //     // // Text extraction
        
    //     // extractDocumentOutline,
    //     // extractForms,
    //     // extractMedia,
    //     // extractLinks,
    //     // extractStructuredData,
    //     // extractDynamicState,
    //     // extractLayoutInfo,
    //     // extractPaginationInfo,

    //     // CONTAINER_CLASSES,
    //     // CONTAINER_ATTRS,
    // };

    // For backward compatibility, also export to window
    if (typeof window !== 'undefined') {
        window.extractElements = extractElements;
        window.drawBoundingBoxes = drawBoundingBoxes;
        window.toggleVisualization = toggleVisualization;
        window.clearCanvas = clearCanvas;
        window.getSelectorId = getSelectorId;
        window.getSelectorById = getSelectorById;
        window.drawRuler = drawRuler;
        window.drawDot = drawDot;
        
        // Export helper functions for processing steps
        window.getRawActions = getRawActions;
        window.getGroupedActions = getGroupedActions;
        window.getScoredActions = getScoredActions;
        window.getTransformedActions = getTransformedActions;
        window.getFilteredActions = getFilteredActions;
        window.getMappedActions = getMappedActions;
        window.getFieldFilteredActions = getFieldFilteredActions;
    }

})();
//# sourceMappingURL=dom-parser.js.map
