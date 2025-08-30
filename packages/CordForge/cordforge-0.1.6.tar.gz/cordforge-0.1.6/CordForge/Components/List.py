from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: from Cord import Cord

from decimal import Decimal, InvalidOperation

from .Component import *
from .ListItem import ListItem

from ..Utilities import Format_Numeric


class List(Component):
    def __init__(_, Cord:Cord, X:int, Y:int, Parent:Component,
                 Width:int|None, Height:int|None,
                 Items:list[str], Font:CFFont, Separation:int,
                 Horizontal:bool, VerticalCenter:bool, HorizontalCenter:bool) -> None:
        super().__init__(Cord=Cord, X=X, Y=Y, Parent=Parent, Width=Width, Height=Height)
        _.Font = Font if Font is not None else Cord.Font
        _.Height = _.Cord.Height
        _.Items = Items
        _.Separation = Separation
        _.Horizontal = Horizontal
        _.VerticalCenter = VerticalCenter
        _.HorizontalCenter = HorizontalCenter


    async def Draw(_) -> PillowImage:
        _.Image = PillowImage.new("RGBA", (_.Width, _.Height), color=TRANSPRENCY)
        Drawing = ImageDraw.Draw(_.Image)
        if _.Border:
            Drawing.rectangle([0, 0, _.Width-1, _.Height-1], outline=_.BorderColor, width=_.BorderWidth)
        Y = _.YCenter - ((_.Font.Height + _.Separation) * len(_.Items) // 2) if _.VerticalCenter else _.Y
        TotalHeight = 0
        Item:ListItem
        for Item in _.Items:
            Numeric = None
            try:Numeric = await Format_Numeric(float(Decimal(Item.Text.replace(",",""))))
            except InvalidOperation: pass
            FontWidth = await _.Get_Text_Width(Numeric) if Numeric else await _.Get_Text_Width(Item.Text)
            if Item.Image:
                ImageX = _.XCenter - FontWidth//2 - Item.Image.width + Item.Separation
                _.Image.paste(im=Item.Image, box=(ImageX, Y + TotalHeight), mask=Item.Image)
            TextX = _.XCenter - FontWidth//2 + ((Item.Image.width + Item.Separation)//2 if Item.Image else 0)
            Drawing.text((TextX, Y + TotalHeight),
                            Numeric if Numeric else Item.Text,
                            font=_.Font.Font,
                            fill=WHITE)
            TotalHeight += _.Font.Height + _.Separation
        return _.Image