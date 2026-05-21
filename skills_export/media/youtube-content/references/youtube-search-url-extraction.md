# YouTube Search: Video URL Extraction via browser_console

Use these JavaScript snippets in `browser_console(expression=...)` to extract video URLs from YouTube search results pages programmatically. This bypasses cookie-consent and navigation issues that occur when trying to click individual video links.

## Extract top N video links from search results

```js
Array.from(document.querySelectorAll('a#video-title'))
  .slice(0, 8)
  .map(a => ({title: a.title || a.innerText.trim(), url: a.href}))
  .filter(x => x.url)
```

Returns: `[{title: "Video Name", url: "https://www.youtube.com/watch?v=..."}, ...]`

Works on `youtube.com/results?search_query=...` pages. The selector `a#video-title` targets the main result links specifically (not shorts, not sidebar recommendations).

## Clean video IDs (strip tracking params)

```js
Array.from(document.querySelectorAll('a#video-title'))
  .slice(0, 8)
  .map(a => ({
    title: a.title || a.innerText.trim(),
    id: new URL(a.href).searchParams.get('v')
  }))
  .filter(x => x.id)
```

Returns raw 11-char video IDs ready for `youtube-transcript-api`.

## Verify all results loaded

```js
document.querySelectorAll('a#video-title').length
```

Returns the count. If < 5, the page may be bot-blocked or cookie-banner-covered.

## Known selectors

| Selector | Target |
|----------|--------|
| `a#video-title` | Main video result links (search page) |
| `a#video-title[href*="/watch?v="]` | Video results only (excludes shorts) |
| `a.yt-simple-endpoint` | General YouTube navigation links |
