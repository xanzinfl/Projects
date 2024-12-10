-------------------- AUTO CLICKER By xanzinfl --------------------

Enable = true -- Enable Auto Clicker

ToggleKey = "CapsLock" -- Usable Keys: "CapsLock", "NumLock", "ScrollLock"

RequireToggle = false -- Change to false if you want it to always be on.

Button = 5  -- 1: LMB, 2: Scroll Click, 3: RMB, 4: Sidebutton1, 5: Sidebutton2

clickDelay = 60 -- Delay in milliseconds between clicks

EnablePrimaryMouseButtonEvents(true)

function AutoClick()
  repeat
    PressAndReleaseMouseButton(1)
    Sleep(clickDelay)
  until not IsMouseButtonPressed(Button)
end

function OnEvent(event, arg)
  if not Enable then return end

  if RequireToggle then
    if IsKeyLockOn(ToggleKey) and IsMouseButtonPressed(Button) then
      AutoClick()
    end
  else
    if IsMouseButtonPressed(Button) then
      AutoClick()
    end
  end
end
