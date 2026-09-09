//
//  WhatsNewProvider.swift
//  ComicToPDF
//
//  Created for InkSync Pro.
//  Point-Free Swift 6 & Apple Design Standards.
//

import Foundation
import SwiftUI

// MARK: - Models

public struct WhatsNewFeature: Identifiable, Codable, Sendable {
    public var id: String { "\(category)_\(title)" }
    public let icon: String
    public let colorHex: String
    public let title: String
    public let description: String
    public let category: String
    
    public init(
        icon: String,
        colorHex: String,
        title: String,
        description: String,
        category: String = "Feature"
    ) {
        self.icon = icon
        self.colorHex = colorHex
        self.title = title
        self.description = description
        self.category = category
    }
    
    public var accentColor: Color {
        switch colorHex.lowercased() {
        case "yellow": return .yellow
        case "orange": return .orange
        case "blue": return .blue
        case "purple": return .purple
        case "green": return .green
        case "red": return .red
        case "cyan": return .cyan
        case "teal": return .teal
        case "indigo": return .indigo
        default:
            return Color(hex: colorHex)
        }
    }
}

public struct WhatsNewRelease: Identifiable, Codable, Sendable {
    public var id: String { "\(buildNumber)_\(commitSHA)" }
    public let buildNumber: String
    public let commitSHA: String
    public let version: String
    public let releaseDate: String
    public let title: String
    public let subtitle: String
    public let features: [WhatsNewFeature]
    
    public init(
        buildNumber: String,
        commitSHA: String,
        version: String,
        releaseDate: String,
        title: String,
        subtitle: String,
        features: [WhatsNewFeature]
    ) {
        self.buildNumber = buildNumber
        self.commitSHA = commitSHA
        self.version = version
        self.releaseDate = releaseDate
        self.title = title
        self.subtitle = subtitle
        self.features = features
    }
}

// MARK: - Provider

@MainActor
public final class WhatsNewProvider: ObservableObject {
    public static let shared = WhatsNewProvider()
    
    @Published public private(set) var allReleases: [WhatsNewRelease] = []
    
    public init() {
        loadReleases()
    }
    
    public func loadReleases() {
        var loaded: [WhatsNewRelease] = []
        
        // 1. Try loading from bundled WhatsNew.json resource
        if let url = Bundle.main.url(forResource: "WhatsNew", withExtension: "json"),
           let data = try? Data(contentsOf: url),
           let decoded = try? JSONDecoder().decode([WhatsNewRelease].self, from: data),
           !decoded.isEmpty {
            loaded = decoded
        }
        
        // 2. Merge with built-in catalog so milestone builds are always available
        if loaded.isEmpty {
            loaded = WhatsNewCatalog.builtInReleases
        } else {
            for builtIn in WhatsNewCatalog.builtInReleases {
                if !loaded.contains(where: { $0.buildNumber == builtIn.buildNumber || (!builtIn.commitSHA.isEmpty && $0.commitSHA == builtIn.commitSHA) }) {
                    loaded.append(builtIn)
                }
            }
        }
        
        // Sort descending by numeric build number
        loaded.sort {
            (Int($0.buildNumber) ?? 0) > (Int($1.buildNumber) ?? 0)
        }
        
        self.allReleases = loaded
    }
    
    /// Returns the release matching the running binary's build number or commit SHA,
    /// falling back to the latest release in the catalog.
    public var currentRelease: WhatsNewRelease {
        let currentBuild = AppBuildInfo.buildNumber
        let currentSHA = AppBuildInfo.shortCommitSHA
        
        if let match = allReleases.first(where: {
            $0.buildNumber == currentBuild ||
            (!currentSHA.isEmpty && currentSHA != "local" && $0.commitSHA.hasPrefix(currentSHA))
        }) {
            return match
        }
        
        return allReleases.first ?? WhatsNewCatalog.fallbackRelease
    }
}

// MARK: - Built-in Milestone Catalog

public struct WhatsNewCatalog: Sendable {
    
    public static let fallbackRelease = WhatsNewRelease(
        buildNumber: AppBuildInfo.buildNumber,
        commitSHA: AppBuildInfo.shortCommitSHA,
        version: AppBuildInfo.version,
        releaseDate: "Current",
        title: "Latest System Updates",
        subtitle: "Continuous performance, study, and reader enhancements",
        features: [
            WhatsNewFeature(
                icon: "sparkles",
                colorHex: "orange",
                title: "Active Study & 4-Titan Readers",
                description: "Deep reader-to-notebook integration, Spaced Repetition (SM-2), and 0ms highlighting.",
                category: "Core"
            )
        ]
    )
    
