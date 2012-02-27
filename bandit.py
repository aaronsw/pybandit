import math, random, sys

class BanditArm:
    def __init__(self):
        self.observations = 0
        self.victories = 0
    
    def __repr__(self):
        return '<Arm: %s/%s %s,%s>' % (self.victories, self.observations, self.mean(), self.stddev())
    
    def watch(self): self.observations += 1
    def win(self): self.victories += 1
    
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
    

class Gambler:
    def __init__(self, arms):
        self.arms = arms
    
    def choose(self):
        choices = [x.guess() for x in self.arms]
        bestchoice = max(choices)
        winners = [arm for arm, choice in zip(self.arms, choices) if choice == bestchoice]
        winner = random.choice(winners)
        winner.watch()
        return winner

def test(d=1):
    # tried setting priors
    # don't do that, because you're not as smart as you think you are
    # it really throws it off if you get your priors wrong
    a = BanditArm(); a.name = 'a'; a.hidden = .02
    b = BanditArm(); b.name = 'b'; b.hidden = .03
    c = BanditArm(); c.name = 'c'; c.hidden = .00
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

def test_magics():
    global MAGIC
    def mean(l): return float(sum(l))/len(l)
    def stddev(l):
        mymean = mean(l)
        return math.sqrt(1./len(l) * sum((x-mymean)**2 for x in l))

    MAGIC = 1
    regrets = [test(d=0) for x in range(100)]
    print mean(regrets), stddev(regrets)
    MAGIC = 2
    regrets = [test(d=0) for x in range(100)]
    print mean(regrets), stddev(regrets)
    
    # seems to be pretty much a wash

test_magics()