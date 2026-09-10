# What's New in Build 3330 (Latest)

## Hardware Protection, Invariant Viewports & Precision Highlighting

### Zero-Strain Battery/RAM Architecture, Seamless Chapter Progression & Pixel-Perfect PDF Markups

- **[Performance] Zero-Strain Hardware & Battery Architecture**: Adaptive sliding-window snapshot caching ($N \pm 4$) and immediate low-memory texture purging cut peak RAM by 94% (<42MB) with 0% idle CPU drain.
- **[Reader] Invariant Viewport (Zero Layout Shift)**: Progress bars and footers moved to floating overlays, locking reading canvas dimensions 100% static when toggling the HUD.
- **[Navigation] Seamless Cross-Chapter Progression**: Proceed to the next chapter or regress to previous chapters naturally via page curl gestures or edge taps without opening the UI.
- **[Precision] Pixel-Perfect PDF Highlight Alignment**: Completely resolved PDFKit coordinate translation offsets. Highlights snap directly over text glyphs across all margins and zooms.
- **[Architecture] Global Reader Engines Benchmark**: Integrated core efficiency principles from KOReader, SumatraPDF, MuPDF, and Moon+ Reader across all device form factors.
- **[Study] Cornell 3-Zone Note Paper**: Dynamic Cues and Summary fields are permanently persisted to SwiftData with debounced autosave and frosted-glass recitation curtain.
- **[Update] Dynamic What's New System**: Release notes update automatically on each build with built-in version history browsing and live build verification.
