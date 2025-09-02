from heapq import heappush, heappop

from time import monotonic


class TimeQueue:
    OOB = -(10**6)
    NOW = -(10**3)

    def __init__(self):
        self.near = []

    def push(self, item, expires=0):
        if isinstance(expires, (int, float)):
            now = monotonic()
            when = now + expires
        else:
            when = 0
        heappush(self.near, (when, item))

    def qsize(self):
        return len(self.near)

    def deadline(self):
        if self.near:
            return self.near[0][0] - monotonic()

    def pop(self):
        return heappop(self.near)
