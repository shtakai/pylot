$(function(){

    //-- Category and Type admin
    var modalCatType = $("#modal-cat-type")
    modalCatType.on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget) // Button that triggered the modal
        var modal = $(this)
        var nameEl = modal.find(".modal-body [name='name']")
        var slugEl = modal.find(".modal-body [name='slug']")
        var delButton = modal.find("button.delete-btn")

        if (button.data("id") == "") {
            delButton.hide()
        } else {
            delButton.show()
        }
        slugEl.slugify(nameEl)
        modal.find("input[name='action']").val("update")
        modal.find("[name='id']").val(button.data("id"))
        nameEl.val(button.data("name"))
        slugEl.val(button.data("slug"))
    })
    modalCatType.find("button.delete-btn").click(function(){
        if(confirm("Do you want to DELETE this ?")) {
            modalCatType.find("input[name='action']").val("delete")
            modalCatType.find("form").submit()
        }
    })


    //-- Inline Category in Post Edit
    var modalCatInline = $("#modal-insert-cat-inline")
    var modalCatInlineForm = modalCatInline.find("form").first()
    var modalCatInlineSaveBtn = modalCatInlineForm.find(".save-button")

    modalCatInlineSaveBtn.click(function(){
        $.post(modalCatInlineForm.attr("action"), modalCatInlineForm.serialize(), function(data){
            if (data.status == "OK") {

                var label = $("<label />", {text: data.name})
                var field = $("<input />", {type: "checkbox",
                                            name: "post_categories",
                                            value: data.id,
                                            checked: "checked"})
                $("<div />", {"class": "checkbox-group"})
                    .append(field)
                    .append(label)
                    .appendTo($(".post-categories-list"))
            } else {
                alert("Couldn't save the category. It probably exists already")
            }
        }, "json")
        modalCatInline.modal('hide')
    })


    //-- Edit Post
    var formPostEdit = $("#form-post-edit");
    if (formPostEdit.length > 0) {
        var titleInput = formPostEdit.find("[name='title']")
        var statusInput = formPostEdit.find("[name='status']")
        var postType = formPostEdit.find("[name='type_id']")
        var contentInput = formPostEdit.find("[name='content']")
        var slugInput = formPostEdit.find("[name='slug']").first()

        // Slug
        slugInput.slugify(titleInput)

        $(".action-btn").click(function(){
            var el = $(this)
            var action = el.data("action")

            if (action == "draft" || action == "publish") {
                if (titleInput.val().trim() == "") {
                    alert("Your Post Title is missing")
                } else if (! postType.is(":checked")) {
                    alert("You need to select a post type")
                } else {
                    statusInput.val(action)
                    formPostEdit.submit()
                }

            } else if (action == "delete") {
                if (confirm("Do you really want to delete this post ?")) {
                    statusInput.val("delete")
                    formPostEdit.submit()
                }
            }
        })
    }
})