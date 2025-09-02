from nr_vocabularies.config import NR_VOCABULARIES_CF


class NRVocabulariesExt:
    """extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["nr-vocabularies"] = self

    def init_config(self, app):
        """Initialize configuration."""

        # we can now have the following directly in the vocabulary model,
        # but can not disable them - so at least will not load/dump them
        app.config.setdefault("DEFAULT_DATASTREAMS_EXCLUDES", []).extend(
            ["affiliations", "awards", "funders", "names", "subjects"]
        )

        app.config.setdefault("VOCABULARIES_CF", []).extend(NR_VOCABULARIES_CF)
