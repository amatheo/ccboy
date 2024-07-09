-- ComputerCraft Startup Script
-- Connect to websocket and display on monitor

local displayEnabled = true
local base_url = "ws://localhost:8081"

local websocket
local mMonitor
local jMonitor


-- map up, down, left, right, a,b, select, start to zone on screen of 100x52
local joypad_zone = {
    up = {x = 8, y = 3, width = 6, height = 6},
    left = {x = 2, y = 9, width = 6, height = 6},
    down = {x = 8, y = 15, width = 6, height = 6},
    right = {x = 14, y = 9, width = 6, height = 6},
    select = {x = 36, y = 18, width = 12, height = 3},
    start = {x = 52, y = 18, width = 12, height = 3},
    A = {x = 66, y = 3, width = 12, height = 12},
    B = {x = 84, y = 9, width = 12, height = 12}
}



local function downloadFile(url, path)
    -- Faire une requête GET à l'URL
    local response, err = http.get(url, nil, true)

    -- Vérifier si la requête a réussi
    if not response then
        print("Erreur lors de la requête HTTP : " .. err)
        return
    end

    -- Lire le contenu de la réponse
    local content = response.readAll()
    print("Contenu téléchargé : " .. content)
    response.close()

    -- Sauvegarder le contenu dans un fichier local
    local file = fs.open(path, "w")
    file.write(content)
    file.close()

    print("Fichier téléchargé avec succès !")
end

local function get(pasteId, filename)
    local f, reason = io.open(filename, "w")
    if not f then
        io.stderr:write("Failed opening file for writing: " .. reason)
        return
    end

    io.write("Downloading from pastebin.com... ")
    local url = "https://pastebin.com/raw/" .. pasteId
    local result, response = http.get(url)
    if result then
        io.write("success.\n")
        f:write(result.readAll())

        f:close()
        io.write("Saved data to " .. filename .. "\n")
    else
        io.write("failed.\n")
        f:close()
        fs.remove(filename)
        io.stderr:write("HTTP request failed: " .. response .. "\n")
    end
end

local function downloadLibraries()
    print("Downloading libraries")
    get("fN3HFQ9f", "/LibDeflate.lua")
    get("QiaQ2KBr", "/surface.lua")
end

local function checkLibraries()
    if not fs.exists("/LibDeflate.lua") or not fs.exists("/surface.lua") then
        downloadLibraries()
    end
end

checkLibraries()

local LibDeflate = dofile("/LibDeflate.lua")
local surface = dofile("/surface.lua")

-- Function to connect to the websocket
local function connectWebsocket(url)
    print("Connecting to websocket at " .. url)
    local ws, err = http.websocket(url)
    if not ws then
        print("Failed to connect to websocket: " .. err)
        return
    end
    return ws
end

-- Function to find and set up the monitor
local function setupMonitor(direction)
    local monitor
    for i = 1, #direction do
        monitor = peripheral.wrap(direction[i])
        if monitor then
            break
        end
    end

    if not monitor then
        print("No main monitor found")
        return
    end

    print("Monitor found!")
    monitor.setTextScale(0.5)
    local mWidth, mHeight = monitor.getSize()
    print("Monitor Resolution (w x h) " .. mWidth .. "x" .. mHeight)
    monitor.clear()

    return monitor, mWidth, mHeight
end

-- Function to process received message
local function processMessage(message)
    message = LibDeflate:DecompressZlib(message)

    -- Header contains image width and height on 2 bytes
    local imgWidth = string.byte(message, 1)
    local imgHeight = string.byte(message, 2)
    local reducedWidth = imgWidth / 2
    local reducedHeight = imgHeight / 3
    return message:sub(3), imgWidth, imgHeight, reducedWidth, reducedHeight
end


-- Function to calculate image position
local function calculateImagePosition(screenWidth, screenHeight, reducedWidth, reducedHeight)
    local x = math.floor((screenWidth - reducedWidth) / 2)
    local y = math.floor((screenHeight - reducedHeight) / 2)
    return x, y
end

-- Function to draw image on monitor
local function drawImage(screen, s, x, y, monitor)
    screen:drawSurfaceSmall(s, x, y)
    screen:output(monitor)
end

local function drawController(joypad_zone, monitor)

    if not monitor then
        return
    end
    local width, height =  monitor.getSize()
    local surface = surface.create(width, height)

    for name, zone in pairs(joypad_zone) do
        surface:fillRect(zone.x, zone.y, zone.width, zone.height, colors.white)
    end

    --surface:drawSurface(surface, 0,0, width, height, 1, 1, width, height)
    surface:output(monitor)
end

local function handleTouchEvents()

    drawController(joypad_zone, jMonitor)

    -- Load /base.nfp image
    local imageData = fs.open("/base.nfp", "r")
    local image = surface.load(imageData.readAll(), true)

    --[[local paintimage = paintutils.loadImage("/base.nfp")

    term.redirect(jMonitor)
    paintutils.drawImage(paintimage, 0, 0)
    term.redirect(term.native())]]

    --drawImage(screen, image, 0, 0, jMonitor)

    while true do
        local event, side, touchx, touchy = os.pullEvent("monitor_touch")
        local peripheral = peripheral.wrap(side)

        if peripheral.getSize() == jMonitor.getSize() then
            local button
            for name, zone in pairs(joypad_zone) do
                if touchx >= zone.x and touchx < zone.x + zone.width and
                        touchy >= zone.y and touchy < zone.y + zone.height then
                    button = name
                    break
                end
            end
            if button then
                websocket.send(button)
            end
        end
    end
end

local function handleScreen()
    local width, height = mMonitor.getSize()
    local screen = surface.create(width, height)
    local previousTerm = term.redirect(mMonitor)

    while true do
        local message = websocket.receive()
        if not message then
            term.clear()
            term.redirect(term.native())
            print("Connection closed")
            break
        end

        local imageData, imgWidth, imgHeight, reducedWidth, reducedHeight = processMessage(message)
        local x, y = calculateImagePosition(width, height, reducedWidth, reducedHeight)

        if displayEnabled then
            local s = surface.load(imageData, true)
            drawImage(screen, s, x, y, mMonitor)
        end
    end
end

-- Main function
local function main()
    websocket = connectWebsocket(base_url)
    if not websocket then return end

    mMonitor = setupMonitor({"top"})
    jMonitor = setupMonitor({"front", "back", "left", "right"})
    if not mMonitor then
        print("No main monitor found")
        return
    end

    parallel.waitForAny(handleScreen, handleTouchEvents)
end

main()