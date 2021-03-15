//
//  MapBoxViewController.swift
//  WaffleWar
//
//  Created by Len Norton on 3/13/21.
//

import UIKit
import MapboxMaps
import Turf

class MapBoxViewController: UIViewController {

    var mapView: MapView!

    var houses = [House]()

    override public func viewDidLoad() {
        super.viewDidLoad()

        let accessToken = Bundle.main.object(forInfoDictionaryKey: "MBXAccessToken") as! String
        let myResourceOptions = ResourceOptions(accessToken: accessToken)
        mapView = MapView(with: view.bounds, resourceOptions: myResourceOptions)
        mapView.autoresizingMask = [.flexibleWidth, .flexibleHeight]

        mapView.update { (mapOptions) in
            mapOptions.ornaments.showsScale = true
        }

        self.view.addSubview(mapView)

        // dispersit, suffocati, operuit
        let centerCoordinate = CLLocationCoordinate2D(latitude: 33.77555534, longitude: -84.27381381)

        mapView.cameraManager.setCamera(centerCoordinate: centerCoordinate, zoom: 5.0)

        mapView.on(.mapLoadingFinished) { [weak self] event in
            guard let self = self else { return }
            self.loadPolygons()
         }
    }

    private func loadPolygons() {
        do {
            if let data = ViewController.readLocalJSONFile(forName: "houses") {

                houses = try JSONDecoder().decode([House].self, from: data)

                /*
                // This does NOT work. MapBox is far worse than MapKit when it comes to the memory efficiency of annotations.
                var polygons = [PolygonAnnotation]()
                for house in houses {
                    let coordinates: [CLLocationCoordinate2D] = house.region.map { CLLocationCoordinate2DMake($0[0], $0[1]) }
                    polygons.append(PolygonAnnotation(coordinates: coordinates))
                }
                mapView.annotationManager.addAnnotations(polygons)
                */

                // Turn the "houses" into GeoJSON data, but skipping the nasty JSON part.

                let geoJSONDataSourceIdentifier = "geoJSON-data-source"

                var features = [Feature]()
                for house in houses {
                    let coordinates: [CLLocationCoordinate2D] = house.region.map { CLLocationCoordinate2DMake($0[0], $0[1]) }
                    let polygon = Polygon([coordinates])
                    let geometry = Geometry.polygon(polygon)
                    var feature = Feature(geometry: geometry)
                    var properties = [String:Any]()
                    properties["house"] = house.house
                    feature.properties = properties
                    features.append(feature)
                }

                let featureCollection = FeatureCollection(features: features)

                var geoJSONSource = GeoJSONSource()
                geoJSONSource.data = .featureCollection(featureCollection)

                var waffleLayer = FillLayer(id: "waffle-layer")
                waffleLayer.source = geoJSONDataSourceIdentifier
                waffleLayer.filter = Exp(.eq) {
                    Exp(.get) { "house" }
                    "WH"
                }
                waffleLayer.paint?.fillColor = .constant(ColorRepresentable(color: UIColor.yellow.withAlphaComponent(0.25)))
                waffleLayer.paint?.fillOutlineColor = .constant(ColorRepresentable(color: UIColor.darkGray))

                var huddleLayer = FillLayer(id: "huddle-layer")
                huddleLayer.source = geoJSONDataSourceIdentifier
                huddleLayer.filter = Exp(.eq) {
                    Exp(.get) { "house" }
                    "HH"
                }
                huddleLayer.paint?.fillColor = .constant(ColorRepresentable(color: UIColor.orange.withAlphaComponent(0.25)))
                huddleLayer.paint?.fillOutlineColor = .constant(ColorRepresentable(color: UIColor.darkGray))

                var pancakeLayer = FillLayer(id: "pancake-layer")
                pancakeLayer.source = geoJSONDataSourceIdentifier
                pancakeLayer.source = geoJSONDataSourceIdentifier
                pancakeLayer.filter = Exp(.eq) {
                    Exp(.get) { "house" }
                    "IHOP"
                }
                pancakeLayer.paint?.fillColor = .constant(ColorRepresentable(color: UIColor.blue.withAlphaComponent(0.25)))
                pancakeLayer.paint?.fillOutlineColor = .constant(ColorRepresentable(color: UIColor.darkGray))

                mapView.style.addSource(source: geoJSONSource, identifier: geoJSONDataSourceIdentifier)
                mapView.style.addLayer(layer: waffleLayer)
                mapView.style.addLayer(layer: huddleLayer)
                mapView.style.addLayer(layer: pancakeLayer)
            }
        } catch {
        }
    }

}
