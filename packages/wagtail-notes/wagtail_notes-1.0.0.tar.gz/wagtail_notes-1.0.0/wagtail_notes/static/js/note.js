React = window.React;
Modifier = window.DraftJS.Modifier;
EditorState = window.DraftJS.EditorState;
ContentState = window.DraftJS.ContentState;
SelectionState = window.DraftJS.SelectionState;
convertFromHTML = window.DraftJS.convertFromHTML;
TooltipEntity = window.draftail.TooltipEntity;


const REFERENCE_SUFFIX = '-reference';


function slugify(text) {
  if (!text) {
      return '';
  }
  return text
    .toString() // Cast to string (optional)
    .normalize('NFKD') // The normalize() using NFKD method returns the Unicode Normalization Form of a given string.
    .toLowerCase() // Convert the string to lowercase letters
    .trim() // Remove whitespace from both sides of a string (optional)
    .replace(/\s+/g, '-') // Replace spaces with -
    .replace(/[^\w\-]+/g, '') // Remove all non-word chars
    .replace(/\-\-+/g, '-'); // Replace multiple - with single -
}


class Icon extends React.PureComponent {
  render() {
    const { name } = this.props;
    return React.createElement(
      'svg',
      {
        className: `icon icon-${name}`,
        style: { marginRight: 0 },
      },
      [
        React.createElement('use', { href: `#icon-${name}` }),
      ],
    );
  }
}


function getDefaultAnchor(content, selection) {
  const currentBlock = content.getBlockForKey(selection.getAnchorKey());
  return slugify(currentBlock.getText().slice(selection.getStartOffset(), selection.getEndOffset())).slice(0, 50);
}


function getExistingNotes(contentState) {
  const availableNotes = [];
  const usedNotes = [];
  contentState.getBlocksAsArray().forEach(block =>
    block.getCharacterList().forEach(characterList => {
      const entityKey = characterList.getEntity();
      if (entityKey !== null) {
        const data = contentState.getEntity(entityKey).getData();
        if (data.linktype === 'note-reference') {
          const value = data.id.slice(0, -REFERENCE_SUFFIX.length);
          if (!usedNotes.includes(value)) {
            usedNotes.push(value);
          }
        } else if (data.linktype === 'note-anchor') {
          if (!availableNotes.includes(data.id)) {
            availableNotes.push(data.id);
          }
        }
      }
    })
  );
  return [availableNotes, usedNotes];
}


function renderModal(
    formContentHtml,
    getValue,
) {
    const dialog = document.createElement('dialog');
    dialog.innerHTML = `
    <style>
      dialog {
        border-radius: 3px;
      }
      dialog::backdrop {
        background-color: var(--w-color-black-50);
      }
    </style>
    <form method="dialog" style="display: flex; flex-flow: column nowrap; align-items: center;">
        ${formContentHtml}
        <menu style="padding: 0">
            <button type="button" value="cancel" class="button button-secondary">Annuler</button>
            <button type="submit" value="confirm" class="button">Valider</button>
        </menu>
    </form>
    `;

    document.body.appendChild(dialog);
    document.body.style['overflow-y'] = 'hidden';
    dialog.style.zIndex = '1000';
    dialog.showModal();

    const cancelButton = dialog.querySelector('button[value="cancel"]');

    return new Promise((resolve, reject) => {
        cancelButton.addEventListener('click', () => {
            dialog.close();
        });
        dialog.addEventListener('close', () => {
            const value = getValue(dialog);
            document.body.removeChild(dialog);
            document.body.style.removeProperty('overflow-y');
            if (dialog.returnValue === 'confirm') {
                resolve(value);
            } else {
                reject();
            }
        });
    });
}


class NoteReferenceSource extends React.PureComponent {
  componentDidMount() {
    const { editorState, entity, entityType, onComplete, onClose } = this.props;

    const content = editorState.getCurrentContent();
    const selection = editorState.getSelection();

    let previousAnchor = entity ? entity.getData().id.toString().slice(0, -REFERENCE_SUFFIX.length) : '';
    if (!previousAnchor) {
        previousAnchor = getDefaultAnchor(content, selection);
    }

    const [availableNotes, usedNotes] = getExistingNotes(content);
    const options = availableNotes.map(value =>
        `<option value="${value}"${value === previousAnchor ? ' selected' : ''}>${value}</option>`
    );
    renderModal(
        `
            <div style="width: 100%">
                <label for="id_note_anchor" class="w-field__label">
                    Nom de l’ancre :
                    <span class="w-required-mark">*</span>
                </label>
                <div class="w-field__input">
                    <select name="anchor" id="id_note_anchor" style="width: 100%">
                        ${options.join('')}
                    </select>
                    <span></span>
                </div>
            </div>
`       ,
        function getValue(dialog) {
            const select = dialog.querySelector('select');
            return select.value;
        },
    ).then(anchor => {
        if (!anchor) {
          onClose();
          return;
        }
        const newEntity = content.createEntity(
          entityType.type, 'MUTABLE', {
              'linktype': 'note-reference',
              id: `${anchor}${REFERENCE_SUFFIX}`,
              'href': `#${anchor}`,
            },
        );
        const entityKey = newEntity.getLastCreatedEntityKey();

        const newContent = Modifier.applyEntity(newEntity, selection, entityKey);
        const newEditorState = EditorState.push(editorState, newContent, 'apply-entity');
        onComplete(newEditorState);
    }).catch(err => {
        onClose();
    });
  }

  render() {
    return null;
  }
}


