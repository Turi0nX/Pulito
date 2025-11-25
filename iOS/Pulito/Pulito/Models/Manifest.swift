import Foundation

struct BlockerManifest: Decodable, Sendable {
    let kind: String
    let version: String
    let generatedAt: Date
    let blockerListURL: URL
    let blockerListSHA256: String
    let signature: String

    enum CodingKeys: String, CodingKey {
        case kind
        case version
        case generatedAt = "generated_at"
        case blockerListURL = "blocker_list_url"
        case blockerListSHA256 = "blocker_list_sha256"
        case signature
    }
}
