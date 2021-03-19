# A predictive model for pitch selection
Individual models for each pitcher. Ganesh? used a naive model to predict Mariano Rivera's pitch selection with 92 percent accuracy. In fact, every batter who faced Rivera could have sat on cutters and it made no difference. He is still widely considered the best reliever of all time. Astros hitters commented on the lack of advantage gained by their cheating. Knowing what pitch is coming cannot tell you location (why notpredict it!) and it can not give a hitter the talent to square up a nasty pitch. seat touch

* Models
	knn
	SVM G
	Naîve (base) -most frequent pitch by count
		Improvement factor I =  A1 - A0 / A0 where A0 is acc. of naive guess and A1 is model
	LDA
	NN (last)

* Feature vector
	choose indpendent features
* Engineered
	velo. gradient (3 prior)
	Pitcher/batter priors -pitch type -wOBP -LS angle (thanks Ganesh)
		low support (history pitcher/batter): overall prior scaled for support
* Original
	Count diff (s-b)
	Handedness MATCH (not L/R) -not good
	Last pitch type & velocity
	>> this is not a classification problem therefore using post-pitch information (speed) is forbidden
	>> useful features can be identified with a linear classifier

* Feature selection
	ROC (AUC) -visualize and select classifiers; here AUC is used to compare feature against random (.5)
	Hypothesis test: significant at alpha = .01 -given f, H0 mean(FF class) == mean(non FF class)

* Metrics
	Accuracy

* CV
	k=10
	split in half
	avg. acuracy from 10 tests (prevents overfitting)