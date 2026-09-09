import SwiftUI

/// Professional InksyncPro signature progress footer.
/// Floating glassmorphic HUD pill displaying real-time reading progress, pages remaining in current chapter, and estimated reading pace.
struct InksyncProgressFooterView: View {
    let currentPage: Int            // 1-indexed chapter or book page
    let totalPages: Int             // total chapters or total book pages
    var chapterPage: Int = 0        // 0-indexed page inside current chapter
    var chapterTotalPages: Int = 1  // total pages in current chapter
    var chapterTitle: String? = nil // Optional semantic chapter or TOC title (e.g. "Introduction", "Chapter 1")
    var isBookSection: Bool = false // True if dividing an EPUB spine
    let estimatedMinutesLeft: Int?
    var accentColor: Color = Color(hex: "#7B5EA7")

    @ObservedObject private var prefs = EBookPreferences.shared
    @Environment(\.colorScheme) private var colorScheme

    private var progressPercentage: Int {
        if isBookSection && chapterTotalPages > 1 && totalPages > 0 {
            let sectionFraction = Double(max(0, currentPage - 1)) / Double(totalPages)
            let pageFraction = (Double(sanitizedChapterPage) / Double(max(1, chapterTotalPages))) / Double(totalPages)
            let total = min(1.0, max(0.0, sectionFraction + pageFraction))
            return Int(total * 100)
        } else {
            return Int((Double(min(totalPages, max(1, currentPage))) / Double(max(1, totalPages))) * 100)
        }
    }

    private var sanitizedChapterPage: Int {
        if chapterPage >= 99900 {
            return max(0, chapterTotalPages - 1)
        }
        return min(max(0, chapterPage), max(0, chapterTotalPages - 1))
    }

    private var pagesLeftInChapter: Int {
        max(0, chapterTotalPages - (sanitizedChapterPage + 1))
    }

    private var pagesLeftInBook: Int {
        max(0, totalPages - currentPage)
    }

    private var primaryText: String {
        let trimmedTitle = chapterTitle?.trimmingCharacters(in: .whitespacesAndNewlines)

        switch prefs.progressMode {
        case 1:
            // Mode 1: Pages left
            if isBookSection && chapterTotalPages > 1 {
                let left = pagesLeftInChapter
                if let title = trimmedTitle, !title.isEmpty {
                    return left == 1 ? "1 page left in \(title)" : "\(left) pages left in \(title)"
                } else {
                    return left == 1 ? "1 page left in chapter" : "\(left) pages left in chapter"
                }
            } else {
                let left = pagesLeftInBook
                return left == 1 ? "1 page left in book" : "\(left) pages left in book"
            }
        case 2:
            // Mode 2: Estimated time remaining
            if let mins = estimatedMinutesLeft, mins > 0 {
                if mins < 60 {
                    return "~\(mins) min\(mins == 1 ? "" : "s") left in book"
                } else {
                    let hrs = mins / 60
                    let rem = mins % 60
                    return rem > 0 ? "~\(hrs)h \(rem)m left in book" : "~\(hrs)h left in book"
                }
            } else {
                return "\(progressPercentage)% completed"
            }
        case 3:
            // Mode 3: Reading Pace WPM & Completion
            let currentWPM = Int(prefs.readingSpeedWPM)
            return "\(currentWPM) WPM · Reading Pace"
        default:
            // Mode 0: Semantic Chapter Title & Page Indicator
            if let title = trimmedTitle, !title.isEmpty {
                if chapterTotalPages > 1 {
                    return "Page \(sanitizedChapterPage + 1) of \(chapterTotalPages)  ·  \(title)"
                } else {
                    return "\(title)  ·  Page \(currentPage) of \(totalPages)"
                }
            } else if chapterTotalPages > 1 {
                if isBookSection {
                    return "Page \(sanitizedChapterPage + 1) of \(chapterTotalPages)  ·  Section \(currentPage) of \(totalPages)"
                } else {
                    return "Page \(sanitizedChapterPage + 1) of \(chapterTotalPages)"
                }
            } else {
                return "Page \(currentPage) of \(totalPages)"
            }
        }
    }

    var body: some View {
        VStack {
            Spacer()
            HStack {
                if prefs.progressMode == ReadingProgressMode.hidden.rawValue || prefs.progressMode == 4 {
                    // Invisible 140x44pt bottom-left tap zone so tapping unhides the tracker
                    Color.clear
                        .frame(width: 140, height: 44)
                        .contentShape(Rectangle())
                        .onTapGesture {
                            HapticEngine.selection()
                            withAnimation(.spring(response: 0.35, dampingFraction: 0.82)) {
                                prefs.progressMode = 0
                            }
                        }
                } else {
                    HStack(spacing: 8) {
                        // Pulsing/glowing active status indicator dot
                        Circle()
                            .fill(accentColor)
                            .frame(width: 5, height: 5)
                            .shadow(color: accentColor.opacity(0.6), radius: 3, x: 0, y: 0)

                        Text(primaryText)
                            .font(.system(size: 11, weight: .semibold, design: .rounded))
                            .foregroundStyle(prefs.activeTheme.foreground(colorScheme: colorScheme).opacity(colorScheme == .dark ? 0.78 : 0.88))
                            .lineLimit(1)
                            .truncationMode(.tail)
                            .frame(maxWidth: 240, alignment: .leading)

                        if prefs.progressMode != 2 && prefs.progressMode != 3 {
                            Text("\(progressPercentage)%")
                                .font(.system(size: 10, weight: .bold, design: .rounded))
                                .foregroundStyle(accentColor.opacity(0.85))
                        }
                    }
                    .padding(.horizontal, 14)
                    .padding(.vertical, 7)
                    .background(
                        Capsule()
                            .fill(prefs.activeTheme.background(colorScheme: colorScheme).opacity(colorScheme == .dark ? 0.85 : 0.92))
                            .background(.ultraThinMaterial, in: Capsule())
                    )
                    .overlay(
                        Capsule()
                            .stroke(colorScheme == .dark ? Color.white.opacity(0.14) : Color.black.opacity(0.08), lineWidth: 0.5)
                    )
                    .shadow(color: colorScheme == .dark ? Color.black.opacity(0.28) : Color.black.opacity(0.08), radius: 6, x: 0, y: 2)
                    .contentShape(Capsule())
                    .onTapGesture {
                        HapticEngine.selection()
                        withAnimation(.spring(response: 0.35, dampingFraction: 0.82)) {
                            prefs.progressMode = (prefs.progressMode + 1) % 5
                        }
                    }
                }

                Spacer()
            }
            .padding(.horizontal, 16)
        }
        .padding(.bottom, 6)
    }
}

/// Backward compatibility alias for KindleProgressFooterView
typealias KindleProgressFooterView = InksyncProgressFooterView
