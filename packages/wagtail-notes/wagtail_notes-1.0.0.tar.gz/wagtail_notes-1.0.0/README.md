# Comparison with other solutions

This package is similar to https://github.com/torchbox/wagtail-footnotes but in general:
- our approach is more lightweight
- our approach is similar to what users do in Microsoft Word
- our approach is more flexible, you can use it to make a handcrafted table of contents, for example
- our approach is not structured, so developers have no control over where the notes should be and what they should look like, since any inline selection of text can become a note anchor or reference
- as a consequence, our approach relies more on editor consistency across a site

More technical details:
- we save notes inside the same rich text field/block
- we do not create an extra database model
- we do not require an extra `InlinePanel`
- you can copy anchors and their references directly from Office documents (only from LibreOffice, for now), the links are created automatically
- future database migrations can be easier as the data is less spread
- We are not limited to 1 set of footnotes per page, you can have many footnotes section if needed, one per rich text field/block

# Install

1. `pip install wagtail-notes`
2. Add `'wagtail_notes',` to `INSTALLED_APPS`, **before** `'wagtail.admin',`
3. Add `'wagtailfontawesomesvg',` to `INSTALLED_APPS` if it is not already added. Its position does not matter.
4. Add `'note-anchor'` and `'note-reference'` features to your Draftaileditor features. Example:
   ```python
    WAGTAILADMIN_RICH_TEXT_EDITORS = {
        'default': {
            'WIDGET': 'flaubert.rich_text.TypographicDraftailRichTextArea',
            'OPTIONS': {
                'features': [
                    'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'bold', 'italic',
                    'link', 'document-link', 'note-anchor', 'note-reference', 'image', 'embed',
                ],
            },
        },
    }
   ```

# Usage

2 new buttons will appear in the Draftail bar. To use them, you must select some text first. You also need to create a note before making a reference to this note.

Typically, for creating footnotes:
1. Add a paragraph to your `RichTextField`/`RichTextBlock`.
2. Add another paragraph at the end of the same rich text, starting with `1.` and containing a comment about something in the paragraph written in step 1.
3. Select just `1.` and click on “Note anchor”, then give a unique name to that note. It can be a number too, but we recommend you to give a more meaningful name, as it makes it easier to change the order of notes later.
4. Go back to the step 1 paragraph, and write `[1]` just after the place that the note will comment (no space). Select `[1]` and click on “Note reference”. Select the unique name of the note you wrote in step 3.
5. The `[1]` part will be rendered as:
   ```html
   <a id="slugified-unique-name-reference" href="#slugified-unique-name" data-note="reference">[1]</a>
   ```
   The `1.` part will be rendered as:
   ```html
   <a id="slugified-unique-name" href="#slugified-unique-name-reference" data-note="anchor">1.</a>
   ```
