from typing import Literal

class GroupInterface:
    @staticmethod
    def getPS(text: str) -> tuple[str, Literal[4]]:
        if len(text) > 8: text = text[:8]
        return text.ljust(8), 4
    @staticmethod
    def getRT(text: str,full:bool=False) -> tuple[None, None] | tuple[str, int] | tuple[str, Literal[16]]:
        if len(text) >= 64: text = text[:64]
        elif not full: text += "\r"
        if not full:
            while len(text) % 4:
                text = text + " "
            segments = 0.0
            for _ in range(len(text)):
                segments = segments + 0.25
            if not float(segments).is_integer(): raise Exception("Segment error (segment is not int)")
            if int(segments) > 16: return None, None
            return text, int(segments)
        else:
            return text.ljust(64), 16
    @staticmethod
    def getLongPS(text: str,full:bool=False) -> tuple[None, None] | tuple[str, int] | tuple[str, Literal[8]]:
        if len(text) >= 32: text = text[:32]
        elif not full: text += "\r"
        if not full:
            while len(text) % 4:
                text = text + " "
            segments = 0.0
            for _ in range(len(text)):
                segments = segments + 0.25
            if not float(segments).is_integer(): raise Exception("Segment error (segment is not int)")
            if int(segments) > 8: return None, None
            return text, int(segments)
        else:
            return text.ljust(32), 8
    @staticmethod
    def getPTYN(text: str) -> tuple[str, Literal[2]]:
        if len(text) > 8: text = text[:8]
        return text.ljust(8), 2