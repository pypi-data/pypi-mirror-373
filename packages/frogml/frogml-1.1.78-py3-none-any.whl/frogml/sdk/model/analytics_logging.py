from frogml.core.inner.singleton_meta import SingletonMeta


class FrogMLAnalyticsLogger(metaclass=SingletonMeta):
    """
    Base class for Frogml analytics logger
    """

    def log(self, log):
        """
        Log data to Frogml's data lake
        :param log: data to be persisted
        """
        pass
