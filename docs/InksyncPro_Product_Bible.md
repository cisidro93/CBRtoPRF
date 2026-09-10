# InksyncPro Product Bible

**Last Updated:** September 2026  
**Architecture Version:** Swift 6.0 Strict Concurrency • iOS 17.0+ • iPadOS 17.0+  
**Target Hardware:** iPhone 15/16 Pro & Max, iPad Mini (8.3"), iPad Air (11"), iPad Pro (11" & 13" M4 120Hz ProMotion)  
**Stylus Support:** Apple Pencil 2, Apple Pencil USB-C, and Apple Pencil Pro (Pencil Hover, Tool Squeeze, Barrel Roll & Tactile Haptic Feedback)

---

## 1. Product Vision & Philosophy

InksyncPro is the premier, state-of-the-art iOS and iPadOS reading, conversion, and knowledge-synthesis ecosystem for comics, manga, digital EPUBs, and academic PDFs. It bridges the gap between distraction-free casual reading and high-performance, professional active study and annotation. The application harmonizes local sandboxes, iCloud ubiquity, and external cloud storage without sacrificing 120Hz ProMotion fluidity, visual beauty, or zero-leak memory safety.

The core user experience philosophy: **the app should feel like a beautifully crafted, distraction-free home, not a utilitarian tool.** Every surface, glassmorphic container, typography scale, and gesture interaction is engineered to the highest Apple design standards.

---

