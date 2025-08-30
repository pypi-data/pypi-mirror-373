from maleo.soma.enums.request import Header, Method
from maleo.soma.types.base.string import SequenceOfStrings


DEFAULT_ALLOW_METHODS: SequenceOfStrings = (
    Method.GET.value,
    Method.POST.value,
    Method.PUT.value,
    Method.PATCH.value,
    Method.DELETE.value,
    Method.OPTIONS.value,
)

DEFAULT_ALLOW_HEADERS: SequenceOfStrings = (
    str(Header.AUTHORIZATION.value),
    Header.CONTENT_TYPE.value,
    Header.X_OPERATION_ID.value,
    Header.X_REQUEST_ID.value,
    Header.X_REQUESTED_AT.value,
    Header.X_SIGNATURE.value,
)

DEFAULT_EXPOSE_HEADERS: SequenceOfStrings = (
    Header.X_NEW_AUTHORIZATION.value,
    Header.X_OPERATION_ID.value,
    Header.X_PROCESS_TIME.value,
    Header.X_REQUEST_ID.value,
    Header.X_REQUESTED_AT.value,
    Header.X_RESPONDED_AT.value,
    Header.X_SIGNATURE.value,
)
