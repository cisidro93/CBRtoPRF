import Foundation
import SwiftUI

/// Unified service that resolves and triggers the next book or comic in a series,
/// custom user collection (story arc / reading order), or virtual omnibus.
/// Enforces strict `@MainActor` and `Sendable` guarantees with zero race conditions.
@MainActor
final class ReadingContinuationResolver {
    static let shared = ReadingContinuationResolver()

    private var isContinuationInProgress: Bool = false

    private init() {}

    // MARK: - Next Book Resolution

    /// Resolves the next chronological candidate in sequence without triggering navigation.
    ///
    /// Resolution Order:
    /// 1. **Active Filtered Reading List**: If the reader was launched with an explicit subset list
    ///    (`explicitList.count > 1` and `< catalog.count`), advance to `explicitList[currentIdx + 1]`.
    /// 2. **Custom Collection Story Arc (`PDFCollection`)**: If the item belongs to a custom collection
    ///    (`currentBook.collectionId != nil`), advance according to the user's `manualSortOrder`
    ///    (or chronological issue ordering if no manual sort was arranged).
    /// 3. **Virtual Omnibus Story Arc (`VirtualOmnibus`)**: If the item is part of a cross-series
    ///    omnibus reading order, advance to the next issue ID in `omnibus.fileIDs`.
    /// 4. **Publisher Series (`metadata.series`)**: Match all series siblings in the library catalog
    ///    and sort chronologically by numeric issue number (`Double(issueNumber ?? volume)`),
    ///    advancing to `siblings[currentIdx + 1]`.
    /// 5. **Explicit List Fallback**: If `explicitList` has multiple items and wasn't caught by Tier 1.
    func nextBook(after currentBook: ConvertedPDF, in explicitList: [ConvertedPDF] = []) -> ConvertedPDF? {
        // 1. Determine effective full library catalog
        var catalog: [ConvertedPDF] = LibraryService.shared.items
        if catalog.isEmpty {
            catalog = ConversionManager.shared.convertedPDFs
        }
        if catalog.isEmpty {
            catalog = explicitList
        }

        // Tier 1: Explicit curated subset list (e.g. from active search, smart collection, or filtered shelf)
        if explicitList.count > 1 && explicitList.count < catalog.count {
            if let currentIdx = explicitList.firstIndex(where: { $0.id == currentBook.id }) {
                let nextIdx = currentIdx + 1
                if explicitList.indices.contains(nextIdx) {
                    Logger.shared.log("Continuation resolved via Tier 1 (Explicit Subset List): '\(explicitList[nextIdx].name)'", category: "Continuation", type: .info)
                    return explicitList[nextIdx]
                }
            }
        }

        // Tier 2: Custom User Collection (Story Arc or Reading List)
        if let collectionID = currentBook.collectionId {
            let collections = !LibraryService.shared.collections.isEmpty
                ? LibraryService.shared.collections
                : ConversionManager.shared.collections

            if let collection = collections.first(where: { $0.id == collectionID }) {
                let collectionItems = catalog.filter { $0.collectionId == collection.id }
                let sortedItems: [ConvertedPDF]

                if let manualOrder = collection.manualSortOrder, !manualOrder.isEmpty {
                    // Enforce user-defined chronological story arc order
                    let orderDict = Dictionary(uniqueKeysWithValues: manualOrder.enumerated().map { ($0.element, $0.offset) })
                    sortedItems = collectionItems.sorted { a, b in
                        let idxA = orderDict[a.id] ?? Int.max
                        let idxB = orderDict[b.id] ?? Int.max
                        if idxA == idxB {
                            return Self.compareChronological(a, b)
                        }
                        return idxA < idxB
                    }
                } else {
                    // Chronological sort within collection
                    sortedItems = collectionItems.sorted(by: Self.compareChronological)
                }

                if let currentIdx = sortedItems.firstIndex(where: { $0.id == currentBook.id }) {
                    let nextIdx = currentIdx + 1
                    if sortedItems.indices.contains(nextIdx) {
                        Logger.shared.log("Continuation resolved via Tier 2 (Custom Collection '\(collection.name)'): '\(sortedItems[nextIdx].name)'", category: "Continuation", type: .info)
                        return sortedItems[nextIdx]
                    } else {
                        // Reached the end of this custom collection
                        Logger.shared.log("Reached end of Custom Collection '\(collection.name)'. No next candidate.", category: "Continuation", type: .info)
                        return nil
                    }
                }
            }
        }

        // Tier 3: Story Arc via Virtual Omnibus
        let omnibuses = !LibraryService.shared.virtualOmnibuses.isEmpty
            ? LibraryService.shared.virtualOmnibuses
            : ConversionManager.shared.virtualOmnibuses

        for omnibus in omnibuses {
            if let fileIdx = omnibus.fileIDs.firstIndex(of: currentBook.id) {
                let nextFileIdx = fileIdx + 1
                if omnibus.fileIDs.indices.contains(nextFileIdx) {
                    let nextID = omnibus.fileIDs[nextFileIdx]
                    if let nextFile = catalog.first(where: { $0.id == nextID }) {
                        Logger.shared.log("Continuation resolved via Tier 3 (Virtual Omnibus '\(omnibus.name)'): '\(nextFile.name)'", category: "Continuation", type: .info)
                        return nextFile
                    }
                } else {
                    // Reached the end of this omnibus story arc
                    Logger.shared.log("Reached end of Virtual Omnibus '\(omnibus.name)'. No next candidate.", category: "Continuation", type: .info)
                    return nil
                }
            }
        }

        // Tier 4: Series Chronological Continuation
        if let rawSeries = currentBook.metadata.series?.trimmingCharacters(in: .whitespacesAndNewlines), !rawSeries.isEmpty {
            let siblings = catalog.filter {
                guard let s = $0.metadata.series?.trimmingCharacters(in: .whitespacesAndNewlines) else { return false }
                return s.localizedCaseInsensitiveCompare(rawSeries) == .orderedSame
            }

            let sortedSiblings = siblings.sorted(by: Self.compareChronological)
            if let currentIdx = sortedSiblings.firstIndex(where: { $0.id == currentBook.id }) {
                let nextIdx = currentIdx + 1
                if sortedSiblings.indices.contains(nextIdx) {
                    Logger.shared.log("Continuation resolved via Tier 4 (Series '\(rawSeries)'): '\(sortedSiblings[nextIdx].name)'", category: "Continuation", type: .info)
                    return sortedSiblings[nextIdx]
                } else {
                    Logger.shared.log("Reached end of Series '\(rawSeries)'. No next candidate.", category: "Continuation", type: .info)
                    return nil
                }
            }
        }

        // Tier 5: Fallback to explicit list if provided
        if explicitList.count > 1 {
            if let currentIdx = explicitList.firstIndex(where: { $0.id == currentBook.id }) {
                let nextIdx = currentIdx + 1
                if explicitList.indices.contains(nextIdx) {
                    Logger.shared.log("Continuation resolved via Tier 5 (Explicit List Fallback): '\(explicitList[nextIdx].name)'", category: "Continuation", type: .info)
                    return explicitList[nextIdx]
                }
            }
        }

        Logger.shared.log("No continuation candidate found for '\(currentBook.name)'", category: "Continuation", type: .info)
        return nil
    }

