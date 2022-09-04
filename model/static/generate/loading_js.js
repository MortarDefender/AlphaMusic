function overlay() {
    $(document).ready(function() {

      var counter = 0;
      var c = 0;
      var i = setInterval(function(){
          $(".loading-page .counter h1").html(c + "%");
          $(".loading-page .counter hr").css("width", c + "%");

        counter++;
        c++;

        if(counter == 101) {
            clearInterval(i);
        }
      }, 110);
    });
};

function on() {
    document.getElementById("overlay").style.display = "block";
    overlay()
}
