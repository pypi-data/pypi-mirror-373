""" Extensions module for conversion into Context """
import uuid
from Client.model.api.context.context import Context
from Client.model.api.context.evidence import Evidence


def to_context(*, dictionary: dict, context_guid: uuid.UUID = None) -> Context:
    """Convert dependences of instance into context relates

    Args:
        dictionary (dict): Dependencies to convert
        context_guid (uuid.UUID, optional): Id to assign to dependency. Defaults to None.

    Returns:
        Context: Dependeny context object
    """
    context: Context = Context()
    context.evidences = list()

    if context_guid is not None:
        context.guid = context_guid

    for key, value in dictionary.items():
        context.evidences.append(Evidence(name=key, value=value))

    return context
