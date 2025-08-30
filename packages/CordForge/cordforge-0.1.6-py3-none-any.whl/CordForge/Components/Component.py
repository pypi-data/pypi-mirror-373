from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: from Cord import Cord

from PIL import Image as PillowImage
from PIL import ImageDraw, ImageFont

from ..Vector2 import Vector2
from ..Colors import *
from ..Font import Font as CFFont

class Component:
    Width:int
    Height:int
    X:int
    Y:int
    Background:Color
    Color:Color
    Border:bool
    BorderColor:Color
    BorderWidth:int
    Parent:"Component"
    Children:list["Component"]
    Image:PillowImage
    Font:CFFont


    def __init__(_, Cord:Cord=None, X:int=0, Y:int=0, Parent:"Component"=None,
                 Width:int|None=0, Height:int|None=0,
                 Color:Color=None,Background:Color=GRAY, Font:CFFont=None):
        _.Cord = Cord
        if Parent:
            if Parent.Border:
                _.X = Parent.X + X + Parent.BorderWidth
                _.Y = Parent.Y + Y + Parent.BorderWidth
                _.Width = Parent.Width - Parent.BorderWidth * 2
                _.Height = Parent.Height - Parent.BorderWidth * 2
            else:
                _.X = X + Parent.X
                _.Y = Y + Parent.Y
                _.Width = Parent.Width
                _.Height = Parent.Height
        else:
            _.X = X
            _.Y = Y
            _.Width = _.Cord.Width if Width is None else Width
            _.Height = _.Cord.Height if Height is None else Height
        _.Parent = Parent
        _.Color = Color
        _.Background = Background
        _.Border = False
        _.BorderColor = WHITE
        _.BorderWidth = 1
        _.Children = []
        _.Font = _.Cord.Font if not Parent else Font
        _.ImageWidth = _.Cord.Width if not Parent else Parent.Width
        _.ImageHeight = _.Cord.Height if not Parent else Parent.Height


    @property
    def XCenter(_): return _.Width // 2
    @property
    def YCenter(_): return _.Height // 2
    @property
    def ImageCenter(_): return Vector2(_.XCenter, _.YCenter)


    async def Draw() -> PillowImage:...


    async def Construct_Components(_):
        Child:Component
        for Child in _.Children:
            ChildImage = await Child.Draw()
            _.Image.paste(ChildImage, (Child.X, Child.Y), mask=ChildImage.split()[3])


    async def Get_Text_Width(_, Text, Font=None) -> list:
        _.Font = Font if Font is not None else _.Cord.Font
        MeasuringImage = PillowImage.new("RGBA", (10, 10))
        Drawing = ImageDraw.Draw(MeasuringImage)
        return int(Drawing.textlength(Text, font=_.Font.Font))
