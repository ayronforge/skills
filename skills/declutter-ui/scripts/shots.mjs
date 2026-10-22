import { mkdirSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join, resolve } from "node:path";

const [configFile, outDir] = process.argv.slice(2);

if (!configFile || !outDir) {
  console.error("uso: node shots.mjs <config.json> <pasta-de-saida>");
  process.exit(1);
}

function loadPlaywright() {
  const require = createRequire(join(process.cwd(), "package.json"));
  const candidates = [process.env.PLAYWRIGHT_MODULE, "playwright", "@playwright/test"].filter(Boolean);

  for (const candidate of candidates) {
    try {
      return require(require.resolve(candidate));
    } catch {}
  }

  console.error("Playwright não encontrado. Instale playwright ou @playwright/test, ou defina PLAYWRIGHT_MODULE.");
  process.exit(1);
}

const config = JSON.parse(readFileSync(configFile, "utf8"));
const { chromium } = loadPlaywright();

mkdirSync(outDir, { recursive: true });

const settleMs = config.settleMs ?? 600;

const baseCss = `
  *, *::before, *::after {
    animation-delay: 0s !important;
    animation-duration: 0s !important;
    caret-color: transparent !important;
    transition: none !important;
  }
`;

const hideCss = (config.hide ?? []).map((selector) => `${selector} { display: none !important; }`).join("\n");

const browser = await chromium.launch(
  process.env.SHOTS_CHROMIUM ? { executablePath: process.env.SHOTS_CHROMIUM } : {},
);

const context = await browser.newContext({
  bypassCSP: true,
  colorScheme: config.colorScheme ?? "light",
  deviceScaleFactor: config.deviceScaleFactor ?? 1,
  locale: config.locale ?? "pt-BR",
  reducedMotion: "reduce",
  storageState: config.storageState ? resolve(config.storageState) : undefined,
  viewport: config.viewport ?? { height: 900, width: 1440 },
});

if (config.localStorage) {
  await context.addInitScript((entries) => {
    try {
      for (const [key, value] of Object.entries(entries)) localStorage.setItem(key, value);
    } catch {}
  }, config.localStorage);
}

if (config.blockThirdParty) {
  const origin = new URL(config.baseUrl).origin;
  await context.route((url) => url.origin !== origin, (route) => route.abort());
}

async function unstick(page) {
  await page.evaluate(() => {
    for (const element of document.querySelectorAll("body *")) {
      const position = getComputedStyle(element).position;

      if (position === "fixed" || position === "sticky") element.style.setProperty("position", "static", "important");
    }
  });
}

async function prepare(page, url) {
  await page.goto(url, { waitUntil: "load" });
  await page.waitForLoadState("networkidle").catch(() => undefined);
  await page.evaluate(async () => {
    const end = Math.min(document.body.scrollHeight, 30_000);

    for (let y = 0; y < end; y += 600) {
      window.scrollTo(0, y);
      await new Promise((done) => setTimeout(done, 60));
    }
    window.scrollTo(0, 0);
  });
  await page.addStyleTag({ content: `${baseCss}\n${hideCss}\n${config.css ?? ""}` });

  if (config.unstick) await unstick(page);

  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(settleMs);
}

const page = await context.newPage();
let current = "";
let failures = 0;

for (const shot of config.shots) {
  const url = new URL(shot.path, config.baseUrl).href;
  const file = join(outDir, `${shot.name}.png`);

  try {
    if (current !== url) {
      await prepare(page, url);
      current = url;
    }

    const target = shot.target ?? "top";

    if (target === "full") await page.screenshot({ fullPage: true, path: file });
    else if (target === "top") {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.screenshot({ path: file });
    }
    else {
      const element = page.locator(target).first();

      if ((await element.count()) === 0) throw new Error(`seletor sem resultado: ${target}`);

      await element.screenshot({ path: file });
    }

    console.log("ok", shot.name);
  } catch (error) {
    failures += 1;
    console.log("FALHOU", shot.name, String(error).split("\n")[0]);
  }
}

await browser.close();
process.exit(failures > 0 ? 1 : 0);
