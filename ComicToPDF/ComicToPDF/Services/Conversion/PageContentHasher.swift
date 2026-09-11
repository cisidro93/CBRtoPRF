import Foundation
import UIKit
import CryptoKit

/// Pure SHA-256 thumbprint of base page visual content.
/// Used to anchor annotations across format conversions or reflows that reorder pages.
///
/// CRITICAL ARCHITECTURE INVARIANT:
/// Hashing is strictly computed from the unadorned, raw base source content (raw image archive bitmap
/// or underlying CGPDFPage vector streams) BEFORE any user highlight annotations, PencilKit strokes,
/// or UI overlays are composited. This guarantees page hashes remain 100% stable as annotations are
/// added or modified, preventing self-invalidation cascades.
struct PageContentHasher {

    /// Computes SHA-256 thumbprint from a raw unannotated page image.
    /// Caller MUST pass the original source texture without user annotation overlays.
    static func sha256Hex(of image: UIImage) -> String? {
        guard let cgImage = image.cgImage else { return nil }

        let size = CGSize(width: 256, height: 256)
        let colorSpace = CGColorSpaceCreateDeviceGray()
        guard let context = CGContext(
            data: nil,
            width: Int(size.width),
            height: Int(size.height),
            bitsPerComponent: 8,
            bytesPerRow: Int(size.width),
            space: colorSpace,
            bitmapInfo: CGImageAlphaInfo.none.rawValue
        ) else { return nil }

        context.draw(cgImage, in: CGRect(origin: .zero, size: size))

        guard let rawData = context.data else { return nil }
        let byteCount = Int(size.width) * Int(size.height)
        let buffer = Data(bytes: rawData, count: byteCount)

        let digest = SHA256.hash(data: buffer)
        return digest.map { String(format: "%02hhx", $0) }.joined()
    }

    /// Computes SHA-256 thumbprint directly from the base `CGPDFPage` vector representation.
    /// CGContext.drawPDFPage draws strictly the document stream without rendering PDFKit's PDFAnnotation
    /// overlay objects, guaranteeing annotation-invariant hashing.
    static func sha256Hex(ofBasePDFPage page: CGPDFPage) -> String? {
        let size = CGSize(width: 256, height: 256)
        let colorSpace = CGColorSpaceCreateDeviceGray()
        guard let context = CGContext(
            data: nil,
            width: Int(size.width),
            height: Int(size.height),
            bitsPerComponent: 8,
            bytesPerRow: Int(size.width),
            space: colorSpace,
            bitmapInfo: CGImageAlphaInfo.none.rawValue
        ) else { return nil }

        let pageRect = page.getBoxRect(.cropBox)
        guard pageRect.width > 0, pageRect.height > 0 else { return nil }

        // Scale page into 256x256 thumbnail
        let scaleX = size.width / pageRect.width
        let scaleY = size.height / pageRect.height
        let scale = min(scaleX, scaleY)

        context.saveGState()
        context.scaleBy(x: scale, y: scale)
        context.translateBy(x: -pageRect.origin.x, y: -pageRect.origin.y)
        context.drawPDFPage(page)
        context.restoreGState()

        guard let rawData = context.data else { return nil }
        let byteCount = Int(size.width) * Int(size.height)
        let buffer = Data(bytes: rawData, count: byteCount)

        let digest = SHA256.hash(data: buffer)
        return digest.map { String(format: "%02hhx", $0) }.joined()
    }

    /// Computes SHA-256 thumbprint from raw file byte streams.
    static func sha256Hex(of data: Data) -> String {
        let digest = SHA256.hash(data: data)
        return digest.map { String(format: "%02hhx", $0) }.joined()
    }
}
