//
//  ContentBlockerRequestHandler.swift
//  PulitoContentBlocker
//
//  Created by Turi0nX
//

import Foundation
import MobileCoreServices
import UniformTypeIdentifiers

final class ContentBlockerRequestHandler: NSObject, NSExtensionRequestHandling {

    // Scegli se usare PRO o BASE
    private var usePro: Bool { true }   // per ora sempre PRO

    func beginRequest(with context: NSExtensionContext) {
        let filename = usePro ? "blockerList_pro.json" : "blockerList_base.json"

        // 1. Prende il container dell’App Group
        guard let containerURL = FileManager.default
            .containerURL(forSecurityApplicationGroupIdentifier: AppEnvironment.appGroupId) else {

            // In caso di errore, come fallback usa il vecchio blockerList.json di bundle
            if let fallbackURL = Bundle.main.url(forResource: "blockerList", withExtension: "json") {
                complete(context: context, withFileAt: fallbackURL)
                return
            }

            context.cancelRequest(withError: NSError(
                domain: "PulitoContentBlocker",
                code: 1,
                userInfo: [NSLocalizedDescriptionKey: "App Group container not found"]
            ))
            return
        }

        let listURL = containerURL.appendingPathComponent(filename)

        // 2. Se il file non esiste ancora, fallback
        guard FileManager.default.fileExists(atPath: listURL.path) else {
            if let fallbackURL = Bundle.main.url(forResource: "blockerList", withExtension: "json") {
                complete(context: context, withFileAt: fallbackURL)
                return
            }

            context.cancelRequest(withError: NSError(
                domain: "PulitoContentBlocker",
                code: 2,
                userInfo: [NSLocalizedDescriptionKey: "Blocker list not found in App Group"]
            ))
            return
        }

        // 3. Restituisce il file a Safari
        complete(context: context, withFileAt: listURL)
    }

    private func complete(context: NSExtensionContext, withFileAt url: URL) {
        let provider = NSItemProvider(contentsOf: url)!

        let item = NSExtensionItem()
        item.attachments = [provider]

        context.completeRequest(returningItems: [item], completionHandler: nil)
    }
}
