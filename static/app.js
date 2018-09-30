require.config({
    shim : {
	'jquerymobile' : {
	    deps : ['jquery']
	},
	'jquery-ui/datepicker' : {
	    deps : ['jquerymobile']
	},
	'jquerymobile/datepicker' : {
	    deps : ['jquery-ui/datepicker']
	}
    },
    paths: {
	"jquery" : "https://code.jquery.com/jquery-1.11.3.min",
	"jquerymobile" : "https://code.jquery.com/mobile/1.4.1/jquery.mobile-1.4.1.min",
	"jquery-ui/datepicker" : "https://rawgithub.com/jquery/jquery-ui/1.10.4/ui/jquery.ui.datepicker",
	"jquerymobile/datepicker" : "https://rawgithub.com/arschmitz/jquery-mobile-datepicker-wrapper/master/jquery.mobile.datepicker",
	"mustache" : "https://cdnjs.cloudflare.com/ajax/libs/mustache.js/2.3.0/mustache.min"
    }
});






requirejs(['mustache','jquery','recur','utils','jquerymobile','jquery-ui/datepicker','jquerymobile/datepicker'],
	  function(Mustache){

    

//TODO should not be global
var dateFormat='dd-M-yy';

function initCreatePage()
{
    $("#createPage").page({
	beforecreate : function(){$("#create_content").prepend(Mustache.render($("#task_form_template").text(),{"action":"create"}))}
    });

}


function initEditPage()
{
    $("#editPage").page({
	beforecreate : function(){$("#edit_content").prepend(Mustache.render($("#task_form_template").text(),{"action":"edit"}))}
    });
    
}


function initDatePicker()
{
    
    $.datepicker.setDefaults({dateFormat: dateFormat,showOn: "button",
			      buttonImage: "https://cdnjs.cloudflare.com/ajax/libs/Zebra_datepicker/1.9.4/images/calendar.png",
			      buttonImageOnly: true,
			      buttonText: "Select date"});
}



var allTasks;
function processTasks(tasks)
{
    allTasks = tasks;
    for(var t in tasks)
    {
	var task = tasks[t];
	//if due_date not present in task , make current time as due date
	if(!('due_date' in task))
	{
	    task.due_date = {};
	    task.due_date['$date'] = (new Date()).getTime();
	}
	var taskComparedToday = taskComparedToToday(task);
	if(taskComparedToday == 0)
	{
	    task.task_state = "today";
	}
	else if(taskComparedToday < 0)
	{
	    task.task_state= "pending";
	}
	else
	{
	    task.task_state = "upcoming";
	    if(taskToBeRemindedToday(task))
	    {
		task.due_in_days = calculateRemainingDays(task);
	    }
	}
	
    }
}
    


function markAsDone(todo_id)
{
    var payload={};
    payload.todo_action="Done";
    payload.todo_id=todo_id;
    updateDoneOrSkip(payload);
}

function markAsSkip(todo_id)
{
    var payload={};
    payload.todo_action="Skip";
    payload.todo_id=todo_id;
    updateDoneOrSkip(payload);
}

function updateDoneOrSkip(payload)
{
    var todo_id=payload.todo_id;
    var newDate = $("#"+payload.todo_id+"_date").datepicker("getDate");
    payload['due_date']= Math.floor(newDate.getTime()/1000);
    var dateStr=$.datepicker.formatDate(dateFormat,newDate)
    $("#"+todo_id+"_loading").css("display","");
    $("#"+todo_id+"_label_due").html(dateStr);
    $("."+todo_id+"_action").addClass("ui-state-disabled");
    $.ajax({url:'../todos/'+todo_id,type:"POST",
	    data:JSON.stringify(payload),
	    contentType:"application/json"})
	.done(
	    function(data)
	    {
		$("#"+todo_id+"_loading").css("display","none");
		$("#"+todo_id+"_success").css("display","");
	    }
	).fail(
	    function()
	    {
		$("#"+todo_id+"_loading").css("display","none");
		$("#"+todo_id+"_failed").css("display","");
		$("."+todo_id+"_action").removeClass("ui-state-disabled");
	    }
	);
    
}




function updateUIForNextDate(todo_id,dateStr)
{
    $("#"+todo_id+"_label_next").html(dateStr);
    $("."+todo_id+"_action").removeClass("ui-state-disabled");
}



function calculateNextDayForTodos()
{
    for(var t in allTasks)
    {
	var task = allTasks[t];
	var freq = parseFrequency(task.frequency);
	var dateValue=new Date(0);
	dateValue.setUTCSeconds(task.due_date['$date']/1000);
	var nextDate = getNextOccurrence(freq,dateValue);
	if(nextDate!=null)
	{
	    $("#"+task.todo_id+"_date").datepicker("setDate",$.datepicker.formatDate(dateFormat,nextDate));
	    updateUIForNextDate(task.todo_id,$.datepicker.formatDate(dateFormat,nextDate));
	}
    }
}



	    initDatePicker();
	    initCreatePage();
	    initEditPage();

	    //tasklist listener on all done and skip objects
	      $("#tasklist").on("click",".todo-button",function(event){
		  var classes = $(event.target).attr("class").split(/\s+/);
		  var todo_id = -1;
		  classes.forEach(function(c){
		      if(c.endsWith("action"))
		      {
			  todo_id = c.substring(0,c.indexOf("_"));
		      }
		  })

		  
		  if($(event.target).hasClass("done-button") && todo_id!=-1)
		  {
		      markAsDone(todo_id);
		  }
		  else if(todo_id != -1)
		  {
		      markAsSkip(todo_id);
		  }
		      
	     }); 
	      
	    //TODO move these 2 lines
	    $("#create_dueDate").datepicker();
	    $("#edit_dueDate").datepicker();


	    $("#createSubmitBtn").bind("click",function(e)
				               {
						   var subData={};
						   subData.task=$("#create_taskTitle").val();
						   subData.frequency=$("#create_freq").val();
						   if($("#create_dueDate").datepicker("getDate")!=null)
						   {
						       subData.due_date=$("#create_dueDate").datepicker("getDate").getTime()/1000
						   }
						   subData.timeSlot=$("input[name='create_slot']:checked").val();
						   subData.timeSlot=subData.timeSlot.substring(subData.timeSlot.indexOf("slot")+4)
						   subData.remindBeforeDays=$("#create_remindBeforeDays").val();
						   subData.trackHabit=$("#create_trackHabit").prop("checked");
						   $.ajax({type:'POST',url:'../todos',data:JSON.stringify(subData),contentType:"application/json"}).done(
						       function(data)
						       {
							   console.log(data);
							   $( ":mobile-pagecontainer" ).pagecontainer( "change", "#mainpage" );
						       }
						   )
						   
						   
					       });
	    



	    $("#editSubmitBtn").bind("click",function(e)
				             {
						 var subData={};
						 subData.task=$("#edit_taskTitle").val();
						 subData.frequency=$("#edit_freq").val();
						 if($("#edit_dueDate").datepicker("getDate")!=null)
						 {
						     subData.due_date=$("#edit_dueDate").datepicker("getDate").getTime()/1000
						 }
						 subData.timeSlot=$("input[name='edit_slot']:checked").val();
						 subData.timeSlot=subData.timeSlot.substring(subData.timeSlot.indexOf("slot")+4)
						 subData.remindBeforeDays=$("#edit_remindBeforeDays").val();
						 subData.trackHabit=$("#edit_trackHabit").prop("checked");
						 todo_id=$("#edit_todo_id").val();
						 
						 $.ajax({type:'POST',url:'../todos/'+todo_id,data:JSON.stringify(subData),contentType:"application/json"}).done(
						     function(data)
						     {
							 console.log(data);
							 $( ":mobile-pagecontainer" ).pagecontainer( "change", "#mainpage" );
						     }
						 )
						 
						 
					     });
	    


	    function renderTasks(tasks)
	    {
		for(t in tasks)
		{
		    task = tasks[t];
		    var view={};
		    view.taskName=task.task;
		    view.taskFrequency=task.frequency;
		    dateValue=new Date(0);
		    dateValue.setUTCSeconds(task.due_date['$date']/1000);
		    view.dateString=$.datepicker.formatDate(dateFormat,dateValue)
		    view.todo_id=task.todo_id
		    view.timeSlot=task.timeSlot || 'None'
		    view.trackHabit=task.trackHabit;
		    if('due_in_days' in task)
		    {
			view.dueIn=(task.due_in_days != 1)?"Due in "+task.due_in_days+" days":"Due Tomorrow";	
		    }
		    $('#tasklistdata').append(Mustache.render(document.getElementById("listview-template").innerHTML, view));
		}
		
	    }
	    

	    
	    tasks={};
	    $.ajax('../todos').done(
		function(data){
		    
		    $('#tasklist').append('<ul data-role="listview" id="tasklistdata"></ul>')
		    $('#tasklist').trigger("create")
		    tasks=data
		    processTasks(tasks);





		    /* Pending tasks */

		    
		    $('#tasklistdata').append('<li data-role="list-divider">Pending</li>')
		    pendingTasks=[];
		    for(t in data) //Pending
		    {
			task = data[t];
			
			if(taskComparedToToday(task)<0)
			{
			    pendingTasks.push(task);
			}
			
		    }

		    renderTasks(pendingTasks);
		    


		    /* Today's Tasks */
		    todaysTasks=[];
		    $('#tasklistdata').append('<li data-role="list-divider">Today</li>')
		    for(t in data) //Today
		    {
			task = data[t];
			
			if(taskComparedToToday(task)==0 || taskToBeRemindedToday(task))
			{
			    todaysTasks.push(task);
			}
			
			
		    }
		    todaysTasks.sort(function(a,b)
				     {
					 if(a.timeSlot==undefined)
					 {
					     return 1;
					 }
					 if(b.timeSlot==undefined)
					 {
					     return -1;
					 }
					 if(a.timeSlot < b.timeSlot)
					 {
					     return -1;
					 }
					 else if(a.timeSlot==b.timeSlot)
					 {
					     return 0;
					 }
					 return 1;
				     });
		    renderTasks(todaysTasks);
		    
		    /* Upcoming Tasks */
		    upcomingTasks=[];
		    $('#tasklistdata').append('<li data-role="list-divider">Upcoming</li>')
		    for(t in data) //Upcoming
		    {
			task = data[t];

			if(taskComparedToToday(task)>0 && !taskToBeRemindedToday(task)) //reminded tasks already in Todays list
			{
			    upcomingTasks.push(task);
			}
			

		    }
		    renderTasks(upcomingTasks);

		    


		    
		    $('#tasklistdata').listview("refresh");
		    					     
		    $('#tasklistdata').ready(function()
					     {
						 $("input[id$='_date']")
						     .datepicker({
							 onSelect :   function(dateStr,datePickerObject)
							             {
									 
									 todo_id=datePickerObject.id.substring(0,datePickerObject.id.indexOf("_"))
									 updateUIForNextDate(todo_id,dateStr);									 									
								     }
							 
							 
						     })
						 calculateNextDayForTodos();
					     })
		    $('#tasklistdata').ready(function(){
			$("#tasklistdata li").on("taphold",function(event){
			    
			    
			    objectId=event.currentTarget.attributes['data-region-id'].value;
			    objectId=objectId.substr(0,objectId.indexOf('_'))
			    taskToDelete = tasks.find(function(f){if(f.todo_id==objectId){return true}});
			    var d = confirm("Delete : "+taskToDelete.task+"?")
			    if(d==true)
			    {
				$("."+objectId+"_action").addClass("ui-state-disabled");
				$.ajax({url:"../todos/"+objectId,method:"DELETE"})
				$("[data-region-id='"+objectId+"_region'] div.ui-grid-a").get(0).style.background="brown"
			    }
			    
			})
		    })


		    
		})
	    $('#tasklistdata').ready(function(){
		
		$("#tasklist").on("click","[id$='edit_link']",function(event)
				  {

				      todo_id=event.currentTarget.id;
				      todo_id=todo_id.substring(0,todo_id.indexOf("_"));
				      $("#edit_todo_id").val(todo_id);
				      $.ajax('../todos/'+todo_id).done(
					  function(data){
					      task=data[0];
					      $("#edit_taskTitle").val(task.task);
					      $("#edit_freq").val(task.frequency);
					      $("#edit_remindBeforeDays").val(task.remindBeforeDays);
					      if('due_date' in task)
					      {
						  dateValue=new Date(0);
						  dateValue.setUTCSeconds(task.due_date['$date']/1000);
						  console.log(task);
						  console.log(dateValue);
						  $("#edit_dueDate").datepicker("setDate",dateValue)
					      }
					      $("#edit_slot"+(task.timeSlot||'None')).prop("checked",true);
					      if('trackHabit' in task)
					      {
						  $("#edit_trackHabit").prop("checked",task.trackHabit).checkboxradio("refresh");
					      }
					      else
					      {
						  $("#edit_trackHabit").prop("checked",false).checkboxradio("refresh");
					      }
					      
					      $("input[name='edit_slot']").checkboxradio("refresh")
					      $( ":mobile-pagecontainer" ).pagecontainer( "change", "#editPage" );
					  })
				      
				  }

				 )
	    })


	    

	    var temp;    

	    

});
