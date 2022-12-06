// Toggle for task, red to green, incomplete to complete functionality
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

// Delete task
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

// Update task
$("form#updateTask").submit(async function() {
    var idInput = $('input[name="formId"]').val().trim();
    var titleInput = $('input[name="formTitle"]').val().trim();
    var descriptionInput = $('input[name="formDescription"]').val().trim();
    if (titleInput && descriptionInput) {
        // Create Ajax Call
        $.ajax({
            url: '/events/edittask',
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

// Edit task form
function editTask(id, eid) {
    if (id) {
      tr_id = "#task-" + id;
      title = $(tr_id).find(".taskTitle").text();
      description = $(tr_id).find(".taskDescription").text();
      $('#event-id').val(eid);
      $('#task-id').val(id);
      $('#task-title').val(title);
      $('#task-description').val(description);
    }
  }

  // Update task view after editing
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

// Publish event
async function setPublish(event_id) {
    $.ajax({
        url: 'publish',
        type: 'get',
        data: {
            event_id: event_id,
        },
        success: function(response) {
            if(response.publish == true)
            {
               $("#publish-"+event_id).html("Unpublish");
            }
            else
            {
                $("#publish-"+event_id).html("Publish");
            }
        }
    });
}

// Register for an event
async function register(event_id, user_id) {
        $.ajax({
            url: 'home/register',
            type: 'get',
            data: {
                event_id: event_id,
                user_id: user_id,
            },
            dataType: 'json',
            success: function (response) {
                if (response.register_success == true) {
                    alert("You have been registered! Check our 'Registered Events page'");
                } 
                if (response.register_success == false) { 
                    alert("You are already registered.");
                }
            } 
        });
}
    