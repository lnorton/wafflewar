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

enum Quadrant: Int, CaseIterable {
    case topLeft
    case bottomLeft
    case topRight
    case bottomRight
}

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

    func quadRect(quadrant: Quadrant) -> MKMapRect {
        switch quadrant {
        case .topLeft:
            return topLeftRect
        case .bottomLeft:
            return bottomLeftRect
        case .topRight:
            return topRightRect
        case .bottomRight:
            return bottomRightRect
        }
    }
}

class QuadNode<Element: MKOverlay> {

    var children = [QuadNode<Element>?](repeating: nil, count: 4)

    var elements: [Element] = []
    var bounds: MKMapRect

    init(rect: MKMapRect) {
        bounds = rect
    }

    @discardableResult
    func insert(element: Element) -> Bool {

        let elementRect = element.boundingMapRect

        if !bounds.contains(elementRect) {
            return false
        }

        for quadrant in Quadrant.allCases {
            let quadRect = bounds.quadRect(quadrant: quadrant)
            if quadRect.contains(elementRect) {
                let index = quadrant.rawValue
                if children[index] == nil {
                    children[index] = QuadNode<Element>(rect: quadRect)
                }
                if let child = children[index] {
                    child.insert(element: element)
                }
                return true
            }
        }

        elements.append(element)

        return true
    }

    func elementsIn(rect: MKMapRect) -> [Element] {

        if (!bounds.intersects(rect)) {
            return []
        }

        var collected = [Element]()

        for element in elements {
            if rect.intersects(element.boundingMapRect) {
                collected.append(element)
            }
        }

        for case let child? in children {
            collected.append(contentsOf: child.elementsIn(rect: rect))
        }

        return collected
    }

    func elementsNotInIntersection(newRect: MKMapRect, inNewRect: inout [Element], oldRect: MKMapRect, inOldRect: inout [Element]) {

        if (!bounds.intersects(newRect) && !bounds.intersects(oldRect)) {
            return
        }

        let intersectRect = newRect.intersection(oldRect)

        for element in elements {
            let elementRect = element.boundingMapRect
            if !intersectRect.intersects(elementRect) {
                if newRect.intersects(elementRect) {
                    inNewRect.append(element)
                } else if oldRect.intersects(elementRect) {
                    inOldRect.append(element)
                }
            }
        }

        for case let child? in children {
            child.elementsNotInIntersection(newRect: newRect, inNewRect: &inNewRect, oldRect: oldRect, inOldRect: &inOldRect)
        }
    }
}
