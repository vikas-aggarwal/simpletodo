require.config({
    paths: {
	"jquery" : "libs/jquery-1.11.3.min",
	"mustache" : "libs/mustache.min",
	"jstz" : "libs/jstz"
    }
});


requirejs(['mustache','jquery','jstz','recur','utils'],
	  function(Mustache,$,jstz){

	      window.tasks = null; //TODO delete
	      window.taskStats = null; //TODO delete
	      
	      //load Tasks
	      $.when($.ajax('../todos'),$.ajax('../todos/logs/stats')).done(
		  function(responseTaskdata,stats){
		      tasks = responseTaskdata; //TODO delete
		      taskStats = stats;  //TODO delete
		      processTasks(responseTaskdata[0], stats[0]);
		  });


	      var buckets = {"alertTasks":[],"todaysTasks":[],"pendingTasks":[],"upcomingTasks":[]};
	      var bucketDetectors = {"alertTasks":{"method":taskToBeRemindedToday,"value":true},
				      "todaysTasks":{"method":taskComparedToToday,"value":0},
				      "pendingTasks":{"method":taskComparedToToday,"value":-1},
				      "upcomingTasks":{"method":taskComparedToToday,"value":1}};

	      function processTasks(tasks, stats) {
		  for(var taskIndex in tasks) {
		      var task = tasks[taskIndex];
		      
		      //if due_date not present in task , make current time as due date
		      if(!('due_date' in task))
		      {
			  task.due_date = {};
			  task.due_date['$date'] = (new Date()).getTime();
		      }

		      var bucket = getTaskBucket(task)
		      buckets[bucket].push(task);
		  }
		  renderTasks();
	      }

	      function getTaskBucket(task) {
		  for(bucket in bucketDetectors) {
		      if(bucketDetectors[bucket].method(task) == bucketDetectors[bucket].value)
			  return bucket;
		  }
		  return "todaysTasks"; //default
	      }

	      function renderTasks() {
		  var template = document.getElementById("taskCardTemplate");
		  var templateContent = template.innerHTML;
		  for(var bucket in buckets) {
		      var tasks = buckets[bucket];
		      for(var taskIndex in tasks) {
			  var task = tasks[taskIndex];
			  var dateValue=new Date(0);
			  dateValue.setUTCSeconds(task.due_date['$date']/1000);
			  
			  $("#"+bucket).append(Mustache.render(templateContent, {"Title":task.task,"Frequency":task.frequency,"DueDate":dateValue.toLocaleDateString()}))
		      }
		  }
	      }
	  });
	  
