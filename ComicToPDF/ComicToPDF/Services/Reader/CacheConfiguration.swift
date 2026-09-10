import Foundation

/// Centralized, authoritative cache limits and hardware-tier memory boundaries
/// across InksyncPro reading engines, eliminating magic numbers (Clean Code Handbook).
enum ReaderCacheLimits {
    /// Reflowable EPUB 3D Page Curl: Maximum distance in pages for the sliding-window snapshot cache.
    /// A distance of 4 retains a window of (centerIndex ± 4) = 9 pages maximum.
    static let epubSnapshotDistance: Int = 4

    /// Comic & Manga JIT Page Buffer: Dynamic NSCache count limits based on device capability class.
    static let comicBufferLowDevice: Int = 8
    static let comicBufferStandardDevice: Int = 16
    static let comicBufferProDevice: Int = 32
    /// Dual-page spread mode covers: currentL, currentR, prevL, prevR, nextL, nextR + 1 spare.
    static let comicDualPageSpread: Int = 7

    /// Webtoon Continuous Scroll: Image tile cache count limit.
    static let webtoonContinuous: Int = 12

    /// Reader Navigation: Scrub bar thumbnail image cache limit.
    static let thumbnailScrubBar: Int = 64

    /// Batch Document Converter: In-memory processed page cache limit.
    static let conversionManager: Int = 150
}