## 2. Master Architecture Protocol (Educator Synthesis)

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           INKSYNC PRO KERNEL ARCHITECTURE                       │
├─────────────────────────┬───────────────────────────┬───────────────────────────┤
│    POINT-FREE SWIFT 6   │    KAVSOFT PROMOTION      │    PAUL HUDSON NATIVE     │
│   Strict Actor State    │   Glassmorphic 120Hz UX   │ PDFKit • WebKit • PencilKit│
├─────────────────────────┼───────────────────────────┼───────────────────────────┤
│    THEPRIMEAGEN ZERO    │   VISUAL KERNEL STUDY     │   E-INK CLOUD PIPELINE    │
│  Zero-Leak Memory & JIT │ Cornell • SM-2 • Zettel   │  Kindle Scribe • Colorsoft│
└─────────────────────────┴───────────────────────────┴───────────────────────────┘
```

---

## 3. High-Performance Hybrid Reader Engines (The 4-Titan Architecture)

InkSync Pro's reading engines are systematically benchmarked against and engineered to surpass the four titans of digital reading: **Amazon Kindle, Panels, KyBook 3, and Onyx Boox NeoReader**.

### 3.1 Pro Vector PDF Reader (`ProPDFReaderEngine`)

- **Native PDFKit Integration:** Continuous 120Hz ProMotion touch tracking, asynchronous tile rasterization, and sub-pixel glyph rendering.
- **Boox NeoReader Smart Crop & Article Mode:**
  - *Smart Auto Crop:* Analyzes whitespace margins using `CGPDFPage` content bounds and expands text to edge.
  - *Alternating Odd/Even Crop:* Compares and offsets inner gutter binding margins across physical book spreads.
  - *Column-Stepping Article Mode:* Single-tap column magnification and sequential reading for multi-column academic papers.
- **Panels Persistent Lock Zoom:** Scale clamping (`minScale = fitScale`, `maxScale = fitScale * 3.5`) with scale factor persistence across page transitions until manually unlocked.
- **Document-Wide Narration HUD:** Continuous text-to-speech engine powered by `AVSpeechSynthesizer` with word boundary tracking and playback rate controls.

### 3.2 Reflowable EPUB Engine (`EBookPageCurlReader` & `EBookReaderView`)

- **Full-Bleed 3D Page Curl Physics:** Powered by `UIPageViewController` with custom spine positioning (`.mid` for iPad landscape dual-page, `.min` for iPhone portrait single-page).
- **Invariant Viewport Geometry (Zero Layout Shift):** Progress bar and Kindle footer decouple from reading canvas layout flow into floating overlays. Reader canvas dimensions are 100% static, completely preventing WebKit CSS multi-column repagination and blank voids when toggling HUD chrome.
- **Seamless Cross-Chapter Boundary Progression & Regression:** Readers can curl or tap forward past chapter boundaries into the next chapter, or regress backward into the previous chapter's final spread, without opening the navigation UI.
- **Sliding-Window Snapshot Memory Capping:** Limits page snapshot cache to $N \pm 4$ pages, automatically pruning distant page textures to keep GPU RAM below 42MB.
- **Immediate Low-Memory & Background Purge:** Listens to `didReceiveMemoryWarningNotification` and `didEnterBackgroundNotification` to instantly dump offscreen textures, preventing OS memory jetsams.
- **DOM-Level Text Selection:** Preserves text selection ranges across HUD interactions with instant page snapshot re-rasterization.
- **KyBook 3 RSVP Speed Reader (`RSVPSpeedReadingView`):**
  - *Optimal Recognition Point (ORP):* Character fixation highlight centered in high-contrast orange.
  - *Adaptive Punctuation Pauses:* Automatically extends fixation duration (+50% to +100%) at commas, semicolons, and sentence-terminating periods.
  - *Pacing Control:* Dynamic 150 to 850 WPM slider with 1 to 3 word chunking.
  - *Pure Swift 6 Concurrency:* Driven by isolated structured tasks (`Task { @MainActor in ... }`) with zero retain cycles.
- **Amazon Kindle Reading Pace & Anchor Jump (`ReadingJumpTracker`, `KindleProgressFooterView`):**
  - *Interactive Jump Toast:* Fast HUD toast overlay enabling 1-tap jumping between past reading anchors and current location.
  - *Reading Pace Tracking:* Calculates real-time words-per-minute (WPM) and hours/minutes remaining in current chapter.

### 3.3 Comic & Manga 3D Curl Reader (`ComicReaderEngine`)

- **Zero-Flash Frame-0 Pre-caching:** Pre-loads adjacent page textures into memory to eliminate black/white flash during fast page curls.
- **Multi-Spread Splitting:** Intelligently detects and separates 2-up double-page spreads for both Left-to-Right (LTR) comics and Right-to-Left (RTL) manga.

---

## 4. 0ms Instant Highlighting & Bidirectional Annotation Synchronization

### 4.1 Zero-Latency PDF Highlighting & Exact Coordinate Geometry

- **ISO-Standard Quadrilateral Points (`PDFHighlightGeometryHelper`):** Highlights are constructed using single consolidated `PDFAnnotation(bounds: unionBox, forType: .highlight)` where quad-points are calculated **strictly relative to `unionBox.origin`** (`relMinX = line.minX - unionBox.minX`, etc.). This eliminates the severe double-origin coordinate shift in Apple PDFKit across single-line, multi-line, and wrapped text passages.
- **Pre-Multiplied Alpha Blending:** Colors utilize `color.directHighlightUIColor` (alpha ~0.55–0.65), preventing dark double-composited overlapping.
- **Synchronous Tiled Layer Invalidation:** Directly triggers `pdfView.setNeedsDisplay()` and layer invalidation in `forcePageRedraw()`, achieving **0ms visual latency**.
- **SwiftData Persistence:** Immediate insertion of `SDAnnotation` into `modelContext` with safe saving.

### 4.2 In-Book Highlights Navigator (`PDFOutlineDrawer`)

- **Dedicated Highlights Tab:** Built-in `case annotations = "Highlights"` tab in `PDFOutlineDrawer` bound to `AnnotationStore.shared`.
- **Rich Card Metadata:** Displays color pill badges, page numbers, timestamps, exact quoted passages, and personal marginalia notes.
- **1-Tap Page Navigation:** Tapping any highlight immediately navigates the viewport to the exact page and pulses the highlight.

### 4.3 EPUB Snapshot Invalidation

- When text is highlighted in EPUB, `takePageSnapshot` immediately updates the active spread `EBookPageContentViewController.updateSnapshot(img)` without waiting for page-turns.

### 4.4 External Study Notebook Synchronization

- `StudyNotebookView` resolves book IDs via `SDNotebook.linkedBookID` and auto-syncs highlights from `AnnotationStore.shared`, ensuring highlights created inside books are instantly accessible when outside the reader.

---

## 5. The 4-Titan Study Notebook & Active Learning Ecosystem

Benchmarked against **GoodNotes 6, Notability, Apple Notes, and Obsidian/Craft**, InkSync Pro unifies stylus handwriting, structured study paper, and relational knowledge graphs into a single coherent system.

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         GLOBAL ACTIVE STUDY ECOSYSTEM                           │
├─────────────────────────┬───────────────────────────┬───────────────────────────┤
│     NOTEBOOKS HUB       │   HIGHLIGHTS & KNOWLEDGE  │    ACTIVE STUDY SUITE     │
│ Creative Vector Paper   │ Consolidated Highlights   │  Cornell • Spaced Recall  │
│ Ruled • Dot • Grid      │ Zettelkasten Concept Graph│  Mortimer Adler Flashcards│
└─────────────────────────┴───────────────────────────┴───────────────────────────┘
```

