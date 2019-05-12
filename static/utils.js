function calculateRemainingDays(task)
{
    if("remindBeforeDays" in task && !isNaN(task.remindBeforeDays))
    {
	//remindBeforeDays should be positive
	if(parseInt(task.remindBeforeDays,10) <= 0)
	{
	    return 0;
	}
	
	var dateValue=new Date(0);
	dateValue.setUTCSeconds(task.due_date['$date']/1000);
	var sysDate = new Date();
	sysDate.setHours(0);
	sysDate.setMinutes(0);
	sysDate.setSeconds(0);
	sysDate.setMilliseconds(0);
	if(dateValue.getTime() > sysDate.getTime())
	{
	    //+1 beacuse task due date is considered at 00:00 hrs, but we want at 23:59 hrs while calculating days
	    return Math.round((dateValue.getTime()-sysDate.getTime())/(24*60*60*1000));
	    
      	    
	}
    }
    
    return 0;
}

function taskComparedToToday(task)
{
    var dateValue=new Date(0);
    dateValue.setUTCSeconds(task.due_date['$date']/1000);
    var sysDate = new Date();
    sysDate.setHours(0);
    sysDate.setMinutes(0);
    sysDate.setSeconds(0);
    sysDate.setMilliseconds(0);
    
    if(dateValue.getTime() < sysDate.getTime() && dateValue.toDateString() != sysDate.toDateString())
    {
	return -1;
    }
    else   if(dateValue.toDateString() == sysDate.toDateString())
    {
	return 0;
    }
    else
    {
	return 1;
    }
    
}


function taskToBeRemindedToday(task)
{
    if(taskComparedToToday(task) > 0 && "remindBeforeDays" in task && !isNaN(task.remindBeforeDays))
    {
	//remindBeforeDays should be positive
	if(parseInt(task.remindBeforeDays,10) <= 0)
	{
	    return false;
	}
	
	var dateValue=new Date(0);
	dateValue.setUTCSeconds(task.due_date['$date']/1000);
	dateValue.setUTCDate(dateValue.getUTCDate()-parseInt(task.remindBeforeDays,10));
	var sysDate = new Date();
	sysDate.setHours(0);
	sysDate.setMinutes(0);
	sysDate.setSeconds(0);
	sysDate.setMilliseconds(0);

	if(dateValue.getTime() <= sysDate.getTime())
	{
	    return true;
      	    
	}
    }
    return false;
}

/**
* @param dateObject {Date}
*/
function getDateInLocalISO(dateObject) {
    var date = dateObject.getDate()+'';
    if((date+'').length == 1){
	date = "0"+date;
    }
    
    var month = (dateObject.getMonth()+1)+'';
    if((month+'').length == 1){
	month = "0"+month;
    }
    
    
    var year = dateObject.getFullYear();

    return year+"-"+month+"-"+date;
}
