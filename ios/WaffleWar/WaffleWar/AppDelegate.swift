//
//  AppDelegate.swift
//  WaffleWar
//
//  Created by Len Norton on 3/3/21.
//

import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        window = UIWindow(frame: UIScreen.main.bounds)
        window!.rootViewController = MapBoxViewController()
        window!.makeKeyAndVisible()
        return true
    }
}
