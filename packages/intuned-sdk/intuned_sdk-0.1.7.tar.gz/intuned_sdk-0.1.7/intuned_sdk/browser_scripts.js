(function () {
    'use strict';

    function convertElementToMarkdown(element) {
        const mdCharsMatcher = /([\\[\]()])/g;
        function escapeMd(text) {
            // Escapes markdown-sensitive characters within other markdown constructs.
            return text.replace(mdCharsMatcher, "\\$1");
        }
        function listNumberingStart(attrs) {
            const start = attrs.getNamedItem("start")?.value;
            if (start) {
                return parseInt(start, 10) - 1;
            }
            else {
                return 0;
            }
        }
        // Define the characters that require escaping
        const slashChars = "\\`*_{}[]()#+-.!";
        // Escape any special regex characters in slashChars
        const escapedSlashChars = slashChars.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
        // Create the regular expression
        const mdBackslashMatcher = new RegExp(`\\\\(?=[${escapedSlashChars}])`, "g");
        const mdDotMatcher = new RegExp(`^(\\s*\\d+)(\\.)(?=\\s)`, "gm");
        const mdPlusMatcher = new RegExp(`^(\\s*)(\\+)(?=\\s)`, "gm");
        const mdDashMatcher = new RegExp(`^(\\s*)(-)(?=\\s|-)`, "gm");
        function escapeMdSection(text) {
            text = text.replace(mdBackslashMatcher, "\\\\");
            text = text.replace(mdDotMatcher, "$1\\$2");
            text = text.replace(mdPlusMatcher, "$1\\$2");
            text = text.replace(mdDashMatcher, "$1\\$2");
            return text;
        }
        function isFirstTbody(element) {
            const previousSibling = element.previousSibling;
            return (element.nodeName === "TBODY" &&
                (!previousSibling ||
                    (previousSibling.nodeName === "THEAD" &&
                        /^\s*$/i.test(previousSibling.textContent ?? ""))));
        }
        function isHeadingRow(tr) {
            const parentNode = tr.parentNode;
            return (parentNode.nodeName === "THEAD" ||
                (parentNode.firstChild === tr &&
                    (parentNode.nodeName === "TABLE" ||
                        isFirstTbody(parentNode)) &&
                    Array.from(tr.childNodes).every(function (n) {
                        return n.nodeName === "TH";
                    })));
        }
        class Html2Text {
            p_p = 0;
            abbrData; // last inner HTML (for abbr being defined)
            pre = false;
            code = false;
            startPre = false;
            blockquote = 0;
            list = [];
            start = true;
            breakToggle = "";
            space;
            lastWasNewLine = false;
            a = null;
            outCount = 0;
            baseurl;
            abbrList = {};
            outText = "";
            outTextList = [];
            abbr_title;
            skipInternalLinks = true;
            aStack = [];
            maybeAutomaticLink;
            lastWasList = false;
            absoluteUrlMatcher = new RegExp("^[a-zA-Z+]+://");
            emphasis_mark = "_";
            strong_mark = "**";
            break() {
                if (this.p_p === 0) {
                    this.p_p = 1;
                }
            }
            softBreak() {
                this.break();
                this.breakToggle = "  ";
            }
            processOutput(data, pureData = 0, force = 0) {
                if (this.abbrData !== undefined) {
                    this.abbrData += data;
                }
                if (pureData && !this.pre) {
                    data = data.replace(/\s+/g, " ");
                    if (data && data[0] === " ") {
                        this.space = 1;
                        data = data.substring(1);
                    }
                }
                if (!data && force !== "end")
                    return;
                if (this.startPre) {
                    if (!data.startsWith("\n")) {
                        data = "\n" + data;
                    }
                }
                let newLineIndent = ">".repeat(this.blockquote ?? 0);
                if (!(force === "end" && data && data[0] === ">") && this.blockquote) {
                    newLineIndent += " ";
                }
                if (this.pre) {
                    if (this.list.length === 0) {
                        newLineIndent += "    ";
                    }
                    else {
                        for (let i = 0; i < this.list.length + 1; i++) {
                            newLineIndent += "    ";
                        }
                    }
                    data = data.replace(/\n/g, `\n${newLineIndent}`);
                }
                if (this.startPre) {
                    this.startPre = false;
                    if (this.list.length > 0) {
                        data = data.trimStart();
                    }
                }
                if (this.start) {
                    this.space = 0;
                    this.p_p = 0;
                    this.start = false;
                }
                if (force === "end") {
                    this.p_p = 0;
                    this.out("\n");
                    this.space = 0;
                }
                if (this.p_p) {
                    this.out((this.breakToggle + "\n" + newLineIndent).repeat(this.p_p));
                    this.space = 0;
                    this.breakToggle = "";
                }
                if (this.space) {
                    if (!this.lastWasNewLine) {
                        this.out(" ");
                    }
                    this.space = 0;
                }
                if (this.a && force === "end") {
                    if (force === "end") {
                        this.out("\n");
                    }
                    const newA = this.a.filter((link) => {
                        if (this.outCount > link.outcount) {
                            this.out("   [" +
                                link.count +
                                "]: " +
                                new URL(link.href, this.baseurl).toString());
                            if (link.title) {
                                this.out(" (" + link.title + ")");
                            }
                            this.out("\n");
                            return false;
                        }
                        return true;
                    });
                    if (this.a.length !== newA.length) {
                        this.out("\n");
                    }
                    this.a = newA;
                }
                if (this.abbrList && force === "end") {
                    for (const [abbr, definition] of Object.entries(this.abbrList)) {
                        this.out("\n *[" + abbr + "]: " + definition + "\n");
                    }
                }
                this.p_p = 0;
                this.out(data);
                this.outCount++;
            }
            out(string) {
                this.outTextList.push(string);
                if (string) {
                    this.lastWasNewLine = string.charAt(string.length - 1) === "\n";
                }
            }
            getResult() {
                this.processOutput("", 0, "end");
                this.outText = this.outTextList.join("");
                this.outText = this.outText.replace("&nbsp_place_holder;", " ");
                return this.outText;
            }
            getHeadingLevel(tag) {
                if (tag[0] === "h" && tag.length === 2) {
                    try {
                        const n = parseInt(tag[1]);
                        if (!isNaN(n) && n >= 1 && n <= 9) {
                            return n;
                        }
                    }
                    catch (error) {
                        return 0;
                    }
                }
                return 0;
            }
            padding() {
                this.p_p = 2;
            }
            handleData(node) {
                if (this.maybeAutomaticLink) {
                    const href = this.maybeAutomaticLink;
                    if (href?.value === node.nodeValue &&
                        this.absoluteUrlMatcher.test(href.value)) {
                        this.processOutput(`<${node.nodeValue}>`);
                        return;
                    }
                    else {
                        this.processOutput("[");
                        this.maybeAutomaticLink = null;
                    }
                }
                if (!this.code && !this.pre && node.nodeValue) {
                    const data = escapeMdSection(node.nodeValue);
                    this.processOutput(data, 1);
                    return;
                }
                this.processOutput(node.textContent || "", 1);
            }
            handleTag(node) {
                const tag = node.nodeName.toLowerCase();
                if (["head", "style", "script"].includes(tag)) {
                    return;
                }
                if (this.getHeadingLevel(tag)) {
                    this.padding();
                    this.processOutput("#".repeat(this.getHeadingLevel(tag)) + " ");
                }
                if (tag == "br")
                    this.processOutput("  \n");
                if (tag == "hr") {
                    this.padding();
                    this.processOutput("---");
                    this.padding();
                }
                if (tag == "blockquote") {
                    this.padding();
                    this.processOutput("> ", 0, 1);
                }
            }
            handleTagPrefix(node) {
                const nodeName = node.nodeName.toLowerCase();
                let attrs = node.nodeType === node.ELEMENT_NODE
                    ? node.attributes
                    : null;
                if (["table"].includes(nodeName)) {
                    this.padding();
                }
                if (nodeName == "td" || nodeName == "th") {
                    const index = Array.from(node.parentNode?.children ?? []).indexOf(node);
                    let prefix = " ";
                    if (index === 0)
                        prefix = "| ";
                    this.processOutput(prefix);
                    // this.break();
                }
                if (["div", "p"].includes(nodeName)) {
                    this.padding();
                }
                if (nodeName === "blockquote") {
                    this.blockquote += 1;
                }
                if (nodeName === "pre") {
                    this.pre = true;
                    this.startPre = true;
                    this.padding();
                }
                if (["code", "tt"].includes(nodeName)) {
                    this.processOutput("`");
                }
                if (["em", "i", "u"].includes(nodeName)) {
                    this.processOutput(this.emphasis_mark);
                }
                if (["strong", "b"].includes(nodeName)) {
                    this.processOutput(this.strong_mark);
                }
                if (["del", "strike", "s"].includes(nodeName)) {
                    this.processOutput("<" + nodeName + ">");
                }
                if (nodeName === "abbr") {
                    this.abbr_title = null;
                    this.abbrData = "";
                    const title = attrs && attrs.getNamedItem("title");
                    if (attrs && title) {
                        this.abbr_title = title.value;
                    }
                }
                if (nodeName === "dl") {
                    this.padding();
                }
                if (nodeName === "dd") {
                    this.processOutput("    ");
                }
                if (nodeName == "a") {
                    const href = attrs ? attrs.getNamedItem("href") : null;
                    if (href && !(this.skipInternalLinks && href.value.startsWith("#"))) {
                        this.aStack.push(attrs);
                        this.maybeAutomaticLink = href;
                    }
                    else {
                        this.aStack.push(null);
                    }
                }
                if (nodeName === "img") {
                    const src = attrs ? attrs.getNamedItem("src") : null;
                    if (src) {
                        node.setAttribute("href", src.value);
                        attrs = node.attributes;
                        const alt = attrs.getNamedItem("alt")?.value;
                        this.processOutput("![" + escapeMd(alt ?? "") + "]");
                        this.processOutput("(" + escapeMd(attrs.getNamedItem("href")?.value ?? "") + ")");
                    }
                }
                if (["ul", "ol"].includes(nodeName)) {
                    const listStyle = nodeName;
                    const numberingStart = listNumberingStart(node.attributes);
                    this.list.push({ name: listStyle, num: numberingStart });
                    this.lastWasList = true;
                }
                else {
                    this.lastWasList = false;
                }
                if (nodeName === "li") {
                    let li;
                    this.break();
                    if (this.list.length > 0) {
                        li = this.list[this.list.length - 1];
                    }
                    else {
                        li = { name: "ul", num: 0 };
                    }
                    const nestCount = this.list.length;
                    this.processOutput("   ".repeat(nestCount));
                    if (li["name"] == "ul")
                        this.processOutput("*" + " ");
                    else if (li["name"] == "ol") {
                        li["num"] += 1;
                        this.processOutput(li["num"] + ". ");
                    }
                    this.start = true;
                }
            }
            handleTagSuffix(node) {
                const nodeName = node.nodeName.toLowerCase();
                if (nodeName === "blockquote") {
                    this.blockquote -= 1;
                }
                if (nodeName == "td" || nodeName == "th") {
                    this.processOutput(" |");
                }
                if (nodeName == "tr") {
                    const cell = (content, node) => {
                        const index = Array.from(node.parentNode.childNodes).indexOf(node);
                        let prefix = " ";
                        if (index === 0)
                            prefix = "| ";
                        return prefix + content + " |";
                    };
                    let borderCells = "";
                    const alignMap = { left: ":--", right: "--:", center: ":-:" };
                    if (isHeadingRow(node)) {
                        for (let i = 0; i < node.children.length; i++) {
                            let border = "---";
                            const align = (node.children[i].getAttribute("align") || "").toLowerCase();
                            if (align)
                                border = alignMap[align] || border;
                            borderCells += cell(border, node.childNodes[i]);
                        }
                    }
                    this.processOutput(borderCells ? "\n" + borderCells + "\n" : "\n");
                }
                if (nodeName === "pre") {
                    this.pre = false;
                    this.padding();
                }
                if (["code", "tt"].includes(nodeName)) {
                    this.processOutput("`");
                }
                if (["em", "i", "u"].includes(nodeName)) {
                    this.processOutput(this.emphasis_mark);
                }
                if (["strong", "b"].includes(nodeName)) {
                    this.processOutput(this.strong_mark);
                }
                if (["div", "p"].includes(nodeName)) {
                    this.padding();
                }
                if (["del", "strike", "s"].includes(nodeName)) {
                    this.processOutput("</" + nodeName + ">");
                }
                if (nodeName === "abbr") {
                    if (this.abbr_title && this.abbrData) {
                        this.abbrList[this.abbrData] = this.abbr_title;
                        this.abbr_title = null;
                    }
                    this.abbrData = "";
                }
                if (nodeName === "dt") {
                    this.break();
                }
                if (nodeName === "dd") {
                    this.break();
                }
                if (nodeName === "a") {
                    if (this.aStack.length > 0) {
                        const a = this.aStack.pop();
                        if (this.maybeAutomaticLink) {
                            this.maybeAutomaticLink = null;
                        }
                        else if (a) {
                            this.processOutput(`](${escapeMd(a.getNamedItem("href")?.value || "")})`);
                        }
                    }
                }
                if (["ul", "ol"].includes(nodeName)) {
                    if (this.list.length > 0)
                        this.list.pop();
                    this.lastWasList = true;
                }
                else {
                    this.lastWasList = false;
                }
                if (nodeName === "li") {
                    this.break();
                }
            }
            previousIndex(attrs) {
                // Returns the index of a certain set of attributes (of a link) in the
                // this.a list.
                // If the set of attributes is not found, returns null.
                const href = attrs.getNamedItem("href");
                if (!attrs.getNamedItem("href"))
                    return null;
                let itemIndex = -1;
                for (const a of this.a ?? []) {
                    itemIndex += 1;
                    let match = false;
                    if (a.getNamedItem("href") === href) {
                        if (a.getNamedItem("title") || attrs.getNamedItem("title")) {
                            if (a.getNamedItem("title") &&
                                attrs.getNamedItem("title") &&
                                a.getNamedItem("title") === attrs.getNamedItem("title")) {
                                match = true;
                            }
                        }
                        else {
                            match = true;
                        }
                    }
                    if (match)
                        return itemIndex;
                }
                return null;
            }
            handle(htmlElement) {
                // Nodes to be removed
                const filteredNodes = ["style", "script", "noscript"];
                for (const node of filteredNodes) {
                    const nodeSelectors = htmlElement.querySelectorAll(node);
                    nodeSelectors.forEach((nodeSelector) => {
                        if (nodeSelector && nodeSelector.parentNode) {
                            nodeSelector.parentNode.removeChild(nodeSelector);
                        }
                    });
                }
                // Get the cleaned-up HTML content
                const htmlContent = htmlElement.outerHTML;
                const parser = new DOMParser();
                const doc = parser.parseFromString(htmlContent, "text/html");
                const traverseDOM = (node) => {
                    const tag = node.nodeName.toLowerCase();
                    if (node.nodeType === node.TEXT_NODE) {
                        const element = node;
                        this.handleData(element);
                        return;
                    }
                    if (node.nodeType === node.ELEMENT_NODE) {
                        const element = node;
                        this.handleTag(element);
                    }
                    if (!["head", "style", "script"].includes(tag)) {
                        this.handleTagPrefix(node);
                        node.childNodes.forEach((child) => traverseDOM(child));
                        this.handleTagSuffix(node);
                    }
                };
                traverseDOM(doc.documentElement);
                return this.getResult();
            }
        }
        const converter = new Html2Text();
        const result = converter.handle(element);
        return result;
    }

    var node = {};

    var htmlToMarkdownAST$1 = {};

    var ElementNode = {};

    Object.defineProperty(ElementNode, "__esModule", { value: true });
    ElementNode._Node = void 0;
    // this is by value copy of the global Node
    ElementNode._Node = {
        /** node is an element. */
        ELEMENT_NODE: 1,
        ATTRIBUTE_NODE: 2,
        /** node is a Text node. */
        TEXT_NODE: 3,
        /** node is a CDATASection node. */
        CDATA_SECTION_NODE: 4,
        ENTITY_REFERENCE_NODE: 5,
        ENTITY_NODE: 6,
        /** node is a ProcessingInstruction node. */
        PROCESSING_INSTRUCTION_NODE: 7,
        /** node is a Comment node. */
        COMMENT_NODE: 8,
        /** node is a document. */
        DOCUMENT_NODE: 9,
        /** node is a doctype. */
        DOCUMENT_TYPE_NODE: 10,
        /** node is a DocumentFragment node. */
        DOCUMENT_FRAGMENT_NODE: 11,
        NOTATION_NODE: 12,
        /** Set when node and other are not in the same tree. */
        DOCUMENT_POSITION_DISCONNECTED: 0x01,
        /** Set when other is preceding node. */
        DOCUMENT_POSITION_PRECEDING: 0x02,
        /** Set when other is following node. */
        DOCUMENT_POSITION_FOLLOWING: 0x04,
        /** Set when other is an ancestor of node. */
        DOCUMENT_POSITION_CONTAINS: 0x08,
        /** Set when other is a descendant of node. */
        DOCUMENT_POSITION_CONTAINED_BY: 0x10,
        DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC: 0x20,
    };

    Object.defineProperty(htmlToMarkdownAST$1, "__esModule", { value: true });
    htmlToMarkdownAST$1.htmlToMarkdownAST = htmlToMarkdownAST;
    const ElementNode_1$1 = ElementNode;
    function htmlToMarkdownAST(element, options, indentLevel = 0) {
        let result = [];
        const debugLog = (message) => {
            if (options?.debug) {
                console.log(message);
            }
        };
        const debugError = (message, error) => {
            if (options?.debug) {
                console.error(message, error);
            }
        }
        element.childNodes.forEach((childElement) => {
            const overriddenElementProcessing = options?.overrideElementProcessing?.(childElement, options, indentLevel);
            if (overriddenElementProcessing) {
                debugLog(`Element Processing Overridden: '${childElement.nodeType}'`);
                result.push(...overriddenElementProcessing);
            }
            else if (childElement.nodeType === ElementNode_1$1._Node.TEXT_NODE) {
                const textContent = escapeMarkdownCharacters(childElement.textContent?.trim() ?? '');
                if (textContent && !!childElement.textContent) {
                    debugLog(`Text Node: '${textContent}'`);
                    // preserve whitespaces when text childElement is not empty
                    result.push({ type: 'text', content: childElement.textContent?.trim() });
                }
            }
            else if (childElement.nodeType === ElementNode_1$1._Node.ELEMENT_NODE) {
                const elem = childElement;
                if (/^h[1-6]$/i.test(elem.tagName)) {
                    const level = parseInt(elem.tagName.substring(1));
                    const content = escapeMarkdownCharacters(elem.textContent || '').trim();
                    if (content) {
                        debugLog(`Heading ${level}: '${elem.textContent}'`);
                        result.push({ type: 'heading', level, content });
                    }
                }
                else if (elem.tagName.toLowerCase() === 'p') {
                    debugLog("Paragraph");
                    result.push(...htmlToMarkdownAST(elem, options));
                    // Add a new line after the paragraph
                    result.push({ type: 'text', content: '\n\n' });
                }
                else if (elem.tagName.toLowerCase() === 'a') {
                    debugLog(`Link: '${elem.href}' with text '${elem.textContent}'`);
                    // Check if the href is a data URL for an image
                    if (typeof elem.href === 'string' && elem.href.startsWith("data:image")) {
                        // If it's a data URL for an image, skip this link
                        result.push({
                            type: 'link',
                            href: '-',
                            content: htmlToMarkdownAST(elem, options)
                        });
                    }
                    else {
                        // Process the link as usual
                        let href = elem.href;
                        if (typeof href === 'string') {
                            href = options?.websiteDomain && href.startsWith(options.websiteDomain) ?
                                href.substring(options.websiteDomain.length) : href;
                        }
                        else {
                            href = '#'; // Use a default value when href is not a string
                        }
                        // if all children are text,
                        if (Array.from(elem.childNodes).every(_ => _.nodeType === ElementNode_1$1._Node.TEXT_NODE)) {
                            result.push({
                                type: 'link',
                                href: href,
                                content: [{ type: 'text', content: elem.textContent?.trim() ?? '' }]
                            });
                        }
                        else {
                            result.push({
                                type: 'link',
                                href: href,
                                content: htmlToMarkdownAST(elem, options)
                            });
                        }
                    }
                }
                else if (elem.tagName.toLowerCase() === 'img') {
                    debugLog(`Image: src='${elem.src}', alt='${elem.alt}'`);
                    if (elem.src?.startsWith("data:image")) {
                        result.push({
                            type: 'image',
                            src: '-',
                            alt: escapeMarkdownCharacters(elem.alt)
                        });
                    }
                    else {
                        const src = options?.websiteDomain && elem.src?.startsWith(options.websiteDomain) ?
                            elem.src?.substring(options.websiteDomain.length) :
                            elem.src;
                        result.push({ type: 'image', src, alt: escapeMarkdownCharacters(elem.alt) });
                    }
                }
                else if (elem.tagName.toLowerCase() === 'video') {
                    debugLog(`Video: src='${elem.src}', poster='${elem.poster}', controls='${elem.controls}'`);
                    result.push({
                        type: 'video',
                        src: elem.src,
                        poster: escapeMarkdownCharacters(elem.poster),
                        controls: elem.controls
                    });
                }
                else if (elem.tagName.toLowerCase() === 'ul' || elem.tagName.toLowerCase() === 'ol') {
                    debugLog(`${elem.tagName.toLowerCase() === 'ul' ? 'Unordered' : 'Ordered'} List`);
                    result.push({
                        type: 'list',
                        ordered: elem.tagName.toLowerCase() === 'ol',
                        items: Array.from(elem.children).map(li => ({
                            type: 'listItem',
                            content: htmlToMarkdownAST(li, options, indentLevel + 1)
                        }))
                    });
                }
                else if (elem.tagName.toLowerCase() === 'br') {
                    debugLog("Line Break");
                    result.push({ type: 'text', content: '\n' });
                }
                else if (elem.tagName.toLowerCase() === 'table') {
                    debugLog("Table");
                    let colIds = [];
                    if (options?.enableTableColumnTracking) {
                        // Generate unique column IDs
                        const headerCells = Array.from(elem.querySelectorAll('th, td'));
                        headerCells.forEach((_, index) => {
                            colIds.push(`col-${index}`);
                        });
                    }
                    const tableRows = Array.from(elem.querySelectorAll('tr'));
                    const markdownTableRows = tableRows.map(row => {
                        let columnIndex = 0;
                        const cells = Array.from(row.querySelectorAll('th, td')).map((cell) => {
                            const colspan = parseInt(cell.getAttribute('colspan') || '1', 10);
                            const rowspan = parseInt(cell.getAttribute('rowspan') || '1', 10);
                            const cellNode = {
                                type: 'tableCell',
                                content: cell.nodeType === ElementNode_1$1._Node.TEXT_NODE
                                    ? escapeMarkdownCharacters(cell.textContent?.trim() ?? '')
                                    : htmlToMarkdownAST(cell, options, indentLevel + 1),
                                colId: colIds[columnIndex],
                                colspan: colspan > 1 ? colspan : undefined,
                                rowspan: rowspan > 1 ? rowspan : undefined
                            };
                            columnIndex += colspan;
                            return cellNode;
                        });
                        return { type: 'tableRow', cells };
                    });
                    if (markdownTableRows.length > 0) {
                        // Check if the first row contains header cells
                        const hasHeaders = tableRows[0].querySelector('th') !== null;
                        if (hasHeaders) {
                            // Create a header separator row
                            const headerSeparatorCells = Array.from(tableRows[0].querySelectorAll('th, td'))
                                .map(() => ({
                                type: 'tableCell',
                                content: '---',
                                colId: undefined,
                                colspan: undefined,
                                rowspan: undefined,
                            }));
                            const headerSeparatorRow = {
                                type: 'tableRow',
                                cells: headerSeparatorCells,
                            };
                            markdownTableRows.splice(1, 0, headerSeparatorRow);
                        }
                    }
                    result.push({ type: 'table', rows: markdownTableRows, colIds });
                }
                else if (elem.tagName.toLowerCase() === 'head' && !!options?.includeMetaData) {
                    const node = {
                        type: 'meta',
                        content: {
                            standard: {},
                            openGraph: {},
                            twitter: {},
                        }
                    };
                    elem.querySelectorAll('title')
                        .forEach(titleElem => {
                        node.content.standard['title'] = escapeMarkdownCharacters(titleElem.text);
                    });
                    // Extract meta tags
                    const metaTags = elem.querySelectorAll('meta');
                    const nonSemanticTagNames = [
                        "viewport",
                        "referrer",
                        "Content-Security-Policy"
                    ];
                    metaTags.forEach(metaTag => {
                        const name = metaTag.getAttribute('name');
                        const property = metaTag.getAttribute('property');
                        const content = metaTag.getAttribute('content');
                        if (property && property.startsWith('og:') && content) {
                            if (options.includeMetaData === 'extended') {
                                node.content.openGraph[property.substring(3)] = content;
                            }
                        }
                        else if (name && name.startsWith('twitter:') && content) {
                            if (options.includeMetaData === 'extended') {
                                node.content.twitter[name.substring(8)] = content;
                            }
                        }
                        else if (name && !nonSemanticTagNames.includes(name) && content) {
                            node.content.standard[name] = content;
                        }
                    });
                    // Extract JSON-LD data
                    if (options.includeMetaData === 'extended') {
                        const jsonLdData = [];
                        const jsonLDScripts = elem.querySelectorAll('script[type="application/ld+json"]');
                        jsonLDScripts.forEach(script => {
                            try {
                                const jsonContent = script.textContent;
                                if (jsonContent) {
                                    const parsedData = JSON.parse(jsonContent);
                                    jsonLdData.push(parsedData);
                                }
                            }
                            catch (error) {
                                debugError('Failed to parse JSON-LD', error);
                            }
                        });
                        node.content.jsonLd = jsonLdData;
                    }
                    result.push(node);
                }
                else {
                    const content = escapeMarkdownCharacters(elem.textContent || '');
                    switch (elem.tagName.toLowerCase()) {
                        case 'noscript':
                        case 'script':
                        case 'style':
                        case 'html':
                            // blackhole..
                            break;
                        case 'strong':
                        case 'b':
                            if (content) {
                                debugLog(`Bold: '${content}'`);
                                result.push({
                                    type: 'bold',
                                    content: htmlToMarkdownAST(elem, options, indentLevel + 1)
                                });
                            }
                            break;
                        case 'em':
                        case 'i':
                            if (content) {
                                debugLog(`Italic: '${content}'`);
                                result.push({
                                    type: 'italic',
                                    content: htmlToMarkdownAST(elem, options, indentLevel + 1)
                                });
                            }
                            break;
                        case 's':
                        case 'strike':
                            if (content) {
                                debugLog(`Strikethrough: '${content}'`);
                                result.push({
                                    type: 'strikethrough',
                                    content: htmlToMarkdownAST(elem, options, indentLevel + 1)
                                });
                            }
                            break;
                        case 'code':
                            if (content) {
                                // Handling inline code differently
                                const isCodeBlock = elem.parentNode && elem.parentNode.nodeName.toLowerCase() === 'pre';
                                debugLog(`${isCodeBlock ? 'Code Block' : 'Inline Code'}: '${content}'`);
                                const languageClass = elem.className?.split(" ").find(cls => cls.startsWith("language-"));
                                const language = languageClass ? languageClass.replace("language-", "") : "";
                                result.push({
                                    type: 'code',
                                    content: elem.textContent?.trim() ?? '',
                                    language,
                                    inline: !isCodeBlock
                                });
                            }
                            break;
                        case 'blockquote':
                            debugLog(`Blockquote`);
                            result.push({
                                type: 'blockquote',
                                content: htmlToMarkdownAST(elem, options)
                            });
                            break;
                        case 'article':
                        case 'aside':
                        case 'details':
                        case 'figcaption':
                        case 'figure':
                        case 'footer':
                        case 'header':
                        case 'main':
                        case 'mark':
                        case 'nav':
                        case 'section':
                        case 'summary':
                        case 'time':
                            debugLog(`Semantic HTML Element: '${elem.tagName}'`);
                            result.push({
                                type: 'semanticHtml',
                                htmlType: elem.tagName.toLowerCase(),
                                content: htmlToMarkdownAST(elem, options)
                            });
                            break;
                        default:
                            const unhandledElementProcessing = options?.processUnhandledElement?.(elem, options, indentLevel);
                            if (unhandledElementProcessing) {
                                debugLog(`Processing Unhandled Element: '${elem.tagName}'`);
                                result.push(...unhandledElementProcessing);
                            }
                            else {
                                debugLog(`Generic HTMLElement: '${elem.tagName}'`);
                                result.push(...htmlToMarkdownAST(elem, options, indentLevel + 1));
                            }
                            break;
                    }
                }
            }
        });
        return result;
    }
    function escapeMarkdownCharacters(text, isInlineCode = false) {
        if (isInlineCode || !text?.trim()) {
            // In inline code, we don't escape any characters
            return text;
        }
        // First, replace special HTML characters with their entity equivalents
        let escapedText = text.replace(/&/g, '&amp;') // Replace & first
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        // Then escape characters that have special meaning in Markdown
        escapedText = escapedText.replace(/([\\`*_{}[\]#+!|])/g, '\\$1');
        return escapedText;
    }

    var markdownASTToString = {};

    var hasRequiredMarkdownASTToString;

    function requireMarkdownASTToString () {
        if (hasRequiredMarkdownASTToString) return markdownASTToString;
        hasRequiredMarkdownASTToString = 1;
        Object.defineProperty(markdownASTToString, "__esModule", { value: true });
        markdownASTToString.markdownASTToString = markdownASTToString$1;
        const index_1 = requireNode();
        function markdownASTToString$1(nodes, options, indentLevel = 0) {
            let markdownString = '';
            markdownString += markdownMetaASTToString(nodes, options, indentLevel);
            markdownString += markdownContentASTToString(nodes, options, indentLevel);
            return markdownString;
        }
        function markdownMetaASTToString(nodes, options, indentLevel = 0) {
            let markdownString = '';
            if (options?.includeMetaData) {
                // include meta-data
                markdownString += '---\n';
                const node = (0, index_1.findInMarkdownAST)(nodes, _ => _.type === 'meta');
                if (node?.type === 'meta') {
                    if (node.content.standard) {
                        Object.keys(node.content.standard).forEach(key => {
                            markdownString += `${key}: "${node.content.standard[key]}"\n`;
                        });
                    }
                    if (options.includeMetaData === 'extended') {
                        if (node.content.openGraph) {
                            if (Object.keys(node.content.openGraph).length > 0) {
                                markdownString += 'openGraph:\n';
                                for (const [key, value] of Object.entries(node.content.openGraph)) {
                                    markdownString += `  ${key}: "${value}"\n`;
                                }
                            }
                        }
                        if (node.content.twitter) {
                            if (Object.keys(node.content.twitter).length > 0) {
                                markdownString += 'twitter:\n';
                                for (const [key, value] of Object.entries(node.content.twitter)) {
                                    markdownString += `  ${key}: "${value}"\n`;
                                }
                            }
                        }
                        if (node.content.jsonLd && node.content.jsonLd.length > 0) {
                            markdownString += 'schema:\n';
                            node.content.jsonLd.forEach(item => {
                                const { '@context': jldContext, '@type': jldType, ...semanticData } = item;
                                markdownString += `  ${jldType ?? '(unknown type)'}:\n`;
                                Object.keys(semanticData).forEach(key => {
                                    markdownString += `    ${key}: ${JSON.stringify(semanticData[key])}\n`;
                                });
                            });
                        }
                    }
                }
                markdownString += '---\n\n';
            }
            return markdownString;
        }
        function markdownContentASTToString(nodes, options, indentLevel = 0) {
            let markdownString = '';
            nodes.forEach((node) => {
                const indent = ' '.repeat(indentLevel * 2); // Adjust the multiplier for different indent sizes
                const nodeRenderingOverride = options?.overrideNodeRenderer?.(node, options, indentLevel);
                if (nodeRenderingOverride) {
                    markdownString += nodeRenderingOverride;
                }
                else {
                    switch (node.type) {
                        case 'text':
                        case 'bold':
                        case 'italic':
                        case 'strikethrough':
                        case 'link':
                            let content = node.content; // might be a nodes array but we take care of that below
                            if (Array.isArray(node.content)) {
                                content = markdownContentASTToString(node.content, options, indentLevel);
                            }
                            const isMarkdownStringNotEmpty = markdownString.length > 0;
                            const isFirstCharOfContentWhitespace = /\s/.test(content.slice(0, 1));
                            const isLastCharOfMarkdownWhitespace = /\s/.test(markdownString.slice(-1));
                            const isContentPunctuation = content.length === 1 && /^[.,!?;:]/.test(content);
                            if (isMarkdownStringNotEmpty && !isContentPunctuation && !isFirstCharOfContentWhitespace && !isLastCharOfMarkdownWhitespace) {
                                markdownString += ' ';
                            }
                            if (node.type === 'text') {
                                markdownString += `${indent}${content}`;
                            }
                            else {
                                if (node.type === 'bold') {
                                    markdownString += `**${content}**`;
                                }
                                else if (node.type === 'italic') {
                                    markdownString += `*${content}*`;
                                }
                                else if (node.type === 'strikethrough') {
                                    markdownString += `~~${content}~~`;
                                }
                                else if (node.type === 'link') {
                                    // check if the link contains only text
                                    if (node.content.length === 1 && node.content[0].type === 'text') {
                                        // use native markdown syntax for text-only links
                                        markdownString += `[${content}](${encodeURI(node.href)})`;
                                    }
                                    else {
                                        // Use HTML <a> tag for links with rich content
                                        markdownString += `<a href="${node.href}">${content}</a>`;
                                    }
                                }
                            }
                            break;
                        case 'heading':
                            const isEndsWithNewLine = markdownString.slice(-1) === '\n';
                            if (!isEndsWithNewLine) {
                                markdownString += '\n';
                            }
                            markdownString += `${'#'.repeat(node.level)} ${node.content}\n\n`;
                            break;
                        case 'image':
                            if (!node.alt?.trim() || !!node.src?.trim()) {
                                markdownString += `![${node.alt || ''}](${node.src})`;
                            }
                            break;
                        case 'list':
                            node.items.forEach((item, i) => {
                                const listItemPrefix = node.ordered ? `${i + 1}.` : '-';
                                const contents = markdownContentASTToString(item.content, options, indentLevel + 1).trim();
                                if (markdownString.slice(-1) !== '\n') {
                                    markdownString += '\n';
                                }
                                if (contents) {
                                    markdownString += `${indent}${listItemPrefix} ${contents}\n`;
                                }
                            });
                            markdownString += '\n';
                            break;
                        case 'video':
                            markdownString += `\n![Video](${node.src})\n`;
                            if (node.poster) {
                                markdownString += `![Poster](${node.poster})\n`;
                            }
                            if (node.controls) {
                                markdownString += `Controls: ${node.controls}\n`;
                            }
                            markdownString += '\n';
                            break;
                        case 'table':
                            const maxColumns = Math.max(...node.rows.map(row => row.cells.reduce((sum, cell) => sum + (cell.colspan || 1), 0)));
                            node.rows.forEach((row) => {
                                let currentColumn = 0;
                                row.cells.forEach((cell) => {
                                    let cellContent = typeof cell.content === 'string'
                                        ? cell.content
                                        : markdownContentASTToString(cell.content, options, indentLevel + 1).trim();
                                    if (cell.colId) {
                                        cellContent += ` <!-- ${cell.colId} -->`;
                                    }
                                    if (cell.colspan && cell.colspan > 1) {
                                        cellContent += ` <!-- colspan: ${cell.colspan} -->`;
                                    }
                                    if (cell.rowspan && cell.rowspan > 1) {
                                        cellContent += ` <!-- rowspan: ${cell.rowspan} -->`;
                                    }
                                    markdownString += `| ${cellContent} `;
                                    currentColumn += cell.colspan || 1;
                                    // Add empty cells for colspan
                                    for (let i = 1; i < (cell.colspan || 1); i++) {
                                        markdownString += '| ';
                                    }
                                });
                                // Fill remaining columns with empty cells
                                while (currentColumn < maxColumns) {
                                    markdownString += '|  ';
                                    currentColumn++;
                                }
                                markdownString += '|\n';
                            });
                            markdownString += '\n';
                            break;
                        case 'code':
                            if (node.inline) {
                                const isLsatWhitespace = /\s/.test(markdownString.slice(-1));
                                if (!isLsatWhitespace) {
                                    markdownString += ' ';
                                }
                                markdownString += `\`${node.content}\``;
                            }
                            else {
                                // For code blocks, we do not escape characters and preserve formatting
                                markdownString += '\n```' + (node.language ?? '') + '\n';
                                markdownString += `${node.content}\n`;
                                markdownString += '```\n\n';
                            }
                            break;
                        case 'blockquote':
                            markdownString += `> ${markdownContentASTToString(node.content, options).trim()}\n\n`;
                            break;
                        case "meta":
                            // already handled
                            break;
                        case 'semanticHtml':
                            switch (node.htmlType) {
                                case "article":
                                    markdownString += '\n\n' + markdownContentASTToString(node.content, options);
                                    break;
                                case "summary":
                                case "time":
                                case "aside":
                                case "nav":
                                case "figcaption":
                                case "main":
                                case "mark":
                                case "header":
                                case "footer":
                                case "details":
                                case "figure":
                                    markdownString += `\n\n<-${node.htmlType}->\n` + markdownContentASTToString(node.content, options) + `\n\n</-${node.htmlType}->\n`;
                                    break;
                                case "section":
                                    markdownString += '---\n\n';
                                    markdownString += markdownContentASTToString(node.content, options);
                                    markdownString += '\n\n';
                                    markdownString += '---\n\n';
                                    break;
                            }
                            break;
                        case "custom":
                            const customNodeRendering = options?.renderCustomNode?.(node, options, indentLevel);
                            if (customNodeRendering) {
                                markdownString += customNodeRendering;
                            }
                            break;
                    }
                }
            });
            return markdownString;
        }
        return markdownASTToString;
    }

    var domUtils = {};

    Object.defineProperty(domUtils, "__esModule", { value: true });
    domUtils.findMainContent = findMainContent;
    domUtils.wrapMainContent = wrapMainContent;
    domUtils.isElementVisible = isElementVisible;
    domUtils.getVisibleText = getVisibleText;
    const ElementNode_1 = ElementNode;
    const debugMessage = (message) => {
    };
    /**
     * Attempts to find the main content of a web page.
     * @param document The Document object to search.
     * @returns The Element containing the main content, or the body if no main content is found.
     */
    function findMainContent(document) {
        const mainElement = document.querySelector('main');
        if (mainElement) {
            return mainElement;
        }
        if (!document.body) {
            return document.documentElement;
        }
        return detectMainContent(document.body);
    }
    function wrapMainContent(mainContentElement, document) {
        if (mainContentElement.tagName.toLowerCase() !== 'main') {
            const mainElement = document.createElement('main');
            mainContentElement.before(mainElement);
            mainElement.appendChild(mainContentElement);
            mainElement.id = 'detected-main-content';
        }
    }
    function detectMainContent(rootElement) {
        const candidates = [];
        const minScore = 20;
        collectCandidates(rootElement, candidates, minScore);
        if (candidates.length === 0) {
            return rootElement;
        }
        candidates.sort((a, b) => calculateScore(b) - calculateScore(a));
        let bestIndependentCandidate = candidates[0];
        for (let i = 1; i < candidates.length; i++) {
            if (!candidates.some((otherCandidate, j) => j !== i && otherCandidate.contains(candidates[i]))) {
                if (calculateScore(candidates[i]) > calculateScore(bestIndependentCandidate)) {
                    bestIndependentCandidate = candidates[i];
                    debugMessage(`New best independent candidate found: ${elementToString(bestIndependentCandidate)}`);
                }
            }
        }
        debugMessage(`Final main content candidate: ${elementToString(bestIndependentCandidate)}`);
        return bestIndependentCandidate;
    }
    function elementToString(element) {
        if (!element) {
            return 'No element';
        }
        return `${element.tagName}#${element.id || 'no-id'}.${Array.from(element.classList).join('.')}`;
    }
    function collectCandidates(element, candidates, minScore) {
        const score = calculateScore(element);
        if (score >= minScore) {
            candidates.push(element);
            debugMessage(`Candidate found: ${elementToString(element)}, score: ${score}`);
        }
        Array.from(element.children).forEach(child => {
            collectCandidates(child, candidates, minScore);
        });
    }
    function calculateScore(element) {
        let score = 0;
        let scoreLog = [];
        // High impact attributes
        const highImpactAttributes = ['article', 'content', 'main-container', 'main', 'main-content'];
        highImpactAttributes.forEach(attr => {
            if (element.classList.contains(attr) || element.id.includes(attr)) {
                score += 10;
                scoreLog.push(`High impact attribute found: ${attr}, score increased by 10`);
            }
        });
        // High impact tags
        const highImpactTags = ['article', 'main', 'section'];
        if (highImpactTags.includes(element.tagName.toLowerCase())) {
            score += 5;
            scoreLog.push(`High impact tag found: ${element.tagName}, score increased by 5`);
        }
        // Paragraph count
        const paragraphCount = element.getElementsByTagName('p').length;
        const paragraphScore = Math.min(paragraphCount, 5);
        if (paragraphScore > 0) {
            score += paragraphScore;
            scoreLog.push(`Paragraph count: ${paragraphCount}, score increased by ${paragraphScore}`);
        }
        // Text content length
        const textContentLength = element.textContent?.trim().length || 0;
        if (textContentLength > 200) {
            const textScore = Math.min(Math.floor(textContentLength / 200), 5);
            score += textScore;
            scoreLog.push(`Text content length: ${textContentLength}, score increased by ${textScore}`);
        }
        // Link density
        const linkDensity = calculateLinkDensity(element);
        if (linkDensity < 0.3) {
            score += 5;
            scoreLog.push(`Link density: ${linkDensity.toFixed(2)}, score increased by 5`);
        }
        // Data attributes
        if (element.hasAttribute('data-main') || element.hasAttribute('data-content')) {
            score += 10;
            scoreLog.push('Data attribute for main content found, score increased by 10');
        }
        // Role attribute
        if (element.getAttribute('role')?.includes('main')) {
            score += 10;
            scoreLog.push('Role attribute indicating main content found, score increased by 10');
        }
        if (scoreLog.length > 0) {
            debugMessage(`Scoring for ${elementToString(element)}:`);
        }
        return score;
    }
    function calculateLinkDensity(element) {
        const linkLength = Array.from(element.getElementsByTagName('a'))
            .reduce((sum, link) => sum + (link.textContent?.length || 0), 0);
        const textLength = element.textContent?.length || 1; // Avoid division by zero
        return linkLength / textLength;
    }
    function isElementVisible(element) {
        if (!(element instanceof HTMLElement)) {
            return true; // Non-HTMLElements are considered visible
        }
        const style = window.getComputedStyle(element);
        return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
    }
    function getVisibleText(element) {
        if (!isElementVisible(element)) {
            return '';
        }
        let text = '';
        for (const child of Array.from(element.childNodes)) {
            if (child.nodeType === ElementNode_1._Node.TEXT_NODE) {
                text += child.textContent;
            }
            else if (child.nodeType === ElementNode_1._Node.ELEMENT_NODE) {
                text += getVisibleText(child);
            }
        }
        return text.trim();
    }

    var urlUtils = {};

    Object.defineProperty(urlUtils, "__esModule", { value: true });
    urlUtils.refifyUrls = refifyUrls;
    const mediaSuffixes = ["jpeg", "jpg", "png", "gif", "bmp", "tiff", "tif", "svg",
        "webp", "ico", "avi", "mov", "mp4", "mkv", "flv", "wmv", "webm", "mpeg",
        "mpg", "mp3", "wav", "aac", "ogg", "flac", "m4a", "pdf", "doc", "docx",
        "ppt", "pptx", "xls", "xlsx", "txt", "css", "js", "xml", "json",
        "html", "htm"
    ];
    const addRefPrefix = (prefix, prefixesToRefs) => {
        if (!prefixesToRefs[prefix]) {
            prefixesToRefs[prefix] = 'ref' + Object.values(prefixesToRefs).length;
        }
        return prefixesToRefs[prefix];
    };
    const processUrl = (url, prefixesToRefs) => {
        if (!url.startsWith('http')) {
            return url;
        }
        else {
            const mediaSuffix = url.split('.').slice(-1)[0];
            if (mediaSuffix && mediaSuffixes.includes(mediaSuffix)) {
                const parts = url.split('/'); // Split URL keeping the slash before text
                const prefix = parts.slice(0, -1).join('/'); // Get the prefix by removing last part
                const refPrefix = addRefPrefix(prefix, prefixesToRefs);
                return `${refPrefix}://${parts.slice(-1).join('')}`;
            }
            else {
                if (url.split('/').length > 4) {
                    return addRefPrefix(url, prefixesToRefs);
                }
                else {
                    return url;
                }
            }
        }
    };
    function refifyUrls(markdownElement, prefixesToRefs = {}) {
        if (Array.isArray(markdownElement)) {
            markdownElement.forEach(element => refifyUrls(element, prefixesToRefs));
        }
        else {
            switch (markdownElement.type) {
                case 'link':
                    markdownElement.href = processUrl(markdownElement.href, prefixesToRefs);
                    refifyUrls(markdownElement.content, prefixesToRefs);
                    break;
                case 'image':
                case 'video':
                    markdownElement.src = processUrl(markdownElement.src, prefixesToRefs);
                    break;
                case 'list':
                    markdownElement.items.forEach(item => item.content.forEach(_ => refifyUrls(_, prefixesToRefs)));
                    break;
                case 'table':
                    markdownElement.rows.forEach(row => row.cells.forEach(cell => typeof cell.content === 'string' ? null : refifyUrls(cell.content, prefixesToRefs)));
                    break;
                case 'blockquote':
                case 'semanticHtml':
                    refifyUrls(markdownElement.content, prefixesToRefs);
                    break;
            }
        }
        return prefixesToRefs;
    }

    var astUtils = {};

    (function (exports) {
        Object.defineProperty(exports, "__esModule", { value: true });
        exports.isNot = exports.getMainContent = void 0;
        exports.findInAST = findInAST;
        exports.findAllInAST = findAllInAST;
        const getMainContent = (markdownStr) => {
            if (markdownStr.includes('<-main->')) {
                const regex = /(?<=<-main->)[\s\S]*?(?=<\/-main->)/;
                const match = markdownStr.match(regex);
                return match?.[0] ?? '';
            }
            else {
                const removeSectionsRegex = /(<-nav->[\s\S]*?<\/-nav->)|(<-footer->[\s\S]*?<\/-footer->)|(<-header->[\s\S]*?<\/-header->)|(<-aside->[\s\S]*?<\/-aside->)/g;
                return markdownStr.replace(removeSectionsRegex, '');
            }
        };
        exports.getMainContent = getMainContent;
        const isNot = (tPred) => (t) => !tPred(t);
        exports.isNot = isNot;
        const isString = (x) => typeof x === "string";
        function findInAST(markdownElement, checker) {
            const loopCheck = (z) => {
                for (const element of z) {
                    const found = findInAST(element, checker);
                    if (found) {
                        return found;
                    }
                }
                return undefined;
            };
            if (Array.isArray(markdownElement)) {
                return loopCheck(markdownElement);
            }
            else {
                if (checker(markdownElement)) {
                    return markdownElement;
                }
                switch (markdownElement.type) {
                    case 'link':
                        return loopCheck(markdownElement.content);
                    case 'list':
                        return loopCheck(markdownElement.items
                            .map(_ => _.content)
                            .flat());
                    case 'table':
                        return loopCheck(markdownElement.rows
                            .map(row => row.cells.map(_ => _.content)
                            .filter((0, exports.isNot)(isString)))
                            .flat());
                    case 'blockquote':
                    case 'semanticHtml':
                        return loopCheck(markdownElement.content);
                }
                return undefined;
            }
        }
        function findAllInAST(markdownElement, checker) {
            const loopCheck = (z) => {
                let out = [];
                for (const element of z) {
                    const found = findAllInAST(element, checker);
                    out = [...out, ...found];
                }
                return out;
            };
            if (Array.isArray(markdownElement)) {
                return loopCheck(markdownElement);
            }
            else {
                if (checker(markdownElement)) {
                    return [markdownElement];
                }
                switch (markdownElement.type) {
                    case 'link':
                        return loopCheck(markdownElement.content);
                    case 'list':
                        return loopCheck(markdownElement.items
                            .map(_ => _.content)
                            .flat());
                    case 'table':
                        return loopCheck(markdownElement.rows
                            .map(row => row.cells.map(_ => _.content)
                            .filter((0, exports.isNot)(isString)))
                            .flat());
                    case 'blockquote':
                    case 'semanticHtml':
                        return loopCheck(markdownElement.content);
                }
                return [];
            }
        } 
    } (astUtils));

    var hasRequiredNode;

    function requireNode () {
        if (hasRequiredNode) return node;
        hasRequiredNode = 1;
        (function (exports) {
            Object.defineProperty(exports, "__esModule", { value: true });
            exports.wrapMainContent = exports.refifyUrls = exports.findMainContent = exports.markdownASTToString = exports.htmlToMarkdownAST = void 0;
            exports.convertHtmlToMarkdown = convertHtmlToMarkdown;
            exports.convertElementToMarkdown = convertElementToMarkdown;
            exports.findInMarkdownAST = findInMarkdownAST;
            exports.findAllInMarkdownAST = findAllInMarkdownAST;
            const htmlToMarkdownAST_1 = htmlToMarkdownAST$1;
            Object.defineProperty(exports, "htmlToMarkdownAST", { enumerable: true, get: function () { return htmlToMarkdownAST_1.htmlToMarkdownAST; } });
            const markdownASTToString_1 = requireMarkdownASTToString();
            Object.defineProperty(exports, "markdownASTToString", { enumerable: true, get: function () { return markdownASTToString_1.markdownASTToString; } });
            const domUtils_1 = domUtils;
            Object.defineProperty(exports, "findMainContent", { enumerable: true, get: function () { return domUtils_1.findMainContent; } });
            Object.defineProperty(exports, "wrapMainContent", { enumerable: true, get: function () { return domUtils_1.wrapMainContent; } });
            const urlUtils_1 = urlUtils;
            Object.defineProperty(exports, "refifyUrls", { enumerable: true, get: function () { return urlUtils_1.refifyUrls; } });
            const astUtils_1 = astUtils;
            /**
             * Converts an HTML string to Markdown.
             * @param html The HTML string to convert.
             * @param options Conversion options.
             * @returns The converted Markdown string.
             */
            function convertHtmlToMarkdown(html, options) {
                const parser = options?.overrideDOMParser ?? (typeof DOMParser !== 'undefined' ? new DOMParser() : null);
                if (!parser) {
                    throw new Error('DOMParser is not available. Please provide an overrideDOMParser in options.');
                }
                const doc = parser.parseFromString(html, 'text/html');
                let element;
                if (options?.extractMainContent) {
                    element = (0, domUtils_1.findMainContent)(doc);
                    if (options.includeMetaData && !!doc.querySelector('head')?.innerHTML && !element.querySelector('head')) {
                        // content container was found and extracted, re-attaching the head for meta-data extraction
                        element = parser.parseFromString(`<html>${doc.head.outerHTML}${element.outerHTML}`, 'text/html').documentElement;
                    }
                }
                else {
                    // If there's a body, use it; otherwise, use the document element
                    if (options?.includeMetaData && !!doc.querySelector('head')?.innerHTML) {
                        element = doc.documentElement;
                    }
                    else {
                        element = doc.body || doc.documentElement;
                    }
                }
                return convertElementToMarkdown(element, options);
            }
            /**
             * Converts an HTML Element to Markdown.
             * @param element The HTML Element to convert.
             * @param options Conversion options.
             * @returns The converted Markdown string.
             */
            function convertElementToMarkdown(element, options) {
                let ast = (0, htmlToMarkdownAST_1.htmlToMarkdownAST)(element, options);
                if (options?.refifyUrls) {
                    options.urlMap = (0, urlUtils_1.refifyUrls)(ast);
                }
                return (0, markdownASTToString_1.markdownASTToString)(ast, options);
            }
            /**
             * Finds a node in the Markdown AST that matches the given predicate.
             * @param ast The Markdown AST to search.
             * @param predicate A function that returns true for the desired node.
             * @returns The first matching node, or undefined if not found.
             */
            function findInMarkdownAST(ast, predicate) {
                return (0, astUtils_1.findInAST)(ast, predicate);
            }
            /**
             * Finds all nodes in the Markdown AST that match the given predicate.
             * @param ast The Markdown AST to search.
             * @param predicate A function that returns true for the desired nodes.
             * @returns An array of all matching nodes.
             */
            function findAllInMarkdownAST(ast, predicate) {
                return (0, astUtils_1.findAllInAST)(ast, predicate);
            } 
        } (node));
        return node;
    }

    var nodeExports = requireNode();

    //@ts-ignore
    window.__INTUNED__ = {
        convertElementToMarkdown: nodeExports.convertElementToMarkdown,
        convertHtmlStringToSemanticMarkdown: nodeExports.convertHtmlToMarkdown,
    };

})();
