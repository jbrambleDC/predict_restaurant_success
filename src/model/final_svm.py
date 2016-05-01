from pyspark.sql import HiveContext

from pyspark.mllib.classification import SVMWithSGD, SVMModel, LogisticRegressionWithSGD

from pyspark.mllib.regression import LabeledPoint
from pyspark.sql.functions import col, sum

from pyspark.mllib.evaluation import BinaryClassificationMetrics
from pyspark.mllib.evaluation import MulticlassMetrics

from copy import deepcopy

sc = SparkContext()
sqlContext = HiveContext(sc)
qry = """SELECT if(AVG(success_metric)>0.11864548120240495,1,0) as success_class,
         2016_02, zipcode
         from census_rest_success
         group by zipcode, 2016_02"""

df = sqlContext.sql(qry)

## Lets train a Support Vector Classifier on this data
#CITATION:
#http://stackoverflow.com/questions/33900726/count-number-of-non-nan-entries-in-each-column-of-spark-dataframe-with-pyspark
def count_not_null(c):
    return sum(col(c).isNotNull().cast("integer")).alias(c)

exprs = [count_not_null(c) for c in df.columns]
df.agg(*exprs).show()

df = df.dropna()

features = df.select(df['success_class'], df['2016_02'])

training, test = features.randomSplit([0.7, 0.3], seed=11L)

feats_train = training.collect()
train_dict = [i.asDict() for i in feats_train]

feats_test = test.collect()
test_dict = [i.asDict() for i in feats_test]

def parsePoint(d):
    d_copy = deepcopy(d) # I hate using deepcopy so much
    pred = d_copy['success_class']
    d.pop('success_class', None)
    values = [float(x) for x in d.values()]
    return LabeledPoint(pred, map(float,values))

trainParsed = sc.parallelize(map(parsePoint, train_dict))
testParsed = sc.parallelize(map(parsePoint, test_dict))

model = SVMWithSGD.train(trainParsed, iterations=100)

# Training Error
trainLabelsAndPreds = trainParsed.map(lambda p: (p.label, float(model.predict(p.features))))
trainErr = trainLabelsAndPreds.filter(lambda (v, p): v != p).count()/float(trainParsed.count())
print trainErr

# Test Error
testLabelsAndPreds = testParsed.map(lambda p: (p.label, float(model.predict(p.features))))
testErr = testLabelsAndPreds.filter(lambda (v, p): v != p).count()/float(testParsed.count())
print testErr

metrics = BinaryClassificationMetrics(testLabelsAndPreds)

print metrics.areaUnderROC
print metrics.areaUnderPR

mcMetrics = MulticlassMetrics(testLabelsAndPreds)

#TODO: Do this for classes 1.0,0.0 and not just overall
print mcMetrics.precision()
print mcMetrics.recall()
print mcMetrics.fMeasure()

model.save(sc, "SVMModel")