class NoteReference extends React.PureComponent {
  render() {
    const { entityKey, onEdit, onRemove, children, contentState } = this.props;
    const { id } = contentState.getEntity(entityKey).getData();
    return React.createElement(
      'sup',
      {},
      React.createElement(TooltipEntity, {
          entityKey,
          onEdit,
          onRemove,
          icon: React.createElement(Icon, { name: 'asterisk' }),
          label: id.slice(0, -REFERENCE_SUFFIX.length),
        },
        children,
      ),
    );
  }
}


window.draftail.registerPlugin({
  type: 'NOTE_REFERENCE',
  source: NoteReferenceSource,
  decorator: NoteReference,
});


class NoteAnchorSource extends React.PureComponent {
  componentDidMount() {
    const { editorState, entity, entityType, onComplete, onClose } = this.props;

    const content = editorState.getCurrentContent();
    const selection = editorState.getSelection();

    let previousAnchor = entity ? entity.getData().id : '';
    if (!previousAnchor) {
        previousAnchor = getDefaultAnchor(content, selection);
    }

    renderModal(
        `
            <div style="width: 100%">
                <label for="id_note_anchor" class="w-field__label">
                    Nom de l’ancre :
                    <span class="w-required-mark">*</span>
                </label>
                <div class="w-field__input">
                    <input type="text" name="anchor" id="id_note_anchor" value="${previousAnchor}" />
                </div>
            </div>
`       ,
        function getValue(dialog) {
            const input = dialog.querySelector('input');
            return slugify(input.value);
        },
    ).then(anchor => {
        if (!anchor) {
          onClose();
          return;
        }

        const [availableNotes, usedNotes] = getExistingNotes(content);
        if (anchor !== previousAnchor) {
            if (availableNotes.includes(anchor)) {
                alert(`« ${anchor} » est déjà utilisé ! Merci de choisir un autre nom.`)
                onClose();
                return;
            }
            if (usedNotes.includes(previousAnchor)) {
                alert(`« ${anchor} » est utilisé par des appels de note, merci de mettre à jour les appels de notes, autrement ces appels de notes seront cassés.`);
            }
        }

        const newEntity = content.createEntity(
          entityType.type, 'MUTABLE', {
              'linktype': 'note-anchor',
              id: anchor,
              'href': `#${anchor}${REFERENCE_SUFFIX}`,
            },
        );
        const entityKey = newEntity.getLastCreatedEntityKey();

        const newContent = Modifier.applyEntity(newEntity, selection, entityKey);
        const newEditorState = EditorState.push(editorState, newContent, 'apply-entity');
        onComplete(newEditorState);
    }).catch(err => {
        onClose();
    });
  }

  render() {
    return null;
  }
}


class NoteAnchor extends React.PureComponent {
  render() {
    const { entityKey, onEdit, onRemove, children, contentState } = this.props;
    const { id } = contentState.getEntity(entityKey).getData();
    return React.createElement(TooltipEntity, {
        entityKey,
        onEdit,
        onRemove,
        icon: React.createElement(Icon, { name: 'anchor' }),
        label: id,
      },
      children,
      React.createElement('small', {}, '↑'),
    );
  }
}


window.draftail.registerPlugin({
  type: 'NOTE_ANCHOR',
  source: NoteAnchorSource,
  decorator: NoteAnchor,
});


const NOTE_PLUGIN = {
    handlePastedText(
        text,
        html,
        editorState,
        pluginFunctions,
    ) {
        let newState = editorState;
        const contentState = editorState.getCurrentContent();
        const converted = convertFromHTML(html);
        let newContentState = ContentState.createFromBlockArray(
            converted.contentBlocks,
            contentState.getEntityMap(),
        );
        converted.contentBlocks.forEach(
            contentBlock => {
                contentBlock.findEntityRanges(
                    (characterMetadata => characterMetadata.getEntity() !== null),
                    (start, end) => {
                        const entityKey = contentBlock.getEntityAt(start);
                        const entity = newContentState.getEntity(entityKey);
                        const href = entity.getData().href;
                        if (href && href.startsWith('#')) {
                            const data = {};
                            let entityType;
                            if (href.endsWith('anc')) {
                                entityType = 'NOTE_ANCHOR';
                                data['linktype'] = 'note-anchor';
                                data.id = href.slice(1, -'anc'.length);
                                data['href'] = `#${data.id}${REFERENCE_SUFFIX}`;
                            } else if (href.endsWith('sym')) {
                                entityType = 'NOTE_REFERENCE';
                                data['linktype'] = 'note-reference';
                                data['href'] = href.slice(0, -'sym'.length);
                                data.id = `${data['href'].slice(1)}${REFERENCE_SUFFIX}`;
                            }
                            if (!entityType) {
                                return;
                            }
                            let selectionState = SelectionState.createEmpty(contentBlock.getKey());
                            selectionState = selectionState.merge({
                                anchorOffset: start,
                                focusOffset: end,
                            });
                            newContentState = Modifier.applyEntity(newContentState, selectionState, null);
                            newContentState = newContentState.createEntity(
                                entityType,
                                entity.getMutability(),
                                data,
                            );
                            const newEntityKey = newContentState.getLastCreatedEntityKey();
                            newContentState = Modifier.applyEntity(newContentState, selectionState, newEntityKey);
                        }
                    }
                );
            }
        );
        newState = EditorState.push(
            editorState,
            Modifier.replaceWithFragment(
                contentState,
                editorState.getSelection(),
                newContentState.getBlockMap(),
            ),
            'insert-fragment',
        );
        pluginFunctions.setEditorState(newState);
        return 'handled';
    },
};
