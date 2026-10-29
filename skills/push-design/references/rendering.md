# Building editable boards from rendered UI

Use this reference for a first import, reconstructing a screen from the browser,
or correcting status badge alignment.

## Capture the intended surface

Wait for hydration and visible images to settle. Keep the route, language, theme,
viewport, and UI state consistent while measuring and capturing. Isolate the
requested component or plugin from surrounding demo controls and navigation.
Capture open dialogs, menus, tooltips, and toasts in their actual visible states;
they may render outside the preview root through portals.

DOM bounds alone do not establish visibility. Exclude screen-reader-only text,
collapsed content, and content outside ancestor clips. Traverse children of
`display: contents` elements even though the parent has no box. An `aria-hidden`
attribute alone does not make an element visually hidden: decorative icons often
use it. Verify the result against the rendered screen.

Preserve scroll viewports and sticky columns as clipped compositions. A root
board's clipping does not reproduce a nested table's clipping. Check fixed or
sticky footers, wide banners, and small viewports for overlap or overflow.

## Keep the result editable

Use native text, shapes, linked components, image fills, and original vector
icons. Inspect native controls separately: DOM text extraction can miss file
picker labels, checkbox ticks, radio selection, and range slider tracks or thumbs.
Verify visible marks and disabled appearance, not just the control's background.

Use the font actually rendered and confirm it is available in Penpot. A CSS font
family list does not prove its first font loaded. Disclose substitutions. Apply
computed text transformations and preserve line breaks, weight, spacing, and
sizing behavior. Give changed text enough width and height, then inspect an
export: a correct `characters` getter can coexist with stale or clipped rendering.
If an update remains stale, narrowly replace the affected text layer while
preserving its styling and placement; retain designer edits outside the change.

Verify imported group order, especially ticks over filled controls and borders
over surfaces. Inspect both the main component and its instances. Preserve actual
opacity, shadows, and blur where supported; identify approximations in the report.

Upload required local assets through the design tool's media API when its server
cannot reach a development URL. Reuse uploaded media within the file. Keep image
bytes out of ordinary tool output and respect payload limits. If an external embed
cannot be reproduced, leave an explicitly named placeholder and report it.

## Align status badges

DOM line boxes and Penpot's rendered text bounds can differ. For a single-line
status pill whose source centers its contents, align the label's `textBounds`
center with the pill's center; centering the text layer's nominal height can
leave the visible label too high. Measure both in the same coordinate space
after resolving the font and text sizing. For manually positioned text:

```js
const bounds = label.textBounds;
label.y += pill.y + pill.height / 2 - (bounds.y + bounds.height / 2);
```

Use the owning layout's alignment when flex/grid controls positioning. Preserve
horizontal padding, typography, and already centered dots and chevrons. Derive
the correction from current bounds each time; a fixed pixel nudge can drift on
repeated syncs or misalign other fonts and sizes. Leave aligned labels unchanged.

Check matching status badges throughout the affected flow, including mobile and
theme variants and descendants of clipped table viewports. Re-read the bounds
and inspect an export before repeating the correction across those occurrences.
Confirm label, dot, and chevron centers align within the pill without clipping.

## Verify in bounded batches

Compare one representative export with the source before creating more boards.
Keep mutations small enough to inspect and resume after interruption. Record IDs
as shapes are created, and inspect partial state after failures before retrying.

For a page copy, verify native content and styling as well as component links;
an SVG or screenshot import may look correct while losing editable text or links.
Preserve child order and explicit constraints after reparenting. A clipboard
command completing is insufficient: confirm the expected destination boards exist
before deleting any originals.

Export and inspect affected boards, including changed mobile or theme variants.
Check nested links recursively, even inside clipped viewports. Board and component
counts help detect omissions and duplicates; they do not replace visual inspection.
