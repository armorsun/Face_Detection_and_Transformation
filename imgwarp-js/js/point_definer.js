var ImgWarper = ImgWarper || {};

ImgWarper.PointDefiner = function(canvas, image, imgData, scale) {
	this.oriPoints = new Array();
	this.dstPoints = new Array();

	//set up points for change; 
	var c = canvas;
	this.canvas = canvas;
	var that = this;
	this.dragging_ = false;
	this.computing_ = false;
	var src_split = image.src.split("/");
	var fn = src_split[src_split.length - 1];
	var fn_split = fn.split(".");
	var filename = fn_split[0];
	this.landmarks = {};
	that.read_detect_data(scale, filename);
	$(c).unbind();
	$(c).bind('mousedown', function (e) { that.touchStart(e); });
	$(c).bind('mousemove', function (e) { that.touchDrag(e); });
	$(c).bind('mouseup', function (e) { that.touchEnd(e); });
	this.currentPointIndex = -1;
	this.imgWarper = new ImgWarper.Warper(c, image, imgData);
};

ImgWarper.PointDefiner.prototype.adjust = function(alpha, beta) {
	var mouth_left_corner = this.landmarks["mouth_left_corner"];
	var nose_contour_lower_middle = this.landmarks["nose_contour_lower_middle"];
	var contour_left1 = this.landmarks["contour_left1"];
	var new_x = alpha * this.oriPoints[mouth_left_corner].x + (1.0 - alpha) * this.oriPoints[contour_left1].x;
	var new_y = beta * this.oriPoints[nose_contour_lower_middle].y + (1.0 - beta) * this.oriPoints[mouth_left_corner].y;
	this.dstPoints[mouth_left_corner] = new ImgWarper.Point(new_x, new_y);

	var dx = this.oriPoints[mouth_left_corner].x - this.dstPoints[mouth_left_corner].x;
	var mouth_lower_lip_bottom = this.landmarks["mouth_lower_lip_bottom"];
	var A = (this.oriPoints[mouth_lower_lip_bottom].y - this.dstPoints[mouth_left_corner].y) / Math.pow(this.dstPoints[mouth_left_corner].x - this.oriPoints[mouth_lower_lip_bottom].x, 2);
	var new_x = - dx * 0.3 + this.oriPoints[mouth_left_corner].x;
	var new_y = - A * Math.pow((this.dstPoints[mouth_lower_lip_bottom].x - new_x), 2) + this.oriPoints[mouth_lower_lip_bottom].y;
	var mouth_lower_lip_left_contour2 = this.landmarks["mouth_lower_lip_left_contour2"];
	this.dstPoints[mouth_lower_lip_left_contour2] = new ImgWarper.Point(new_x, new_y);
	/*
	var new_x = - dx * 0.1 + this.oriPoints[mouth_left_corner].x;
	var new_y = - A * Math.pow((this.dstPoints[mouth_lower_lip_bottom].x - new_x), 2) + this.oriPoints[mouth_lower_lip_bottom].y;
	var mouth_lower_lip_left_contour3 = this.landmarks["mouth_lower_lip_left_contour3"];
	this.dstPoints[mouth_lower_lip_left_contour3] = new ImgWarper.Point(new_x, new_y);
	///
	var mouth_upper_lip_bottom = this.landmarks["mouth_upper_lip_bottom"];
	var A = (this.oriPoints[mouth_upper_lip_bottom].y - this.dstPoints[mouth_left_corner].y) / Math.pow(this.dstPoints[mouth_left_corner].x - this.oriPoints[mouth_upper_lip_bottom].x, 2);
	var new_x = - dx * 0.2 + this.oriPoints[mouth_left_corner].x;
	var new_y = - A * Math.pow((this.dstPoints[mouth_upper_lip_bottom].x - new_x), 2) + this.oriPoints[mouth_upper_lip_bottom].y;
	var mouth_upper_lip_left_contour2 = this.landmarks["mouth_upper_lip_left_contour2"];
	this.dstPoints[mouth_upper_lip_left_contour2] = new ImgWarper.Point(new_x, new_y);
	var new_x = - dx * 0.05 + this.oriPoints[mouth_left_corner].x;
	var new_y = - A * Math.pow((this.dstPoints[mouth_upper_lip_bottom].x - new_x), 2) + this.oriPoints[mouth_upper_lip_bottom].y;
	var mouth_upper_lip_left_contour3 = this.landmarks["mouth_upper_lip_left_contour3"];
	this.dstPoints[mouth_upper_lip_left_contour3] = new ImgWarper.Point(new_x, new_y);
	///
	var mouth_lower_lip_top = this.landmarks["mouth_lower_lip_top"];
	var A = (this.oriPoints[mouth_lower_lip_top].y - this.dstPoints[mouth_left_corner].y) / Math.pow(this.dstPoints[mouth_left_corner].x - this.oriPoints[mouth_lower_lip_top].x, 2);
	var new_x = - dx * 0.05 + this.oriPoints[mouth_left_corner].x;
	var new_y = - A * Math.pow((this.dstPoints[mouth_lower_lip_top].x - new_x), 2) + this.oriPoints[mouth_lower_lip_top].y;
	var mouth_lower_lip_left_contour1 = this.landmarks["mouth_lower_lip_left_contour1"];
	this.dstPoints[mouth_lower_lip_left_contour1] = new ImgWarper.Point(new_x, new_y);
	*/

	var mouth_right_corner = this.landmarks["mouth_right_corner"];
	var nose_contour_lower_middle = this.landmarks["nose_contour_lower_middle"];
	var contour_right1 = this.landmarks["contour_right1"];
	var new_x = alpha * this.oriPoints[mouth_right_corner].x + (1.0 - alpha) * this.oriPoints[contour_right1].x;
	var new_y = beta * this.oriPoints[nose_contour_lower_middle].y + (1.0 - beta) * this.oriPoints[mouth_right_corner].y;
	this.dstPoints[mouth_right_corner] = new ImgWarper.Point(new_x, new_y);

	var dx = this.dstPoints[mouth_right_corner].x - this.oriPoints[mouth_right_corner].x;
	var A = (this.oriPoints[mouth_lower_lip_bottom].y - this.dstPoints[mouth_right_corner].y) / Math.pow(this.dstPoints[mouth_right_corner].x - this.oriPoints[mouth_lower_lip_bottom].x, 2);
	var new_x = dx * 0.3 + this.oriPoints[mouth_right_corner].x;
	var new_y = - A * Math.pow((this.dstPoints[mouth_lower_lip_bottom].x - new_x), 2) + this.oriPoints[mouth_lower_lip_bottom].y;
	var mouth_lower_lip_right_contour2 = this.landmarks["mouth_lower_lip_right_contour2"];
	this.dstPoints[mouth_lower_lip_right_contour2] = new ImgWarper.Point(new_x, new_y);
	/*
	var new_x = dx * 0.1 + this.oriPoints[mouth_right_corner].x;
	var new_y = - A * Math.pow((this.dstPoints[mouth_lower_lip_bottom].x - new_x), 2) + this.oriPoints[mouth_lower_lip_bottom].y;
	var mouth_lower_lip_right_contour3 = this.landmarks["mouth_lower_lip_right_contour3"];
	this.dstPoints[mouth_lower_lip_right_contour3] = new ImgWarper.Point(new_x, new_y);
	///
	var A = (this.oriPoints[mouth_upper_lip_bottom].y - this.dstPoints[mouth_right_corner].y) / Math.pow(this.dstPoints[mouth_right_corner].x - this.oriPoints[mouth_upper_lip_bottom].x, 2);
	var new_x = dx * 0.2 + this.oriPoints[mouth_right_corner].x;
	var new_y = - A * Math.pow((this.dstPoints[mouth_upper_lip_bottom].x - new_x), 2) + this.oriPoints[mouth_upper_lip_bottom].y;
	var mouth_upper_lip_right_contour2 = this.landmarks["mouth_upper_lip_right_contour2"];
	this.dstPoints[mouth_upper_lip_right_contour2] = new ImgWarper.Point(new_x, new_y);
	var new_x = dx * 0.05 + this.oriPoints[mouth_right_corner].x;
	var new_y = - A * Math.pow((this.dstPoints[mouth_upper_lip_bottom].x - new_x), 2) + this.oriPoints[mouth_upper_lip_bottom].y;
	var mouth_upper_lip_right_contour3 = this.landmarks["mouth_upper_lip_right_contour3"];
	this.dstPoints[mouth_upper_lip_right_contour3] = new ImgWarper.Point(new_x, new_y);
	///
	var A = (this.oriPoints[mouth_lower_lip_top].y - this.dstPoints[mouth_right_corner].y) / Math.pow(this.dstPoints[mouth_right_corner].x - this.oriPoints[mouth_lower_lip_top].x, 2);
	var new_x = dx * 0.05 + this.oriPoints[mouth_right_corner].x;
	var new_y = - A * Math.pow((this.dstPoints[mouth_lower_lip_top].x - new_x), 2) + this.oriPoints[mouth_lower_lip_top].y;
	var mouth_lower_lip_right_contour1 = this.landmarks["mouth_lower_lip_right_contour1"];
	this.dstPoints[mouth_lower_lip_right_contour1] = new ImgWarper.Point(new_x, new_y);
	*/

	this.redraw();
}

