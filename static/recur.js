/*
Basic Grammar
~~~~~~~~~~~~~

S = Daily | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday | Sunday | Every <digit> <F> | Monthly | Weekly | Yearly |
    Every <F> on <P> 
F = Week |Weeks | Month | Months |Year | Years | Day | Days
P = first | last | 1st | 2nd | 3rd | 4th | 5th ... | 31st


Internal Structure
~~~~~~~~~~~~~~~~~~
Attribute will not be present

Preference

Month : Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec
Day : 1-31 | Last 
Week : 1-5 | Last 
Day_of_week : Mo | Tu | We | Th | Fr | Sa | Su
Frequency : Day | Week | Month | Year
FrequencyCount : <digit>




db.todos.distinct("frequency")
[
	"Irregular",
	"Monthly",
	"Wednesday",
	"Yearly",
	"Quaterly",
	"Semi Annually",
	"Six months",
	"Weekly",
	"",
	"3 months",
	"Every 3 months",
	"Monthly on first Saturday",
	"Saturday",
	"Weekend",
	"Daily",
	"Alternate Day",
	"Sunday",
	"Monday",
	"Tuesday",
	"Thursday",
	"Six Months"
]

*/

var ONE_DAY = 60*60*24*1000;
var ONE_WEEK = 7*ONE_DAY;
var DAY_OF_WEEK_MAP={"Sun":0,
		     "Mon":1,
		     "Tue":2,
		     "Wed":3,
		     "Thu":4,
		     "Fri":5,
		     "Sat":6};

function getNextOccurrence(recur,startDate)
{

    if(recur.Frequency == "Day")
    {
	startDate.setTime(startDate.getTime()+recur.FrequencyCount*ONE_DAY);
	return startDate;
    }
    else if(recur.Frequency == "Week")
    {
	startDate.setTime(startDate.getTime()+recur.FrequencyCount*ONE_WEEK);
	if("Day_of_week" in recur)
	{
	    if(DAY_OF_WEEK_MAP[recur.Day_of_week] != startDate.getDay())
	    {
		//add difference to date
		startDate.setTime(startDate.getTime()+ONE_DAY*(Math.abs(DAY_OF_WEEK_MAP[recur.Day_of_week] - startDate.getDay())));
	    }
	}
	return startDate; 
    }
    else if(recur.Frequency == "Month")
    {
	startDate.setMonth(startDate.getMonth()+recur.FrequencyCount);
	return startDate;
    }
    else if(recur.Frequency == "Year")
    {
	startDate.setFullYear(startDate.getFullYear()+recur.FrequencyCount);
	return startDate;
    }

    return null;
}




/**
   @param {string} frequencyStringInput
*/

function parseFrequency(frequencyStringInput)
{
    var frequencyString  = frequencyStringInput || "";
    frequencyString = frequencyString.toLowerCase();
    var components = frequencyString.split(" ");

    //As of now 2 lengths are supported
    if(components.length == 1)
    {
	switch(components[0])
	{
	    case "daily":
	    return {
		"Frequency" : "Day",
		"FrequencyCount" : 1
	    };
	    case "monday":
	    return    {
		"Frequency" : "Week",
		"FrequencyCount" : 1,
		"Day_of_week" : "Mon"
	    }
	    case "tuesday":
	    return    {
		"Frequency" : "Week",
		"FrequencyCount" : 1,
		"Day_of_week" : "Tue"
	    }
	    case "wednesday":
	    return 	    {
		"Frequency" : "Week",
		"FrequencyCount" : 1,
		"Day_of_week" : "Wed"
	    }
	    case "thursday":
	    return	    {
		"Frequency" : "Week",
		"FrequencyCount" : 1,
		"Day_of_week" : "Thu"
	    }
	    case "friday":
	    return	    {
		"Frequency" : "Week",
		"FrequencyCount" : 1,
		"Day_of_week" : "Fri"
	    }
	    case "saturday":
	    return	    {
		"Frequency" : "Week",
		"FrequencyCount" : 1,
		"Day_of_week" : "Sat"
	    }
	    case "sunday":
	    return	    {
		"Frequency" : "Week",
		"FrequencyCount" : 1,
		"Day_of_week" : "Sun"
	    }
	    case "monthly":
	    return	    {
		"Frequency" : "Month",
		"FrequencyCount" : 1,
	    }
	    case "weekly":
	    return	    {
		"Frequency" : "Week",
		"FrequencyCount" : 1
	    }
	    case "yearly":
	    return	    {
		"Frequency" : "Year",
		"FrequencyCount" : 1
	    }
	}
    }
    else if(components.length==3)
    {
	if(components[0] == "every")
	{
	    if(parseInt(components[1]).toString() == components[1])
	    {
		var x = ["week","weeks", "month",  "months" ,"year" , "years" , "day" , "days"];
		if(x.indexOf(components[2])!=-1)
		{
		    if(components[2].charAt(0) == 'w')
		    {
			return 			{
			    "Frequency" : "Week",
			    "FrequencyCount" : parseInt(components[1])
			}

		    }
		    else if(components[2].charAt(0) == 'y')
		    {
			return 			{
			    "Frequency" : "Year",
			    "FrequencyCount" : parseInt(components[1])
			}
		    }
		    else if(components[2].charAt(0) == 'd')
		    {
			return 			{
			    "Frequency" : "Day",
			    "FrequencyCount" : parseInt(components[1])
			}
		    }
		    else if(components[2].charAt(0) == 'm')
		    {
			return 			{
			    "Frequency" : "Month",
			    "FrequencyCount" : parseInt(components[1])
			}
		    }

		}
		
	    }
	}
    }

    return {};
}
