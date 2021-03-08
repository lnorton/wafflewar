//
//  QuadTree.swift
//  WaffleWar
//
//  Created by Len Norton on 3/7/21.
//

import Foundation
import MapKit

// https://en.wikipedia.org/wiki/Quadtree
// https://github.com/raywenderlich/swift-algorithm-club/tree/master/QuadTree

extension MKMapSize {

    var halfSize: MKMapSize {
        MKMapSize(width: width / 2.0, height: height / 2.0)
    }
}

extension MKMapRect {

    var topLeftRect: MKMapRect {
        return MKMapRect(origin: MKMapPoint(x: minX, y: minY), size: size.halfSize)
    }

    var bottomLeftRect: MKMapRect {
        return MKMapRect(origin: MKMapPoint(x: minX, y: midY), size: size.halfSize)
    }

    var topRightRect: MKMapRect {
        return MKMapRect(origin: MKMapPoint(x: midX, y: minY), size: size.halfSize)
    }

    var bottomRightRect: MKMapRect {
        return MKMapRect(origin: MKMapPoint(x: midX, y: midY), size: size.halfSize)
    }
}

class QuadNode<Element: MKOverlay> {

    var topLeft: QuadNode<Element>?
    var bottomLeft: QuadNode<Element>?
    var topRight: QuadNode<Element>?
    var bottomRight: QuadNode<Element>?

    var elements: [Element] = []
    var rect: MKMapRect

    init(rect: MKMapRect) {
        self.rect = rect;
    }

    @discardableResult
    func insert(element: Element) -> Bool {

        if !rect.contains(element.boundingMapRect) {
            return false
        }

        if insertIntoChildren(element: element) {
            return true
        }

        elements.append(element)

        return true
    }

    @discardableResult
    private func insertIntoChildren(element: Element) -> Bool {

        if topLeft == nil {
            topLeft = QuadNode<Element>(rect: rect.topLeftRect)
            bottomLeft = QuadNode<Element>(rect: rect.bottomLeftRect)
            topRight = QuadNode<Element>(rect: rect.topRightRect)
            bottomRight = QuadNode<Element>(rect: rect.bottomRightRect)
        }

        if let topLeft = topLeft, let bottomLeft = bottomLeft, let topRight = topRight, let bottomRight = bottomRight {
            for child in [topLeft, bottomLeft, topRight, bottomRight] {
                if child.insert(element: element) {
                    return true
                }
            }
        }

        return false
    }

    func elementsIn(rect: MKMapRect) -> [Element] {

        if (!self.rect.intersects(rect)) {
            return []
        }

        var collected = [Element]()

        for element in elements {
            if rect.intersects(element.boundingMapRect) {
                collected.append(element)
            }
        }

        if let topLeft = topLeft, let bottomLeft = bottomLeft, let topRight = topRight, let bottomRight = bottomRight {
            for child in [topLeft, bottomLeft, topRight, bottomRight] {
                collected.append(contentsOf: child.elementsIn(rect: rect))
            }
        }

        return collected
    }
}
