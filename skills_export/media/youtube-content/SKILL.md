---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Also use for **multi-video research compilation**: the user asks you to find YouTube videos on a topic and compile their practices into a single structured reference document. This workflow: search YouTube → select top videos → batch fetch transcripts → synthesize into a structured guide.

## Resilience note

This task type commonly hits external obstacles: cookie consent banners, bot detection, navigation failures. Never stop mid-task — retry with a different approach (browser_console JS extraction, direct API call, or alternate search). If the browser stacks a cookie consent dialog, handle it (find and click "Accept all" or the equivalent) before attempting to click result links.

## Setup

```bash
pip install youtube-transcript-api
```

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Multi-Video Research Compilation Workflow

When the user asks to find and compile practices from multiple YouTube videos on a topic:

### Step 1: Search and collect video URLs
- Navigate to `https://www.youtube.com/results?search_query=<keywords>` via browser
- If cookie consent appears, find and click "Accept all" or equivalent before interacting with results
- Extract video URLs programmatically using `browser_console` with JavaScript:
  ```js
  Array.from(document.querySelectorAll('a#video-title'))
    .slice(0,N)
    .map(a => ({title: a.title || a.innerText.trim(), url: a.href}))
    .filter(x => x.url)
  ```
  This bypasses navigation issues with clicking individual result links on YouTube.
- See `references/youtube-search-url-extraction.md` for detailed JS snippets.

### Step 2: Select top videos
- Pick 3-6 videos based on: views, relevance, language match, channel authority
- Prefer a mix: one scientific/authoritative, one practical/actionable, one Russian-language if the user prefers Russian

### Step 3: Batch fetch transcripts
- Use `youtube-transcript-api` directly in `execute_code` (or the fetch_transcript.py script)
- For each video, try the user's language first, then fall back to `api.fetch(vid)` (auto-detect)
- Strip query parameters from URLs to get clean 11-char video IDs

### Step 4: Synthesize into structured reference document
- Group practices by category (morning, health, psychology, environment, etc.)
- For each practice note: source video, difficulty level, how to implement
- Include a "Plan of action" section — week-by-week rollout
- Save to a user-visible location (Desktop, Documents) as a .md file
- Tell the user the absolute path

### Step 5: Deliver as PDF when user needs a usable file
If the user asks for a file they can open (e.g. "скинь в телеграм", "не открывается", "сделай нормальный файл"), compile the .md into a professional PDF.

See `references/pdf-generation-windows.md` for the complete technique:
- Install `pip install fpdf2`
- Register both `arial.ttf` (regular) and `arialbd.ttf` (bold) from `C:\Windows\Fonts\`
- Clean emoji/unicode before rendering (replace 🟢 with text labels)
- Professional styling: section headers with rules, alternating table rows, page numbers
- Send via Telegram: `send_message(target="...", message="MEDIA:C:\\path\\to\\file.pdf")`

### Output format: Reference guide
When compiling multiple videos, produce:
- **Table of contents** with video sources + links
- **Per-video breakdown** (numbered practices with descriptions)
- **Synthesis table** — all practices grouped by category with difficulty ratings
- **Action plan** — suggested week-by-week rollout
- **Quick-start recommendations** — which 1-2 videos to watch first

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Pitfalls & Error Handling

### Cookie consent banners
YouTube often shows a cookie consent dialog over search results. Before clicking any result links, look for and click "Accept all" or "Пропустить" / "Skip" buttons visible in the snapshot. If links produce `Unknown ref` errors, a banner is likely in the way.

### Bot detection
YouTube may serve empty or stripped pages in headless browser sessions. If the snapshot shows few or no results, try:
- Using `browser_console` with JS to extract video URLs instead of clicking links
- Navigating to a direct `youtube.com/results?search_query=...` URL rather than clicking around

### Transcript not available for specific language
Some videos have transcripts only in certain languages. Always try the requested language first, then fall back to `api.fetch(vid)` (auto-detect). If the video is no longer available (Matt Cutts TED talk style), skip it and use another source.

### Partial results on fallback language
Some videos tagged as "Russian" by the title may only have English transcripts available. Note this to the user — the practices are still usable even if the voiceover language differs.

### Large transcripts
If a single transcript exceeds ~8K characters, truncate to avoid flooding context. For multi-video compilation, batch-fetch via `execute_code` which can handle all videos in one script run.

### User wants PDF deliverable
If the user asks for a file they can open (e.g. in Telegram, on desktop), compile the research into a PDF using fpdf2. See `references/pdf-generation-windows.md` for the complete technique: font setup, Unicode/emoji sanitization, professional styling with headers/rules/tables, and page numbering.

On Windows: install `pip install fpdf2`, register both `arial.ttf` (regular) and `arialbd.ttf` (bold) from `C:\Windows\Fonts\`, clean emoji before rendering.

### Dependency missing
Run `pip install youtube-transcript-api` and retry.

### Private/unavailable video
Relay the error and ask the user to verify the URL, or skip and use another source.
