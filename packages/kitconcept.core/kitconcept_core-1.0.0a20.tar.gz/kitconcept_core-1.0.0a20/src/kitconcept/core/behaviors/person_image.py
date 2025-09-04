from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.volto import _
from zope.interface import provider


@provider(IFormFieldProvider)
class IPersonImage(model.Schema):
    image = namedfile.NamedBlobImage(
        title=_("label_person_image", default="Profile Picture/Portrait"),
        description=_(
            "help_person_image",
            default="Use a normal portrait image with your face centered.",
        ),
        required=False,
    )
