from pyspark.sql import HiveContext
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

sqlContext = HiveContext(sc)

qry = "select success_class, latitude, longitude from census_rest_success"

df = sqlContext.sql(qry)

fig = plt.figure()

mymap = Basemap(projection='gall',
                llcrnrlon = -125,              # lower-left corner longitude
                llcrnrlat = 18.5,               # lower-left corner latitude
                urcrnrlon = -62,               # upper-right corner longitude
                urcrnrlat = 49.5,               # upper-right corner latitude
                resolution='h')

mymap.drawcoastlines()
mymap.drawcountries()
mymap.drawstates()
mymap.drawmapboundary()
mymap.drawcounties()

rows = df.collect()

lon = [float(r.longitude) for r in rows]
lat = [float(r.latitude) for r in rows]

x, y = mymap(lon, lat)

mymap.plot(x, y, 'b.', alpha=0.3)

plt.savefig("../../reports/figures/restaurants_map.png", format='png')
