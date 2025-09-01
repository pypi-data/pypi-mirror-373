""" 
Simple jupyter widget to draw and explore a large set of 2D datapoints

Example
-------

import numpy as np

X = np.random.randn(200000, 2)
Y = np.arange(X.shape[0])

import big_scatter

big_scatter.draw(X, Y)


Arguments to draw()
-------------------

points                point coordinates as a numpy array of shape (N, 2)
labels                point labels as a list or numpy array of size N
width='700px%'           width of widget in jupyter
color='blue'          point color as a list of size N or a single string
size=1                point size as list or number
shape='square'        point shape as list or string (square or circle)
pick_radius=15        radius when searching for points closest to the cursor
pick_limit=20         number of closest labels to show
html_labels=False     set to True to interpret labels as HTML

"""

__version__ = '0.1.4'

import json
import random

from IPython.core.display import HTML
import IPython

def draw(points, labels, width="700px%", color='blue', size=1, shape='square', pick_radius=15, pick_limit=10, html_labels=False):
    # normalize X
    points = (points - points.min(0)) / (points.max(0) - points.min(0))
    if type(labels) is not list:
        labels = labels.tolist()
    if type(color) is not list and type(color) is not str:
        color = color.tolist()
    if type(size) is not list and type(size) is not float and type(size) is not int:
        size = size.tolist()
    if type(shape) is not list and type(shape) is not str:
        shape = shape.tolist()

    js_points = '<script>var X = %s, Y = %s, point_color = %s; point_size = %s; point_shape = %s </script>' % (json.dumps(points.tolist()), json.dumps(labels), json.dumps(color), json.dumps(size), json.dumps(shape))

    # unique id for locating elements
    rnd_id = str(int(random.random() * (1 << 64)))

    # elements for displaying result
    js_canvas = f'''<div id="container:{rnd_id}" style="border: 1px solid black; width: {width}; aspect-ratio: 1">
    <div style="position: absolute">
      <div id="result:{rnd_id}" style="position: relative;pointer-events:none;background:rgba(255, 255, 255, .5);display:none"></div>
    </div>
      <canvas id="canvas:{rnd_id}" style="width:100%" width="128" height="128"></canvas></div>'''

    # direct copy of script from kdbush (https://github.com/mourner/kdbush)
    js_kdbush = '''<script>
function sortKD(ids, coords, nodeSize, left, right, depth) {
    if (right - left <= nodeSize) { return; }

    var m = (left + right) >> 1;

    select(ids, coords, m, left, right, depth % 2);

    sortKD(ids, coords, nodeSize, left, m - 1, depth + 1);
    sortKD(ids, coords, nodeSize, m + 1, right, depth + 1);
}

function select(ids, coords, k, left, right, inc) {

    while (right > left) {
        if (right - left > 600) {
            var n = right - left + 1;
            var m = k - left + 1;
            var z = Math.log(n);
            var s = 0.5 * Math.exp(2 * z / 3);
            var sd = 0.5 * Math.sqrt(z * s * (n - s) / n) * (m - n / 2 < 0 ? -1 : 1);
            var newLeft = Math.max(left, Math.floor(k - m * s / n + sd));
            var newRight = Math.min(right, Math.floor(k + (n - m) * s / n + sd));
            select(ids, coords, k, newLeft, newRight, inc);
        }

        var t = coords[2 * k + inc];
        var i = left;
        var j = right;

        swapItem(ids, coords, left, k);
        if (coords[2 * right + inc] > t) { swapItem(ids, coords, left, right); }

        while (i < j) {
            swapItem(ids, coords, i, j);
            i++;
            j--;
            while (coords[2 * i + inc] < t) { i++; }
            while (coords[2 * j + inc] > t) { j--; }
        }

        if (coords[2 * left + inc] === t) { swapItem(ids, coords, left, j); }
        else {
            j++;
            swapItem(ids, coords, j, right);
        }

        if (j <= k) { left = j + 1; }
        if (k <= j) { right = j - 1; }
    }
}

function swapItem(ids, coords, i, j) {
    swap(ids, i, j);
    swap(coords, 2 * i, 2 * j);
    swap(coords, 2 * i + 1, 2 * j + 1);
}

function swap(arr, i, j) {
    var tmp = arr[i];
    arr[i] = arr[j];
    arr[j] = tmp;
}

function range(ids, coords, minX, minY, maxX, maxY, nodeSize) {
    var stack = [0, ids.length - 1, 0];
    var found = [];
    var x, y;

    while (stack.length) {
        var axis = stack.pop();
        var right = stack.pop();
        var left = stack.pop();

        if (right - left <= nodeSize) {
            for (var i = left; i <= right; i++) {
                x = coords[2 * i];
                y = coords[2 * i + 1];
                if (x >= minX && x <= maxX && y >= minY && y <= maxY) { found.push(ids[i]); }
            }
            continue;
        }

        var m = Math.floor((left + right) / 2);

        x = coords[2 * m];
        y = coords[2 * m + 1];

        if (x >= minX && x <= maxX && y >= minY && y <= maxY) { found.push(ids[m]); }

        var nextAxis = (axis + 1) % 2;

        if (axis === 0 ? minX <= x : minY <= y) {
            stack.push(left);
            stack.push(m - 1);
            stack.push(nextAxis);
        }
        if (axis === 0 ? maxX >= x : maxY >= y) {
            stack.push(m + 1);
            stack.push(right);
            stack.push(nextAxis);
        }
    }

    return found;
}

function within(ids, coords, qx, qy, r, nodeSize) {
    var stack = [0, ids.length - 1, 0];
    var found = [];
    var r2 = r * r;

    while (stack.length) {
        var axis = stack.pop();
        var right = stack.pop();
        var left = stack.pop();

        if (right - left <= nodeSize) {
            for (var i = left; i <= right; i++) {
                if (sqDist(coords[2 * i], coords[2 * i + 1], qx, qy) <= r2) { found.push(ids[i]); }
            }
            continue;
        }

        var m = Math.floor((left + right) / 2);

        var x = coords[2 * m];
        var y = coords[2 * m + 1];

        if (sqDist(x, y, qx, qy) <= r2) { found.push(ids[m]); }

        var nextAxis = (axis + 1) % 2;

        if (axis === 0 ? qx - r <= x : qy - r <= y) {
            stack.push(left);
            stack.push(m - 1);
            stack.push(nextAxis);
        }
        if (axis === 0 ? qx + r >= x : qy + r >= y) {
            stack.push(m + 1);
            stack.push(right);
            stack.push(nextAxis);
        }
    }

    return found;
}

function sqDist(ax, ay, bx, by) {
    var dx = ax - bx;
    var dy = ay - by;
    return dx * dx + dy * dy;
}

var defaultGetX = function (p) { return p[0]; };
var defaultGetY = function (p) { return p[1]; };

var KDBush = function KDBush(points, getX, getY, nodeSize, ArrayType) {
    if ( getX === void 0 ) getX = defaultGetX;
    if ( getY === void 0 ) getY = defaultGetY;
    if ( nodeSize === void 0 ) nodeSize = 64;
    if ( ArrayType === void 0 ) ArrayType = Float64Array;

    this.nodeSize = nodeSize;
    this.points = points;

    var IndexArrayType = points.length < 65536 ? Uint16Array : Uint32Array;

    var ids = this.ids = new IndexArrayType(points.length);
    var coords = this.coords = new ArrayType(points.length * 2);

    for (var i = 0; i < points.length; i++) {
        ids[i] = i;
        coords[2 * i] = getX(points[i]);
        coords[2 * i + 1] = getY(points[i]);
    }

    sortKD(ids, coords, nodeSize, 0, ids.length - 1, 0);
};

KDBush.prototype.range = function range$1 (minX, minY, maxX, maxY) {
    return range(this.ids, this.coords, minX, minY, maxX, maxY, this.nodeSize);
};

KDBush.prototype.within = function within$1 (x, y, r) {
    return within(this.ids, this.coords, x, y, r, this.nodeSize);
};
</script>'''

    js_script = '''<script>
function f() {
  var container = document.getElementById("container:''' + rnd_id + '''");
  var canvas = document.getElementById("canvas:''' + rnd_id + '''");
  var result = document.getElementById("result:''' + rnd_id + '''");
  var rect = canvas.getBoundingClientRect();
  var width = rect.width, height = rect.height;
  canvas.width = width;
  canvas.height = height;
  var g = canvas.getContext('2d');
  for(i = 0; i < X.length; i++) {
      var x = X[i][0] * width, y = X[i][1] * height;
      var shape = Array.isArray(point_shape) ? point_shape[i] : point_shape;
      var color = Array.isArray(point_color) ? point_color[i] : point_color;
      var size = Array.isArray(point_size) ? point_size[i] : point_size;
      g.fillStyle = color;
      g.beginPath();
      if(shape == 'square') {
          g.rect(x - size, y - size, 2 * size, 2 * size);
      } else {
          g.arc(x, y, size, 0, Math.PI * 2);
      }
      g.fill();
  }
  var index = new KDBush(X);
  canvas.onmousemove = function(e) {
      console.log(event.clientX, event.clientY);
      var parent_rect = canvas.parentElement.getBoundingClientRect();
      var canvas_rect = canvas.getBoundingClientRect();
      var x = (event.clientX - parent_rect.left) / canvas_rect.width, y = (event.clientY - parent_rect.top) / canvas_rect.height;
      console.log('x/y=', x, y);
      var found = index.within(x, y, ''' + str(pick_radius) + ''' / canvas_rect.width);
      var distances = {};
      for(i of found) {
          var dx = x - X[i][0], dy = y - X[i][1];
          distances[i] = dx * dx + dy * dy;
      }
      found.sort((a, b) => distances[a] - distances[b]).slice(''' + str(pick_limit) + ''');
      if(''' + ('true' if html_labels is True else 'false') + ''') {
          result.innerHTML = '';
          for(i of found) {
              var div = document.createElement('div');
              div.innerHTML = Y[i];
              result.appendChild(div);
          }
      } else {
          var text = '';
          for(i of found) {
              text += Y[i] + '\\n';
          }
          result.innerText = text;
      }
      result.style.left = '' + (event.clientX - parent_rect.left + 15) + 'px';
      result.style.top = '' + (event.clientY - parent_rect.top) + 'px';
      result.style.display = 'block';
      container.parentElement.style.overflow = 'hidden';
  }
  canvas.onmouseleave = function(e) {
      result.style.display = 'none';
  }
}
f();
</script>'''

    # create html data and display it
    html = js_points + js_kdbush + js_canvas + js_script

    IPython.display.display(HTML(html))