ImgWarper.PointDefiner.prototype.read_detect_data = function(scale, filename) {
	this.landmarks = {};
	that = this;
	$.getJSON( "face_detection_result/" + filename + ".json", function(data) {
		that.landmarks = {};
		var i = 0;
		var items = [];
		for (key in data["faces"][0]["landmark"]) {
			var val = data["faces"][0]["landmark"][key];
			items.push( "<li id='" + key + "'>" + key + ": " + val["x"].toString() + ", " + val["y"].toString() + "</li>" );
  			var q = new ImgWarper.Point(val["x"] * scale, val["y"] * scale);
    		that.oriPoints.push(q);
    		that.dstPoints.push(q);
			that.landmarks[key] = i;
			i++;
		}

		$( "<ul/>", {
			"class": "my-new-list",
			html: items.join( "" )
		}).appendTo( "body" );	
	});
}

ImgWarper.PointDefiner.prototype.touchEnd = function(e) {
  this.dragging_ = false;
}

ImgWarper.PointDefiner.prototype.touchDrag = function(e) {
  if (this.computing_ || !this.dragging_ || this.currentPointIndex < 0) {
    return;
  }
  this.computing_ = true;
  e.preventDefault();
  var endX = (e.offsetX || e.clientX - $(e.target).offset().left);
  var endY = (e.offsetY || e.clientY - $(e.target).offset().top);

  movedPoint = new ImgWarper.Point(endX, endY);
  this.dstPoints[this.currentPointIndex] = new ImgWarper.Point(endX, endY);
  this.redraw();
  this.computing_ = false;
};

