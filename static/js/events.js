async function togglecomplete(task_id){ 
    $.ajax({
    url: '/events/togglecomplete', 
    type: 'get',
    data: {
    task_id: task_id, 
    },
    success: function(response){
    if(response.complete == true) 
    {
    $("#task-"+response.tid).removeClass("incomplete");
    $("#task-"+response.tid).addClass("complete"); 
    }
    else 
    {
    $("#task-"+response.tid).removeClass("complete");
    $("#task-"+response.tid).addClass("incomplete"); 
    }
    } 
    });
}

async function delete_t(task_id){ 
    $.ajax({
    url: '/events/deletetask', 
    type: 'get',
    data: {
    task_id: task_id, 
    },
    success: function(response){

    if(response.delete_success == true) 
    {
    $("#task-"+response.tid).hide(); 
    }
    } 
    });
}

$("form#updateTask").submit(async function() {
    var idInput = $('input[name="formId"]').val().trim();
    var titleInput = $('input[name="formTitle"]').val().trim();
    var descriptionInput = $('input[name="formDescription"]').val().trim();
    if (titleInput && descriptionInput) {
        // Create Ajax Call
        $.ajax({
            // url: '{% "task_ajax_update" %}',
            url: '/events/edittask',
            type: 'get',
            data: {
                id: idInput,
                title: titleInput,
                description: descriptionInput,
            },
            dataType: 'json',
            success: function (data) {
                if (data.task) {
                  updateToTaskTable(data.task);
                }
            }
        });
       } else {
        alert("All fields must have a valid value.");
    }
    $('form#updateTask').trigger("reset");
    $('#myModal').modal('hide');
    return false;
});

// Update Django Ajax Call
function editTask(id) {
    if (id) {
      tr_id = "#task-" + id;
      title = $(tr_id).find(".taskTitle").text();
      description = $(tr_id).find(".taskDescription").text();
      $('#task-id').val(id);
      $('#task-title').val(title);
      $('#task-description').val(description);
    }
  }

function updateToTaskTable(task){
    $("#task-" + task.id).children(".taskData").each(function() {
        var attr = $(this).attr("name");
        if (attr == "title") {
        $(this).text(task.title);
        } else if (attr == "description") {
        $(this).text(task.description);
        }
    });
}