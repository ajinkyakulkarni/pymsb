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

    for_test = """
    for i = 1 to 10
      TextWindow.WriteLine("i = " + i)
    endfor
    textwindow.writeline("-------------------")
    for i = 1 to 1
      TextWindow.WriteLine("i = " + i)
    endfor
    textwindow.writeline("-------------------")
    for i = 10 to 1
      TextWindow.WriteLine("this should not be printed.")
    endfor

    for i = "" to "a"
      textwindow.writeline("apparently this should print once and exit.")
    endfor

    ' This kills the PyMSB
    for i = "a" to "a11"  ' NOTE: this shouldn't allow the loop to exit
      Textwindow.writeLINE("i: " + i)
      textwindow.writeline("continue?")
      textwindow.pausewithoutmessage()  ' for sanity
    endfor
    """

    while_test = """
    Textwindow.writeline("Keep writing 'okay' please.")
    while TextWindow.Read() = "okay"
        TextWindow.WriteLine("Yay")
    endwhile
    """

    goto_and_sub_test = """
    ' I know this is a disgusting language feature
    Sub sayhi
      TextWindow.WriteLine("Hello world!")
    endsub
    start:
    sayhi()
    counter = 1
    five_factorial = 1
    loop:
    if counter <= 5 then
      five_factorial = five_factorial * counter
      counter = counter + 1
      goto loop
    endif
    goto end
    TextWindow.WriteLine("shouldn't print this line")
    end:
    TextWindow.WriteLine("5! = " + five_factorial)
    sayhi()
    TextWindow.WriteLine("All done!")
    """

    clock_test = """
    TextWindow.WriteLine(Clock.Date)
    TextWindow.WriteLine(Clock.Day)
    TextWindow.WriteLine(Clock.ElapsedMilliseconds)
    TextWindow.WriteLine(Clock.Hour)
    TextWindow.WriteLine(Clock.Millisecond)
    TextWindow.WriteLine(Clock.Minute)
    TextWindow.WriteLine(Clock.Month)
    TextWindow.WriteLine(Clock.Second)
    TextWindow.WriteLine(Clock.Time)
    TextWindow.WriteLine(Clock.WeekDay)
    TextWindow.WriteLine(Clock.Year)
    """

    math_test = """
    TextWindow.WriteLine("Arctan of " + Math.Pi + " is " + Math.ArcTan(Math.Pi))
    deg_ang = 60
    TextWindow.WriteLine("In degrees, the angle is " + deg_ang)
    rad_ang = Math.GetRadians(deg_ang)
    TextWindow.WriteLine("In radians, the angle is " + rad_ang)
    TextWindow.WriteLine("The sine is " + Math.Sin(rad_ang))
    TextWindow.WriteLine("The arcsine of the sine is " + Math.ArcSin(Math.Sin(rad_ang)))
    TextWindow.WriteLine("The arcsine of the sine in degrees is " + Math.GetDegrees(Math.ArcSin(Math.Sin(rad_ang))))
    """

    graphics_test_basic = """
    textwindow.foregroundcolor = "darkgreen"
    textwindow.backgroundcolor = "green"
    textwindow.writeline(textwindow.foregroundcolor)
    textwindow.writeline(textwindow.backgroundcolor)
    GraphicsWindow.Show()
    GraphicsWindow.Title = "A Graphics Window"
    GraphicsWindow.BackgroundColor = "Cyan"
    TextWindow.writeline(GraphicsWindow.GetColorFromRGB(266,100,-1))
    GraphicsWindow.ShowMessage("Hello text", "Hello title")

    textwindow.hide()
    graphicswindow.drawline(100,100,200,200)
    textwindow.writeline("width: " + graphicswindow.width + ", height: " + graphicswindow.height)
'    graphicswindow.width = 5
    graphicswindow.width = 800
    textwindow.writeline("width: " + graphicswindow.width + ", height: " + graphicswindow.height)
    graphicswindow.height = 800
    textwindow.writeline("width: " + graphicswindow.width + ", height: " + graphicswindow.height)
    """

    textwindow_colors_test = """
    For i = 0 to 15
        TextWindow.ForegroundColor = i
        TextWindow.WriteLine(TextWindow.ForegroundColor)
    EndFor
    """

    text_test = """
    TextWindow.Title = Text.Append("10","10")
    """

    interpreter = Interpreter()
    interpreter.run(text_test)