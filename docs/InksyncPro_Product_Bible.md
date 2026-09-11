# InksyncPro Product Bible

**Last Updated:** September 2026  
**Architecture Version:** Swift 6.0 Strict Concurrency • iOS 17.0+ • iPadOS 17.0+  
**Target Hardware:** iPhone 15/16 Pro & Max, iPad Mini (8.3"), iPad Air (11"), iPad Pro (11" & 13" M4 120Hz ProMotion)  
**Stylus Support:** Apple Pencil 2, Apple Pencil USB-C, and Apple Pencil Pro (Pencil Hover, Tool Squeeze, Barrel Roll & Tactile Haptic Feedback)

### Revision History

| Version | Date | Key Architectural Adjustments & Reconciliations |
| :--- | :--- | :--- |
| **v1.0** | May 2026 | Initial system architecture, multi-format reader engine design, and hardware profile baselines. |
| **v2.0** | September 2026 | Unified cache limits (`ReaderCacheLimits`), added measured/target telemetry tags, documented `ConversionLedger`, `ComicVineRateTracker`, and `CloudCoverExtractor`; introduced 3-tier roadmap, Security, Accessibility, and Non-Goals. |
| **v2.1** | September 2026 | Aligned e-ink device profiles with `TargetDeviceProfile` enum (splitting Colorsoft 7" and Boox Note Air3 C); replaced personal attributions in kernel diagram with descriptive architectural pillars; clarified unadorned source-layer content hashing; implemented intentional rereading regression handling & FIFO session eviction in `ReadingProgress.merge`; documented 6-digit PIN, 5-attempt IP lockout & 500ms anti-timing delay in `WiFiServer`; added inline tier tags across all sections and declared localization baseline. |
| **v2.2** | September 2026 | Explicitly designated Core PDF Annotation, Highlighting & Apple Pencil Inking as Tier 1 MVP baseline; documented ISO 32000-1 quad points, Adler 5-color palette, 120Hz PencilKit canvas overlays, and bi-directional native sync bridge under Tier 1; updated Section 2.1, Section 3.1, and Section 6. |
| **v2.3** | September 2026 | Expanded Tier 1 Core MVP scope to encompass EPUB Annotation & In-Book Search (`EPUBSearchView`), full Comic/Manga Reading Modes (LTR, RTL Manga, Webtoon Vertical Scroll, Dual Spreads in `ComicReaderEngine`), and Library "Read Now" Shelving & Progress Resume (`ModernLibraryView`, `ReadNowTabView`); hardened search task cancellation and progress persistence on disappear. |

---

## 1. Product Vision & Philosophy

InksyncPro is a high-performance iOS and iPadOS reading, conversion, and knowledge-synthesis ecosystem for comics, manga, digital EPUBs, and academic PDFs. It bridges the gap between distraction-free casual reading and high-performance, professional active study and annotation. The application harmonizes local sandboxes, iCloud ubiquity, and external cloud storage without sacrificing 120Hz ProMotion fluidity, visual beauty, or zero-leak memory safety.

The core user experience philosophy: **the app should feel like a beautifully crafted, distraction-free home, not a utilitarian tool.** Every surface, glassmorphic container, typography scale, and gesture interaction is engineered to the highest Apple design standards.

> [!NOTE]
> References to commercial reading software and hardware throughout this document denote internal engineering benchmarks and behavioral interaction models (e.g., Kindle progress pacing, Boox auto-crop geometry, KyBook RSVP reading, GoodNotes inking). They represent architectural design targets rather than customer-facing marketing claims or comparative endorsements.

---

## 2. Master Architecture Protocol

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           INKSYNC PRO KERNEL ARCHITECTURE                       │
├─────────────────────────┬───────────────────────────┬───────────────────────────┤
│   STRICT CONCURRENCY    │    PROMOTION 120HZ UX     │    NATIVE FRAMEWORKS      │
│   Pure Actor State      │   Glassmorphic Micro-UX   │ PDFKit • WebKit • PencilKit│
├─────────────────────────┼───────────────────────────┼───────────────────────────┤
│    HARDWARE DEFENSE     │   ACTIVE STUDY ENGINE     │    E-INK OPTIMIZATION     │
│  Zero-Leak Memory Caps  │ Cornell • SM-2 • Zettel   │  Kindle Scribe • Colorsoft│
└─────────────────────────┴───────────────────────────┴───────────────────────────┘
```

The system architecture is structured across six self-reinforcing engineering pillars:
1. **Strict Concurrency**: Swift 6 actor-isolated state management and single-source-of-truth stores (`ReaderProgressTracker.shared`, `AnnotationStore.shared`).
2. **ProMotion 120Hz UX**: Low-latency rendering, fluid spring physics, glassmorphic materials (`.ultraThinMaterial`), and rich haptic feedback.
3. **Native Frameworks**: Deep integration of first-party Apple frameworks (PDFKit, WebKit, PencilKit, Accelerate vImage, SwiftData).
4. **Hardware Defense**: Zero-leak memory safety via device-tiered buffer capping (`ReaderCacheLimits`), immediate Jetsam flushes, and zero-idle background watchdog tasks.
5. **Active Study Engine**: Visual knowledge management unifying Cornell notes, SuperMemo SM-2 spaced repetition, and Zettelkasten concept auto-linking.
6. **E-Ink Optimization**: Dynamic resolution-aware downsampling and Floyd-Steinberg error diffusion dithering tailored to specific e-paper hardware profiles.

---

## 2.1 Phased Development Roadmap & Scope Tiers

To maintain architectural focus and high engineering standards during development, features are partitioned into three explicit delivery tiers:

### Tier 1: Core Reading MVP (Active Production Baseline)

- **Vector & Reflowable Reader Engines:** Robust, crash-free viewing for PDF (`ProPDFReaderEngine` with Smart Margin Crop and Panels-style lock zoom), Reflowable EPUB (`EBookPageCurlReader` with invariant viewport geometry and 3D curl), and Comic archives (`ComicReaderEngine` with spread splitting and JIT decompression).
- **Core PDF Annotation, Highlighting & Inking:** Full native PDFKit text markup (`PDFAnnotation` for highlight, underline, and strikethrough), Mortimer Adler 5-color semantic palette, ISO 32000-1 quadrilateral point geometry (`PDFHighlightGeometryHelper`), fluid word-snapping touch and Apple Pencil glide selection, note popovers, and bookmarks.
- **EPUB Reading, Formatting & In-Book Search Suite:** DOM-level Mortimer Adler text highlighting (`EBookReaderView`), custom reader typography (Literata, Bookerly, Atkinson Hyperlegible, OpenDyslexic), line/margin spacing, theme modes (Light/Sepia/Dark/OLED), chapter Table of Contents, and full-text asynchronous chapter search with snippet highlighting (`EPUBSearchView`).
- **Full Comic & Manga Reading Engine:** LTR Western layout, RTL Japanese Manga mode (`.mangaRTL`), continuous vertical Webtoon infinite scroll (`WebtoonScrollView`), 2-page landscape spreads with intelligent split detection, and hardware-capped thumbnail scrub bar.
- **Library "Read Now" Dashboard & Shelving Engine:** Continue reading carousel, reading speed velocity forecasting (`VelocityViewModel`), finished counters, custom shelving, fast search/filter, batch actions, and instant progress resume.
- **120Hz Native Apple Pencil Inking:** `PDFPageCanvasProvider` zero-drift `PassthroughPKCanvasView` overlays anchored directly into `PDFPageView` scroll tiles with floating tool dock, tool squeeze, barrel roll, eraser, and stroke persistence.
- **Authoritative State & Unified Annotation Persistence:** Multi-level storage with instant memory cache (`AnnotationStore.shared`), background SwiftData persistence (`SDAnnotation`), and debounced native PDF disk synchronization (`PDFAnnotationSyncBridge`). Single source of truth reading progress with non-destructive field-level iCloud merge (`ReadingProgress.merge(local:remote:)`) supporting intentional rereading regression.
- **Content-Hash Page Anchoring:** Dual keying of annotations via absolute page index and cryptographic page content hashes (`PageContentHasher`, `AnnotationStore.hashIndex`) computed strictly on unadorned source layers.
- **Zero-Leak Hardware Defense:** Centralized cache limits (`ReaderCacheLimits`), immediate `didReceiveMemoryWarningNotification` memory flushing, and zero-idle background watchdog tasks.
- **Cross-Process File Ingestion:** Resilient document import via Files.app, AirDrop, and Share Extension with file stability settle loops (`SharedImportCoordinator`).

### Tier 2: Pro Active Study & Knowledge Synthesis (Secondary Focus)

- **Cornell 3-Zone Note Paper:** Left Cue, Notes Canvas, and Summary zones with interactive recitation curtain and SwiftData persistence (`StudyNotebookView`, `CornellNotesZoneView`).
- **Spaced Repetition (SuperMemo SM-2):** Algorithmic flashcard scheduling and 3D flip card active recall HUD (`StudyCardScheduler`, `StudyDeckReviewView`).
- **Zettelkasten Concept Auto-Linking:** Algorithmic knowledge graph formation (`ZettelkastenAutoLinker`), automated cross-document concept indexing, and bi-directional linked node navigation.
- **Relational Markdown Exporter:** Clean Markdown and Obsidian vault export with YAML frontmatter, pre-rendered vector PNG assets, and `[[WikiLinks]]`.

### Tier 3: Collaborative, Conversion & Ecosystem Extensions (Stretch / Non-Blocking)

- **Collaborative Reading:** Local peer synchronization via Apple Multipeer Connectivity (`ReadingRoomSession`, `PeerManager`).
- **Embedded Web Server:** Local Wi-Fi HTTP daemon (`WiFiServer`) with dynamic 6-digit PIN authentication, 5-attempt IP lockout, and 500ms anti-timing delay.
- **Kindle Scribe / Colorsoft Pipeline:** E-ink conversion pipeline with 16-level Floyd-Steinberg dithering and transactional ledger tracking (`EInkOptimizer`, `ConversionLedger`).
- **Cross-Platform Companion:** Android APK build pipeline and cross-platform verification.

---

## 3. High-Performance Hybrid Reader Engines (The 4-Titan Architecture)

> **Roadmap Scope:** Tier 1 (Core Reading MVP)

InkSync Pro's reading engines are systematically benchmarked against and engineered to match or surpass the four titans of digital reading: **Amazon Kindle, Panels, KyBook 3, and Onyx Boox NeoReader**.

### 3.1 Pro Vector PDF Reader (`ProPDFReaderEngine`)

- **Native PDFKit Integration:** Continuous 120Hz ProMotion touch tracking [Target: 8.33ms frame interval], asynchronous tile rasterization, and sub-pixel glyph rendering.
- **Core PDF Annotation & Highlighting Engine (Tier 1 Baseline):**
  - *Adler 5-Color Semantic Palette:* 🟡 Core Thesis, 🔵 Empirical Evidence, 🟢 Technical Definition, 🟣 Methodology, 🔴 Counter-Argument.
  - *Quad-Point Glyph Geometry:* ISO 32000-1 compliant quadrilateral points (`PDFHighlightGeometryHelper.createQuadPoints`) for sub-pixel text alignment matching glyph angles.
  - *Touch & Apple Pencil Glide Selection:* 180ms finger glide and 20ms stylus glide with proximity-assisted word snapping.
  - *Multi-Level Persistence:* Instant memory lookup via `AnnotationStore.shared`, background SwiftData persistence (`SDAnnotation`), and bi-directional Adobe-standard disk sync via `PDFAnnotationSyncBridge`.
- **120Hz Apple Pencil Canvas Overlays (Tier 1 Baseline):**
  - *Zero-Drift Tile Overlays:* `PDFPageCanvasProvider` binds scoped `PassthroughPKCanvasView` overlays to each `PDFPageView` scroll tile, preventing coordinate drift on zoom.
  - *Hardware Stylus Features:* PencilKit floating dock, double-tap eraser toggle, Apple Pencil Pro squeeze gesture, and tactile haptic feedback.
- **Boox NeoReader Smart Crop & Article Mode:**
  - *Smart Auto Crop:* Analyzes whitespace margins using `CGPDFPage` content bounds and expands text to edge.
  - *Alternating Odd/Even Crop:* Compares and offsets inner gutter binding margins across physical book spreads.
  - *Column-Stepping Article Mode:* Single-tap column magnification and sequential reading for multi-column academic papers.
- **Panels Persistent Lock Zoom:** Scale clamping (`minScale = fitScale`, `maxScale = fitScale * 3.5 [Target]`) with scale factor persistence across page transitions until manually unlocked.
- **Document-Wide Narration HUD:** Continuous text-to-speech engine powered by `AVSpeechSynthesizer` with word boundary tracking and playback rate controls.

### 3.2 Reflowable EPUB Engine (`EBookPageCurlReader` & `EBookReaderView`)

- **Full-Bleed 3D Page Curl Physics:** Powered by `UIPageViewController` with custom spine positioning (`.mid` for iPad landscape dual-page, `.min` for iPhone portrait single-page).
- **Invariant Viewport Geometry (Zero Layout Shift):** Progress bar and Kindle footer decouple from reading canvas layout flow into floating overlays. Reader canvas dimensions are 100% static, completely preventing WebKit CSS multi-column repagination and blank voids when toggling HUD chrome.
- **Seamless Cross-Chapter Boundary Progression & Regression:** Readers can curl or tap forward past chapter boundaries into the next chapter, or regress backward into the previous chapter's final spread, without opening the navigation UI.
- **EPUB Sliding-Window Snapshot Memory Capping (`ReaderCacheLimits.epubSnapshotDistance = 4`):** Limits page snapshot cache to a strict sliding window of $N \pm 4$ pages (maximum 9 active page textures centered on the active spread), automatically pruning distant page textures to keep GPU RAM below 42MB [Measured on Apple A17 Pro / M4].
- **Immediate Low-Memory & Background Purge:** Listens to `didReceiveMemoryWarningNotification` and `didEnterBackgroundNotification` to instantly dump offscreen textures, preventing OS memory jetsams.
- **DOM Ready-State Watchdog:** 450ms watchdog task [Target] automatically invalidates upon DOM completion to prevent WebKit rendering hangs.
- **DOM-Level Text Selection:** Preserves text selection ranges across HUD interactions with instant page snapshot re-rasterization.
- **KyBook 3 RSVP Speed Reader (`RSVPSpeedReadingView`):**
  - *Optimal Recognition Point (ORP):* Character fixation highlight centered in high-contrast orange.
  - *Adaptive Punctuation Pauses:* Automatically extends fixation duration (+50% to +100%) at commas, semicolons, and sentence-terminating periods.
  - *Pacing Control:* Dynamic 150 to 850 WPM slider with 1 to 3 word chunking.
  - *Pure Swift 6 Concurrency:* Driven by isolated structured tasks (`Task { @MainActor in ... }`) with zero retain cycles.
- **Amazon Kindle Reading Pace & Anchor Jump (`ReadingJumpTracker`, `KindleProgressFooterView`):**
  - *Interactive Jump Toast:* Fast HUD toast overlay enabling 1-tap jumping between past reading anchors and current location.
  - *Reading Pace Tracking:* Calculates real-time words-per-minute (WPM) and hours/minutes remaining in current chapter.

### 3.3 Comic & Manga 3D Curl Reader (`ComicReaderEngine` & `PageBufferManager`)

- **Hardware-Tiered Buffer Sizing (`ReaderCacheLimits`):** Dynamically allocates uncompressed page cache limits (`low: 8`, `standard: 16`, `pro: 32`, `dualSpread: 7`) based on device performance class to guarantee zero jetsams.
- **Zero-Flash Frame-0 Pre-caching:** Pre-loads adjacent page textures into memory to eliminate black/white flash during fast page curls.
- **Multi-Spread Splitting:** Intelligently detects and separates 2-up double-page spreads for both Left-to-Right (LTR) comics and Right-to-Left (RTL) manga.

---

## 4. Instant Highlighting & Bidirectional Annotation Synchronization

> **Roadmap Scope:** Tier 1 (Core In-Book Highlighting) & Tier 2 (Content-Hash Anchoring & Study Sync)

### 4.1 Zero-Latency PDF Highlighting & Exact Coordinate Geometry

- **ISO-Standard Quadrilateral Points (`PDFHighlightGeometryHelper`):** Highlights are constructed using single consolidated `PDFAnnotation(bounds: unionBox, forType: .highlight)` where quad-points are calculated **strictly relative to `unionBox.origin`** (`relMinX = line.minX - unionBox.minX`, etc.). This eliminates the severe double-origin coordinate shift in Apple PDFKit across single-line, multi-line, and wrapped text passages.
- **Pre-Multiplied Alpha Blending:** Colors utilize `color.directHighlightUIColor` (alpha ~0.55–0.65), preventing dark double-composited overlapping.
- **Synchronous Main-Runloop Layer Invalidation:** Directly triggers `pdfView.setNeedsDisplay()` and layer invalidation in `forcePageRedraw()` within the active runloop pass, eliminating asynchronous thread hops and redraw delays [Target: < 16ms frame deadline for 60Hz / < 8.3ms for 120Hz ProMotion; Measured: 0 dropped frames on Apple A17 Pro / M4].
- **Content-Hash Page Anchoring (`PageContentHasher`, `AnnotationStore.hashIndex`):**
  - Anchors highlights and annotations not only to absolute page numbers (which shift when documents are edited or re-paginated) but also to cryptographic SHA-256 hashes of base page visual content.
  - **Source-Layer Invariant:** Hashes are computed strictly from the **unadorned base source content** (raw image archive bitmap or underlying `CGPDFPage` vector stream via `PageContentHasher.sha256Hex(ofBasePDFPage:)`) **BEFORE** any user highlight overlays, PencilKit ink layers, or UI badges are composited. This guarantees page hashes remain 100% stable as annotations are added or modified, completely eliminating self-invalidation cascades.
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

## 5. The Active Study Notebook & Learning Ecosystem

> **Roadmap Scope:** Tier 2 (Pro Active Study)

Benchmarked against modern digital study environments, InkSync Pro unifies stylus handwriting, structured study paper, and relational knowledge graphs into a single coherent system.

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

> **Roadmap Scope:** Tier 1 (Core In-Book Highlighting & Markup MVP) & Tier 2 (Active Study Deck Integration)

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

> **Roadmap Scope:** Tier 1 (Core Release Infrastructure)

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

## 8. Cross-Process Staging, Ingestion & Cloud Synchronization

> **Roadmap Scope:** Tier 1 (Core Ingestion) & Tier 2 (Metadata & Cloud Sync)

### 8.1 Ingestion Pipeline (`SharedImportCoordinator`)

- **`SharedImportCoordinator` Background Actor:** Handles incoming documents from Share Extension, AirDrop, and Files.app.
- **Settle Checks & Retry Loops:** Verifies file size stability over a minimum 150ms delta [Measured: prevents ingestion of active AirDrop or Files chunk transfers], ensuring incomplete byte streams are not prematurely ingested.
- **Unified Navigation Bridge:** Automatically selects newly ingested documents and triggers `AppRouter.presentFullScreen(.read(pdf))` for instant reading.

### 8.2 External Metadata & Cloud Resilience (`ComicVineRateTracker`, `CloudCoverExtractor`)

- **ComicVine Rate Limiter (`ComicVineRateTracker`):** Enforces a sliding 1-hour 200 req/hr rate limit defense with token-bucket pacing and persistent timestamps, preventing developer API lockouts during bulk metadata scrapes.
- **Dropbox Cover Art & Thumbnail Cache (`CloudCoverExtractor`):** Handles automatic OAuth token refresh for 4-hour token lifespans and performs atomic image extraction with persistent local disk caching to prevent blank or corrupted cover art thumbnails.

### 8.3 Non-Destructive iCloud Sync Merge (`ReaderProgressTracker`)

- **Bidirectional Progress Reconciliation:**
  - `ReadingProgress.merge(local:remote:)` evaluates furthest forward progress across chapter indices, chapter offsets, completion fractions, and page numbers for standard stale-device catch-up.
  - **Intentional Backward Reread Preservation:** If a device has an earlier page position but displays a distinctly newer active reading interaction (> 60 seconds newer than the other device's last activity), the system treats this as an intentional rereading session and preserves that deliberate position instead of forcefully snapping forward to a stale furthest point.
- **Session History Union & FIFO Eviction:**
  - Preserves lifetime page counts (`max(local, remote)`).
  - Merges and deduplicates unique reading days across devices.
  - Unions reading session events within 60-second deduplication windows, enforcing a strict **FIFO (First-In, First-Out) eviction policy** when history exceeds the 200-event cap (dropping oldest records to maintain a clean rolling window).
- **Display Preference Preservation:** Retains local custom crops, manga mode toggles, and color filters non-destructively.

---

## 9. Local Wi-Fi Server & Device Ecosystem

> **Roadmap Scope:** Tier 3 (Collaborative & Local Network Extensions)

- **Local Wi-Fi Server (`WiFiServer`):**
  - Embedded HTTP daemon on port 8080 supporting web uploads and downloads directly from any local browser.
  - **Security Baseline:** Cryptographically random 6-digit PIN (`%06d`, 1,000,000 combinations), automatic 5-attempt IP lockout (`ipBlockThreshold = 5`, HTTP 403), a non-blocking 500ms anti-timing attack delay on failed authentications, and a 15-minute auto-shutdown timer.
  - **TLS Integration Roadmap:** `WiFiCertificateManager` manages P-256 key-pair generation stored in the Apple Keychain, architected for future TLS transport binding.
- **Apple Multipeer Connectivity (`ReadingRoomSession` & `PeerManager`):** Real-time collaborative reading and page synchronization across nearby iPads and iPhones.

---

## 10. E-Ink Conversion & Sideloading Pipeline

> **Roadmap Scope:** Tier 3 (Sideloading & Format Conversion)

### 10.1 Resolution-Aware Device Profiles (`TargetDeviceProfile`, `EInkOptimizer`)

Device profiles are mapped directly to physical display resolutions to eliminate runtime downsampling lag and letterboxing artifacts:

| Device | Resolution | PPI | Target Profile |
| :--- | :--- | :--- | :--- |
| **Kindle Scribe Colorsoft 11" (2025)** | 1980 × 2640 px | 300 PPI | Primary E-Ink Stylus Target (`.scribeColorsoft`) |
| **Kindle Colorsoft 7" (2024)** | 1264 × 1680 px | 300 PPI | Portable Color Reader (`.colorsoft7`) |
| **Kindle Paperwhite (2024)** | 1264 × 1680 px | 300 PPI | Standard E-Reader (`.paperwhite2024`) |
| **Kindle Scribe 1st Gen (2022)** | 1860 × 2480 px | 300 PPI | Monochrome 10.2" Scribe (`.scribe`) |
| **Kobo Elipsa 2E (2023)** | 1404 × 1872 px | 227 PPI | Open Kobo 10.3" Large Format (`.koboElipsa2E`) |
| **Boox Note Air3 C / Tab Ultra C Pro** | 1860 × 2480 px | 300 PPI B&W / 150 PPI Color | Kaleido 3 10.3" Color E-Paper (`.booxNoteAir3C`) |

### 10.2 Kindle EPUB Compliance Standard

- Viewport declared via `<meta name="viewport" content="width=1980, height=2640"/>` (**NO `initial-scale=1.0`**).
- No forbidden CSS (`position: fixed`, `overflow: hidden`, `@page { size }`, `@media amzn-*`).
- Sequential Floyd-Steinberg 16-level error diffusion dithering for smooth grayscale transitions without banding.
- Srgb standard color space enforcement preventing wide-gamut (P3) rendering panics.

### 10.3 Transactional Conversion Ledger (`ConversionLedger`)

- **Transactional Job Tracking:** Resilient job lifecycle tracking with exponential backoff retry policies for interrupted rendering tasks.
- **Scratch Directory Garbage Collection:** Automatic detection and reclamation of orphaned conversion scratch directories on app launch and memory warnings.
- **Structured Audit Logging:** Complete audit trail logging of all document conversion stages, optimization parameters, and execution timings.

---

## 11. Technical Specifications & Concurrency Invariants

> **Roadmap Scope:** Core Architectural Foundation (Applies to all Tiers)

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
| **Comic Buffer Cache** | Device-Tiered `NSCache` (`low: 8`, `standard: 16`, `pro: 32`, `dualSpread: 7`) | Prevents Jetsam memory kills on high-DPI spreads (`ReaderCacheLimits`) |
| **EPUB Snapshot Cache** | Sliding Window $N \pm 4$ (Max 9 textures) | Prunes textures outside active window to keep GPU RAM < 42MB [Measured] (`ReaderCacheLimits.epubSnapshotDistance`) |
| **Thumbnail Strip Cache** | LRU `NSCache` $\le$ 64 Thumbnails | Low-overhead scrub-bar slider previews (`ReaderCacheLimits.thumbnailScrubBar`) |
| **File Sandbox Scope** | Security-Scoped Bookmarks | Explicit `startAccessingSecurityScopedResource()` lifecycle |
| **Observer Teardown** | Clean `dismantleUIView` | Unregister all notification observers and dismiss tasks on view deinit |

---

## 12. File Structure & Module Map

> **Roadmap Scope:** System-Wide Directory Structure

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
│       │   ├── Core/             # AppBuildInfo, WhatsNewProvider, NarrationEngine, ZipUtilities, SharedModels
│       │   ├── Reader/           # CacheConfiguration, JITComicCacheEngine, PageBufferManager, PageOCRService
│       │   ├── Reflow/           # PDFSpatialParser, ReflowDOMSynthesizer
│       │   ├── State/            # ReaderProgressTracker, EBookPreferences, ReadingJumpTracker
│       │   ├── Study/            # StudyNotebookStore, StudyCardScheduler, DeterministicStudyIndexer
│       │   ├── Conversion/       # ConversionLedger, EInkOptimizer, PageContentHasher, ArchiveMutatorService
│       │   └── Network/          # ComicVineRateTracker, CloudCoverExtractor, CloudDownloadManager, WiFiServer, WiFiCertificateManager
│       ├── Views/
│       │   ├── Core/             # ContentView, WhatsNewInBuildSheet, AppLoadingScreenView, DesignSystem
│       │   ├── Library/          # LibraryGridView, ModernLibraryView, ReadNowTabView, DualExportView
│       │   ├── Reader/           # ProPDFReaderEngine, EBookPageCurlReader, ComicReaderEngine, UnifiedReaderView
│       │   │   └── Components/   # PDFOutlineDrawer, RSVPSpeedReadingView, KindleProgressFooterView
│       │   ├── Notebook/         # GlobalNotebookView, StudyNotebookView, CornellNotesZoneView
│       │   ├── Study/            # StudyNotebookContainerView, StudyDeckReviewView, CorkboardView
│       │   ├── Settings/         # SettingsView, CloudSettingsView, EBookSettingsPanel, WiFiView
│       │   └── Conversion/       # ConvertView, EInkOptimizer, ArchiveMutatorService
│       └── Models/               # SDAnnotation, SDConvertedPDF, SDNotebook, StudyCard, StudyNote, ReadingProgress
└── docs/
    ├── InksyncPro_Product_Bible.md   # Authoritative Product Bible & Architecture Reference
    ├── SmartList_and_Readwise_Formats.md
    └── MASTER_MVP_PROMPT.md
```

---

## 13. Deployment & Release Verification Baseline

> **Roadmap Scope:** System-Wide CI/CD Pipeline

- **Latest Production Release Tag**: [`build-3330-latest`](https://github.com/cisidro93/InksyncPro/releases)
- **Active Release Branch**: `ios-port`
- **Compiler Status**: 0 Errors, 0 Concurrency Warnings (Swift 6.0 Complete Concurrency Checking)
- **Automated Artifacts**: Direct-download unsigned `.ipa` published on every push to `ios-port`.

---

## 14. Hardware Defense Architecture

> **Roadmap Scope:** Core Architectural Foundation (Applies to all Tiers)

Benchmarked across leading mobile and e-ink reading engines, InksyncPro implements strict hardware-efficiency boundaries to ensure the app never strains device battery, RAM, or CPU:

1. **EPUB Sliding-Window Snapshot Memory Capping ($N \pm 4$, Max 9 Textures):**
   - Eliminates unbounded GPU texture growth in reflowable WebKit curls. Page snapshot memory is strictly bounded to the active spread plus 4 adjacent pages forward and backward (`ReaderCacheLimits.epubSnapshotDistance = 4`), preventing multi-hundred-megabyte RAM bloat and keeping steady-state GPU RAM under 42MB [Measured on Apple A17 Pro / M4].
2. **Adaptive Hardware-Tiered Comic Buffer (`ReaderCacheLimits`):**
   - Dynamically provisions memory limits based on device performance class (`low: 8`, `standard: 16`, `pro: 32` uncompressed high-resolution pages, capped at 7 pages during dual-spread mode) via `ProcessInfo.processInfo.performanceClass`, eliminating jetsam crashes on high-DPI graphic novels.
3. **Immediate Memory Warning & Background Flush:**
   - Registers `UIApplication.didReceiveMemoryWarningNotification` and `UIApplication.didEnterBackgroundNotification` across `EBookPageCurlReader`, `PageBufferManager`, and `ProPDFReaderEngine` to immediately purge off-screen textures, release PDFView references, and pause audio/speech engines.
4. **100% Invariant Viewport Geometry:**
   - Isolates UI overlays (Kindle progress footer and top progress bar) from document canvas geometry. Toggling the HUD chrome alters 0 pixels of the reader canvas, completely eliminating WebKit CSS multi-column repagination, layout shifts, and CPU spikes.
5. **Zero-Idle CPU Rule:**
   - No continuous animation timers or polling loops run during static reading. 450ms watchdog tasks [Target] auto-invalidate upon completion, allowing device SoCs to enter ultra-low-power sleep states for multi-day battery endurance.
6. **Exact Relative Coordinate Geometry:**
   - Normalizes annotation bounding boxes relative to annotation origins, preventing PDFKit from allocating oversized offscreen raster contexts.

---

## 15. Security, Privacy & Threat Model

> **Roadmap Scope:** Core Foundation & Tier 3 Network Boundaries

InksyncPro is engineered with an on-device privacy-first architecture, treating user library documents and personal annotations as strictly confidential personal data:

1. **iOS Data Protection & Storage Encryption:**
   - SwiftData stores (`.store` SQLite databases) and local document sandboxes inherit iOS hardware-backed encryption at rest using `NSFileProtectionCompleteUntilFirstUserAuthentication`.
2. **Credential Management (Apple Keychain):**
   - All third-party authentication tokens and API credentials (ComicVine API keys, Dropbox OAuth bearer tokens, Google Drive secrets) are stored exclusively in the Apple Keychain with device-scoped accessibility (`kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`). Tokens are never persisted in plaintext, `UserDefaults`, or unencrypted property lists.
3. **Embedded Wi-Fi Server Threat Model:**
   - The local Wi-Fi transfer daemon (`WiFiServer`) binds strictly to local network interfaces and loopback; WAN port forwarding is never initiated.
   - Access requires a dynamic 6-digit numeric PIN generated on-device per session (1,000,000 combinations).
   - Automated brute-force attacks are defeated via an immediate 5-attempt IP block threshold (`ipBlockThreshold = 5`, HTTP 403) and an artificial 500ms non-blocking response delay to prevent timing side-channels.
   - The server defaults to off, requires deliberate user activation in Settings, and automatically shuts down after 15 minutes of inactivity.
4. **Zero Remote Telemetry or Tracking:**
   - InksyncPro contains zero third-party analytics SDKs, advertising frameworks, or remote telemetry beacons. All document parsing, OCR text recognition, and metadata processing occurs entirely on-device.

---

## 16. Accessibility, Inclusivity & Localization Baseline

> **Roadmap Scope:** Core Architectural Foundation (Tier 1 Baseline)

InksyncPro treats accessibility as a foundational engineering requirement rather than a secondary cosmetic overlay:

1. **Dynamic Type & Typography Scaling:**
   - All HUD controls, menus, outline drawers, and library cards support Apple Dynamic Type, automatically adjusting point size, line spacing, and padding to match user system preferences.
   - Reflowable EPUB readers support continuous typography scaling with invariant viewport geometry, allowing large text magnification without breaking page layout.
2. **VoiceOver & Assistive Touch Instrumentation:**
   - Every toolbar icon, navigation button, highlight card, and study deck item provides descriptive `accessibilityLabel`, `accessibilityValue`, and `accessibilityHint` properties.
   - PDF and EPUB reading engines expose native accessibility text trees to VoiceOver for continuous page-by-page screen reading.
3. **Specialized Reading Typography & High-Contrast Themes:**
   - Integrated OpenDyslexic and Atkinson Hyperlegible typefaces to assist readers with dyslexia and visual processing conditions.
   - Curated high-contrast reading themes (Pure Black OLED, Warm Sepia, High-Contrast White-on-Black) engineered to minimize visual fatigue.
4. **Hardware Keyboard Navigation:**
   - Comprehensive iPad hardware keyboard shortcuts: Space / Shift-Space (page forward / back), Left / Right Arrow (page step), Cmd+F (search), Cmd+H (highlight toggle), and Esc (dismiss chrome).
5. **Localization Scope:**
   - English (US) is the launch baseline (`en-US`).
   - All user-facing strings are decoupled from views into standard Apple String Catalogs (`Localizable.xcstrings`), ensuring complete isolation of interface copy ready for Tier 2/3 multi-language localization (Spanish, Japanese, French, German).

---

## 17. Non-Goals & System Boundaries

> **Roadmap Scope:** System Scope Invariants

To protect architectural simplicity, prevent scope creep, and avoid legal/security hazards, the following capabilities are explicitly defined as out-of-scope non-goals:

1. **No Proprietary Central Accounts or Backend Servers:**
   - InksyncPro will not operate a proprietary user database, user registration system, or central storage cloud. All synchronization is delegated strictly to Apple iCloud Ubiquity (`NSUbiquitousKeyValueStore` / iCloud Drive).
2. **No DRM Circumvention or Decryption:**
   - The application explicitly does not strip, break, or circumvent Adobe ADEPT, Amazon Kindle DRM, Apple FairPlay, or other digital rights management schemes. Only unencrypted or user-owned formats (EPUB, PDF, CBZ, CBR, ZIP) are supported.
3. **Native iOS/iPadOS Experience First:**
   - Engineering efforts prioritize deep, uncompromising integration with Apple native frameworks (PDFKit, PencilKit, Metal, SwiftData, ProMotion). Cross-platform web or Android ports remain strictly secondary and non-blocking.
