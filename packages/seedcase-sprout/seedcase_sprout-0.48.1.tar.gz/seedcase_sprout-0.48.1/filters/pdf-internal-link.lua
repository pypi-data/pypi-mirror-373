-- Make internal links work in a single-document PDF.
-- Remove the document path from internal links, leaving only the fragment.
-- Fragments must be present and globally unique in the source code for internal
-- links to work.
function Link(el)
    if quarto.doc.is_format("pdf") then
        -- Match links like path/to/file.qmd#fragment
        local new_target = string.match(el.target, "^%S+%.qmd(#%S+)$")
        if new_target then
            el.target = new_target
        end
    end
    return el
end
