import SwiftUI

// MARK: - Study Flashcard Spaced Repetition Overlay
struct StudyFlashcardDeckOverlay: View {
    @Binding var isStudyModeActive: Bool
    let studyCards: [SDAnnotation]
    @Binding var currentCardIndex: Int
    @Binding var isAnswerRevealed: Bool
    let correctAnswersCount: Int
    let onGrade: (Bool) -> Void
    
    @Environment(\.colorScheme) private var colorScheme
    
    init(
        isStudyModeActive: Binding<Bool>,
        studyCards: [SDAnnotation],
        currentCardIndex: Binding<Int>,
        isAnswerRevealed: Binding<Bool>,
        correctAnswersCount: Int,
        onGrade: @escaping (Bool) -> Void
    ) {
        self._isStudyModeActive = isStudyModeActive
        self.studyCards = studyCards
        self._currentCardIndex = currentCardIndex
        self._isAnswerRevealed = isAnswerRevealed
        self.correctAnswersCount = correctAnswersCount
        self.onGrade = onGrade
    }
    
    var body: some View {
        ZStack {
            Color.black.opacity(0.4)
                .background(.ultraThinMaterial)
                .ignoresSafeArea()
                .onTapGesture {
                    withAnimation {
                        isStudyModeActive = false
                    }
                }
            
            VStack(spacing: 24) {
                HStack {
                    Text("ACTIVE RECALL DECK")
                        .font(.system(size: 13, weight: .bold, design: .rounded))
                        .foregroundColor(.secondary)
                        .kerning(1.2)
                    
                    Spacer()
                    
                    Button {
                        withAnimation {
                            isStudyModeActive = false
                        }
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 22))
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.horizontal, 32)
                .padding(.top, 24)
                
                if currentCardIndex < studyCards.count {
                    let card = studyCards[currentCardIndex]
                    
                    VStack(spacing: 0) {
                        VStack(spacing: 12) {
                            HStack {
                                Image(systemName: "bookmark.fill")
                                    .foregroundColor(.orange)
                                Text("Page \(card.pageIndex + 1)")
                                    .font(.system(size: 14, weight: .semibold, design: .rounded))
                                    .foregroundColor(.orange)
                                
                                Spacer()
                                
                                Text("\(currentCardIndex + 1) of \(studyCards.count)")
                                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                                    .foregroundColor(.secondary)
                            }
                            
                            if let chapter = card.chapterTitle, !chapter.isEmpty {
                                Text(chapter)
                                    .font(.system(size: 16, weight: .bold, design: .rounded))
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .padding(.top, 4)
                            }
                            
                            if let tags = card.tags, !tags.isEmpty {
                                ScrollView(.horizontal, showsIndicators: false) {
                                    HStack(spacing: 6) {
                                        ForEach(tags, id: \.self) { tag in
                                            Text("#\(tag)")
                                                .font(.system(size: 11, weight: .semibold, design: .rounded))
                                                .padding(.horizontal, 8)
                                                .padding(.vertical, 4)
                                                .background(Color.orange.opacity(0.12), in: Capsule())
                                                .foregroundColor(.orange)
                                        }
                                    }
                                }
                                .padding(.top, 4)
                            }
                            
                            Spacer()
                            
                            Text("Recall the highlighted concept or note below:")
                                .font(.system(size: 14, weight: .medium))
                                .foregroundColor(.secondary)
                                .frame(maxWidth: .infinity, alignment: .center)
                                .multilineTextAlignment(.center)
                            
                            Spacer()
                        }
                        .padding(24)
                        .frame(height: 180)
                        
                        Divider()
                        
                        ZStack {
                            if !isAnswerRevealed {
                                Button {
                                    withAnimation(.easeOut(duration: 0.25)) {
                                        isAnswerRevealed = true
                                    }
                                } label: {
                                    VStack(spacing: 8) {
                                        Image(systemName: "eye.fill")
                                            .font(.system(size: 24))
                                        Text("Tap to Reveal Answer")
                                            .font(.system(size: 14, weight: .semibold, design: .rounded))
                                    }
                                    .foregroundColor(.blue)
                                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                                    .background(.ultraThinMaterial)
                                }
                            } else {
                                ScrollView {
                                    VStack(alignment: .leading, spacing: 14) {
                                        if let text = card.selectedText, !text.isEmpty {
                                            Text(text)
                                                .font(.system(size: 15, weight: .medium, design: .serif))
                                                .foregroundColor(.primary)
                                                .italic()
                                                .padding(12)
                                                .background(Color.primary.opacity(0.04))
                                                .cornerRadius(6)
                                        }
                                        
                                        if let note = card.noteText, !note.isEmpty {
                                            HStack(alignment: .top, spacing: 6) {
                                                Image(systemName: "note.text")
                                                    .foregroundColor(.blue)
                                                    .font(.system(size: 14))
                                                    .padding(.top, 2)
                                                Text(note)
                                                    .font(.system(size: 14, weight: .medium, design: .rounded))
                                                    .foregroundColor(.primary)
                                            }
                                        }
                                    }
                                    .padding(20)
                                }
                            }
                        }
                        .frame(height: 220)
                    }
                    .background(colorScheme == .dark ? Color(hex: "#1C1C1E") : Color.white)
                    .cornerRadius(18)
                    .overlay(
                        RoundedRectangle(cornerRadius: 18)
                            .stroke(Color.primary.opacity(0.08), lineWidth: 1.5)
                    )
                    .shadow(color: Color.black.opacity(0.12), radius: 16, x: 0, y: 8)
                    .padding(.horizontal, 32)
                    
                    if isAnswerRevealed {
                        HStack(spacing: 16) {
                            Button {
                                onGrade(false)
                            } label: {
                                HStack {
                                    Image(systemName: "xmark.circle.fill")
                                    Text("Forgot / Hard")
                                }
                                .font(.system(size: 14, weight: .bold, design: .rounded))
                                .foregroundColor(.red)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                                .background(Color.red.opacity(0.08))
                                .cornerRadius(12)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(Color.red.opacity(0.2), lineWidth: 1)
                                )
                            }
                            
                            Button {
                                onGrade(true)
                            } label: {
                                HStack {
                                    Image(systemName: "checkmark.circle.fill")
                                    Text("Recalled / Easy")
                                }
                                .font(.system(size: 14, weight: .bold, design: .rounded))
                                .foregroundColor(.green)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                                .background(Color.green.opacity(0.08))
                                .cornerRadius(12)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(Color.green.opacity(0.2), lineWidth: 1)
                                )
                            }
                        }
                        .padding(.horizontal, 32)
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                    } else {
                        Color.clear.frame(height: 48)
                    }
                    
                } else {
                    VStack(spacing: 20) {
                        Image(systemName: "trophy.fill")
                            .font(.system(size: 56))
                            .foregroundStyle(
                                LinearGradient(colors: [.yellow, .orange], startPoint: .top, endPoint: .bottom)
                            )
                            .padding(.top, 16)
                        
                        Text("Congratulations!")
                            .font(.system(size: 24, weight: .bold, design: .rounded))
                        
                        Text("You have completed this spaced repetition study session.")
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 24)
                        
                        let accuracy = studyCards.isEmpty ? 0 : Int(round(Double(correctAnswersCount) / Double(studyCards.count) * 100))
                        VStack(spacing: 4) {
                            Text("\(accuracy)%")
                                .font(.system(size: 28, weight: .black, design: .monospaced))
                                .foregroundColor(.green)
                            Text("Active Recall Accuracy")
                                .font(.system(size: 12, weight: .semibold, design: .rounded))
                                .foregroundColor(.secondary)
                        }
                        .padding(16)
                        .background(Color.primary.opacity(0.04), in: RoundedRectangle(cornerRadius: 12))
                        
                        Button {
                            withAnimation {
                                isStudyModeActive = false
                            }
                        } label: {
                            Text("Done")
                                .font(.system(size: 15, weight: .bold, design: .rounded))
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                                .background(Theme.blue)
                                .cornerRadius(12)
                        }
                        .padding(.horizontal, 32)
                        .padding(.bottom, 16)
                    }
                    .background(colorScheme == .dark ? Color(hex: "#1C1C1E") : Color.white)
                    .cornerRadius(18)
                    .overlay(
                        RoundedRectangle(cornerRadius: 18)
                            .stroke(Color.primary.opacity(0.08), lineWidth: 1.5)
                    )
                    .shadow(color: Color.black.opacity(0.12), radius: 16, x: 0, y: 8)
                    .padding(.horizontal, 32)
                    .onAppear {
                        UINotificationFeedbackGenerator().notificationOccurred(.success)
                    }
                }
                
                Spacer()
            }
            .frame(maxWidth: 420)
        }
    }
}
