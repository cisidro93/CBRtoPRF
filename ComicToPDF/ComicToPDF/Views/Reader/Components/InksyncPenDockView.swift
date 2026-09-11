import SwiftUI
import PencilKit

// MARK: - Inksync Floating Pen Dock

/// Next-Generation floating glassmorphic pen dock for study-grade PDF and book markup.
/// Synthesizes the tactile ergonomics of reMarkable Paper Pro, the clean non-blocking footprint
/// of Kindle Scribe, and 120Hz ProMotion Apple Pencil Pro tactile micro-interactions.
public struct InksyncPenDockView: View {

    @ObservedObject var inkingState = InksyncInkingState.shared
    var onClearPage: (() -> Void)? = nil
    var onClose: (() -> Void)? = nil

    @State private var isExpanded: Bool = false
    @State private var showColorPalette: Bool = false
    @State private var showWidthSlider: Bool = false
    @State private var showClearConfirmation: Bool = false
    @State private var isMinimized: Bool = false
    @GestureState private var dragOffset: CGSize = .zero
    @State private var accumulatedOffset: CGSize = .zero

    public init(onClearPage: (() -> Void)? = nil, onClose: (() -> Void)? = nil) {
        self.onClearPage = onClearPage
        self.onClose = onClose
    }

    public var body: some View {
        VStack(spacing: 8) {
            if !isMinimized {
                if showColorPalette {
                    colorPaletteBar
                        .transition(.asymmetric(
                            insertion: .scale(scale: 0.9).combined(with: .opacity),
                            removal: .scale(scale: 0.9).combined(with: .opacity)
                        ))
                }

                if showWidthSlider {
                    widthSliderBar
                        .transition(.asymmetric(
                            insertion: .scale(scale: 0.9).combined(with: .opacity),
                            removal: .scale(scale: 0.9).combined(with: .opacity)
                        ))
                }

                mainDockCapsule
                    .transition(.move(edge: .bottom).combined(with: .opacity))
            } else {
                minimizedPill
                    .transition(.scale.combined(with: .opacity))
            }
        }
        .offset(x: accumulatedOffset.width + dragOffset.width, y: accumulatedOffset.height + dragOffset.height)
        .gesture(
            DragGesture()
                .updating($dragOffset) { value, state, _ in
                    state = value.translation
                }
                .onEnded { value in
                    accumulatedOffset.width += value.translation.width
                    accumulatedOffset.height += value.translation.height
                    HapticEngine.selection()
                }
        )
        .animation(.spring(response: 0.35, dampingFraction: 0.82), value: isMinimized)
        .animation(.spring(response: 0.3, dampingFraction: 0.85), value: showColorPalette)
        .animation(.spring(response: 0.3, dampingFraction: 0.85), value: showWidthSlider)
        .alert("Clear Page Markup?", isPresented: $showClearConfirmation) {
            Button("Clear All", role: .destructive) {
                onClearPage?()
                HapticEngine.medium()
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("This will erase all ink and highlights on the current page.")
        }
    }

    // MARK: - Main Dock Capsule

    private var mainDockCapsule: some View {
        HStack(spacing: 10) {
            // Minimize button
            Button {
                withAnimation(.spring(response: 0.32, dampingFraction: 0.85)) {
                    isMinimized = true
                }
                HapticEngine.light()
            } label: {
                Image(systemName: "chevron.down")
                    .font(.system(size: 11, weight: .bold))
                    .foregroundStyle(.secondary)
                    .padding(6)
                    .background(.ultraThinMaterial, in: Circle())
            }
            .buttonStyle(.plain)
            .help("Minimize Toolbar")

            // Kindle-Style Master Tool Mode Switcher
            HStack(spacing: 4) {
                ForEach(ReaderToolMode.allCases) { mode in
                    let isSelected = inkingState.activeToolMode == mode
                    Button {
                        withAnimation(.spring(response: 0.28, dampingFraction: 0.8)) {
                            inkingState.activeToolMode = mode
                        }
                        HapticEngine.selection()
                    } label: {
                        HStack(spacing: 4) {
                            Image(systemName: mode.iconSystemName)
                                .font(.system(size: 13, weight: isSelected ? .bold : .medium))
                            if isSelected {
                                Text(mode.displayName)
                                    .font(.system(size: 11, weight: .bold, design: .rounded))
                            }
                        }
                        .foregroundStyle(isSelected ? Color.white : Color.secondary)
                        .padding(.horizontal, isSelected ? 10 : 7)
                        .padding(.vertical, 6)
                        .background(
                            isSelected ? (mode == .textHighlight ? Color.inkOrange : Color.inkGreen) : Color.clear,
                            in: Capsule()
                        )
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(3)
            .background(Color.primary.opacity(0.06), in: Capsule())

            Divider()
                .frame(height: 24)
                .background(Color.secondary.opacity(0.3))

            if inkingState.activeToolMode == .write {
                // 4 Favorite Tool Slots
                HStack(spacing: 6) {
                    ForEach(0..<inkingState.favorites.count, id: \.self) { index in
                        favoriteSlotButton(at: index)
                    }
                }

                // Tool Type Selector
                Menu {
                    ForEach(InkingToolKind.allCases, id: \.self) { kind in
                        Button {
                            inkingState.updateActiveKind(kind)
                            HapticEngine.selection()
                        } label: {
                            Label(kind.displayName, systemImage: kind.iconSystemName)
                        }
                    }
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: inkingState.activePreset.kind.iconSystemName)
                            .font(.system(size: 14, weight: .medium))
                        Image(systemName: "chevron.up.chevron.down")
                            .font(.system(size: 8, weight: .bold))
                            .foregroundStyle(.secondary)
                    }
                    .foregroundStyle(inkingState.activePreset.color.color)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 6)
                    .background(.ultraThinMaterial, in: Capsule())
                }
                .buttonStyle(.plain)

                // Active Color Chip Button
                Button {
                    withAnimation {
                        showColorPalette.toggle()
                        if showColorPalette { showWidthSlider = false }
                    }
                    HapticEngine.selection()
                } label: {
                    Circle()
                        .fill(inkingState.activePreset.color.color)
                        .frame(width: 22, height: 22)
                        .overlay(
                            Circle()
                                .stroke(Color.primary.opacity(0.2), lineWidth: 1.5)
                        )
                        .shadow(color: inkingState.activePreset.color.color.opacity(0.35), radius: 3, y: 1)
                }
                .buttonStyle(.plain)

                // Stroke Width Button
                Button {
                    withAnimation {
                        showWidthSlider.toggle()
                        if showWidthSlider { showColorPalette = false }
                    }
                    HapticEngine.selection()
                } label: {
                    HStack(spacing: 3) {
                        Circle()
                            .fill(Color.primary)
                            .frame(
                                width: max(3, min(12, inkingState.activePreset.width * 1.5)),
                                height: max(3, min(12, inkingState.activePreset.width * 1.5))
                            )
                        Text(String(format: "%.1f", inkingState.activePreset.width))
                            .font(.system(size: 10, weight: .semibold, design: .monospaced))
                            .foregroundStyle(.secondary)
                    }
                    .padding(.horizontal, 7)
                    .padding(.vertical, 5)
                    .background(.ultraThinMaterial, in: Capsule())
                }
                .buttonStyle(.plain)
            } else if inkingState.activeToolMode == .textHighlight {
                Text("Glide across text to highlight")
                    .font(.system(size: 11, weight: .semibold, design: .rounded))
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 4)
            } else if inkingState.activeToolMode == .eraser {
                // Clear Current Page Ink
                Button {
                    showClearConfirmation = true
                    HapticEngine.light()
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: "trash")
                            .font(.system(size: 12, weight: .medium))
                        Text("Clear Page")
                            .font(.system(size: 11, weight: .semibold, design: .rounded))
                    }
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 5)
                    .background(Color.primary.opacity(0.06), in: Capsule())
                }
                .buttonStyle(.plain)
            } else {
                Text("Pan, zoom & turn pages freely")
                    .font(.system(size: 11, weight: .semibold, design: .rounded))
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 4)
            }

            // Close / Exit Markup Mode
            if let onClose = onClose {
                Button {
                    onClose()
                    HapticEngine.medium()
                } label: {
                    Image(systemName: "xmark")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundStyle(.secondary)
                        .padding(6)
                        .background(.ultraThinMaterial, in: Circle())
                }
                .buttonStyle(.plain)
                .help("Close Pen Toolbar")
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(
            Capsule()
                .fill(.ultraThinMaterial)
                .shadow(color: Color.black.opacity(0.18), radius: 14, x: 0, y: 6)
                .overlay(
                    Capsule()
                        .stroke(Color.primary.opacity(0.08), lineWidth: 1)
                )
        )
    }

    // MARK: - Favorite Slot Button

    @ViewBuilder
    private func favoriteSlotButton(at index: Int) -> some View {
        let preset = inkingState.favorites[index]
        let isSelected = inkingState.activePreset.id == preset.id

        Button {
            inkingState.selectFavorite(at: index)
            HapticEngine.selection()
        } label: {
            ZStack(alignment: .bottomTrailing) {
                Image(systemName: preset.kind.iconSystemName)
                    .font(.system(size: 15, weight: isSelected ? .bold : .semibold))
                    .foregroundStyle(preset.color == .obsidian ? Color.primary : preset.color.color)
                    .frame(width: 32, height: 32)
                    .background(
                        Circle()
                            .fill(isSelected ? (preset.color == .obsidian ? Color.primary.opacity(0.18) : preset.color.color.opacity(0.18)) : Color.primary.opacity(0.04))
                    )
                    .overlay(
                        Circle()
                            .stroke(isSelected ? (preset.color == .obsidian ? Color.primary : preset.color.color) : Color.clear, lineWidth: 2)
                    )

                // Color Pip with contrast border
                Circle()
                    .fill(preset.color.color)
                    .frame(width: 8, height: 8)
                    .overlay(
                        Circle()
                            .stroke(Color.primary.opacity(0.35), lineWidth: 0.5)
                    )
                    .offset(x: 1, y: 1)
            }
        }
        .buttonStyle(.plain)
        .scaleEffect(isSelected ? 1.08 : 1.0)
        .accessibilityLabel("\(preset.name) - \(preset.color.displayName)")
        .help("\(preset.name) (\(preset.color.displayName))")
    }

    // MARK: - Calibrated 9-Color Palette Bar

    private var colorPaletteBar: some View {
        HStack(spacing: 10) {
            ForEach(InksyncInkColor.allCases, id: \.self) { color in
                let isSelected = inkingState.activePreset.color == color
                Button {
                    inkingState.updateActiveColor(color)
                    HapticEngine.selection()
                    withAnimation {
                        showColorPalette = false
                    }
                } label: {
                    Circle()
                        .fill(color.color)
                        .frame(width: isSelected ? 28 : 22, height: isSelected ? 28 : 22)
                        .overlay(
                            Circle()
                                .stroke(
                                    color == .obsidian
                                        ? Color.primary.opacity(isSelected ? 0.9 : 0.4)
                                        : Color.primary.opacity(isSelected ? 0.9 : 0.15),
                                    lineWidth: isSelected ? 2.5 : 1
                                )
                        )
                        .shadow(color: color.color.opacity(isSelected ? 0.4 : 0.1), radius: 4, y: 2)
                }
                .buttonStyle(.plain)
                .accessibilityLabel(color.displayName)
                .help(color.displayName)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .background(
            Capsule()
                .fill(.ultraThinMaterial)
                .shadow(color: Color.black.opacity(0.15), radius: 10, y: 4)
                .overlay(Capsule().stroke(Color.primary.opacity(0.08), lineWidth: 1))
        )
    }

    // MARK: - Width Slider Bar

    private var widthSliderBar: some View {
        HStack(spacing: 14) {
            Text("Fine")
                .font(.system(size: 11, weight: .medium))
                .foregroundStyle(.secondary)

            Slider(
                value: Binding(
                    get: { Double(inkingState.activePreset.width) },
                    set: { inkingState.updateActiveWidth(CGFloat($0)) }
                ),
                in: inkingState.activePreset.kind == .highlighter ? 8.0...36.0 : 0.5...12.0,
                step: 0.5
            )
            .frame(width: 160)
            .tint(inkingState.activePreset.color.color)

            Text("Broad")
                .font(.system(size: 11, weight: .medium))
                .foregroundStyle(.secondary)

            // Live preview dot
            Circle()
                .fill(inkingState.activePreset.color.color)
                .frame(
                    width: max(4, min(24, inkingState.activePreset.width * 1.2)),
                    height: max(4, min(24, inkingState.activePreset.width * 1.2))
                )
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .background(
            Capsule()
                .fill(.ultraThinMaterial)
                .shadow(color: Color.black.opacity(0.15), radius: 10, y: 4)
                .overlay(Capsule().stroke(Color.primary.opacity(0.08), lineWidth: 1))
        )
    }

    // MARK: - Minimized Pill

    private var minimizedPill: some View {
        Button {
            withAnimation(.spring(response: 0.32, dampingFraction: 0.82)) {
                isMinimized = false
            }
            HapticEngine.medium()
        } label: {
            HStack(spacing: 6) {
                Image(systemName: inkingState.activeToolMode.iconSystemName)
                    .font(.system(size: 13, weight: .bold))
                    .foregroundStyle(inkingState.activeToolMode == .textHighlight ? Color.inkOrange : inkingState.activePreset.color.color)
                Text(inkingState.activeToolMode.displayName)
                    .font(.system(size: 12, weight: .bold, design: .rounded))
                    .foregroundStyle(.primary)
                Circle()
                    .fill(inkingState.activePreset.color.color)
                    .frame(width: 8, height: 8)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 9)
            .background(
                Capsule()
                    .fill(.ultraThinMaterial)
                    .shadow(color: Color.black.opacity(0.25), radius: 8, y: 3)
                    .overlay(Capsule().stroke(Color.primary.opacity(0.12), lineWidth: 1))
            )
        }
        .buttonStyle(.plain)
        .help("Expand Pen Toolbar")
    }
}