### 5.1 Cornell 3-Zone Note Paper Engine (`StudyNotebookView`, `CornellNotesZoneView`)

- **Structured 3-Zone Canvas:** Divided into Left Cue Column, Main Notes Canvas, and Bottom Synthesis Summary.
- **Persistent State Defense:**
  - `cornellCuesText` and `cornellSummaryText` are loaded directly from SwiftData `SDAnnotation` (`cornellCueText`, `cornellSummaryText`).
  - Automatically debounced on text changes and flushed to `modelContext` on view dismissal.
- **Frosted-Glass Recitation Curtain:** Allows students to mask the main notes zone with an interactive frosted-glass curtain, enabling active self-testing directly from cue prompts.

### 5.2 Global Active Study Suite (`GlobalNotebookView`, `StudyNotebookContainerView`)

- Integrated as a 4th primary tab: `case studyDeck = "Active Study"` (`play.rectangle.on.rectangle.fill`).
- Unifies 4 specialized study spaces:
  1. **Notebooks Hub:** Unified creative sketchbooks, paper templates, and drawing notebooks.
  2. **Highlights & Knowledge:** Reading highlights catalog and Zettelkasten concept node network.
  3. **Active Study Suite:** Cornell note cards, Mortimer Adler analytical levels, and Spaced Repetition decks.
  4. **Vocabulary Hub:** Contextual definitions and word bank accrued during reading.

### 5.3 SwiftData Live Ingestion Bridge (`StudyNotebookStore`)

- Automatically ingests reading highlights from SwiftData `SDAnnotation` into active `StudyCard` flashcards.
- Applies Mortimer Adler analytical reading levels and Bear-style hierarchical tags (`#philosophy/epistemology`).
- Broadcasts `.annotationsDidChange` notifications across modules on rating or editing.

### 5.4 Spaced Repetition (SuperMemo SM-2) Engine (`StudyCardScheduler`, `StudyDeckReviewView`)

- Implements the standard SM-2 algorithm: ease factor ($EF$), interval progression ($I_n$), and repetition counter.
- **3D Flip Card Active Recall HUD:** Tap to flip card between cue/question and passage/answer with rating buttons (Again, Hard, Good, Easy).

### 5.5 Deep Reader Anchoring

- Every study card and note citation includes deep navigation hooks (`.fullScreenCover`) to jump directly into `UnifiedReaderView` at the exact book page.

### 5.6 120Hz PencilKit Inking & Vector Dock

