'use strict';

var MdEditor,
    __bind = function(fn, me) {
        return function() {
            return fn.apply(me, arguments);
        };
    };

MdEditor = (function() {
    function MdEditor(selector, options) {
        this.save = __bind(this.save, this);
        this.fullscreen = __bind(this.fullscreen, this);
        this.image = __bind(this.image, this);
        this.link = __bind(this.link, this);
        this.code = __bind(this.code, this);
        this.italic = __bind(this.italic, this);
        this.bold = __bind(this.bold, this);
        this.header = __bind(this.header, this);
        this.list_ul = __bind(this.list_ul, this);
        this.list_ol = __bind(this.list_ol, this);
        this.quote = __bind(this.quote, this);

        this.toggle_preview = __bind(this.toggle_preview, this);
        this.toggle_edit = __bind(this.toggle_edit, this);
        this.textarea = $(selector);
        if (this.textarea.length === 0) {
            return console.log('Aucun élément ne correspond à ce selecteuir');
        }
        this.options = {
            labelClose: 'Do you really want to close this window ? Every edit you did could be lost',
            labelInsert: 'Insert',
            labelDelete: 'Delete',
            labelSuccess: 'Content saved with success',
            labelImage: 'Insert your image url',
            labelConfirm: 'Do you really want to delete this picture ?',
            preview: true,
            uploader: false,
            uploaderData: {},
            ctrls: true,
            imageURL: function(el) {
                return el.url;
            },
            flash: function(message, type) {
                return window.alert(message);
            }
        };
        this.markdownSections = [];
        this.previewSections = [];
        this.lastMardownScrollTop = null;
        this.lastPreviewScrollTop = null;
        this.scrolling = false;
        this.isMarkdownMoving = false;
        this.isPreviewMoving = false;
        if (options !== void 0) {
            $.extend(this.options, options);
        }
        this.canExit = true;
        this.element = $("\
        <div class=\"mdeditor\">\
            <div class=\"mdeditor_toolbar\"></div> \
            <div class=\"mdeditor_body\"> \
                <section class=\"mdeditor_markdown\"> \
                    <div class=\"mdeditor_scroll mdeditor_markdown_scroll\"> \
                        <header class=\"left\">Markdown</header> \
                    </div> \
                </section> \
                <section class=\"mdeditor_preview\"> \
                    <div class=\"mdeditor_scroll mdeditor_preview_scroll\"> \
                        <header  class=\"right\">Preview</header> \
                        <div class=\"mdeditor_render formatted\"></div> \
                    </div> \
                </section> \
            </div> \
            <div class=\"mdeditor_modal\"> \
                <div class=\"mdeditor_drop\"> \
                        <div>Click Here To Upload New Image</div> \
                </div> \
            </div> \
        </div>");

        this.markdownScroll = $('.mdeditor_markdown_scroll', this.element);
        this.previewScroll = $('.mdeditor_preview_scroll', this.element);
        this.preview = $('.mdeditor_render', this.element);
        this.toolbar = $('.mdeditor_toolbar', this.element);
        this.form = this.textarea.parents('form');
        this.textarea.after(this.element);
        if (!this.options.preview) {
            this.element.addClass('has-no-preview');
        }
        $('.mdeditor_markdown .mdeditor_scroll', this.element).append(this.textarea);
        this.editor = CodeMirror.fromTextArea(this.textarea[0], {
            mode: 'markdown',
            tabMode: 'indent',
            theme: 'neo',
            lineWrapping: true,
            viewportMargin: Infinity
        });
        this.updatePreview();
        this._buildToolbar();
        this._buildDropzone();
        this._bindEvents();
    }

    var addMDTag = function(editor, tag_start, tag_end, empty_text ) {
        var content = editor.doc.getSelection('around')
        if (content.trim() == "") {
            content = empty_text
        }
        editor.doc.replaceSelection(tag_start + content + tag_end);
        return editor.focus();
    }

    MdEditor.prototype.updatePreview = function() {

        var text;
        text = this.editor.getValue();
        this.textarea.val(this.editor.getValue());
        /**
        if (this.preview.is(':visible')) {
            this.preview.html(marked(text), {
                breaks: true
            });
            return this._setSections();
        }**/
            this.preview.html(marked(text), {
                breaks: true
            });
    };

    MdEditor.prototype.flash = function(message, type) {
        if (type === void 0) {
            type = 'error';
        }
        return this.options.flash(message, type);
    };

    MdEditor.prototype.toggle_preview = function(e) {
        if (e !== void 0) {
            e.preventDefault();
        }
        this.updatePreview()
        var _preview = $(".mdeditor_preview")
        var _md = $(".mdeditor_markdown")

        if (_md.is(":visible")) {
            _md.hide()
            _preview.css({width: "100%"})
        } else {
            _md.show()
            _preview.css({width: "50%"})
        }
        return this.editor.focus();
    };

    MdEditor.prototype.toggle_edit = function(e) {
        if (e !== void 0) {
            e.preventDefault();
        }
        this.updatePreview()
        var _preview = $(".mdeditor_preview")
        var _md = $(".mdeditor_markdown")

        if (_preview.is(":visible")) {
            _preview.hide()
            _md.css({width: "100%"})
        } else {
            _preview.show()
            _md.css({width: "50%"})
        }
        return this.editor.focus();
    };

    MdEditor.prototype.header = function(e) {
        if (e !== void 0) {
            e.preventDefault();
        }
        return addMDTag(this.editor, "##", "", "Header Text" )
    };


    MdEditor.prototype.bold = function(e) {
        if (e !== void 0) {
            e.preventDefault();
        }
        return addMDTag(this.editor, "**", "**", "Strong Text" )
    };

    MdEditor.prototype.italic = function(e) {
        if (e !== void 0) {
            e.preventDefault();
        }
        return addMDTag(this.editor, "*", "*", "Italic Text" );
    };

    MdEditor.prototype.code = function(e) {
        if (e !== void 0) {
            e.preventDefault();
        }
        return addMDTag(this.editor, "```\n", "\n```", "Code Here" )
    };

    MdEditor.prototype.link = function(e) {
        var cursor;
        if (e !== void 0) {
            e.preventDefault();
        }
        var content = this.editor.doc.getSelection('end')
        if (content.trim() == "" ) {
            content = "Link"
        }
        this.editor.doc.replaceSelection('[' + content + '](http://)');
        cursor = this.editor.doc.getCursor();
        this.editor.doc.setCursor({
            line: cursor.line,
            ch: cursor.ch - 1
        });
        return this.editor.focus();
    };

    MdEditor.prototype.image = function(e) {
        var cursor, url;
        if (e !== void 0) {
            e.preventDefault();
        }
        if (this.options.uploader === false) {
            url = window.prompt(this.options.labelImage);
            this.editor.doc.replaceSelection("![](" + url + ")");
            cursor = this.editor.doc.getCursor();
            this.editor.doc.setCursor({
                line: cursor.line,
                ch: 2
            });
            return this.editor.focus();
        } else {
            return $('.mdeditor_modal', this.element).toggle('fast');
        }
    };

    MdEditor.prototype.list_ul = function(e) {
        if (e !== void 0) {
            e.preventDefault();
        }
        return addMDTag(this.editor, "- ", "", "Unordered List" )
    };

    MdEditor.prototype.list_ol = function(e) {
        if (e !== void 0) {
            e.preventDefault();
        }
        return addMDTag(this.editor, "1. ", "", "Ordered List" )
    };


    MdEditor.prototype.quote = function(e) {
        if (e !== void 0) {
            e.preventDefault();
        }
        return addMDTag(this.editor, "> ", "", "Quote" )
    };

    MdEditor.prototype.fullscreen = function(e) {
        if (e !== void 0) {
            e.preventDefault();
        }
        this.element.toggleClass('is-fullscreen');
        this.editor.refresh();
        return this.updatePreview();
    };

    MdEditor.prototype.save = function(e) {
        if (e !== void 0) {
            e.preventDefault();
        }
        if (this.canExit) {
            return true;
        }
        $.ajax({
            dataType: 'json',
            url: this.form.attr('action'),
            data: this.form.serialize(),
            type: this.form.attr('method')
        }).done((function(_this) {
            return function(data) {
                _this.canExit = true;
                return _this.flash(_this.options.labelSuccess, 'success');
            };
        })(this)).fail((function(_this) {
            return function(jqXHR) {
                return _this.flash(jqXHR.responseText);
            };
        })(this));
        return false;
    };

    MdEditor.prototype._bindEvents = function() {
        this.markdownScroll.click((function(_this) {
            return function() {
                return _this.editor.focus();
            };
        })(this));
        this.editor.on('change', (function(_this) {
            return function() {
                _this.canExit = false;
                return _this.updatePreview();
            };
        })(this));
        this.form.submit((function(_this) {
            return function() {
                _this.canExit = true;
                return true;
            };
        })(this));
        $(document).keydown((function(_this) {
            return function(e) {
                if (e.ctrlKey || e.metaKey || e.altKey) {
                    if (e.which === 83 && _this.options.ctrls) {
                        return _this.save(e);
                    } else if (e.which === 66) {
                        return _this.bold(e);
                    } else if (e.which === 73) {
                        return _this.italic(e);
                    } else if (e.which === 76) {
                        return _this.link(e);
                    }
                }
                if (e.which === 27 && _this.element.hasClass('is-fullscreen')) {
                    return _this.fullscreen(e);
                }
            };
        })(this));
        $(window).bind('beforeunload', (function(_this) {
            return function() {
                if (!_this.canExit) {
                    return _this.options.labelClose;
                }
            };
        })(this));
        this.markdownScroll.scroll((function(_this) {
            return function() {
                if (_this.isMarkdownMoving === false) {
                    _this.scrolling = 'markdown';
                    _this._syncScroll();
                }
                return true;
            };
        })(this));
        return this.previewScroll.scroll((function(_this) {
            return function() {
                if (_this.isPreviewMoving === false) {
                    _this.scrolling = 'preview';
                    _this._syncScroll();
                }
                return true;
            };
        })(this));
    };

    MdEditor.prototype._syncScroll = _.throttle(function() {
        var destScrollTop, markdownScrollTop, previewScrollTop;
        if (!this.preview.is(':visible') || this.markdownSections.length === 0 || this.previewSections.length === 0) {
            return false;
        }
        markdownScrollTop = this.markdownScroll.scrollTop();
        previewScrollTop = this.previewScroll.scrollTop();
        destScrollTop = 0;
        if (this.scrolling === 'markdown') {
            if (Math.abs(markdownScrollTop - this.lastMarkdownScrollTop) <= 9) {
                return false;
            }
            this.scrolling = false;
            this.lastMarkdownScrollTop = markdownScrollTop;
            destScrollTop = this._scrollTop(markdownScrollTop, this.markdownSections, this.previewSections);
            if (Math.abs(destScrollTop - previewScrollTop) <= 9) {
                this.lastPreviewScrollTop = previewScrollTop;
                return false;
            }
            this.isPreviewMoving = true;
            return this.previewScroll.stop().animate({
                scrollTop: destScrollTop
            }, 100, (function(_this) {
                return function() {
                    _this.isPreviewMoving = false;
                    return true;
                };
            })(this));
        }
    }, 100);

    MdEditor.prototype._scrollTop = function(srcScrollTop, srcList, destList) {
        var destSection, posInSection, section, sectionIndex;
        sectionIndex = 0;
        section = _.find(srcList, function(section, index) {
            sectionIndex = index;
            return srcScrollTop < section.endOffset;
        });
        if (section === void 0) {
            return 0;
        }
        posInSection = (srcScrollTop - section.startOffset) / (section.height || 1);
        destSection = destList[sectionIndex];
        return destSection.startOffset + destSection.height * posInSection;
    };

    MdEditor.prototype._buildToolbar = function() {
        $('<button class="mdeditor_header" title="H2"><i class="fa fa-header"></i></button>').appendTo(this.toolbar).click(this.header);
        $('<button class="mdeditor_bold" title="Bold"><i class="fa fa-bold"></i></button>').appendTo(this.toolbar).click(this.bold);
        $('<button class="mdeditor_italic" title="Italic"><i class="fa fa-italic"></i></button>').appendTo(this.toolbar).click(this.italic);
        $('<button class="mdeditor_list_ol" title="Ordered List"><i class="fa fa-list-ol"></i></button>').appendTo(this.toolbar).click(this.list_ol);
        $('<button class="mdeditor_list_ul" title="Unordered List"><i class="fa fa-list-ul"></i></button>').appendTo(this.toolbar).click(this.list_ul);
        $('<button class="mdeditor_link" title="Links"><i class="fa fa-link"></i></button>').appendTo(this.toolbar).click(this.link);
        $('<button class="mdeditor_picture" title="Image"><i class="fa fa-image"></i></button>').appendTo(this.toolbar).click(this.image);
        $('<button class="mdeditor_quote" title="Quote"><i class="fa fa-quote-left"></i></button>').appendTo(this.toolbar).click(this.quote);
        $('<button class="mdeditor_code" title="Code"><i class="fa fa-code"></i></button>').appendTo(this.toolbar).click(this.code);


        $('<button class="pull-right" title="Fullscreen"><i class="fa fa-expand"></i></button>').appendTo(this.toolbar).click(this.fullscreen);
        $('<button class="pull-right" title="Toggle Edit"><i class="fa fa-edit"></i></button>').appendTo(this.toolbar).click(this.toggle_edit);
        $('<button class="pull-right" title="Toggle Preview"><i class="fa fa-eye"></i></button>').appendTo(this.toolbar).click(this.toggle_preview);
        return true;
    };

    MdEditor.prototype._buildDropzone = function() {
        var editor, options, that;
        if (this.options.uploader === false) {
            return false;
        }
        options = this.options;
        editor = this.editor;
        that = this;
        this.dropzone = new Dropzone($('.mdeditor_drop').get(0), {
            maxFiles: 10,
            paramName: 'image',
            url: options.uploader,
            addRemoveLinks: false,
            thumbnailWidth: 150,
            thumbnailHeight: 150,
            init: function() {
                var addButton, drop;
                drop = this;
                addButton = function(file) {
                    var $previewElement;
                    $previewElement = $(file.previewElement);
                    $previewElement.append('<a class="dz-insert"><i class="fa fa-plus-circle"></i></a>');
                    // $previewElement.append('<a class="dz-remove"><i class="fa fa-plus"></i></a>');
                    $('.dz-remove', $previewElement).click(function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        if (window.confirm(options.labelConfirm)) {
                            return $.ajax({
                                url: options.uploader + '/' + file.id,
                                method: 'DELETE'
                            }).done(function(data) {
                                console.log(file);
                                return $(file.previewElement).fadeOut(500, function() {
                                    return drop.removeFile(file);
                                });
                            }).fail(function(jqXHR) {
                                return that.flash(jqXHR.responseText);
                            });
                        }
                    });
                    return $('.dz-insert', $previewElement).click(function(e) {
                        var cursor;
                        e.preventDefault();
                        e.stopPropagation();
                        editor.doc.replaceSelection("![](" + (options.imageURL(file)) + ")");
                        cursor = editor.doc.getCursor();
                        editor.doc.setCursor({
                            line: cursor.line,
                            ch: 2
                        });
                        editor.focus();
                        return $('.mdeditor_modal').hide();
                    });
                };
                this.on('addedfile', function(file) {
                    return addButton(file);
                });
                this.on('sending', function(file, jqXHR, formData) {
                    return $.each(options.uploaderData, function(k, v) {
                        return formData.append(k, v);
                    });
                });
                this.on('success', function(file, response) {
                    $.extend(file, response);
                    return $(file.previewElement).removeClass('dz-processing');
                });
                this.on('error', function(file, errorMessage, xhr) {
                    that.flash(errorMessage);
                    return $(file.previewElement).fadeOut();
                });
                if (options.images) {
                    return $.each(options.images, function(k, image) {
                        drop.options.addedfile.call(drop, image);
                        drop.options.thumbnail.call(drop, image, options.imageURL(image));
                        drop.files.push(image);
                        return addButton(image);
                    });
                }
            }
        });
    };

    MdEditor.prototype._setSections = _.debounce(function() {
        var mdSectionOffset, previewSectionOffset;
        this.markdownSections = [];
        this.previewSections = [];
        mdSectionOffset = null;
        previewSectionOffset = null;
        $('.CodeMirror-code .cm-header', this.element).each((function(_this) {
            return function(index, element) {
                var newSectionOffset;
                if (mdSectionOffset === null) {
                    mdSectionOffset = 0;
                    return;
                }
                newSectionOffset = $(element).offset().top + _this.markdownScroll.scrollTop();
                _this.markdownSections.push({
                    startOffset: mdSectionOffset,
                    endOffset: newSectionOffset,
                    height: newSectionOffset - mdSectionOffset
                });
                mdSectionOffset = newSectionOffset;
            };
        })(this));
        this.markdownSections.push({
            startOffset: mdSectionOffset,
            endOffset: this.markdownScroll[0].scrollHeight,
            height: this.markdownScroll[0].scrollHeight - mdSectionOffset
        });
        this.preview.find('h1, h2, h3, h4, h5').each((function(_this) {
            return function(index, element) {
                var newSectionOffset;
                if (previewSectionOffset === null) {
                    previewSectionOffset = 0;
                    return;
                }
                newSectionOffset = $(element).offset().top + _this.previewScroll.scrollTop();
                _this.previewSections.push({
                    startOffset: previewSectionOffset,
                    endOffset: newSectionOffset,
                    height: newSectionOffset - previewSectionOffset
                });
                previewSectionOffset = newSectionOffset;
            };
        })(this));
        this.previewSections.push({
            startOffset: previewSectionOffset,
            endOffset: this.previewScroll[0].scrollHeight,
            height: this.previewScroll[0].scrollHeight - previewSectionOffset
        });
        this.lastMardownScrollTop = -10;
        this.lastPreviewScrollTop = -10;
    }, 500);

    return MdEditor;

})();