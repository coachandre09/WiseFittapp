class OfflineConversionProvider:
    name = "base"

    def send(self, events):
        raise NotImplementedError


class MetaAdsProvider(OfflineConversionProvider):
    name = "meta_ads"

    def send(self, events):
        return {"provider": self.name, "status": "stub", "count": len(events)}


class GoogleAdsProvider(OfflineConversionProvider):
    name = "google_ads"

    def send(self, events):
        return {"provider": self.name, "status": "stub", "count": len(events)}


class LinkedInAdsProvider(OfflineConversionProvider):
    name = "linkedin_ads"

    def send(self, events):
        return {"provider": self.name, "status": "stub", "count": len(events)}
