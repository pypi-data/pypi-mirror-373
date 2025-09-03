from __future__ import annotations
from typing import Optional

from ..http import WSApiHttp, ApiResponse
from ..models.entities.messages.message_created import MessageCreated
from ..models.requests.messages import (
    MessageSendTextRequest,
    MessageSendImageRequest,
    MessageSendVideoRequest,
    MessageSendAudioRequest,
    MessageSendVoiceRequest,
    MessageSendStickerRequest,
    MessageSendDocumentRequest,
    MessageSendContactRequest,
    MessageSendLocationRequest,
    MessageSendLinkRequest,
    MessageSendReactionRequest,
    MessageMarkAsReadRequest,
    MessageDeleteRequest,
    MessageDeleteForMeRequest,
    MessageStarRequest,
)


class MessagesClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    # Standard methods
    def send_text(self, req: MessageSendTextRequest) -> MessageCreated:
        return self._http.send_json("POST", "messages/text", model=MessageCreated, json=req.model_dump(by_alias=True))

    def send_image(self, req: MessageSendImageRequest) -> MessageCreated:
        return self._http.send_json("POST", "messages/image", model=MessageCreated, json=req.model_dump(by_alias=True))

    def send_video(self, req: MessageSendVideoRequest) -> MessageCreated:
        return self._http.send_json("POST", "messages/video", model=MessageCreated, json=req.model_dump(by_alias=True))

    def send_audio(self, req: MessageSendAudioRequest) -> MessageCreated:
        return self._http.send_json("POST", "messages/audio", model=MessageCreated, json=req.model_dump(by_alias=True))

    def send_voice(self, req: MessageSendVoiceRequest) -> MessageCreated:
        return self._http.send_json("POST", "messages/voice", model=MessageCreated, json=req.model_dump(by_alias=True))

    def send_sticker(self, req: MessageSendStickerRequest) -> MessageCreated:
        return self._http.send_json("POST", "messages/sticker", model=MessageCreated, json=req.model_dump(by_alias=True))

    def send_document(self, req: MessageSendDocumentRequest) -> MessageCreated:
        return self._http.send_json("POST", "messages/document", model=MessageCreated, json=req.model_dump(by_alias=True))

    def send_contact(self, req: MessageSendContactRequest) -> MessageCreated:
        return self._http.send_json("POST", "messages/contact", model=MessageCreated, json=req.model_dump(by_alias=True))

    def send_location(self, req: MessageSendLocationRequest) -> MessageCreated:
        return self._http.send_json("POST", "messages/location", model=MessageCreated, json=req.model_dump(by_alias=True))

    def send_link(self, req: MessageSendLinkRequest) -> MessageCreated:
        return self._http.send_json("POST", "messages/link", model=MessageCreated, json=req.model_dump(by_alias=True))

    def send_reaction(self, message_id: str, req: MessageSendReactionRequest) -> MessageCreated:
        return self._http.send_json("POST", f"messages/{message_id}/reaction", model=MessageCreated, json=req.model_dump(by_alias=True))

    def edit_text(self, message_id: str, req: MessageSendTextRequest) -> MessageCreated:
        return self._http.send_json("PUT", f"messages/{message_id}/text", model=MessageCreated, json=req.model_dump(by_alias=True))

    def mark_as_read(self, message_id: str, req: MessageMarkAsReadRequest) -> None:
        self._http.send_json("PUT", f"messages/{message_id}/read", model=None, json=req.model_dump(by_alias=True))

    def star(self, message_id: str, req: MessageStarRequest) -> None:
        self._http.send_json("PUT", f"messages/{message_id}/star", model=None, json=req.model_dump(by_alias=True))

    def delete(self, message_id: str, req: MessageDeleteRequest) -> None:
        self._http.send_json("PUT", f"messages/{message_id}/delete", model=None, json=req.model_dump(by_alias=True))

    def delete_for_me(self, message_id: str, req: MessageDeleteForMeRequest) -> None:
        self._http.send_json("PUT", f"messages/{message_id}/delete/forme", model=None, json=req.model_dump(by_alias=True))

    # Try variants
    def try_send_text(self, req: MessageSendTextRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("POST", "messages/text", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_send_image(self, req: MessageSendImageRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("POST", "messages/image", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_send_video(self, req: MessageSendVideoRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("POST", "messages/video", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_send_audio(self, req: MessageSendAudioRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("POST", "messages/audio", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_send_voice(self, req: MessageSendVoiceRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("POST", "messages/voice", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_send_sticker(self, req: MessageSendStickerRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("POST", "messages/sticker", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_send_document(self, req: MessageSendDocumentRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("POST", "messages/document", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_send_contact(self, req: MessageSendContactRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("POST", "messages/contact", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_send_location(self, req: MessageSendLocationRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("POST", "messages/location", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_send_link(self, req: MessageSendLinkRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("POST", "messages/link", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_send_reaction(self, message_id: str, req: MessageSendReactionRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("POST", f"messages/{message_id}/reaction", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_edit_text(self, message_id: str, req: MessageSendTextRequest) -> ApiResponse[MessageCreated]:
        return self._http.try_send_json("PUT", f"messages/{message_id}/text", model=MessageCreated, json=req.model_dump(by_alias=True))

    def try_mark_as_read(self, message_id: str, req: MessageMarkAsReadRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"messages/{message_id}/read", model=None, json=req.model_dump(by_alias=True))

    def try_star(self, message_id: str, req: MessageStarRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"messages/{message_id}/star", model=None, json=req.model_dump(by_alias=True))

    def try_delete(self, message_id: str, req: MessageDeleteRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"messages/{message_id}/delete", model=None, json=req.model_dump(by_alias=True))

    def try_delete_for_me(self, message_id: str, req: MessageDeleteForMeRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"messages/{message_id}/delete/forme", model=None, json=req.model_dump(by_alias=True))
