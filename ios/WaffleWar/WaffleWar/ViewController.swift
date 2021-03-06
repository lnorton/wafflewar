//
//  ViewController.swift
//  WaffleWar
//
//  Created by Len Norton on 3/3/21.
//

import UIKit
import MapKit

class ViewController: UIViewController {

    @IBOutlet
    var mapView: MKMapView?

    var polyToHouse = [MKPolygon:House]()

    override func viewDidLoad() {
        super.viewDidLoad()

        do {
            if let data = readLocalJSONFile(forName: "houses") {
                let houses = try JSONDecoder().decode([House].self, from: data)
                for house in houses {
                    var polys: [CLLocationCoordinate2D] = house.region.map { CLLocationCoordinate2DMake($0[0], $0[1]) }
                    let polygon = MKPolygon(coordinates: &polys, count: polys.count)
                    polyToHouse[polygon] = house
                    mapView!.addOverlay(polygon)
                }
            }
        } catch {
        }
    }

    private func readLocalJSONFile(forName name: String) -> Data? {
        do {
            if let bundlePath = Bundle.main.path(forResource: name, ofType: "json") {
                return try String(contentsOfFile: bundlePath).data(using: .utf8)
            }
        } catch {
        }
        return nil
    }
}

extension ViewController: MKMapViewDelegate {

    func mapView(_ mapView: MKMapView, rendererFor overlay: MKOverlay) -> MKOverlayRenderer {
        if overlay is MKPolygon {
            let polygon = overlay as! MKPolygon
            let house = polyToHouse[polygon]!
            let renderer = MKPolygonRenderer(polygon: polygon)
            let fillColor: UIColor
            switch house.house {
            case "WH":
                fillColor = UIColor.yellow
            case "HH":
                fillColor = UIColor.orange
            case "IHOP":
                fillColor = UIColor.blue
            default:
                fillColor = UIColor.green
            }
            renderer.fillColor = fillColor.withAlphaComponent(0.25)
            renderer.strokeColor = UIColor.gray
            renderer.lineWidth = 0.5
            return renderer
        } else {
            return MKOverlayRenderer()
        }
    }
}

class House: Codable {
    var link: String
    var name: String
    var address: [String]
    var coords: [Double]
    var house: String
    var state: String
    var region: [[Double]]
}
