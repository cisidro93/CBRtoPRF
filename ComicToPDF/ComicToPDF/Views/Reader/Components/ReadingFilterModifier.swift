import SwiftUI

// MARK: - ReadingFilterModifier
// Applies curated color matrices and adjustments for optimal reading comfort.
struct ReadingFilterModifier: ViewModifier {
    let preset: ReadingFilterPreset
    
    @AppStorage("customContrast") private var customContrast: Double = 1.0
    @AppStorage("customBrightness") private var customBrightness: Double = 0.0
    @AppStorage("customSaturation") private var customSaturation: Double = 1.0

    func body(content: Content) -> some View {
        switch preset {
        case .original:
            content
        case .vintage:
            content
                .contrast(0.9)
                .saturation(0.7)
                .colorMultiply(Color(red: 1.0, green: 0.95, blue: 0.9)) // Warm tone
        case .eink:
            content
                .contrast(1.4)
                .saturation(0.0) // Grayscale
        case .vibrant:
            content
                .contrast(1.1)
                .saturation(1.4)
        case .dark:
            content
                .colorInvert()
                .hueRotation(.degrees(180)) // Invert colors preserving hue
        case .amber:
            content
                .colorMultiply(Color(red: 1.0, green: 0.86, blue: 0.65))
        case .sepia:
            content
                .colorMultiply(Color(red: 0.95, green: 0.89, blue: 0.78))
        case .custom:
            content
                .contrast(customContrast)
                .brightness(customBrightness)
                .saturation(customSaturation)
        }
    }
}

// MARK: - View Extension
extension View {
    func applyFilterPreset(_ preset: ReadingFilterPreset) -> some View {
        modifier(ReadingFilterModifier(preset: preset))
    }
}