ImgWarper.PointDefiner.prototype.redraw = function () {
  if (this.oriPoints.length < 3) {
    if (document.getElementById('show-control').checked) {
      this.redrawCanvas();
    }
    return;
  }
  this.imgWarper.warp(this.oriPoints, this.dstPoints);
  if (document.getElementById('show-control').checked) {
    this.redrawCanvas();
  }
};


ImgWarper.PointDefiner.prototype.touchStart = function(e) {
  //this.adjust(0.9, 0.25);
  this.dragging_ = true;
  e.preventDefault();
  var startX = (e.offsetX || e.clientX - $(e.target).offset().left);
  var startY = (e.offsetY || e.clientY - $(e.target).offset().top);
  var q = new ImgWarper.Point(startX, startY);

  if (e.ctrlKey) {
    this.oriPoints.push(q);
    this.dstPoints.push(q);
  } else if (e.shiftKey) {
    var pointIndex = this.getCurrentPointIndex(q);  
    if (pointIndex >= 0) {
      this.oriPoints.splice(pointIndex, 1);
      this.dstPoints.splice(pointIndex, 1);
    }
  } else {
    this.currentPointIndex = this.getCurrentPointIndex(q);  
  }
  this.redraw();
};

ImgWarper.PointDefiner.prototype.getCurrentPointIndex = function(q) {
  var currentPoint = -1;   

  for (var i = 0 ; i< this.dstPoints.length; i++){
    if (this.dstPoints[i].InfintyNormDistanceTo(q) <= 20) {
      currentPoint = i;
      return i;
    }
  }
  return currentPoint;
};

ImgWarper.PointDefiner.prototype.redrawCanvas = function(points) {
  var ctx = this.canvas.getContext("2d");
  for (var i = 0; i < this.oriPoints.length; i++){
    if (i < this.dstPoints.length) {
      if (i == this.currentPointIndex) {
        this.drawOnePoint(this.dstPoints[i], ctx, 'orange');
      } else {
        this.drawOnePoint(this.dstPoints[i], ctx, '#6373CF');
      }

      ctx.beginPath();
      ctx.lineWidth = 3;
      ctx.moveTo(this.oriPoints[i].x, this.oriPoints[i].y);
      ctx.lineTo(this.dstPoints[i].x, this.dstPoints[i].y);
      //ctx.strokeStyle = '#691C50';
      ctx.stroke();
    } else {
      this.drawOnePoint(this.oriPoints[i], ctx, '#119a21');
    }
  } 
  ctx.stroke();
};

ImgWarper.PointDefiner.prototype.drawOnePoint = function(point, ctx, color) {
  var radius = 5; 
  ctx.beginPath();
  ctx.lineWidth = 1;
  ctx.arc(parseInt(point.x), parseInt(point.y), radius, 0, 2 * Math.PI, false);
  ctx.strokeStyle = color;
  ctx.stroke();

  ctx.beginPath();
  ctx.lineWidth = 1;
  ctx.arc(parseInt(point.x), parseInt(point.y), 1, 0, 2 * Math.PI, false);
  ctx.fillStyle = color;
  ctx.fill(); 
};
