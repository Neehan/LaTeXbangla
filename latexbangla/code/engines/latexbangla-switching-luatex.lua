-- Select Latin companions before LuaTeX hyphenates and ligatures text.
-- Part of latexbangla, LPPL 1.3c or later; copyright 2026 Adib Hasan.
-- TeX owns font selection and scoping; this module only handles text nodes.

local glyph_id = node.id("glyph")
local math_id = node.id("math")
local disc_id = node.id("disc")

-- Match the Latin Unicode blocks enabled by ucharclasses in the XeTeX backend.
-- Joiners and Bengali marks are deliberately excluded: changing their font
-- independently would split the clusters HarfBuzz needs to shape.
local latin_characters = {}
local latin_blocks = {
    {0x0020, 0x024F}, -- Basic Latin, Latin-1 Supplement, Latin Extended A/B.
    {0x1E00, 0x1EFF}, -- Latin Extended Additional.
    {0x2C60, 0x2C7F}, -- Latin Extended C.
    {0xA720, 0xA7FF}, -- Latin Extended D.
    {0xAB30, 0xAB6F}, -- Latin Extended E.
    {0xFB00, 0xFB4F}, -- Alphabetic Presentation Forms.
    {0x10780, 0x107BF}, -- Latin Extended F.
    {0x1DF00, 0x1DFFF}, -- Latin Extended G.
}
for _, block in ipairs(latin_blocks) do
    for codepoint = block[1], block[2] do latin_characters[codepoint] = true end
end
for _, codepoint in ipairs({0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026}) do
    latin_characters[codepoint] = true
end

-- Leave glue alone. As with XeTeX's inter-character transitions, ordinary
-- spaces are made by the enclosing text font. This also preserves WordSpace,
-- sentence spacing, explicit skips and glue inserted by other packages.
return function(latin_font_attribute)
    local function switch_text_fonts(head)
        local in_math = false
        for current in node.traverse(head) do
            if current.id == math_id then
                in_math = current.subtype == 0
            elseif not in_math then
                if current.id == glyph_id then
                    local target = node.has_attribute(current, latin_font_attribute)
                    -- LuaTeX adds 256 to protected glyph subtypes. Those glyphs
                    -- have already been processed and must keep their font.
                    if target and current.subtype < 256 and latin_characters[current.char] then
                        current.font = target
                    end
                elseif current.id == disc_id then
                    -- Author-supplied discretionary text needs its companion
                    -- too. Automatic hyphens are created afterwards, using the
                    -- correct surrounding font, so Bangla clusters stay intact.
                    switch_text_fonts(current.pre)
                    switch_text_fonts(current.post)
                    switch_text_fonts(current.replace)
                end
            end
        end
    end
    -- The pre-shaping callback is too late: native TeX ligatures have already
    -- run, and changing an automatic Bangla hyphen's font breaks HarfBuzz's
    -- contextual shaping across that discretionary. Select fonts before both
    -- operations, then delegate hyphenation to LuaTeX's standard algorithm.
    -- This callback also runs for text packed into horizontal boxes.
    luatexbase.add_to_callback("hyphenate", function(head, tail)
        switch_text_fonts(head)
        lang.hyphenate(head, tail)
    end, "latexbangla.font-switching")
end
