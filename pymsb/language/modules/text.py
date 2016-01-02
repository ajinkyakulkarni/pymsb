# TODO: add the superclass for MSB objects that will automatically convert function arguments to strings


# noinspection PyPep8Naming,PyMethodMayBeStatic
class Text:
    def Append(self, t1, t2):
        return str(t1) + str(t2)

    def ConvertToLowerCase(self, t):
        return str(t).lower()

    def ConvertToUpperCase(self, t):
        return str(t).upper()

    def EndsWith(self, t, subt):
        return str(str(t).endswith(str(subt)))

    def GetCharacter(self, code):
        return chr(int(code))

    def GetCharacterCode(self, ch):
        return str(ord(ch))

    def GetIndexOf(self, t, subt):
        ind = t.find(subt)
        if ind == -1:
            return "0"
        return ind

    def GetLength(self, t):
        return str(len(str(t)))

    def GetSubText(self, t, start, length):
        try:
            s = int(float(start)-1)
            l = int(float(length))
            if s < 0 or l < 0:  # Note: if length < 0 in MSB, program crashes
                return ""
            return str(t)[s:s+l]
        except:
            return ""

    def GetSubTextToEnd(self, t, start):
        return self.GetSubText(t, start, len(str(t)))

    def IsSubText(self, t, subt):
        return str(str(subt) in str(t))

    def StartsWith(self, t, subt):
        return str(str(subt).startswith(str(subt)))
