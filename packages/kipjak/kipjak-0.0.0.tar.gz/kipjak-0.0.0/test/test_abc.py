# test_server.py
import kipjak as kj

# A bare-bones implementation of a traditional network server that
# demonstrates the different function-calling options.

def thing(self, publish_as, subscribe_to, seconds=None):
	kj.publish(self, publish_as, scope=kj.ScopeOfDirectory.PROCESS)
	kj.subscribe(self, subscribe_to, scope=kj.ScopeOfDirectory.PROCESS)

	if seconds:
		self.start(kj.T1, seconds)

	published, i = self.select(kj.Published, saving=kj.Subscribed)	# Published...
	subscribed, i = self.select(kj.Subscribed, saving=kj.Published)

	while True:
		m = self.input()
		if not isinstance(m, (kj.Available, kj.Delivered, kj.Dropped)):
			break

	kj.clear_published(self, published)
	self.input()							# PublishedCleared

	kj.clear_subscribed(self, subscribed)
	self.input()							# SubscribedCleared

	return None

kj.bind(thing)

def abc(self, server_address: kj.HostPort=None, flooding: int=64, soaking: int=100):
	a = self.create(thing, "a", "c")
	b = self.create(thing, "b", "a", seconds=5.0)
	c = self.create(thing, "c", "b")

	self.assign(a, 0)
	self.assign(b, 1)
	self.assign(c, 2)

	m = self.input()
	while True:
		if isinstance(m, kj.Stop):
			self.abort()

		elif isinstance(m, kj.Returned):
			self.debrief()
			m = self.input()
			continue

		else:
			continue

		while self.working():
			self.input()
			self.debrief()

		return None

	return None

kj.bind(abc)	# Register with the framework.

if __name__ == '__main__':	# Process entry-point.
	kj.create(abc)
