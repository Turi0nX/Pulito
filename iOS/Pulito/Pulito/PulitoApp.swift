//
//  PulitoApp.swift
//  Pulito
//
//  Created by Turi0nX
//

import SwiftUI

@main
struct PulitoApp: App {

    init() {
        // Test: aggiorna BASE + PRO all’avvio
        Task {
            do {
                let baseUpdated = try await ContentBlockerUpdater.shared.checkAndUpdateBase()
                print("BASE updated:", baseUpdated)
            } catch {
                print("Errore update BASE:", error)
            }

            do {
                let proUpdated = try await ContentBlockerUpdater.shared.checkAndUpdatePro()
                print("PRO updated:", proUpdated)
            } catch {
                print("Errore update PRO:", error)
            }
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
