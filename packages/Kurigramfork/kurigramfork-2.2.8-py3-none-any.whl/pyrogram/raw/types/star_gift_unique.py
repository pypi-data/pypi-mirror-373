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


class StarGiftUnique(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.StarGift`.

    Details:
        - Layer: ``211``
        - ID: ``3A274D50``

    Parameters:
        id (``int`` ``64-bit``):
            N/A

        title (``str``):
            N/A

        slug (``str``):
            N/A

        num (``int`` ``32-bit``):
            N/A

        attributes (List of :obj:`StarGiftAttribute <pyrogram.raw.base.StarGiftAttribute>`):
            N/A

        availability_issued (``int`` ``32-bit``):
            N/A

        availability_total (``int`` ``32-bit``):
            N/A

        require_premium (``bool``, *optional*):
            N/A

        resale_ton_only (``bool``, *optional*):
            N/A

        owner_id (:obj:`Peer <pyrogram.raw.base.Peer>`, *optional*):
            N/A

        owner_name (``str``, *optional*):
            N/A

        owner_address (``str``, *optional*):
            N/A

        gift_address (``str``, *optional*):
            N/A

        resell_amount (List of :obj:`StarsAmount <pyrogram.raw.base.StarsAmount>`, *optional*):
            N/A

        released_by (:obj:`Peer <pyrogram.raw.base.Peer>`, *optional*):
            N/A

    """

    __slots__: List[str] = ["id", "title", "slug", "num", "attributes", "availability_issued", "availability_total", "require_premium", "resale_ton_only", "owner_id", "owner_name", "owner_address", "gift_address", "resell_amount", "released_by"]

    ID = 0x3a274d50
    QUALNAME = "types.StarGiftUnique"

    def __init__(self, *, id: int, title: str, slug: str, num: int, attributes: List["raw.base.StarGiftAttribute"], availability_issued: int, availability_total: int, require_premium: Optional[bool] = None, resale_ton_only: Optional[bool] = None, owner_id: "raw.base.Peer" = None, owner_name: Optional[str] = None, owner_address: Optional[str] = None, gift_address: Optional[str] = None, resell_amount: Optional[List["raw.base.StarsAmount"]] = None, released_by: "raw.base.Peer" = None) -> None:
        self.id = id  # long
        self.title = title  # string
        self.slug = slug  # string
        self.num = num  # int
        self.attributes = attributes  # Vector<StarGiftAttribute>
        self.availability_issued = availability_issued  # int
        self.availability_total = availability_total  # int
        self.require_premium = require_premium  # flags.6?true
        self.resale_ton_only = resale_ton_only  # flags.7?true
        self.owner_id = owner_id  # flags.0?Peer
        self.owner_name = owner_name  # flags.1?string
        self.owner_address = owner_address  # flags.2?string
        self.gift_address = gift_address  # flags.3?string
        self.resell_amount = resell_amount  # flags.4?Vector<StarsAmount>
        self.released_by = released_by  # flags.5?Peer

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StarGiftUnique":
        
        flags = Int.read(b)
        
        require_premium = True if flags & (1 << 6) else False
        resale_ton_only = True if flags & (1 << 7) else False
        id = Long.read(b)
        
        title = String.read(b)
        
        slug = String.read(b)
        
        num = Int.read(b)
        
        owner_id = TLObject.read(b) if flags & (1 << 0) else None
        
        owner_name = String.read(b) if flags & (1 << 1) else None
        owner_address = String.read(b) if flags & (1 << 2) else None
        attributes = TLObject.read(b)
        
        availability_issued = Int.read(b)
        
        availability_total = Int.read(b)
        
        gift_address = String.read(b) if flags & (1 << 3) else None
        resell_amount = TLObject.read(b) if flags & (1 << 4) else []
        
        released_by = TLObject.read(b) if flags & (1 << 5) else None
        
        return StarGiftUnique(id=id, title=title, slug=slug, num=num, attributes=attributes, availability_issued=availability_issued, availability_total=availability_total, require_premium=require_premium, resale_ton_only=resale_ton_only, owner_id=owner_id, owner_name=owner_name, owner_address=owner_address, gift_address=gift_address, resell_amount=resell_amount, released_by=released_by)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 6) if self.require_premium else 0
        flags |= (1 << 7) if self.resale_ton_only else 0
        flags |= (1 << 0) if self.owner_id is not None else 0
        flags |= (1 << 1) if self.owner_name is not None else 0
        flags |= (1 << 2) if self.owner_address is not None else 0
        flags |= (1 << 3) if self.gift_address is not None else 0
        flags |= (1 << 4) if self.resell_amount else 0
        flags |= (1 << 5) if self.released_by is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.id))
        
        b.write(String(self.title))
        
        b.write(String(self.slug))
        
        b.write(Int(self.num))
        
        if self.owner_id is not None:
            b.write(self.owner_id.write())
        
        if self.owner_name is not None:
            b.write(String(self.owner_name))
        
        if self.owner_address is not None:
            b.write(String(self.owner_address))
        
        b.write(Vector(self.attributes))
        
        b.write(Int(self.availability_issued))
        
        b.write(Int(self.availability_total))
        
        if self.gift_address is not None:
            b.write(String(self.gift_address))
        
        if self.resell_amount is not None:
            b.write(Vector(self.resell_amount))
        
        if self.released_by is not None:
            b.write(self.released_by.write())
        
        return b.getvalue()
