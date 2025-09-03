from .message_send_text_request import MessageSendTextRequest
from .message_send_image_request import MessageSendImageRequest
from .message_send_video_request import MessageSendVideoRequest
from .message_send_audio_request import MessageSendAudioRequest
from .message_send_voice_request import MessageSendVoiceRequest
from .message_send_sticker_request import MessageSendStickerRequest
from .message_send_document_request import MessageSendDocumentRequest
from .message_send_contact_request import MessageSendContactRequest
from .message_send_location_request import MessageSendLocationRequest
from .message_send_link_request import MessageSendLinkRequest
from .message_send_reaction_request import MessageSendReactionRequest
from .message_mark_as_read_request import MessageMarkAsReadRequest
from .message_delete_request import MessageDeleteRequest
from .message_delete_for_me_request import MessageDeleteForMeRequest
from .message_star_request import MessageStarRequest

__all__ = [
    "MessageSendTextRequest",
    "MessageSendImageRequest",
    "MessageSendVideoRequest",
    "MessageSendAudioRequest",
    "MessageSendVoiceRequest",
    "MessageSendStickerRequest",
    "MessageSendDocumentRequest",
    "MessageSendContactRequest",
    "MessageSendLocationRequest",
    "MessageSendLinkRequest",
    "MessageSendReactionRequest",
    "MessageMarkAsReadRequest",
    "MessageDeleteRequest",
    "MessageDeleteForMeRequest",
    "MessageStarRequest",
]
