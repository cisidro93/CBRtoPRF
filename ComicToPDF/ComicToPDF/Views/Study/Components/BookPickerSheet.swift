import SwiftUI
import SwiftData

// MARK: - Book Picker Sheet
struct BookPickerSheet: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.modelContext) private var modelContext
    @Environment(\.colorScheme) private var colorScheme
    
    let onSelect: (ConvertedPDF) -> Void
    
    @State private var searchQuery = ""
    @State private var books: [SDConvertedPDF] = []
    
    init(onSelect: @escaping (ConvertedPDF) -> Void) {
        self.onSelect = onSelect
    }
    
    private var filteredBooks: [SDConvertedPDF] {
        if searchQuery.isEmpty {
            return books
        } else {
            return books.filter { $0.name.localizedCaseInsensitiveContains(searchQuery) }
        }
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color(hex: "#0a0a0f").edgesIgnoringSafeArea(.all)
                
                if filteredBooks.isEmpty {
                    VStack(spacing: 12) {
                        Image(systemName: "book.closed")
                            .font(.system(size: 40))
                            .foregroundColor(.gray)
                        Text(searchQuery.isEmpty ? "No books in library" : "No matches found")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.gray)
                    }
                } else {
                    List(filteredBooks) { book in
                        Button {
                            onSelect(book.toDTO())
                            dismiss()
                        } label: {
                            HStack(spacing: 12) {
                                if let data = book.coverImageData, let uiImage = UIImage(data: data) {
                                    Image(uiImage: uiImage)
                                        .resizable()
                                        .aspectRatio(contentMode: .fill)
                                        .frame(width: 40, height: 60)
                                        .cornerRadius(4)
                                        .clipped()
                                } else {
                                    RoundedRectangle(cornerRadius: 4)
                                        .fill(Color.gray.opacity(0.3))
                                        .frame(width: 40, height: 60)
                                        .overlay(Image(systemName: "book").foregroundColor(.gray))
                                }
                                
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(book.name)
                                        .font(.system(size: 15, weight: .bold))
                                        .foregroundColor(.white)
                                        .lineLimit(1)
                                    
                                    Text(book.formattedSize)
                                        .font(.system(size: 12))
                                        .foregroundColor(.gray)
                                }
                            }
                        }
                        .listRowBackground(Color(hex: "#12121e"))
                    }
                    .scrollContentBackground(.hidden)
                }
            }
            .navigationTitle("Link Book")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                        .foregroundColor(.white)
                }
            }
            .searchable(text: $searchQuery, prompt: "Search books...")
            .onAppear {
                let descriptor = FetchDescriptor<SDConvertedPDF>(sortBy: [SortDescriptor(\SDConvertedPDF.name)])
                books = (try? modelContext.fetch(descriptor)) ?? []
            }
        }
        .presentationDragIndicator(.visible)
    }
}