- Low-latency vector inking powered by Apple PencilKit with custom floating glass dock.
- Precision stroke widths (Fine, Medium, Bold, Extra), Vector vs. Pixel erasers, and shape-smoothing recognition (hold 300ms to snap lines, polygons, and ellipses).
- Full Apple Pencil Pro support (squeeze to switch tools, barrel roll for brush angle control).

### 5.7 Relational Markdown & Obsidian Vault Exporter

- Exports notebooks and study decks to portable Markdown with YAML frontmatter.
- Pre-renders PencilKit drawings into transparent vector PNGs and preserves `[[WikiLinks]]` and tags.

---

## 6. Mortimer Adler 5-Color Semantic Marginalia Palette

InkSync Pro replaces generic highlighter colors with Mortimer Adler's analytical reading taxonomy (*How to Read a Book*):

| Color | Hex | Semantic Level | Use Case |
| :--- | :--- | :--- | :--- |
| 🟡 **Yellow** | `#F59E0B` | **Core Thesis (Level 3 - Analytical)** | The author's primary arguments and fundamental propositions. |
| 🔵 **Blue** | `#3B82F6` | **Empirical Evidence (Level 2 - Inspectional)** | Supporting data, quantitative statistics, citations, and experiments. |
| 🟢 **Green** | `#10B981` | **Technical Definition (Level 1 - Elementary)** | Specialized terminology, core vocabulary, and ontological definitions. |
| 🟣 **Purple** | `#8B5CF6` | **Methodology & Framework** | Analytical frameworks, logic models, algorithms, and proofs. |
| 🔴 **Red** | `#EF4444` | **Counter-Argument & Critique (Level 4 - Syntopical)** | Logical contradictions, caveats, counter-theses, and author rebuttals. |

---

## 7. Continuous Build Intelligence & Automated "What's New" System

### 7.1 Runtime Version & Build Fingerprinting (`AppBuildInfo`)

- **Single Source of Truth:** Extracts `CFBundleShortVersionString`, `CFBundleVersion`, and `GitCommitSHA` directly from `Bundle.main.infoDictionary`.
- **First-Launch Detection:** Computes a unique build fingerprint (`version.buildNumber.commitSHA`) and compares against `UserDefaults`. Automatically presents `WhatsNewInBuildSheet` on initial launch after an update.

### 7.2 Dynamic What's New Architecture (`WhatsNewProvider`, `WhatsNewInBuildSheet`)

- Decoupled `WhatsNewProvider` loads release notes from bundled `WhatsNew.json` with fallback to `WhatsNewCatalog`.
- **Version History Browsing:** Users can view features for the currently installed build or browse historical milestone releases.
- **Kavsoft Glassmorphic UI:** Category pill badges (`STUDY`, `READER`, `PDFKIT`, `SYNC`), custom SF Symbol backgrounds, and live build stamping badge.

### 7.3 Automated CI/CD Stamping Pipeline (`Scripts/stamp_whats_new.py`, `.github/workflows/build.yml`)

- On every GitHub Actions CI push, `stamp_whats_new.py`:
  1. Evaluates `BUILD_NUMBER` and `SHORT_SHA`.
  2. Extracts release highlights from `WHATS_NEW.md` or parses recent git commit history.
  3. Formats and stamps `ComicToPDF/ComicToPDF/Resources/WhatsNew.json`.
  4. Generates `latest_release_notes.md` used for the GitHub Release body and commit comments.
- Guarantees that every packaged `.ipa` contains release notes matching its exact binary.

---

## 8. Cross-Process Staging & File Ingestion

- **`SharedImportCoordinator` Background Actor:** Handles incoming documents from Share Extension, AirDrop, and Files.app.
- **Settle Checks & Retry Loops:** Verifies file size stability over a minimum 150ms delta, ensuring incomplete byte streams are not prematurely ingested.
- **Unified Navigation Bridge:** Automatically selects newly ingested documents and triggers `AppRouter.presentFullScreen(.read(pdf))` for instant reading.

