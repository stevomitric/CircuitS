using Blink

w = Window(async=false)

load!(w, "C:/Users/Stevo/Documents/Julia/TEK/gui/ui/main.html")
load!(w, "gui/ui/main.js")



@js test();


while true  # Still an infinite loop, but a _fair_ one.
    yield()  # This will yield to any other computation, allowing the callback to run.
end