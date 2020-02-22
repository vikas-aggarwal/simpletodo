/// <reference path="./libs/jquery-1.11.3.min.js" />
/// <reference path="./utils.js" />
/// <reference path="./recur.js" />
/// <reference path="./libs/require.min.js" />


require.config({
    shim : {
	'jquerymobile' : {
	    deps : ['jquery']
	}
    },
    paths: {
	"jquery" : "libs/jquery-1.11.3.min",
	"jquerymobile" : "libs/jquery.mobile-1.4.1.min",
	"mustache" : "libs/mustache.min",
	"jstz" : "libs/jstz"
    }
});






requirejs(['mustache','jquery','jstz','recur','utils','jquerymobile'],
	  function(Mustache,$,jstz){

	      var locale = document.documentElement.lang;
	      var timeZoneString = jstz.determine().name();
	
	      $("#loadingPane").css("display","none");    


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



var allTasks;
function processTasks(tasks)
{
    allTasks = tasks;
    for(var t in tasks)
    {
	var task = tasks[t];
	//if due_date not present in task , make current time as due date
	if(!('due_date' in task) || !task.due_date)
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
    var newDate = new Date($("#"+payload.todo_id+"_date").val());
    newDate.setHours(0);
    newDate.setMinutes(0);
    newDate.setSeconds(0);
    newDate.setMilliseconds(0);
    payload['due_date']= Math.floor(newDate.getTime()/1000);
    var dateStr=newDate.toLocaleDateString(locale, {timeZone : timeZoneString});
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
	    $("#"+task.todo_id+"_date").val(getDateInLocalISO(nextDate));
	    updateUIForNextDate(task.todo_id,nextDate);
	}
    }
}


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
		  });

		  
		  if($(event.target).hasClass("done-button") && todo_id!=-1)
		  {
		      markAsDone(todo_id);
		  }
		  else if(todo_id != -1)
		  {
		      markAsSkip(todo_id);
		  }
		      
	     }); 
	      
	      $("#refreshData").bind("click", function(e) {
		  loadTasks();
	      });

	    $("#createSubmitBtn").bind("click",function(e)
				               {
						   var subData={};
						   subData.task=$("#create_taskTitle").val();
						   subData.frequency=$("#create_freq").val();
						   if($("#create_dueDate").val())
						   {
						       var dueDate = new Date($("#create_dueDate").val());
						       dueDate.setHours(0)
						       dueDate.setMinutes(0);
						       dueDate.setSeconds(0);
						       dueDate.setMilliseconds(0);

						       subData.due_date=dueDate.getTime()/1000
						   }
						   subData.timeSlot=$("input[name='create_slot']:checked").val();
						   subData.timeSlot=subData.timeSlot.substring(subData.timeSlot.indexOf("slot")+4)
						   subData.remindBeforeDays=$("#create_remindBeforeDays").val();
						   subData.trackHabit=$("#create_trackHabit").prop("checked");
						   $.ajax({type:'POST',url:'../todos',data:JSON.stringify(subData),contentType:"application/json"}).done(
						       function(data)
						       {
							   //clear all values
							   $("#create_taskTitle").val("");
							   $("#create_freq").val("");
							   $("#create_dueDate").val("")
							   $("#create_remindBeforeDays").val("");
							   $("#create_slotNone").prop("checked",true);
							   $("input[name='create_slot']").checkboxradio("refresh");
							   $("#create_trackHabit").prop("checked",false).checkboxradio("refresh");
							   $( ":mobile-pagecontainer" ).pagecontainer( "change", "#mainpage" );
						       }
						   );
						   
						   
					       });
	    



	    $("#editSubmitBtn").bind("click",function(e)
				             {
						 var subData={};
						 subData.task=$("#edit_taskTitle").val();
						 subData.frequency=$("#edit_freq").val();
						 if($("#edit_dueDate").val())
						 {
						     var dueDate = new Date($("#edit_dueDate").val());
						     dueDate.setHours(0)
						     dueDate.setMinutes(0);
						     dueDate.setSeconds(0);
						     dueDate.setMilliseconds(0);

						     subData.due_date=dueDate.getTime()/1000
						 }
						 subData.timeSlot=$("input[name='edit_slot']:checked").val();
						 subData.timeSlot=subData.timeSlot.substring(subData.timeSlot.indexOf("slot")+4)
						 subData.remindBeforeDays=$("#edit_remindBeforeDays").val();
						 subData.trackHabit=$("#edit_trackHabit").prop("checked");
						 var todo_id=$("#edit_todo_id").val();
						 
						 $.ajax({type:'POST',url:'../todos/'+todo_id,data:JSON.stringify(subData),contentType:"application/json"}).done(
						     function(data)
						     {
							 console.log(data);
							 $( ":mobile-pagecontainer" ).pagecontainer( "change", "#mainpage" );
						     }
						 );
						 
						 
					     });
	    


	      function renderTasks(tasks,taskIdWiseStats)
	      {
		  for(var t in tasks)
		  {
		      var task = tasks[t];
		      var view={};
		      view.taskName=task.task;
		      if(view.taskName+"" == ""){
			  view.taskName = "<No Title>";
		      }
		      view.taskFrequency=task.frequency;
		      var dateValue=new Date(0);
		      dateValue.setUTCSeconds(task.due_date['$date']/1000);
		      view.dateString=dateValue.toLocaleDateString(locale, {timeZone : timeZoneString});
		      view.todo_id=task.todo_id;
		      view.timeSlot=task.timeSlot || 'None';
		      view.trackHabit=task.trackHabit;
		      
		      if('due_in_days' in task)
		      {
			  view.dueIn=(task.due_in_days != 1)?"Due in "+task.due_in_days+" days":"Due Tomorrow";	
		      }
		      
		      if(task.todo_id in taskIdWiseStats && task.trackHabit) {
			  view.doneCount = taskIdWiseStats[task.todo_id].done;
			  view.skipCount = taskIdWiseStats[task.todo_id].skip;
			  view.donePercent = Math.floor(view.doneCount*100/(view.doneCount+view.skipCount));
			  view.skipPercent = Math.floor(view.skipCount*100/(view.doneCount+view.skipCount));
		    }
		      else if(task.trackHabit){
			  view.doneCount = 0;
			  view.skipCount = 0;
			  view.donePercent = 0;
			  view.skipPercent = 0;
		      }
		      
		      if(shouldRenderTask(view))
			  $('#tasklistdata').append(Mustache.render(document.getElementById("listview-template").innerHTML, view));
		}
		
	      }


	      function shouldRenderTask(taskData) {
		  if(filters.length > 0){
		      for(var index in filters){
			  var filterFreq = filters[index];
			  if(taskData.taskFrequency === filterFreq){
			      return true;
			  }
		      }

		      return false;
		  }
		  
		  return true;
	      }


	      function processStats(statsResponse){
		  var taskWiseStats = {};
		  (statsResponse[0][0]).forEach(function(stat) {
		      if("todo_id" in stat && "action" in stat){
			  var todoId = stat.todo_id;
			  var action = stat.action;

			  if(!(todoId in taskWiseStats)){
			      taskWiseStats[todoId] = {done:0,skip:0};
			  }

			  if(action === "Done"){
			      taskWiseStats[todoId].done=stat.count;
			  }
			  else if(action === "Skip"){
			      taskWiseStats[todoId].skip=stat.count;
			  }
		      }
		  });
		  return taskWiseStats;
	      }
	    

	    
	      var tasks={};
	      function loadTasks() {
		  $.when($.ajax('../todos'),$.ajax('../todos/logs/stats')).done(
		      function(responseTaskdata,stats){
			  
			  var taskIdWiseStats = processStats(stats);
			  $('#tasklist').html('');
			  $('#tasklist').append('<ul data-role="listview" id="tasklistdata"></ul>');
			  $('#tasklist').trigger("create");
			  tasks=responseTaskdata[0];
			  var data=tasks;
			  processTasks(tasks);

			  /*Alerts*/
			  $('#tasklistdata').append('<li data-role="list-divider">Alerts</li>');
			  var alertTasks=[];
			  for(var t in data) //Pending
			  {
			      var task = data[t];
			      
			      if(taskToBeRemindedToday(task))
			      {
				  alertTasks.push(task);
			      }
			
			  }
			  
			  renderTasks(alertTasks,taskIdWiseStats);
			  
			  
			  
			  
			  /* Pending tasks */
			  
			  
			  $('#tasklistdata').append('<li data-role="list-divider">Pending</li>');
			  var pendingTasks=[];
			  for(t in data) //Pending
			  {
			      task = data[t];
			      
			      if(taskComparedToToday(task)<0)
			      {
				  pendingTasks.push(task);
			      }
			      
			  }
			  
			  renderTasks(pendingTasks,taskIdWiseStats);
			  
			  
			  
			  /* Today's Tasks */
			  var todaysTasks=[];
			  $('#tasklistdata').append('<li data-role="list-divider">Today</li>');
			  for(t in data) //Today
			  {
			      task = data[t];
			      
			      if(taskComparedToToday(task)==0)
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
			  renderTasks(todaysTasks,taskIdWiseStats);
			  
			  /* Upcoming Tasks */
			  var upcomingTasks=[];
			  $('#tasklistdata').append('<li data-role="list-divider">Upcoming</li>');
			  for(t in data) //Upcoming
			  {
			      task = data[t];
			      
			      if(taskComparedToToday(task)>0 && !taskToBeRemindedToday(task)) //reminded tasks already in Todays list
			      {
				  upcomingTasks.push(task);
			      }
			      
			      
			  }
			  renderTasks(upcomingTasks,taskIdWiseStats);
			  
			  
			  
			  
		    
			  $('#tasklistdata').listview("refresh");
		    	  
			  $('#tasklistdata').ready(function()
					     {
						 $("input[id$='_date']")
						     .change(function()
							     {
								 
								 var todo_id=this.id.substring(0,this.id.indexOf("_"));
								 updateUIForNextDate(todo_id,this.value);									 									
							     } );
						 calculateNextDayForTodos();
					     });
			  
			  $('#tasklistdata').ready(function(){
			      $("#tasklistdata li").on("taphold",function(event){
				 
				  var objectId=event.currentTarget.attributes['data-region-id'].value;
				  objectId=objectId.substr(0,objectId.indexOf('_'));
				  var taskToDelete = tasks.find(function(f){if(f.todo_id==objectId){return true;}else{return false;}});
				  var d = confirm("Delete : "+taskToDelete.task+"?");
				  if(d==true)
				  {
				      $("."+objectId+"_action").addClass("ui-state-disabled");
				      $.ajax({url:"../todos/"+objectId,method:"DELETE"});
				      $("[data-region-id='"+objectId+"_region'] div.ui-grid-a").get(0).style.background="brown";
				  }
				  
			      });
			  });
		      });
		  
		  $('#tasklistdata').ready(function(){
		      
		      $("#tasklist").on("click","[id$='edit_link']",function(event)
					{
					    
					    var todo_id=event.currentTarget.id;
					    todo_id=todo_id.substring(0,todo_id.indexOf("_"));
					    $("#edit_todo_id").val(todo_id);
					    $.ajax('../todos/'+todo_id).done(
						function(data){
						    var task=data[0];
						    $("#edit_taskTitle").val(task.task);
						    $("#edit_freq").val(task.frequency);
						    $("#edit_remindBeforeDays").val(task.remindBeforeDays);
						    if('due_date' in task)
						    {
							var dateValue=new Date(0);
							dateValue.setUTCSeconds(task.due_date['$date']/1000);
							$("#edit_dueDate").val(getDateInLocalISO(dateValue));
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
						    
						    $("input[name='edit_slot']").checkboxradio("refresh");
						    $( ":mobile-pagecontainer" ).pagecontainer( "change", "#editPage" );
						});
					    
					}
					
				       );
		  });
		  
	      }


	      var filters = [];
	      $("#filterDoneButton").on("click", function(){
		  filters = [];
		  if($("#dailyFilterCheckbox").get(0).checked){
		      filters.push($("#dailyFilterCheckbox").get(0).value);
		  }
		  loadTasks();
		  $("#filterPopup").popup("close");
		  if(filters.length > 0){
		      $("#filterData").addClass("filter-active");
		  }
	      });
	      
	      $("#filterClearButton").on("click", function(){
		  $("#dailyFilterCheckbox").get(0).checked = false;
		  $("#dailyFilterCheckbox").checkboxradio("refresh");
		  filters = [];
		  loadTasks();
		  $("#filterPopup").popup("close");
		  $("#filterData").removeClass("filter-active");
	      });

	      $( "#filterPopup" ).on( "popupafteropen", function( event, ui ) {
		  if(filters.length == 0) {
		      $("#dailyFilterCheckbox").get(0).checked = false;
		      $("#dailyFilterCheckbox").checkboxradio("refresh");
		  }
	      } );
	      
	      var temp;    
	      loadTasks();
	    

});
