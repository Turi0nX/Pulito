//
//  RSASignatureVerifier.swift
//  
//
//  Created by Turi0nX
//

import Foundation
import Security   // necessario per SecKey*

enum RSASignatureVerifierError: Error {
    case pemNotFound
    case invalidPEM
    case keyImportFailed
    case invalidSignatureBase64
    case verificationFailed
}

final class RSASignatureVerifier {

    // Carica il contenuto di pulito_pubkey.pem dal bundle principale
    private static func loadPublicKeyPEM() throws -> String {
        guard let url = Bundle.main.url(forResource: "pulito_pubkey", withExtension: "pem") else {
            throw RSASignatureVerifierError.pemNotFound
        }
        return try String(contentsOf: url, encoding: .utf8)
    }

    // Estrae i bytes DER dal testo PEM
    private static func derData(fromPEM pem: String) throws -> Data {
        let lines = pem
            .components(separatedBy: .newlines)
            .filter { !$0.hasPrefix("-----") && !$0.isEmpty }

        guard !lines.isEmpty else {
            throw RSASignatureVerifierError.invalidPEM
        }

        let base64String = lines.joined()
        guard let data = Data(base64Encoded: base64String) else {
            throw RSASignatureVerifierError.invalidPEM
        }
        return data
    }

    // Crea una SecKey pubblica a partire dalla PEM RSA
    private static func secKeyFromPEM() throws -> SecKey {
        let pem = try loadPublicKeyPEM()
        let derData = try derData(fromPEM: pem)

        let options: [CFString: Any] = [
            kSecAttrKeyType:  kSecAttrKeyTypeRSA,
            kSecAttrKeyClass: kSecAttrKeyClassPublic,
        ]

        var error: Unmanaged<CFError>?
        guard let key = SecKeyCreateWithData(derData as CFData,
                                             options as CFDictionary,
                                             &error) else {
            if let err = error?.takeRetainedValue() {
                print("SecKeyCreateWithData error:", err)
            }
            throw RSASignatureVerifierError.keyImportFailed
        }

        return key
    }

    // Verifica firma RSA‑PKCS1v1.5 con SHA256 del payload (es. blocker_list_sha256)
    static func verify(payload: String, signatureBase64: String) throws -> Bool {
        let key = try secKeyFromPEM()

        guard let signatureData = Data(base64Encoded: signatureBase64) else {
            throw RSASignatureVerifierError.invalidSignatureBase64
        }

        let payloadData = Data(payload.utf8)

        var error: Unmanaged<CFError>?
        let ok = SecKeyVerifySignature(
            key,
            .rsaSignatureMessagePKCS1v15SHA256,
            payloadData as CFData,
            signatureData as CFData,
            &error
        )

        if let err = error?.takeRetainedValue() {
            print("RSASignatureVerifier verify error:", err)
        }

        if !ok {
            throw RSASignatureVerifierError.verificationFailed
        }

        return ok
    }
}



