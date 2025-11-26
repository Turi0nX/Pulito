//
//  AppEnviroment.swift
//  
//
//  Created by on 23/11/25.
//

import Foundation

struct AppEnvironment {

    // App Group condiviso tra app e content blocker extension
    static let appGroupId: String = "group.com.Turi0nX.Pulito"

    // Bundle identifier ESATTO del target PulitoContentBlocker
    static let contentBlockerExtensionId: String = "com.Turi0nX.Pulito.PulitoContentBlocker"

    // Base URL del backend 
    static let baseURL = URL(string: "https://turi0nx.github.io/Pulito/Backend/output")!

    // Percorsi dei manifest
    static let manifestBasePath = "manifest_base.json"
    static let manifestProPath  = "manifest_pro.json"

    // URL completi dei manifest (se vuoi usarli in ContentBlockerUpdater)
    static var manifestBaseURL: URL {
        baseURL.appendingPathComponent(manifestBasePath)
    }

    static var manifestProURL: URL {
        baseURL.appendingPathComponent(manifestProPath)
    }
}


