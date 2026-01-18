const jsdom = require("jsdom");
const createDOMPurify = require("dompurify");
const fs = require('fs');
const path = require('path');
const { JSDOM } = jsdom;

const window = new JSDOM('').window;
const DOMPurify = createDOMPurify(window);

// Read payload from file
const payloadPath = path.join(__dirname, 'payload.html');
let htmlParam = "";

try {
    htmlParam = fs.readFileSync(payloadPath, 'utf8');
} catch (err) {
    console.error("Error reading payload.html:", err.message);
    process.exit(1);
}

console.log("--- 1. Extracted Payload (from payload.html) ---");
console.log(htmlParam);

// Simulate Server-Side Encoding
const serverEncoded = encodeURIComponent(htmlParam);

// Simulate Client-Side Decoding
const clientDecoded = decodeURIComponent(serverEncoded);

// Simulate DOMPurify
const sanitized = DOMPurify.sanitize(clientDecoded, {
    FORBID_TAGS: ['style'],
    FORBID_ATTR: ['style']
});

console.log("\n--- 2. Final HTML (What the Bot Sees in DOM) ---");
console.log(sanitized);

// Write purified HTML to file
const purifiedPath = path.join(__dirname, 'purified.html');
try {
    fs.writeFileSync(purifiedPath, sanitized);
    console.log(`\n[+] Purified HTML written to: ${purifiedPath}`);
} catch (err) {
    console.error("Error writing purified.html:", err.message);
}

// Generate Bot URL
var baseUrl = "http://web/";
const botUrl = new URL(baseUrl);
botUrl.searchParams.set("html", htmlParam);

console.log("\n--- 3. URL for the Bot ---");
console.log(botUrl.toString());
baseUrl = "http://chals1.eof.ais3.org:20000/";
const testUrl = new URL(baseUrl);
testUrl.searchParams.set("html", htmlParam);

console.log("\n--- 4. URL for Testing ---");
console.log(testUrl.toString());