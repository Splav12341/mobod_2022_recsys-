from .random import Random
from .recommender import Recommender
import random
from .top_pop import TopPop


from collections import defaultdict

class MyContextual(Recommender):
    """
    Recommend tracks closest to the previous one.
    Fall back to the random recommender if no
    recommendations found for the track.
    """

    def __init__(self, tracks_redis, catalog):
        self.tracks_redis = tracks_redis
        self.top_pop = TopPop(tracks_redis, catalog.top_tracks[:100])
        self.fallback = Random(tracks_redis)
        self.catalog = catalog
        self.recommended = defaultdict(list)

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            self.recommended[user]=[]
            next_track = self.top_pop.recommend_next(user, prev_track, prev_track_time)
            self.recommended[user].append(next_track)
            return next_track

        if prev_track_time > 0.65:
            previous_track = self.catalog.from_bytes(previous_track)
            recommendations = previous_track.recommendations
            if not recommendations:
                for i in range(100):
                    try_next_track = self.top_pop.recommend_next(user, prev_track, prev_track_time)
                    if try_next_track not in self.recommended[user]:
                        self.recommended[user].append(try_next_track)
                        return try_next_track
                return self.fallback.recommend_next(user, prev_track, prev_track_time)

            shuffled = list(recommendations)
            random.shuffle(shuffled)
            return shuffled[0]

        else:
            for i in range(100):
                try_next_track = self.top_pop.recommend_next(user, prev_track, prev_track_time)
                if try_next_track not in self.recommended[user]:
                    self.recommended[user].append(try_next_track)
                    return try_next_track
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
