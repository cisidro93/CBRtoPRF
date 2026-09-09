//
//  WhatsNewInBuildSheet.swift
//  ComicToPDF
//
//  Created for InkSync Pro.
//  Point-Free Swift 6 & Apple Design Standards.
//

import SwiftUI

struct WhatsNewInBuildSheet: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject private var provider = WhatsNewProvider.shared
    
    @State private var selectedReleaseID: String = ""
    @State private var showingAllReleasesList: Bool = false
    
    var onDismiss: (() -> Void)?
    
    private var activeRelease: WhatsNewRelease {
        if let match = provider.allReleases.first(where: { $0.id == selectedReleaseID }) {
            return match
        }
        return provider.currentRelease
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.inkBackground.ignoresSafeArea()
                
                VStack(spacing: 16) {
                    // Header
                    headerView
                    
                    // Release Switcher (if historical builds exist)
                    if provider.allReleases.count > 1 {
                        releaseSelectorBar
                    }
                    
                    // Features list
                    ScrollView {
                        LazyVStack(spacing: 14) {
                            ForEach(activeRelease.features) { feat in
                                FeatureRow(feature: feat)
                            }
                        }
                        .padding(.horizontal, 20)
                        .padding(.top, 4)
                        .padding(.bottom, 16)
                    }
                    
                    Spacer()
                    
                    // Acknowledge Button
                    Button {
                        AppBuildInfo.markCurrentBuildAsSeen()
                        dismiss()
                        onDismiss?()
                    } label: {
                        Text("Continue")
                            .font(.system(size: 16, weight: .bold, design: .rounded))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(
                                RoundedRectangle(cornerRadius: 14)
                                    .fill(
                                        LinearGradient(
                                            colors: [Color.orange, Color.orange.opacity(0.85)],
                                            startPoint: .top,
                                            endPoint: .bottom
                                        )
                                    )
                                    .shadow(color: Color.orange.opacity(0.3), radius: 8, x: 0, y: 4)
                            )
                    }
                    .padding(.horizontal, 24)
                    .padding(.bottom, 18)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") {
                        AppBuildInfo.markCurrentBuildAsSeen()
                        dismiss()
                        onDismiss?()
                    }
                    .font(.system(size: 15, weight: .medium))
                    .foregroundColor(.secondary)
                }
                
                if provider.allReleases.count > 1 {
                    ToolbarItem(placement: .primaryAction) {
                        Menu {
                            ForEach(provider.allReleases) { rel in
                                Button {
                                    withAnimation(.easeInOut(duration: 0.2)) {
                                        selectedReleaseID = rel.id
                                    }
                                } label: {
                                    HStack {
                                        Text("Build \(rel.buildNumber) - \(rel.title)")
                                        if activeRelease.id == rel.id {
                                            Image(systemName: "checkmark")
                                        }
                                    }
                                }
                            }
                        } label: {
                            Label("History", systemImage: "clock.arrow.circlepath")
                                .font(.system(size: 14, weight: .medium))
                        }
                    }
                }
            }
            .onAppear {
                if selectedReleaseID.isEmpty {
                    selectedReleaseID = provider.currentRelease.id
                }
            }
        }
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
    }
    
    // MARK: - Header
    
    private var headerView: some View {
        VStack(spacing: 8) {
            Image(systemName: "sparkles")
                .font(.system(size: 38))
                .foregroundStyle(
                    LinearGradient(
                        colors: [.orange, .yellow],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .padding(.top, 16)
            
            Text(activeRelease.title)
                .font(.system(size: 20, weight: .bold, design: .rounded))
                .foregroundColor(.primary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 20)
            
            if !activeRelease.subtitle.isEmpty {
                Text(activeRelease.subtitle)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 24)
            }
            
            // Live Build Stamping Pill
            HStack(spacing: 6) {
                Circle()
                    .fill(Color.green)
                    .frame(width: 6, height: 6)
                Text(AppBuildInfo.formattedBadge)
                    .font(.system(size: 11, weight: .semibold, design: .monospaced))
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 3)
            .background(
                Capsule()
                    .fill(Color.inkSurface.opacity(0.8))
            )
        }
    }
    
    // MARK: - Release Selector Bar
    
    private var releaseSelectorBar: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(provider.allReleases) { rel in
                    let isSelected = activeRelease.id == rel.id
                    Button {
                        withAnimation(.spring(response: 0.25, dampingFraction: 0.8)) {
                            selectedReleaseID = rel.id
                        }
                    } label: {
                        HStack(spacing: 4) {
                            if rel.id == provider.currentRelease.id {
                                Text("LATEST")
                                    .font(.system(size: 8, weight: .black))
                                    .padding(.horizontal, 4)
                                    .padding(.vertical, 1)
                                    .background(Capsule().fill(Color.orange))
                                    .foregroundColor(.white)
                            }
                            Text("Build \(rel.buildNumber)")
                                .font(.system(size: 12, weight: isSelected ? .bold : .medium, design: .monospaced))
                        }
                        .foregroundColor(isSelected ? .white : .secondary)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(
                            Capsule()
                                .fill(isSelected ? Color.orange : Color.inkSurface.opacity(0.6))
                        )
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal, 20)
        }
    }
}

// MARK: - Feature Row

private struct FeatureRow: View {
    let feature: WhatsNewFeature
    
    var body: some View {
        HStack(alignment: .top, spacing: 14) {
            Image(systemName: feature.icon)
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(feature.accentColor)
                .frame(width: 38, height: 38)
                .background(feature.accentColor.opacity(0.14))
                .clipShape(RoundedRectangle(cornerRadius: 10))
            
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(feature.title)
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundColor(.primary)
                    
                    Spacer()
                    
                    Text(feature.category.uppercased())
                        .font(.system(size: 9, weight: .bold, design: .monospaced))
                        .foregroundColor(feature.accentColor)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(
                            Capsule()
                                .fill(feature.accentColor.opacity(0.12))
                        )
                }
                
                Text(feature.description)
                    .font(.system(size: 13))
                    .foregroundColor(.secondary)
                    .lineLimit(4)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.inkSurface.opacity(0.55))
        )
    }
}
