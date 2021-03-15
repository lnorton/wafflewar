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

    var houses = [House]()
    var polyToHouse = [MKPolygon:House]()
    var quadTree: QuadNode<MKPolygon>?

    private var oldMapRect = MKMapRect()

    override func viewDidLoad() {
        super.viewDidLoad()

        quadTree = QuadNode<MKPolygon>(rect: MKMapRect.world)

        do {
            if let data = ViewController.readLocalJSONFile(forName: "houses") {
                houses = try JSONDecoder().decode([House].self, from: data)
                for house in houses {
                    var coordinates: [CLLocationCoordinate2D] = house.region.map { CLLocationCoordinate2DMake($0[0], $0[1]) }
                    let polygon = MKPolygon(coordinates: &coordinates, count: coordinates.count)
                    polyToHouse[polygon] = house
                    quadTree!.insert(element: polygon)
                }
            }
        } catch {
        }
    }

    class func readLocalJSONFile(forName name: String) -> Data? {
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

    func mapView(_ mapView: MKMapView, regionWillChangeAnimated animated: Bool) {
        oldMapRect = mapView.visibleMapRect
    }

    func mapView(_ mapView: MKMapView, regionDidChangeAnimated animated: Bool) {

        let size = mapView.visibleMapRect.size
        let overlays = mapView.overlays

        if max(size.width, size.height) > 8000000.0 {
            if overlays.count > 0 {
                mapView.removeOverlays(overlays)
            }
            return
        }

        if overlays.count == 0 {
            let overlays = quadTree!.elementsIn(rect: mapView.visibleMapRect)
            mapView.addOverlays(overlays)
        } else {
            var inNewRect = [MKPolygon]()
            var inOldRect = [MKPolygon]()
            quadTree!.elementsNotInIntersection(newRect: mapView.visibleMapRect, inNewRect: &inNewRect, oldRect: oldMapRect, inOldRect: &inOldRect)
            mapView.removeOverlays(inOldRect)
            mapView.addOverlays(inNewRect)
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
