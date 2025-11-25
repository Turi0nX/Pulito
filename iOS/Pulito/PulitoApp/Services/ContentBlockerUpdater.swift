//
//  ContentBlockerUpdater.swift
//  
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

final class ContentBlockerUpdater {
    static let shared = ContentBlockerUpdater()
    private init() {}

    // URL dei manifest
    private var baseManifestURL: URL {
        URL(string: "https://Turi0nX.github.io/Pulito/Backend/output/manifest_base.json")!
    }

    private var proManifestURL: URL {
        URL(string: "https://Turi0nX.github.io/Pulito/Backend/output/manifest_pro.json")!
    }

    private lazy var decoder: JSONDecoder = {
        let d = JSONDecoder()
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        d.dateDecodingStrategy = .custom { decoder in
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

    // MARK: - API pubbliche

    /// Aggiorna la lista BASE. Result<Bool> -> true se aggiornata, false se già alla versione più recente.
    func checkAndUpdateBase(completion: @escaping (Result<Bool, Error>) -> Void) {
        checkAndUpdate(
            from: baseManifestURL,
            versionKey: "pulito_blocker_version_base_v1",
            outputFilename: "blockerList_base.json",
            completion: completion
        )
    }

    /// Aggiorna la lista PRO. Result<Bool> -> true se aggiornata, false se già alla versione più recente.
    func checkAndUpdatePro(completion: @escaping (Result<Bool, Error>) -> Void) {
        checkAndUpdate(
            from: proManifestURL,
            versionKey: "pulito_blocker_version_pro_v1",
            outputFilename: "blockerList_pro.json",
            completion: completion
        )
    }

    // MARK: - Implementazione generica

    private func checkAndUpdate(from manifestURL: URL,
                                versionKey: String,
                                outputFilename: String,
                                completion: @escaping (Result<Bool, Error>) -> Void) {

        URLSession.shared.dataTask(with: manifestURL) { [weak self] data, response, error in
            guard let self else { return }

            if let error = error {
                completion(.failure(ContentBlockerUpdaterError.networkError(error)))
                return
            }

            guard let http = response as? HTTPURLResponse,
                  (200..<300).contains(http.statusCode),
                  let data = data else {
                completion(.failure(ContentBlockerUpdaterError.invalidResponse))
                return
            }

            do {
                // 1. Decodifica manifest
                let manifest = try self.decoder.decode(BlockerManifest.self, from: data)

                // 2. Verifica firma RSA sul campo blocker_list_sha256
                let ok = try RSASignatureVerifier.verify(
                    payload: manifest.blockerListSHA256,
                    signatureBase64: manifest.signature
                )

                guard ok else {
                    completion(.failure(ContentBlockerUpdaterError.invalidSignature))
                    return
                }

                // 3. Controlla se questa versione è già applicata
                let defaults = UserDefaults(suiteName: AppEnvironment.appGroupId)
                let localVersion = defaults?.string(forKey: versionKey)
                if localVersion == manifest.version {
                    completion(.success(false)) // già aggiornato
                    return
                }

                // 4. Scarica la blocker list dal blocker_list_url del manifest
                self.downloadBlockerList(from: manifest.blockerListURL) { result in
                    switch result {
                    case .failure(let error):
                        completion(.failure(error))
                    case .success(let listData):
                        do {
                            // 5. Salva nell’App Group
                            try self.saveToAppGroup(data: listData, filename: outputFilename)

                            // 6. Aggiorna versione salvata
                            defaults?.set(manifest.version, forKey: versionKey)

                            // 7. Ricarica l’estensione content blocker
                            SFContentBlockerManager.reloadContentBlocker(
                                withIdentifier: AppEnvironment.contentBlockerExtensionId
                            ) { error in
                                if let error = error {
                                    completion(.failure(error))
                                } else {
                                    completion(.success(true))
                                }
                            }
                        } catch {
                            completion(.failure(error))
                        }
                    }
                }

            } catch {
                completion(.failure(ContentBlockerUpdaterError.decodingError(error)))
            }
        }.resume()
    }

    private func downloadBlockerList(from url: URL,
                                     completion: @escaping (Result<Data, Error>) -> Void) {
        URLSession.shared.dataTask(with: url) { data, _, error in
            if let error = error {
                completion(.failure(ContentBlockerUpdaterError.networkError(error)))
                return
            }
            guard let data = data, !data.isEmpty else {
                completion(.failure(ContentBlockerUpdaterError.emptyBlockerList))
                return
            }
            completion(.success(data))
        }.resume()
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

