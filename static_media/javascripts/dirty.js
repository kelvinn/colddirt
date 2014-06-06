// Part credit goes to the liveData script at AjaxLessons.com
PeriodicalExecuter.prototype.registerCallback = function() {
	this.intervalID = setInterval(this.onTimerEvent.bind(this), this.frequency * 1000);
}
PeriodicalExecuter.prototype.stop = function() {
	clearInterval(this.intervalID);
}
var liveDirt = Class.create();
liveDirt.prototype = {
	pe: 0,
	interval: 10,
	status: 1,
	data: [],
	initialize: function () {
		this.loadDirts()
		this.pe = new PeriodicalExecuter(this.getNewDirts.bind(this), this.interval);
		},
	fillHolder: function () {
		if (this.data[0].length > 1) {
			if (this.data[1]) {
				var resultd = this.data[0].first().pk - this.data[1].first().pk
			}
			this.data[0].each(function(item, i) {
				var holder='hold_' + i;
				var dirtyword=item.fields.dirtword
				var dirtydesc=item.fields.description
				if (i < resultd){
					$(holder).morph('background:#d9deff;color:#333333', {duration:1.3});
					$(holder).morph('background:#ffffff;color:#000000', {delay:5});
				}
				var publish_date=item.fields.publish_date
				$(holder).innerHTML = '<span class="dirtyword"><a href="/dirtword/' + dirtyword + '">' + dirtyword +'</a></span><span class="dirtydate">Submitted at ' + publish_date + '</span><span class="dirtydesc">' + dirtydesc + '</span>';
			});
		}
	},
	loadDirts: function () {
		var showNewDirts = this.showNewDirts.bind(this);
		var pars = 'pk=0';
		new Ajax.Request('/live_update/', {
	  		method:'get',
			parameters: pars,
	 		onComplete: showNewDirts	
		});
	},
	getNewDirts: function () {
		var showNewDirts = this.showNewDirts.bind(this);
		var pars   = 'pk=' + this.data[0].first().pk;
		new Ajax.Request('/live_update/', {
	  		method:'get',
			parameters: pars,
	 		onComplete: showNewDirts
		});
	},
	showNewDirts: function (originalRequest) {
		this.data.unshift(originalRequest.responseText.evalJSON());
		this.fillHolder();
	},
	playFunc: function () {
		if (this.status == 0) {
			this.pe = new PeriodicalExecuter(this.getNewDirts.bind(this), this.interval);
			this.status = 1;
		}
	},
	stopFunc: function () {
		this.pe.stop();
		this.status = 0;
	}
}
var ld;
window.onload = function () {
	ld = new liveDirt;
	var tabs = document.getElementsByClassName('tab');
	
	$('hold_7').style.opacity = 0.70;
	$('hold_8').style.opacity = 0.50;
	$('hold_9').style.opacity = 0.25;

	tabs.each(function (item, index) {
		item.style.cursor = 'pointer';
		item.onmouseover = function () {
			this.style.background = '#fff';
			this.style.borderBottom = '1px solid #999';
		}
		item.onmouseout = function () {
			this.style.background = '#F1FEFC';
			this.style.borderBottom = 0;
		}		
	});
	
}
