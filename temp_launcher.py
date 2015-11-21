from pymsb.language.interpreter import Interpreter

__author__ = 'Simon Tang'

if __name__ == "__main__":
    window_and_cursor_test = """
    TextWindow.WriteLine("The graphics window coordinates: (" + GraphicsWindow.Left + ", " + GraphicsWindow.Top + ", " + GraphicsWindow.Width + ", " + GraphicsWindow.Height + ")")
    GraphicsWindow.Show()
    TextWindow.WriteLine("The graphics window coordinates: (" + GraphicsWindow.Left + ", " + GraphicsWindow.Top + ", " + GraphicsWindow.Width + ", " + GraphicsWindow.Height + ")")
    'TextWindow.Clear()
    GraphicsWindow.Width = GraphicsWindow.Width * 2
    GraphicsWindow.Height = GraphicsWindow.Height * 2
    TextWindow.Top = TextWindow.Top + 200
    GraphicsWindow.Left = TextWindow.Left
    GraphicsWindow.Top = TextWindow.Top - GraphicsWindow.Height - 50
    TextWindow.WriteLine("The graphics window coordinates: (" + GraphicsWindow.Left + ", " + GraphicsWindow.Top + ", " + GraphicsWindow.Width + ", " + GraphicsWindow.Height + ")")
    TextWindow.WriteLine("The cursor position: " + TextWindow.CursorTop + "," + TextWindow.CursorLeft)
    TextWindow.CursorTop = 0
    TextWindow.WriteLine("The cursor position: " + TextWindow.CursorTop + "," + TextWindow.CursorLeft)
    TextWindow.Writeline("bam")
    TextWindow.WriteLine("The cursor position: " + TextWindow.CursorTop + "," + TextWindow.CursorLeft)
    """

    sub_input_if_test = """
    TextWindow.Title = "Go to http://smallbasic.com/"
    TextWindow.WriteLine("Beginning")
    Sub helloworld
      TextWindow.WriteLine("Hello world!")
      sayGoodbye()
    EndSub
    TextWindow.WriteLine("Nice to meet you!")
    helloworld()
    TextWindow.WriteLine("cool!")
    sub saygoodbYE
      TextWindow.WriteLine("Goodbye world!")
    endsub

    TextWindow.WriteLine("What's your name?")
    TextWindow.WriteLine("Oh hello, " + TextWindow.Read() + ".")
    TextWindow.Write("How old are you? ")
    age = TextWindow.readnumber()
    if age > 10 Then
      TextWindow.writeline("Wow!  You're already in the double igits!")
    elSEIf age < 10 Then
      if age < 0 then
        TextWindow.WriteLine("You seem... awfully young.")
      elseif age <> 0 then
          TextWindow.writeLine("Wow, you're only in the single digits!")
      else
        TextWindow.WriteLine("you're 0?")
      endif
    elseif age <> 10 Then
      TextWindow.WriteLine("This code shouldn't be able to execute.")
    else
      textwindow.writeline("you're 10 years old exactly, cool")
    endif
    Textwindow.writELINe("So you'll be " + (age + 1) + " years old a year from now, congratulations.")

    TextWindow.WriteLine("custom pause inserted here: ")
    TextWindow.PauseWithoutmESSAGE()
    TextWindow.BackgroundColor = "green"
    TextWindow.ForegroundColor = "black"
    TextWindow.WriteLine("Goodbye world!")
    TextWindow.Backgroundcolor = "black"
    TextWindow.foregroundcolor = "gray"
    """

    interpreter = Interpreter()
    # interpreter.run(window_and_cursor_test)
    interpreter.run(sub_input_if_test)