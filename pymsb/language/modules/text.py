# noinspection PyPep8Naming,PyMethodMayBeStatic
class Text:
    def Append(self, t1, t2):
        return t1 + t2

    def ConvertToLowerCase(self, t):
        return t.lower()

    def ConvertToUpperCase(self, t):
        return t.upper()

    def EndsWith(self, t, subt):
        return str(t.endswith(subt))

    def GetCharacter(self, code):
        try:
            return chr(int(code))
        except:
            return chr(0)

    def GetCharacterCode(self, ch):
        if not ch:
            return "0"
        return str(ord(ch[0]))

    def GetIndexOf(self, t, subt):
        ind = t.find(subt)
        if ind == -1:
            return "0"
        return str(ind)

    def GetLength(self, t):
        return str(len(t))

    def GetSubText(self, t, start, length):
        try:
            s = int(float(start)-1)
            l = int(float(length))
            if s < 0 or l < 0:  # Note: if length < 0 in MSB, program crashes
                return ""
            return t[s:s+l]
        except:
            return ""

    def GetSubTextToEnd(self, t, start):
        return self.GetSubText(t, start, len(t))

    def IsSubText(self, t, subt):
        return str(subt in t)

    def StartsWith(self, t, subt):
        return str(subt.startswith(subt))
