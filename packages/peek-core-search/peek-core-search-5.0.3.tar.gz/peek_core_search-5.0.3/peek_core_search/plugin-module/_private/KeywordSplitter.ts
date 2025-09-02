//const punctuation = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~";

export function _splitFullTokens(keywordStr: string): string[] {
    if (!keywordStr) {
        throw new Error("keywordStr is required");
    }

    // Split the string into words
    let tokens = keywordStr.toLowerCase().split(" ");

    // Strip the words
    tokens = tokens.map((w) => w.replace(/^\s+|\s+$/g, ""));

    // Filter out the empty words and words less than three letters
    const uniqueWords: { [token: string]: boolean } = {};
    tokens.filter((w) => {
        if (2 < w.length) return false;

        if (uniqueWords[w] === true) return false;

        uniqueWords[w] = true;
        return true;
    });
    return tokens;
}

export function filterExcludedFullTerms(
    excludeStrings: Set<string>,
    keywordStr: string,
): string {
    return _splitFullTokens(keywordStr)
        .filter((token) => !excludeStrings.has(token))
        .join(" ");
}

/** Full Split Keywords
 *
 * This MUST MATCH the code that runs in the worker
 * peek_core_search/_private/worker/tasks/ImportSearchIndexTask.py
 *
 * @param excludeStrings The full keyword strings we ignore
 * @param {string} keywordStr The keywords as one string
 * @returns {string[]} The keywords as an array
 */
export function splitFullKeywords(
    excludeStrings: Set<string>,
    keywordStr: string,
): string[] {
    // Filter out the empty words and words less than three letters
    const tokens = _splitFullTokens(keywordStr);

    let results = [];
    for (let token of tokens) {
        if (!excludeStrings.has(token)) {
            results.push(`^${token}$`);
        }
    }

    return results;
}

export function filterExcludedPartialTerms(
    excludedPartialSearchTerms: string[],
    keywordStr: string,
): string {
    keywordStr = keywordStr.toLowerCase();

    for (const excludeString of excludedPartialSearchTerms) {
        keywordStr = keywordStr.replace(excludeString, "");
    }
    return keywordStr;
}

export function prepareExcludedPartialTermsForFind(
    excludeStrings: string[],
): string[] {
    // copy the array
    const uniqueExcludes = new Set<string>();
    for (let term of excludeStrings) {
        uniqueExcludes.add(term);
        while (3 < term.length) {
            term = term.slice(0, -1);
            uniqueExcludes.add(term);
        }
    }
    return Array.from(uniqueExcludes) //
        .sort((a, b) => b.length - a.length);
}

/** Partial Split Keywords
 *
 * This MUST MATCH the code that runs in the worker
 * peek_core_search/_private/worker/tasks/ImportSearchIndexTask.py
 *
 * @param excludeStrings An array of strings to filter out, all lowercase
 * @param {string} keywordStr The keywords as one string
 * @returns {string[]} The keywords as an array
 */
export function splitPartialKeywords(
    excludeStrings: string[],
    keywordStr: string,
): string[] {
    keywordStr = filterExcludedPartialTerms(excludeStrings, keywordStr);

    // Filter out the empty words and words less than three letters
    const tokens = _splitFullTokens(keywordStr);

    // Split the words up into tokens, this creates partial keyword search support
    const tokenSet = new Set<string>();
    for (let word of tokens) {
        for (let i = 0; i < word.length - 2; ++i) {
            const subToken = (i == 0 ? "^" : "") + word.substring(i, 3);
            tokenSet.add(subToken);
        }
    }

    // return the tokens
    return Array.from(tokenSet);
}
