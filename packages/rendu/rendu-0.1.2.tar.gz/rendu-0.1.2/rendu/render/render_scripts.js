function show(n) {
  var main_div = document.getElementById("main");

  /* Show only current title slide */
  var titles = main_div.getElementsByClassName("titleslide");
  for (var i = 0; i < titles.length; i++) {
    if (i == n) {
      titles[i].style.display = "block";
    }
    else {
      titles[i].style.display = "none";
    }
  }

  /* Show only current slide */
  var slides  = main_div.getElementsByClassName("slide");
  for (var i = 0; i < slides.length; i++) {
    if (i == n) {
      slides[i].style.display = "block";
    }
    else {
      slides[i].style.display = "none";
    }
  }

  /* Show only current side notes */
  var sbar_div = document.getElementById("sidebar");
  var notes = sbar_div.getElementsByClassName("notes");
  for (var i = 0; i < notes.length; i++) {
    if (i == n) {
      notes[i].style.display = "block";
    }
    else {
      notes[i].style.display = "none";
    }
  }

  /* Highlight current menu item */
  var menu = document.getElementById("menulist");
  var items = menu.getElementsByClassName("menuitem");
  for (var i = 0; i < items.length; i++) {
    if (i == n) {
      items[i].className += " active"
    }
    else {
      items[i].className = items[i].className.replace("active", "");
    }
  }
}

function save_raw(section_id) {
    var raw_div = document.getElementById(section_id);
    raw_data = raw_div.innerHTML;
    save(section_id, raw_data)
}

function save(filename, data) {
    const blob = new Blob([data], {type: 'text/csv'});
    // IE
    if(window.navigator && window.navigator.msSaveOrOpenBlob) {
        window.navigator.msSaveBlob(blob, filename);
    }
    // non-IE (chrome, firefox, etc.)
    else{
        const elem = window.document.createElement('a');
        elem.href = window.URL.createObjectURL(blob);
        elem.download = filename;        
        document.body.appendChild(elem);
        elem.click();        
        document.body.removeChild(elem);
    }
}

// When loaded, start by displaying the first slide
show(0);

