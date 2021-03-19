library(Metrics)

nola = read.csv("Nola_binomial.csv")
index = 1:9924 #start of game
train = nola[index,]
test = nola[-index,]

#Drop some stuff
colnames(train)

train <- subset(train, select=-c(3,5,6,8,12,16,17,18,20,24))
test <- subset(test, select=-c(3,5,6,8,12,16,17,18,20,24))
colnames(train)
set.seed(36)

#Modeling is an academic exercise in this case.
#No batter could possibly have this information.
#They could use insights based on EDA however.
#baseline - 53%
base.preds = rep(0, length(train$pitch_type))
sum(train$pitch_type)
sum(train$pitch_type)/length(train$pitch_type)
accuracy(base.preds,train$pitch_type)
table(base.preds,train$pitch_type)

#glm - 58%
#Maybe these models are struggling because strategy
#changes over time. If Nola uses fastballs one year, 
#and curves the next because he learned something
#averaging all strategies will make the predictow worse
#smaller datasets may help 
glm.fit = glm(train$pitch_type~., data=train, family='binomial')
summary(glm.fit)
alias(glm.fit)
glm.probs = predict(glm.fit, train, type='response')
#glm.probs
glm.pred = rep(0, length(train$pitch_type))
glm.pred[glm.probs > .45] = TRUE
#glm.pred - 58% accuracy
table(glm.pred,train$pitch_type)
accuracy(glm.pred,train$pitch_type)
recall(glm.pred,train$pitch_type)
precision(glm.pred,train$pitch_type)
auc(glm.pred,train$pitch_type)

#knn - 53%
library(class)
colnames(train)
train <- subset(train, select=-c(3,5,6,9,11,21))
test <- subset(test, select=-c(3,5,6,9,11,21))
colnames(train)

train.X = model.matrix(train$pitch_type~., train)[,-1]
test.X = model.matrix(test$pitch_type~., test)[,-1]
train.X.scale = scale(train.X)
test.X.scale = scale(test.X)
train.y = train$pitch_type
test.y = test$pitch_type

knn.pred5 = knn(train.X.scale, test.X.scale, train.y, k=5)
mean(test.y == knn.pred5)
mean(test.y == 1)
table(knn.pred5, test.y)
accuracy(test.y, knn.pred5)

#Bagging and Random Forests
library(randomForest)
bag.train = randomForest(train.X, as.factor(train.y),
                         ntree=500, mtry=5, importance=TRUE, do.trace=50)
bag.train
yhat.bag = predict(bag.train, newdata=test.X)
table(yhat.bag, test.y)
accuracy(test.y, yhat.bag)
auc(test.y, yhat.bag)

#Precision = TP / (TP + FP)
5458/(5458+1379)
#Recall = TP / (TP + FN)
5458/(5458+867)

importance(bag.train)
varImpPlot(bag.train)
