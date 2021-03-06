from waffle_scraper import read_json, write_json
from shapely.ops import cascaded_union
from shapely.geometry import Point, MultiPolygon
from geovoronoi import voronoi_regions_from_coords, points_to_coords
from geovoronoi.plotting import subplot_for_map, plot_voronoi_polys_with_points_in_area
from geopandas import read_file
from pyproj import Transformer
import matplotlib.pyplot as plt

waffle_houses = read_json('waffle_houses.json')
huddle_houses = read_json('huddle_houses.json')
intl_houses = read_json('ihops.json')

locations = []
for houses, house in zip([waffle_houses, huddle_houses, intl_houses], ['WH', 'HH', 'IHOP']):
    for state in houses['states']:
        if state not in ['PR', 'AK', 'HI']:
            for location in houses['states'][state]['locations']:
                location['house'] = house
                location['state'] = state
                locations.append(location)

points = list(map(lambda x: x['coords'], locations))

# Waffle House has duplicate locations, so look for any others.
# This finds them by their identical latitude and longitude, and remembers the indices.
duplicates = [i for i, x in enumerate(points) if points.count(x) > 1]

for i in duplicates:
    print(f'duplicate: {locations[i]}')

# The duplicates may not be adjacent, so search ahead for matching duplicates to mark for deletion.
for dup_i, loc_i in enumerate(duplicates):
    if 'duplicate' not in locations[loc_i]:
        for dup_j in range(dup_i + 1, len(duplicates)):
            if locations[loc_i]['coords'] == locations[duplicates[dup_j]]['coords']:
                print(f'removing: {locations[duplicates[dup_j]]}')
                locations[duplicates[dup_j]]['duplicate'] = True

# Not sure if Python iterators remain valid after remove is called, so regenerating with filter.
locations = list(filter(lambda x: 'duplicate' not in x, locations))

points = list(map(lambda x: x['coords'], locations))

# Census TIGER
# usa = read_file('cb_2019_us_nation_5m.shp')
usa = read_file('cb_2019_us_nation_20m.shp')

# GeoPandas provides a map, how thoughtful. We lose locations on the coast with the low-res polygon, though.
# world = read_file(datasets.get_path('naturalearth_lowres'))
# usa = world[world.name == "United States of America"]

# Make sure it is in Web Mercator projection.
usa = usa.to_crs(epsg=3857)

# Need to separate the MultiPolygon into individual Polygons so we can treat the regions separately.
usa_sploded = usa.explode()

# Find the "contiguous" region, it is the biggest. The result is a named tuple.
lower48 = max(usa_sploded.itertuples(), key=lambda r: r.geometry.area)

# This is how to select it within the object that knows how to plot. This was way harder to learn than it looks.
# usa_sploded[usa_sploded.index == lower48.Index].plot()

# Convert latitude and longitude to Web Mercator projection.
to_mercator = Transformer.from_crs('epsg:4326', 'epsg:3857')
numpy_points = list(map(lambda p: Point(to_mercator.transform(p[0], p[1])), points))

# IHOP locations in the Florida Keys are causing headaches, so eliminate them, and any other troublemakers.
for i, pt in enumerate(numpy_points):
    if not(pt.within(lower48.geometry)):
        print(f'outofbounds: {locations[i]}')
        locations[i]['outofbounds'] = True

# Let's go again!
locations = list(filter(lambda x: 'outofbounds' not in x, locations))
points = list(map(lambda x: x['coords'], locations))
numpy_points = list(map(lambda p: Point(to_mercator.transform(p[0], p[1])), points))

coords = points_to_coords(numpy_points)

# A way to plot the locations individually.
# xs = [x[0] for x in coords]
# ys = [x[1] for x in coords]
# plt.scatter(xs, ys, color='red', s=0.1)
# plt.show()

# This is probably unnecessary since we selected a single polygon.
boundary_shape = cascaded_union(lower48.geometry)

# https://towardsdatascience.com/how-to-create-voronoi-regions-with-geospatial-data-in-python-adbb6c5f2134

# Where the magic happens. I first tried to implement the algorithm myself, which was voronoing.
region_polys, region_pts = voronoi_regions_from_coords(coords, boundary_shape)

# This probably won't do anything if you're not running in PyCharm or Jupyter.
fig, ax = subplot_for_map()
plot_voronoi_polys_with_points_in_area(ax, boundary_shape, region_polys, coords, region_pts)
plt.tight_layout()
plt.show()

# Go back to latitude and longitude.
to_latlong = Transformer.from_crs('epsg:3857', 'epsg:4326')

# Assign the region polygons to their location.
for region_id in region_pts:
    region_poly = region_polys[region_id]
    point_indices = region_pts[region_id]
    assert len(point_indices) == 1
    i = point_indices[0]
    # It splits some into MultiPolygons (because they cross water?), so find which has the actual location.
    if isinstance(region_poly, MultiPolygon):
        for poly in region_poly:
            if numpy_points[i].within(poly):
                region_poly = poly
                break
    locations[i]['region'] = list(map(lambda p: list(to_latlong.transform(p[0], p[1])), region_poly.exterior.coords))

write_json(locations, 'houses.json')
