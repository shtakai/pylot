$(function(){

    var modalCatType = $("#modal-cat-type")
    modalCatType.on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget) // Button that triggered the modal
        var modal = $(this)
        modal.find("input[name='action']").val("update")

        var id = button.data("id")
        if (id == "undefined") {
            modal.find("input[name='action']").val("new")
        }

        modal.find(".modal-body [name='id']").val(button.data("id"))
        modal.find(".modal-body [name='name']").val(button.data("name"))
        modal.find(".modal-body [name='slug']").val(button.data("slug"))
    })

    modalCatType.find("button.delete-btn").click(function(){
        if(confirm("Do you want to DELETE this ?")) {
            modalCatType.find("input[name='action']").val("delete")
            modalCatType.find("form").submit()
        }
    })
})