    public static let builtInReleases: [WhatsNewRelease] = [
        WhatsNewRelease(
            buildNumber: "3329",
            commitSHA: "f1488b25",
            version: "1.0.1",
            releaseDate: "September 2026",
            title: "4-Titan Study Suite & Cornell Persistence",
            subtitle: "On par with GoodNotes, Notability, Apple Notes & Obsidian",
            features: [
                WhatsNewFeature(
                    icon: "text.book.closed.fill",
                    colorHex: "orange",
                    title: "Cornell 3-Zone Note Persistence",
                    description: "Cues and Summary columns are now fully persisted to SwiftData with debounced autosave and frosted-glass recitation curtain.",
                    category: "Study"
                ),
                WhatsNewFeature(
                    icon: "play.rectangle.on.rectangle.fill",
                    colorHex: "purple",
                    title: "Global Active Study Suite",
                    description: "New 4th navigation hub in the Notebooks shelf unifying Cornell notes, Mortimer Adler markers, and spaced repetition review.",
                    category: "Navigation"
                ),
                WhatsNewFeature(
                    icon: "arrow.triangle.2.circlepath",
                    colorHex: "blue",
                    title: "SwiftData Live Ingestion Bridge",
                    description: "Reading highlights and passage citations automatically convert into active recall flashcards with Bear tags.",
                    category: "Sync"
                ),
                WhatsNewFeature(
                    icon: "clock.arrow.circlepath",
                    colorHex: "green",
                    title: "Spaced Repetition (SM-2) Engine",
                    description: "Active recall study decks with ease factor calculation, 3D flip card self-testing, and scheduled intervals.",
                    category: "Recall"
                ),
                WhatsNewFeature(
                    icon: "book.pages.fill",
                    colorHex: "cyan",
                    title: "Deep Reader Anchoring",
                    description: "Jump from any flashcard citation directly into the full book viewport in UnifiedReaderView with 1 tap.",
                    category: "Reader"
                )
            ]
        ),
        WhatsNewRelease(
            buildNumber: "3326",
            commitSHA: "f5bef99a",
            version: "1.0.1",
            releaseDate: "September 2026",
            title: "0ms Highlighting & Highlights Tab",
            subtitle: "Instantaneous visual rendering across PDF and EPUB",
            features: [
                WhatsNewFeature(
                    icon: "highlighter",
                    colorHex: "yellow",
                    title: "Instant PDF Vector Highlighting",
                    description: "Single-annotation ISO quad-point geometry with direct alpha and synchronous tiled layer invalidation.",
                    category: "PDFKit"
                ),
                WhatsNewFeature(
                    icon: "list.bullet.rectangle.portrait",
                    colorHex: "orange",
                    title: "In-Book Highlights Drawer",
                    description: "Dedicated Highlights tab in PDFOutlineDrawer with live color badges, page numbers, and 1-tap jump.",
                    category: "Reader"
                ),
                WhatsNewFeature(
                    icon: "book.pages",
                    colorHex: "blue",
                    title: "EPUB 3D Curl Live Invalidation",
                    description: "Page snapshots re-rasterize instantly when text is highlighted, eliminating page-turn delays.",
                    category: "EPUB"
                ),
                WhatsNewFeature(
                    icon: "square.and.pencil",
                    colorHex: "purple",
                    title: "External Study Notebook Sync",
                    description: "Highlights created in documents automatically synchronize to the external study drawer when outside the reader.",
                    category: "Sync"
                )
            ]
        ),
        WhatsNewRelease(
            buildNumber: "3324",
            commitSHA: "bc82d8b2",
            version: "1.0.1",
            releaseDate: "September 2026",
            title: "The 4-Titan Digital Reader Suite",
            subtitle: "Features benchmarked against Kindle, Panels, KyBook 3 & Boox",
            features: [
                WhatsNewFeature(
                    icon: "bolt.horizontal.fill",
                    colorHex: "orange",
                    title: "KyBook 3 RSVP Speed Reader",
                    description: "Optimal Recognition Point (ORP) fixation, adaptive punctuation pauses, and 150–850 WPM chunking.",
                    category: "Reader"
                ),
                WhatsNewFeature(
                    icon: "crop",
                    colorHex: "blue",
                    title: "Boox NeoReader Alternating Crop",
                    description: "Alternating inner gutter offset compensation for bound books and single-tap column stepping.",
                    category: "PDFKit"
                ),
                WhatsNewFeature(
                    icon: "lock.fill",
                    colorHex: "green",
                    title: "Panels Persistent Lock Zoom",
                    description: "Custom zoom magnification level locks across page transitions until manually reset.",
                    category: "Zoom"
                ),
                WhatsNewFeature(
                    icon: "arrow.counterclockwise.circle.fill",
                    colorHex: "purple",
                    title: "Kindle Anchor Jump System",
                    description: "Interactive toast overlay allows 1-tap jumping between past reading anchors and current position.",
                    category: "Navigation"
                )
            ]
        )
    ]
}
