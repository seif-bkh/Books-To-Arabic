#!/usr/bin/env node
/** Offline browser typesetting. Invoked by build_book.py, not a web server. */
import { readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium as playwright } from "playwright-core";

const [inputPath, pdfPath, reportPath] = process.argv.slice(2);
if (!inputPath || !pdfPath || !reportPath) {
  console.error("Usage: node scripts/render_pdf.mjs INPUT.html OUTPUT.pdf REPORT.json");
  process.exit(1);
}

let browser;
try {
  let executablePath = process.env.BOOK_CHROMIUM_PATH;
  let args = [];
  if (!executablePath) {
    if (process.platform !== "linux" || process.arch !== "x64") {
      throw new Error("Set BOOK_CHROMIUM_PATH to a compatible local Chrome/Chromium executable on this platform.");
    }
    const { default: bundled, inflate, setupLambdaEnvironment } = await import("@sparticuz/chromium");
    const packageBuild = dirname(fileURLToPath(import.meta.resolve("@sparticuz/chromium")));
    // Include NSS libraries in minimal Linux environments, without modifying /usr.
    const native = await inflate(join(packageBuild, "../bin/al2023.tar.br"));
    setupLambdaEnvironment(join(native, "lib"));
    executablePath = await bundled.executablePath();
    // The book is local trusted content. Do not disable web security unnecessarily.
    args = bundled.args.filter((arg) => ![
      "--disable-web-security", "--allow-running-insecure-content",
    ].includes(arg));
  }
  browser = await playwright.launch({ executablePath, args, headless: true });
  const context = await browser.newContext({ viewport: { width: 1000, height: 1400 } });
  // No book text, fonts, or assets can be sent to a remote service during rendering.
  await context.route("**/*", (route) => route.abort());
  const page = await context.newPage();
  page.setDefaultTimeout(120_000);
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.emulateMedia({ media: "print" });
  await page.setContent(await readFile(inputPath, "utf8"), { waitUntil: "load" });
  await page.evaluate(async () => {
    await document.fonts.ready;
    window.PagedConfig = { auto: false };
  });
  const pagedRoot = dirname(fileURLToPath(import.meta.resolve("pagedjs")));
  await page.addScriptTag({ path: join(pagedRoot, "../dist/paged.polyfill.js") });
  const report = await page.evaluate(async () => {
    const normalize = (text) => text.replace(/\s+/gu, "");
    const blockSelector = "p,li,pre,td,th,h1,h2,h3,h4,h5,h6,figcaption,.layer,.connector";
    const expectedBlocks = [...document.querySelectorAll(".chapter")].flatMap((chapter) =>
      [...chapter.querySelectorAll(blockSelector)].filter((node) =>
        !node.parentElement.closest(blockSelector)
      )
    ).map((node, index) => {
      node.dataset.auditBlock = String(index);
      return { text: normalize(node.textContent), repeatedHeader: node.tagName === "TH" };
    });
    const observedBlocks = expectedBlocks.map(() => []);
    const flow = await window.PagedPolyfill.preview();
    await document.fonts.ready;
    const pages = [...document.querySelectorAll(".pagedjs_page")];
    const headingPages = {};
    const overflows = [];
    for (const page of pages) {
      const number = Number(page.dataset.pageNumber);
      const content = page.querySelector(".pagedjs_page_content");
      const pageBounds = page.getBoundingClientRect();
      for (const block of content.querySelectorAll("[data-audit-block]")) {
        observedBlocks[Number(block.dataset.auditBlock)].push(normalize(block.textContent));
        // Catch RTL overflow disappearing into an off-page CSS column. Checking
        // just the page count or DOM presence of headings would miss this bug.
        const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
          if (!walker.currentNode.textContent.trim()) continue;
          const range = document.createRange();
          range.selectNodeContents(walker.currentNode);
          for (const rect of range.getClientRects()) {
            if (rect.width < 0.1 || rect.height < 0.1) continue;
            if (rect.left < pageBounds.left - 2 || rect.right > pageBounds.right + 2 ||
                rect.top < pageBounds.top - 2 || rect.bottom > pageBounds.bottom + 2) {
              overflows.push(`Text leaves physical page ${number}: ${block.textContent.slice(0, 70)}`);
              break;
            }
          }
        }
      }
      for (const heading of content.querySelectorAll("h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]")) {
        headingPages[heading.id] ??= number;
      }
      // Commands must never wrap, clip, or quietly change direction.
      for (const pre of content.querySelectorAll("pre")) {
        if (pre.scrollWidth > pre.clientWidth + 1) {
          overflows.push(`Command block overflows on page ${number}: ${pre.textContent.slice(0, 80)}`);
        }
        if (getComputedStyle(pre).direction !== "ltr") {
          overflows.push(`Command block is not LTR on page ${number}`);
        }
      }
    }
    for (const [index, expected] of expectedBlocks.entries()) {
      const observed = observedBlocks[index];
      const matches = expected.repeatedHeader
        ? observed.length > 0 && observed.every((text) => text === expected.text)
        : observed.join("") === expected.text;
      if (!matches) {
        overflows.push(`Text lost or duplicated during pagination, block ${index}: ${expected.text.slice(0, 70)}`);
      }
    }
    // Fixed-width number cells make this change pagination-neutral. The report
    // and the PDF bookmarks derive from the actual paginated DOM, not estimates.
    for (const row of document.querySelectorAll(".pagedjs_page .toc-table tr")) {
      const target = row.querySelector("a").getAttribute("href").slice(1);
      if (!headingPages[target]) throw new Error(`Unresolved contents target: ${target}`);
      row.querySelector(".toc-number").textContent = headingPages[target];
    }
    return { pageCount: flow.total, headingPages, overflows, verifiedBlocks: expectedBlocks.length };
  });
  if (errors.length || report.overflows.length) {
    throw new Error([...errors, ...report.overflows].join("\n"));
  }
  if (!report.pageCount || report.pageCount > 200) {
    throw new Error(`Unexpected page count: ${report.pageCount}`);
  }
  await page.pdf({
    path: pdfPath, format: "A4", preferCSSPageSize: true,
    printBackground: true, tagged: true, outline: true,
  });
  await writeFile(reportPath, JSON.stringify(report, null, 2) + "\n", "utf8");
} catch (error) {
  console.error(`PDF rendering failed: ${error.message}`);
  process.exitCode = 1;
} finally {
  await browser?.close();
}