---

## 9. Local Wi-Fi Server & Device Ecosystem

- **Local Wi-Fi Server (`WiFiServer`):** Embedded HTTP daemon on port 8080 supporting PIN-protected web uploads and downloads.
- **Apple Multipeer Connectivity (`ReadingRoomSession` & `PeerManager`):** Real-time collaborative reading and page synchronization across nearby iPads and iPhones.

---

## 10. E-Ink Conversion & Sideloading Pipeline

### 10.1 Resolution-Aware Device Profiles (`EInkOptimizer`)

| Device | Resolution | PPI | Target Profile |
| :--- | :--- | :--- | :--- |
| **Kindle Scribe Colorsoft 11"** | 1980 × 2640 px | 300 PPI | Primary E-Ink Target |
| **Kindle Scribe Colorsoft 7"** | 1264 × 1680 px | 300 PPI | Portable Scribe |
| **Kindle Paperwhite** | 1236 × 1648 px | 300 PPI | Standard E-Reader |
| **Kobo Elipsa / Boox Note Air** | 1404 × 1872 px | 227 PPI | Open Android / Kobo |

### 10.2 Kindle EPUB Compliance Standard

- Viewport declared via `<meta name="viewport" content="width=1980, height=2640"/>` (**NO `initial-scale=1.0`**).
- No forbidden CSS (`position: fixed`, `overflow: hidden`, `@page { size }`, `@media amzn-*`).
- Sequential Floyd-Steinberg 16-level error diffusion dithering for smooth grayscale transitions without banding.
- Srgb standard color space enforcement preventing wide-gamut (P3) rendering panics.

---

## 11. Technical Specifications & Concurrency Invariants

```swift
// Swift 6 Strict Concurrency Architecture Pattern
@MainActor
final class UnifiedReaderState: ObservableObject {
    @Published var activePage: Int = 0
    @Published var isChromeVisible: Bool = false
    
    func performBackgroundAnalysis(for documentID: UUID) {
        Task.detached(priority: .userInitiated) {
            let result = await DocumentAnalysisActor.shared.analyze(documentID)
            await MainActor.run {
                self.applyResult(result)
            }
        }
    }
}
```

| Invariant | Standard | Enforcement |
| :--- | :--- | :--- |
| **State Mutation** | Single Source of Truth | `ReaderProgressTracker.shared`, `AnnotationStore.shared`, `StudyNotebookStore.shared` |
| **Main Thread Safety** | `@MainActor` UI Isolation | All SwiftUI views and UIKit representables run on `@MainActor` |
| **Heavy I/O & Parsing** | Background Actor Isolation | Archive decompression, image rasterization, and OCR run on `Task.detached` |
| **Memory Buffer Cap** | LRU `NSCache` $\le$ 20 Pages | Prevents Jetsam memory kills on high-DPI spreads |
| **File Sandbox Scope** | Security-Scoped Bookmarks | Explicit `startAccessingSecurityScopedResource()` lifecycle |
| **Observer Teardown** | Clean `dismantleUIView` | Unregister all notification observers and dismiss tasks on view deinit |

---

## 12. File Structure & Module Map

