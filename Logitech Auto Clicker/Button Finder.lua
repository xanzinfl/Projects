EnablePrimaryMouseButtonEvents(true)
function OnEvent(event, arg)
    if event == "MOUSE_BUTTON_PRESSED" then
        OutputLogMessage("Mouse Button Pressed: %d\n", arg)
    elseif event == "MOUSE_BUTTON_RELEASED" then
        OutputLogMessage("Mouse Button Released: %d\n", arg)
    end
end
