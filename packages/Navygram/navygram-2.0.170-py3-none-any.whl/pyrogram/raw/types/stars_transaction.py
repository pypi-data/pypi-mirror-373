#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject
from pyrogram import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class StarsTransaction(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.StarsTransaction`.

    Details:
        - Layer: ``182``
        - ID: ``AA00C898``

    Parameters:
        id (``str``):
            N/A

        stars (``int`` ``64-bit``):
            N/A

        date (``int`` ``32-bit``):
            N/A

        peer (:obj:`StarsTransactionPeer <pyrogram.raw.base.StarsTransactionPeer>`):
            N/A

        refund (``bool``, *optional*):
            N/A

        pending (``bool``, *optional*):
            N/A

        failed (``bool``, *optional*):
            N/A

        title (``str``, *optional*):
            N/A

        description (``str``, *optional*):
            N/A

        photo (:obj:`WebDocument <pyrogram.raw.base.WebDocument>`, *optional*):
            N/A

        transaction_date (``int`` ``32-bit``, *optional*):
            N/A

        transaction_url (``str``, *optional*):
            N/A

    """

    __slots__: List[str] = ["id", "stars", "date", "peer", "refund", "pending", "failed", "title", "description", "photo", "transaction_date", "transaction_url"]

    ID = 0xaa00c898
    QUALNAME = "types.StarsTransaction"

    def __init__(self, *, id: str, stars: int, date: int, peer: "raw.base.StarsTransactionPeer", refund: Optional[bool] = None, pending: Optional[bool] = None, failed: Optional[bool] = None, title: Optional[str] = None, description: Optional[str] = None, photo: "raw.base.WebDocument" = None, transaction_date: Optional[int] = None, transaction_url: Optional[str] = None) -> None:
        self.id = id  # string
        self.stars = stars  # long
        self.date = date  # int
        self.peer = peer  # StarsTransactionPeer
        self.refund = refund  # flags.3?true
        self.pending = pending  # flags.4?true
        self.failed = failed  # flags.6?true
        self.title = title  # flags.0?string
        self.description = description  # flags.1?string
        self.photo = photo  # flags.2?WebDocument
        self.transaction_date = transaction_date  # flags.5?int
        self.transaction_url = transaction_url  # flags.5?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StarsTransaction":
        
        flags = Int.read(b)
        
        refund = True if flags & (1 << 3) else False
        pending = True if flags & (1 << 4) else False
        failed = True if flags & (1 << 6) else False
        id = String.read(b)
        
        stars = Long.read(b)
        
        date = Int.read(b)
        
        peer = TLObject.read(b)
        
        title = String.read(b) if flags & (1 << 0) else None
        description = String.read(b) if flags & (1 << 1) else None
        photo = TLObject.read(b) if flags & (1 << 2) else None
        
        transaction_date = Int.read(b) if flags & (1 << 5) else None
        transaction_url = String.read(b) if flags & (1 << 5) else None
        return StarsTransaction(id=id, stars=stars, date=date, peer=peer, refund=refund, pending=pending, failed=failed, title=title, description=description, photo=photo, transaction_date=transaction_date, transaction_url=transaction_url)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 3) if self.refund else 0
        flags |= (1 << 4) if self.pending else 0
        flags |= (1 << 6) if self.failed else 0
        flags |= (1 << 0) if self.title is not None else 0
        flags |= (1 << 1) if self.description is not None else 0
        flags |= (1 << 2) if self.photo is not None else 0
        flags |= (1 << 5) if self.transaction_date is not None else 0
        flags |= (1 << 5) if self.transaction_url is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.id))
        
        b.write(Long(self.stars))
        
        b.write(Int(self.date))
        
        b.write(self.peer.write())
        
        if self.title is not None:
            b.write(String(self.title))
        
        if self.description is not None:
            b.write(String(self.description))
        
        if self.photo is not None:
            b.write(self.photo.write())
        
        if self.transaction_date is not None:
            b.write(Int(self.transaction_date))
        
        if self.transaction_url is not None:
            b.write(String(self.transaction_url))
        
        return b.getvalue()