    // MARK: - Navigation Trigger

    /// Resolves the next candidate and triggers auto-continuation.
    /// Provides tactile feedback (`HapticEngine.success()`), posts `.openMergedBook`,
    /// and guards against debounce race conditions.
    @discardableResult
    func continueReading(after currentBook: ConvertedPDF, in explicitList: [ConvertedPDF] = []) -> Bool {
        guard !isContinuationInProgress else {
            Logger.shared.log("Continuation already in progress, suppressing duplicate call.", category: "Continuation", type: .info)
            return false
        }

        guard let next = nextBook(after: currentBook, in: explicitList) else {
            Logger.shared.log("No next book available to continue from '\(currentBook.name)'.", category: "Continuation", type: .info)
            return false
        }

        isContinuationInProgress = true
        HapticEngine.success()
        Logger.shared.log("Triggering auto-continuation to '\(next.name)' (ID: \(next.id))", category: "Continuation", type: .info)

        NotificationCenter.default.post(name: .openMergedBook, object: next)

        // Reset debounce flag after transition completes
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { [weak self] in
            self?.isContinuationInProgress = false
        }

        return true
    }

    // MARK: - Chronological Comparator

    /// High-precision chronological comparator handling:
    /// - Decimal issue numbers (`"0.5"`, `"12.1"`, `"100"`)
    /// - Volume numbers (`"Vol. 1"`, `"Volume 2"`)
    /// - Non-numeric issue identifiers (`"Annual #1"`, `"Special #2"`, `"TPB"`)
    /// - Natural alphanumeric fallback
    static func compareChronological(_ lhs: ConvertedPDF, _ rhs: ConvertedPDF) -> Bool {
        // 1. Issue numbers: parse as Double first (handles "0.5", "12.1", etc.)
        let lhsIssueStr = lhs.metadata.issueNumber?.trimmingCharacters(in: .whitespacesAndNewlines)
        let rhsIssueStr = rhs.metadata.issueNumber?.trimmingCharacters(in: .whitespacesAndNewlines)
        let lhsIssueNum = lhsIssueStr.flatMap { Double($0) }
        let rhsIssueNum = rhsIssueStr.flatMap { Double($0) }

        if let l = lhsIssueNum, let r = rhsIssueNum {
            if l != r { return l < r }
        } else if lhsIssueNum != nil && rhsIssueNum == nil {
            return true
        } else if lhsIssueNum == nil && rhsIssueNum != nil {
            return false
        }

        // 2. Volume numbers: parse as Double
        let lhsVolStr = lhs.metadata.volume?.trimmingCharacters(in: .whitespacesAndNewlines)
        let rhsVolStr = rhs.metadata.volume?.trimmingCharacters(in: .whitespacesAndNewlines)
        let lhsVolNum = lhsVolStr.flatMap { Double($0) }
        let rhsVolNum = rhsVolStr.flatMap { Double($0) }

        if let l = lhsVolNum, let r = rhsVolNum {
            if l != r { return l < r }
        } else if lhsVolNum != nil && rhsVolNum == nil {
            return true
        } else if lhsVolNum == nil && rhsVolNum != nil {
            return false
        }

        // 3. Fall back to natural alphanumeric comparison on issue/volume/name
        let lKey = (lhsIssueStr?.isEmpty == false ? lhsIssueStr : nil)
            ?? (lhsVolStr?.isEmpty == false ? lhsVolStr : nil)
            ?? lhs.name
        let rKey = (rhsIssueStr?.isEmpty == false ? rhsIssueStr : nil)
            ?? (rhsVolStr?.isEmpty == false ? rhsVolStr : nil)
            ?? rhs.name

        return lKey.localizedStandardCompare(rKey) == .orderedAscending
    }
}
