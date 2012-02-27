# Bandit Algorithms

	import math, random, sys

Imagine you have four banner ads and you're trying to decide which one to serve. Naturally, your goal is to maximize click-through rate, but you have no idea which ad will perform best. What do you do?

	# In the literature, this is called the multi-armed bandit problem.
	# We imagine the public as a slot machine (one-armed bandit) with
	# multiple arms. Pull an arm and it randomly returns a reward (e.g. 
	# a click). Thus, we'll call our ads BanditArms.
	
	class BanditArm:
	    def __init__(self):
	        self.observations = 0
	        self.victories = 0
    	
		# e.g. showing an ad:
		def watch(self): self.observations += 1
		
		# e.g. a click:
		def win(self): self.victories += 1
	
	# And we'll call the person who picks an arm, the gambler:
	
	class Gambler:
	    def __init__(self, arms):
	        self.arms = arms

Obviously, you should start out by serving them all a quarter of the time. That way you can see which ones get clicked on and determine which is best.
	
	class Gambler:
		...
		def choose(self):
			winner = random.choice(self.arms)
			winner.watch()
			return winner

Now the traditional thing to do next is to keep serving them all equally until you think you know which one is best and then just serve that one. But that has two problems: First, what if you're wrong about which is best? Then you'll end up serving the wrong ad indefinitely. Second, aren't you wasting most of the time when you're pretty sure A is best but you're still serving B, C, and D a majority of the time?

Clearly what we want is a more gently sloping function that gradually shows the one it thinks is the winner more and more as it gets more and more confident. Obviously when it thinks all of them are equally likely to be the best, it should show all of them equally. And when it's 100% sure that A is the winner, it should show A 100% of the time. 

Now while I don't have a proof for it, it seems intuitively right that we just continue this linearly. So if it looks like A has a 10% chance of being the best, you show it 10% of the time.

How do we calculate the probability of A being the best? Well, we don't actually need to. Instead, we can simply select randomly from the probability distribution for A's click-through rate. 

	class Gambler:
		...
		def choose(self):
	        choices = [x.guess() for x in self.arms]
	        winners = [arm for arm, choice in zip(self.arms, choices) 
			  if choice == max(choices)]
	        winner = random.choice(winners)
	        winner.watch()
	        return winner

In the case of our samples of ads, we can just pick from a normal distribution of potential click-through rates. We have our point estimate (the click-through rate up until now) and our confidence (the standard error).

	class BanditArm:
		...
	    def mean(self):
	        return float(self.victories)/(self.observations or 1)
    
	    def stddev(self):
	        # standard error of the mean
	        out = (self.victories * (1-self.mean())**2)
	        out += ((self.observations - self.victories) * (0 - self.mean())**2)
	        out = math.sqrt(out * 1./((self.observations-1) or 1))
	        return (out or 1) / math.sqrt(self.observations or 1)
    
	    def guess(self):
	        return random.normalvariate(self.mean(), self.stddev())
		
	    def __repr__(self):
	        return '<Arm: %s/%s %s,%s>' % (self.victories, self.observations, 
				self.mean(), self.stddev())

And we're done! The result is an algorithm that learns remarkably quickly (it was able to suss out the difference between a CTR of .02 and .03 in several hundred trials), while smoothly adapting and always leaving open the possibility it's wrong.

	def test(d=1):
	    a = BanditArm(); a.name = 'a'; a.hidden = .02
	    b = BanditArm(); b.name = 'b'; b.hidden = .03
	    c = BanditArm(); c.name = 'c'; c.hidden = .01
	    arms = [a, b, c]

	    g = Gambler(arms)

	    for i in xrange(1000):
	        arm = g.choose()
	        if random.random() < arm.hidden: arm.win()
	        if d: sys.stdout.write(arm.name)
    
	    if d:
	        print
	        for arm in arms:
	            print arm
    
	    regret = 0
	    for arm in arms:
	        regret += arm.hidden - arm.mean()
	    return regret

Up to now we've been assuming that all people are alike, but what if you want to target the ads? Perhaps you think some ads will do better with people in the US and others with people in the UK.

Well, if you have an learning oracle that guesses the probability a person will like an ad given their country, you just need the oracle to return its probability estimate and its confidence and then use that as the input into the probability distribution instead of the raw click-through rate.

	class ContextualBanditArm(BanditArm):
		...
		def guess(self):
			return random.normalvariate(
			  self.oracle.probability(), self.oracle.confidence())
