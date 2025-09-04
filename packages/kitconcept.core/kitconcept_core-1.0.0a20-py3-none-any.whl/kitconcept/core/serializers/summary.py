from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from zope.interface import implementer


@implementer(IJSONSummarySerializerMetadata)
class JSONSummarySerializerMetadata:
    """Additional metadata to be exposed on listings."""

    def default_metadata_fields(self):
        return {
            "image_field",
            "image_scales",
            "effective",
            "Subject",
            "contact_email",
            "contact_room",
            "contact_phone",
            "contact_building",
        }
