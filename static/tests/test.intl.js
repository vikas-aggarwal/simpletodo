describe("Test Date manipulation", function() {
    describe("Test date string for local timezone", function() {
	it("1557081000000 should return correct ISO Value ", function(){
	    var date = new Date(1557081000000);
	    chai.assert.equal(date.toISOString(),"2019-05-05T18:30:00.000Z","Date not matching");
	});

	it("1557081000000 should return correct en-GB Value ", function(){
	    var date = new Date(1557081000000);
	    chai.assert.equal(date.toLocaleString("en-GB",{timeZone : "Asia/Kolkata"}),"06/05/2019, 00:00:00","Date not matching");
	});

	it("Time zone should not return UTC", function(){
	    chai.assert.notEqual(jstz.determine().name(),"UTC","UTC is returned as timezone");
	});



    })
});
