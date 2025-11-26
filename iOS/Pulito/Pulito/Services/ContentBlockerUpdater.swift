//  ContentBlockerUpdater.swift
//
//  Created by Turi0nX
//

import Foundation
import SafariServices

enum ContentBlockerUpdaterError: Error {
    case invalidURL
    case networkError(Error)
    case invalidResponse
    case decodingError(Error)
    case invalidSignature
    case emptyBlockerList
    case appGroupContainerNotFound
}



@MainActor
final class ContentBlockerUpdater {
    static let shared = ContentBlockerUpdater()
    private init() {}

    // URL dei manifest
    private var baseManifestURL: URL { AppEnvironment.manifestBaseURL }
    private var proManifestURL: URL  { AppEnvironment.manifestProURL }

    // Decoder configurato una volta sola, senza catturare formatter non-Sendable
    private lazy var decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.dateDecodingStrategy = .custom { decoder in
            // Formatter locale -> non viene catturato al di fuori della closure
            let iso = ISO8601DateFormatter()
            iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]

            let container = try decoder.singleValueContainer()
            let str = try container.decode(String.self)
            if let date = iso.date(from: str) {
                return date
            }
            throw ContentBlockerUpdaterError.decodingError(
                NSError(domain: "date", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid date format \(str)"])
            )
        }
        return d
    }()

    // DEBUG-only network inspector: non altera la logica, stampa info utili
        private func debugFetch(_ url: URL) async throws -> (Data, URLResponse) {
        #if DEBUG
            let start = Date()
            do {
                let (data, response) = try await URLSession.shared.data(from: url)
                let duration = Date().timeIntervalSince(start)
                if let http = response as? HTTPURLResponse {
                    print("CBU-DBG: fetched \(url.absoluteString) -> \(http.statusCode) in \(String(format: "%.2f", duration))s, bytes:", data.count)
                } else {
                    print("CBU-DBG: fetched \(url.absoluteString) -> non-HTTP response in \(String(format: "%.2f", duration))s, bytes:", data.count)
                }
                if let s = String(data: data, encoding: .utf8), s.count < 2000 {
                    print("CBU-DBG: body preview:\n\(s)")
                } else if let s = String(data: data, encoding: .utf8) {
                    print("CBU-DBG: body preview (truncated):\n\(String(s.prefix(1000)))…")
                }
                return (data, response)
            } catch {
                print("CBU-DBG: network error fetching \(url):", error)
                throw error
            }
        #else
            return try await URLSession.shared.data(from: url)
        #endif
        }
    
    // MARK: - API pubbliche (async/await)

    /// Aggiorna la lista BASE.
    /// - Returns: true se aggiornata, false se era già all'ultima versione.
    func checkAndUpdateBase() async throws -> Bool {
        try await checkAndUpdate(
            from: baseManifestURL,
            versionKey: "pulito_blocker_version_base_v1",
            outputFilename: "blockerList_base.json"
        )
    }

    /// Aggiorna la lista PRO.
    /// - Returns: true se aggiornata, false se era già all'ultima versione.
    func checkAndUpdatePro() async throws -> Bool {
        try await checkAndUpdate(
            from: proManifestURL,
            versionKey: "pulito_blocker_version_pro_v1",
            outputFilename: "blockerList_pro.json"
        )
    }

    // MARK: - Implementazione generica (async)

    private func checkAndUpdate(from manifestURL: URL,
                                versionKey: String,
                                outputFilename: String) async throws -> Bool {

        // 1. Scarica il manifest
        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await URLSession.shared.data(from: manifestURL)
        } catch {
            throw ContentBlockerUpdaterError.networkError(error)
        }

        guard let http = response as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            throw ContentBlockerUpdaterError.invalidResponse
        }

        // 2. Decodifica manifest
        let manifest: BlockerManifest
        do {
            manifest = try decoder.decode(BlockerManifest.self, from: data)
        } catch {
            throw ContentBlockerUpdaterError.decodingError(error)
        }

        // 3. Verifica firma RSA sul campo blocker_list_sha256
        let ok = try RSASignatureVerifier.verify(
            payload: manifest.blockerListSHA256,
            signatureBase64: manifest.signature
        )
        guard ok else {
            throw ContentBlockerUpdaterError.invalidSignature
        }

        // 4. Controlla se questa versione è già applicata
        let defaults = UserDefaults(suiteName: AppEnvironment.appGroupId)
        let localVersion = defaults?.string(forKey: versionKey)
        if localVersion == manifest.version {
            return false // già aggiornato
        }

        // 5. Scarica la blocker list dal blocker_list_url del manifest
        let listData = try await downloadBlockerList(from: manifest.blockerListURL)

        // 6. Salva nell’App Group
        try saveToAppGroup(data: listData, filename: outputFilename)

        // 7. Aggiorna versione salvata
        defaults?.set(manifest.version, forKey: versionKey)

        // 8. Ricarica l’estensione content blocker (API async moderna)
        try await SFContentBlockerManager.reloadContentBlocker(
            withIdentifier: AppEnvironment.contentBlockerExtensionId
        )

        return true
    }

    // MARK: - Helpers async

    private func downloadBlockerList(from url: URL) async throws -> Data {
        do {
            let (data, response) = try await URLSession.shared.data(from: url)

            guard let http = response as? HTTPURLResponse,
                  (200..<300).contains(http.statusCode),
                  !data.isEmpty else {
                throw ContentBlockerUpdaterError.emptyBlockerList
            }

            return data
        } catch {
            throw ContentBlockerUpdaterError.networkError(error)
        }
    }

    private func saveToAppGroup(data: Data, filename: String) throws {
        guard let container = FileManager.default
            .containerURL(forSecurityApplicationGroupIdentifier: AppEnvironment.appGroupId) else {
            throw ContentBlockerUpdaterError.appGroupContainerNotFound
        }
        let dest = container.appendingPathComponent(filename)
        try data.write(to: dest, options: .atomic)
    }
}
