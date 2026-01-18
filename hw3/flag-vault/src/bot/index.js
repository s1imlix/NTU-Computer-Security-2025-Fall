const express = require('express');
const puppeteer = require('puppeteer');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.urlencoded({ extended: false }));

const WEB_URL = process.env.WEB_URL || 'http://web:11202';
const FLAG = process.env.FLAG || 'flag{test2}';
const TURNSTILE_SITE_KEY = process.env.TURNSTILE_SITE_KEY || '';
const TURNSTILE_SECRET_KEY = process.env.TURNSTILE_SECRET_KEY || '';
let HTML_CONTENT = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
if (TURNSTILE_SITE_KEY && TURNSTILE_SECRET_KEY) {
    HTML_CONTENT = HTML_CONTENT.replace(/\{\{TURNSTILE_SITE_KEY\}\}/g, TURNSTILE_SITE_KEY);
} else {
    HTML_CONTENT = HTML_CONTENT.replace(/\{\{TURNSTILE_SITE_KEY\}\}/g, '');
}

async function visitUrl(url) {
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: true,
            executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium-browser',
            args: [
                '--no-sandbox',
                '--js-flags=--jitless,--no-expose-wasm',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                "--disable-features=HttpsFirstBalancedModeAutoEnable",
                `--unsafely-treat-insecure-origin-as-secure=${WEB_URL}`
            ]
        });

        const page = await browser.newPage();

        // Register
        const username = crypto.randomUUID();
        const password = crypto.randomUUID();
        console.log(`Username: ${username}`);
        console.log(`Password: ${password}`);
        await page.goto(`${WEB_URL}/register`, { waitUntil: 'networkidle0' });
        await page.type('#username', username);
        await page.type('#password', password);
        await page.click('button[type="submit"]');
        await page.waitForNavigation({ waitUntil: 'networkidle0' });

        // Login
        await page.goto(`${WEB_URL}/login`, { waitUntil: 'networkidle0' });
        await page.type('#username', username);
        await page.type('#password', password);
        await page.click('button[type="submit"]');
        await page.waitForNavigation({ waitUntil: 'networkidle0' });

        // Set flag
        await page.goto(`${WEB_URL}/flag`, { waitUntil: 'networkidle0' });
        await page.click('#editFlagBtn');
        await page.waitForSelector('#flagContentInput', { visible: true });
        await page.evaluate((flag) => {
            document.getElementById('flagContentInput').value = flag;
        }, FLAG);
        await page.click('button[type="submit"]');
        await page.waitForNavigation({ waitUntil: 'networkidle0' });

        // Visit user URL
        console.log(`Visiting URL: ${url}`);
        await page.goto(url, { waitUntil: 'networkidle0', timeout: 10000 });
        await new Promise(resolve => setTimeout(resolve, 2000));

        await browser.close();
        return { success: true };
    } catch (error) {
        if (browser) await browser.close();
        console.error('Error:', error);
        return { success: false, error: "Something went wrong" };
    }
}

async function validateTurnstile(token) {
    try {
        const response = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                secret: TURNSTILE_SECRET_KEY,
                response: token
            })
        });

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Turnstile validation error:', error);
        return { success: false, 'error-codes': ['internal-error'] };
    }
}

app.post('/visit', async (req, res) => {
    const { url, 'cf-turnstile-response': turnstileToken } = req.body;

    // Verify Turnstile token in production mode
    if (TURNSTILE_SITE_KEY && TURNSTILE_SECRET_KEY) {
        const result = await validateTurnstile(turnstileToken);
        if (!result.success) {
            return res.status(400).json({ error: 'Refresh the page and try again' });
        }
    }

    if (!url || typeof url !== 'string') {
        return res.status(400).json({ error: 'Invalid URL' });
    }

    try {
        const userUrl = new URL(url);

        // Only allow http:// or https://
        if (userUrl.protocol !== 'http:' && userUrl.protocol !== 'https:') {
            return res.status(400).json({ error: 'URL must use http:// or https://' });
        }

        const result = await visitUrl(url);
        res.json(result);
    } catch (error) {
        return res.status(400).json({ error: 'Invalid URL format' });
    }
});

app.get('/', (req, res) => {
    res.send(HTML_CONTENT);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Bot server running on port ${PORT}`);
});