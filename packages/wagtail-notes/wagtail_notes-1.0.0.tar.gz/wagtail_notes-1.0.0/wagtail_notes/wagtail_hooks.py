from django.utils.translation import gettext
from draftjs_exporter.dom import DOM
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineEntityElementHandler,
)
from wagtail.admin.rich_text.editors.draftail.features import EntityFeature
from wagtail.rich_text import LinkHandler


@hooks.register('register_icons')
def register_icons(icons):
    return icons + [
        'wagtailfontawesomesvg/solid/anchor.svg',
        'wagtailfontawesomesvg/solid/asterisk.svg',
    ]


def note_anchor_entity_decorator(props):
    return DOM.create_element('a', props, props.get('children'))


class NoteAnchorEntityElementHandler(InlineEntityElementHandler):
    mutability = 'MUTABLE'

    def get_attribute_data(self, attrs: dict):
        return attrs


class NoteAnchorLinkHandler(LinkHandler):
    identifier = 'note-anchor'

    @classmethod
    def expand_db_attributes(cls, attrs):
        try:
            return f'<a id="{attrs["id"]}" href="{attrs["href"]}" data-note="anchor">'
        except KeyError:
            return '<a>'


@hooks.register('register_rich_text_features')
def register_note_anchor(features):
    feature_name = 'note-anchor'
    type_ = 'NOTE_ANCHOR'

    features.register_editor_plugin(
        'draftail',
        feature_name,
        EntityFeature(
            {
                'type': type_,
                'icon': 'anchor',
                'description': gettext('Note anchor'),
                'attributes': ['id', 'href', 'linktype'],
                'allowlist': {
                    'href': '^#',
                    'linktype': 'note-anchor',
                },
            },
            js=['js/note.js'],
            css={},
        )
    )
    features.register_link_type(NoteAnchorLinkHandler)

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {
            f'a[linktype="note-anchor"]': NoteAnchorEntityElementHandler(type_),
        },
        'to_database_format': {
            'entity_decorators': {type_: note_anchor_entity_decorator},
        },
    })


def note_reference_entity_decorator(props):
    return DOM.create_element('a', props, props['children'])


class NoteReferenceEntityElementHandler(InlineEntityElementHandler):
    mutability = 'MUTABLE'

    def get_attribute_data(self, attrs: dict):
        return attrs


class NoteReferenceLinkHandler(LinkHandler):
    identifier = 'note-reference'

    @classmethod
    def expand_db_attributes(cls, attrs):
        try:
            return f'<a id="{attrs["id"]}" href="{attrs["href"]}" data-note="reference">'
        except KeyError:
            return '<a>'


@hooks.register('register_rich_text_features')
def register_note_reference(features):
    feature_name = 'note-reference'
    type_ = 'NOTE_REFERENCE'

    features.register_editor_plugin(
        'draftail',
        feature_name,
        EntityFeature(
            {
                'type': type_,
                'icon': 'asterisk',
                'description': gettext('Note reference'),
                'attributes': ['id', 'href', 'linktype'],
                'allowlist': {
                    'href': '^#',
                    'linktype': 'note-reference',
                },
            },
            js=['js/note.js'],
            css={},
        )
    )
    features.register_link_type(NoteReferenceLinkHandler)

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {
            f'a[linktype="note-reference"]': NoteReferenceEntityElementHandler(type_),
        },
        'to_database_format': {
            'entity_decorators': {type_: note_reference_entity_decorator},
        },
    })
