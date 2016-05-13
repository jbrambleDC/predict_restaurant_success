from pyspark.sql import HiveContext
from pyspark.mllib.regression import LabeledPoint, LinearModel, LinearRegressionWithSGD, LassoWithSGD
from pyspark.ml.regression import LinearRegression
from pyspark.sql.functions import col, sum
from copy import deepcopy
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.evaluation import RegressionMetrics

sc = SparkContext()
sqlContext = HiveContext(sc)
# The races from the census data were normalized in order
qry = """SELECT AVG(success_metric) as success_metric,
         hispanic/population as hispanic_percentage, zipcode
         from census_rest_success where array_contains(categories, 'Mexican')
         group by hispanic, population, zipcode"""

df = sqlContext.sql(qry)
#CITATION:
#http://stackoverflow.com/questions/33900726/count-number-of-non-nan-entries-in-each-column-of-spark-dataframe-with-pyspark
def count_not_null(c):
    return sum(col(c).isNotNull().cast("integer")).alias(c)

exprs = [count_not_null(c) for c in df.columns]
df.agg(*exprs).show()

df = df.dropna()


features = df.select(df['success_metric'], df['hispanic_percentage'])

training, test = features.randomSplit([0.7, 0.3], seed=11L)

feats_train = training.collect()
train_dict = [i.asDict() for i in feats_train]

feats_test = test.collect()
test_dict = [i.asDict() for i in feats_test]

def parsePoint(d): ## wont be able to use line.split here?
    d_copy = deepcopy(d) # I hate using deepcopy so much
    pred = d_copy['success_metric']
    d.pop('success_metric', None)
    values = [float(x) for x in d.values()] ##this block is unusable until we have our Hive Data
    return (pred, Vectors.dense(values))

# training set
trainParsed = sc.parallelize(map(parsePoint, train_dict))
# test set
testParsed = sc.parallelize(map(parsePoint, test_dict))

trainDf = sqlContext.createDataFrame(trainParsed, ["label", "features"])
testDf = sqlContext.createDataFrame(testParsed, ["label", "features"])
lm_model = LinearRegression(featuresCol="features", predictionCol="prediction", maxIter=100, regParam=0.0, elasticNetParam=0.0, tol=1e-6)
lm_model_fit = lm_model.fit(trainDf)
lm_transform = lm_model_fit.transform(trainDf)
results = lm_transform.select(lm_transform['prediction'], lm_transform['label'])
MSE = results.map(lambda (p,l):(p-l)**2).reduce(lambda x,y:x+y)/results.count()
print("Linear Regression training Mean Squared Error = " + str(MSE))

lm_transform = lm_model_fit.transform(testDf)
results = lm_transform.select(lm_transform['prediction'], lm_transform['label'])
MSE = results.map(lambda (p,l):(p-l)**2).reduce(lambda x,y:x+y)/results.count()
print("Linear Regression testing Mean Squared Error = " + str(MSE))

res = results.collect()
predsAndLabels = sc.parallelize([i.asDict().values() for i in res])
metrics = RegressionMetrics(predsAndLabels)


print metrics.meanSquaredError
print metrics.rootMeanSquaredError
print metrics.r2
print metrics.explainedVariance

lm_model.save(sc, "LinerRegressionModel")



# LASSO

lasso_model = LinearRegression(featuresCol="features", predictionCol="prediction", maxIter=100, regParam=1.0, elasticNetParam=0.0, tol=1e-6)
lasso_model_fit = lasso_model.fit(trainDf)
lasso_transform = lasso_model_fit.transform(trainDf) #change to a test model
lasso_results = lasso_transform.select(lasso_transform['prediction'], lasso_transform['label'])
lasso_MSE = lasso_results.map(lambda (p,l):(p-l)**2).reduce(lambda x,y:x+y)/results.count()
print("LASSO training Mean Squared Error = " + str(lasso_MSE))

lasso_transform = lasso_model_fit.transform(testDf) #change to a test model
lasso_results = lasso_transform.select(lasso_transform['prediction'], lasso_transform['label'])
lasso_MSE = lasso_results.map(lambda (p,l):(p-l)**2).reduce(lambda x,y:x+y)/results.count()
print("LASSO testing Mean Squared Error = " + str(lasso_MSE))

model.save(sc, "LASSOModel")