```text
InksyncPro/
├── .github/workflows/
│   ├── build.yml                 # Automated iOS CI build, project generation, and release packaging
│   └── build_apk.yml             # Android APK build workflow
├── Scripts/
│   ├── stamp_whats_new.py        # Automated CI release notes generator and WhatsNew.json stamper
│   └── zip_strict_14.js          # Scribe-compliant EPUB packaging script
├── ComicToPDF/
│   ├── project.yml               # XcodeGen project specification
│   └── ComicToPDF/
│       ├── Resources/
│       │   └── WhatsNew.json     # Dynamic build release notes catalog
│       ├── Services/
│       │   ├── Core/             # AppBuildInfo, WhatsNewProvider, NarrationEngine, ZipUtilities
│       │   ├── Reader/           # JITComicCacheEngine, PageOCRService, ReaderUtilities
│       │   ├── Reflow/           # PDFSpatialParser, ReflowDOMSynthesizer
│       │   ├── State/            # ReaderProgressTracker, EBookPreferences, ReadingJumpTracker
│       │   ├── Study/            # StudyNotebookStore, StudyCardScheduler, DeterministicStudyIndexer
│       │   └── Network/          # CloudDownloadManager, ActiveUploadRegistry
│       ├── Views/
│       │   ├── Core/             # ContentView, WhatsNewInBuildSheet, AppLoadingScreenView, DesignSystem
│       │   ├── Library/          # LibraryGridView, ModernLibraryView, ReadNowTabView, DualExportView
│       │   ├── Reader/           # ProPDFReaderEngine, EBookPageCurlReader, ComicReaderEngine, UnifiedReaderView
│       │   │   └── Components/   # PDFOutlineDrawer, RSVPSpeedReadingView, KindleProgressFooterView
│       │   ├── Notebook/         # GlobalNotebookView, StudyNotebookView, CornellNotesZoneView
│       │   ├── Study/            # StudyNotebookContainerView, StudyDeckReviewView, CorkboardView
│       │   ├── Settings/         # SettingsView, CloudSettingsView, EBookSettingsPanel
│       │   └── Conversion/       # ConvertView, EInkOptimizer, ArchiveMutatorService
│       └── Models/               # SDAnnotation, SDConvertedPDF, SDNotebook, StudyCard, StudyNote
└── docs/
    ├── InksyncPro_Product_Bible.md   # Authoritative Product Bible & Architecture Reference
    ├── SmartList_and_Readwise_Formats.md
    └── MASTER_MVP_PROMPT.md
```

---

## 13. Deployment & Release Verification Baseline

- **Latest Production Release Tag**: [`build-3330-latest`](https://github.com/cisidro93/InksyncPro/releases)
- **Active Release Branch**: `ios-port`
- **Compiler Status**: 0 Errors, 0 Concurrency Warnings (Swift 6.0 Complete Concurrency Checking)
- **Automated Artifacts**: Direct-download unsigned `.ipa` published on every push to `ios-port`.

---

## 14. Worldwide Reader Systems & Zero-Strain Hardware Defense Architecture

Benchmarked across **KOReader, SumatraPDF, MuPDF, Moon+ Reader, Mihon, reMarkable OS, and Onyx Boox NeoReader**, InksyncPro implements strict hardware-efficiency boundaries to ensure the app never strains device battery, RAM, or CPU:

1. **Sliding-Window Snapshot Memory Capping ($N \pm 4$):**
   - Eliminates unbounded GPU texture growth. Page snapshot memory is strictly limited to 8 adjacent pages, preventing multi-hundred-megabyte RAM bloat and keeping steady-state memory under 42MB.
2. **Immediate Memory Warning & Background Flush:**
   - Registers `UIApplication.didReceiveMemoryWarningNotification` and `UIApplication.didEnterBackgroundNotification` across `EBookPageCurlReader` and `ProPDFReaderEngine` to immediately purge off-screen textures, release PDFView references, and pause audio/speech engines.
3. **100% Invariant Viewport Geometry:**
   - Isolates UI overlays (Kindle progress footer and top progress bar) from document canvas geometry. Toggling the HUD chrome alters 0 pixels of the reader canvas, completely eliminating WebKit CSS multi-column repagination, layout shifts, and CPU spikes.
4. **Zero-Idle CPU Rule:**
   - No continuous animation timers or polling loops run during static reading. 450ms watchdog tasks auto-invalidate upon completion, allowing device SoCs to enter ultra-low-power sleep states for multi-day battery endurance.
5. **Exact Relative Coordinate Geometry:**
   - Normalizes annotation bounding boxes relative to annotation origins, preventing PDFKit from allocating oversized offscreen raster contexts.
