import SwiftUI

// MARK: - Paper Styles
enum PaperStyle: String, CaseIterable, Identifiable {
    case plain = "Plain"
    case ruled = "Ruled"
    case grid = "Grid"
    case dots = "Dots"
    case legal = "Legal"
    case collegeRuled = "College Ruled"
    case flashcard = "Flashcard"
    
    var id: String { self.rawValue }
    var icon: String {
        switch self {
        case .plain: return "square"
        case .ruled: return "line.horizontal.3"
        case .grid: return "grid"
        case .dots: return "circle.hexagongrid.fill"
        case .legal: return "signature"
        case .collegeRuled: return "doc.text.fill"
        case .flashcard: return "rectangle.split.2x1"
        }
    }
}

// MARK: - Notebook Paper Background Pattern
struct NotebookPaperBackground: View {
    let style: PaperStyle
    let spacing: CGFloat
    let colorScheme: ColorScheme

    init(style: PaperStyle, spacing: CGFloat, colorScheme: ColorScheme) {
        self.style = style
        self.spacing = spacing
        self.colorScheme = colorScheme
    }

    var body: some View {
        GeometryReader { geo in
            ZStack {
                // Paper Base Color Fill
                Group {
                    if colorScheme == .dark {
                        Color(hex: "#1E1E1E")
                    } else if style == .legal {
                        Color(hex: "#FFFDF0") // Ivory legal pad yellow
                    } else {
                        Color.white
                    }
                }
                .ignoresSafeArea()
                
                // Rule lines/dots
                Path { path in
                    switch style {
                    case .plain:
                        break
                    case .ruled:
                        let lineSpacing: CGFloat = spacing
                        var y: CGFloat = lineSpacing
                        while y < geo.size.height {
                            path.move(to: CGPoint(x: 0, y: y))
                            path.addLine(to: CGPoint(x: geo.size.width, y: y))
                            y += lineSpacing
                        }
                    case .grid:
                        let gridSpacing: CGFloat = spacing
                        var x: CGFloat = gridSpacing
                        while x < geo.size.width {
                            path.move(to: CGPoint(x: x, y: 0))
                            path.addLine(to: CGPoint(x: x, y: geo.size.height))
                            x += gridSpacing
                        }
                        var y: CGFloat = gridSpacing
                        while y < geo.size.height {
                            path.move(to: CGPoint(x: 0, y: y))
                            path.addLine(to: CGPoint(x: geo.size.width, y: y))
                            y += gridSpacing
                        }
                    case .dots:
                        let dotSpacing: CGFloat = spacing
                        var y: CGFloat = dotSpacing
                        while y < geo.size.height {
                            var x: CGFloat = dotSpacing
                            while x < geo.size.width {
                                path.addEllipse(in: CGRect(x: x - 1, y: y - 1, width: 2, height: 2))
                                x += dotSpacing
                            }
                            y += dotSpacing
                        }
                    case .legal:
                        let lineSpacing: CGFloat = spacing * (28.0 / 24.0)
                        var y: CGFloat = lineSpacing * 2
                        while y < geo.size.height {
                            path.move(to: CGPoint(x: 0, y: y))
                            path.addLine(to: CGPoint(x: geo.size.width, y: y))
                            y += lineSpacing
                        }
                    case .collegeRuled:
                        let lineSpacing: CGFloat = spacing * (21.0 / 24.0)
                        var y: CGFloat = lineSpacing * 3
                        while y < geo.size.height {
                            path.move(to: CGPoint(x: 0, y: y))
                            path.addLine(to: CGPoint(x: geo.size.width, y: y))
                            y += lineSpacing
                        }
                    case .flashcard:
                        break
                    }
                }
                .stroke(
                    colorScheme == .dark
                        ? Color.white.opacity(0.14)
                        : Color(hex: style == .legal ? "#B5D3FD" : "#CFE0F5"),
                    lineWidth: style == .dots ? 2 : 0.8
                )

                // Pink/Red Vertical Margin Line for Academic/Legal/Ruled
                if style == .legal || style == .collegeRuled || style == .ruled {
                    Path { path in
                        let marginX: CGFloat = style == .legal ? 88 : 72
                        path.move(to: CGPoint(x: marginX, y: 0))
                        path.addLine(to: CGPoint(x: marginX, y: geo.size.height))
                    }
                    .stroke(
                        colorScheme == .dark ? Color.red.opacity(0.4) : Color.red.opacity(0.45),
                        lineWidth: 1.2
                    )
                }

                // Flashcard Horizontal Dashed Divider and Prompts
                if style == .flashcard {
                    Path { path in
                        let midY = geo.size.height / 2
                        path.move(to: CGPoint(x: 0, y: midY))
                        path.addLine(to: CGPoint(x: geo.size.width, y: midY))
                    }
                    .stroke(
                        colorScheme == .dark ? Color.white.opacity(0.2) : Color.gray.opacity(0.35),
                        style: StrokeStyle(lineWidth: 1.2, dash: [6, 4])
                    )
                    
                    VStack {
                        Text("FRONT / QUESTION")
                            .font(.system(size: 11, weight: .bold, design: .rounded))
                            .foregroundColor(colorScheme == .dark ? Color.white.opacity(0.15) : Color.black.opacity(0.12))
                            .padding(.top, 16)
                        
                        Spacer()
                        
                        Text("BACK / ANSWER")
                            .font(.system(size: 11, weight: .bold, design: .rounded))
                            .foregroundColor(colorScheme == .dark ? Color.white.opacity(0.15) : Color.black.opacity(0.12))
                            .padding(.bottom, 16)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
        }
    }
}

extension Notification.Name {
    static let insertDictatedText = Notification.Name("InsertDictatedText")
}
