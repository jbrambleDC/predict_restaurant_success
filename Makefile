all: restaurants reviews census_data merged zipcodes

restaurants: src/data/restaurants.hql
	beeline -u jdbc:hive2://localhost:10000 -n hadoop -p hadoop -f $<

reviews: src/data/reviews.hql
	beeline -u jdbc:hive2://localhost:10000 -n hadoop -p hadoop -f $<

census_data: src/data/census_data.hql
	beeline -u jdbc:hive2://localhost:10000 -n hadoop -p hadoop -f $<

merged: src/data/merged_tables.hql census_data reviews restaurants
	beeline -u jdbc:hive2://localhost:10000 -n hadoop -p hadoop -f $<

zipcodes: src/data/zipcode_merge.hql merged
	beeline -u jdbc:hive2://localhost:10000 -n hadoop -p hadoop -f $<

clean: src/data/drop_tables.hql
	beeline -u jdbc:hive2://localhost:10000 -n hadoop -p hadoop -f $<
