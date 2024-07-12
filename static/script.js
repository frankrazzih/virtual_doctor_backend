//adds an event listener to check if passwords match before form submission
/*document.getElementById("submit").addEventListener(
    "submit",
    function(event){
        var password = document.getElementById('password').value;
        var confirmPassword = document.getElementById('confirm').value;
        if (password != confirmPassword) {
            alert("Passwords do not match.");
            //prevent form submission
            event.preventDefault();
            return false;
        }
        else {
            // passwords match
            return true;
        }
    }
);*/
function coll_cont(event){
    event.stopPropagation();
    event.preventDefault();
    var cont = document.getElementsByClassName('cont');
    var menu_img = document.getElementById('menu_img');
    
    for (var x = 0; x < cont.length; x++)
    {
        cont[x].style.display = 'flex';
    }
    menu_img.style.display = 'none';
}

window.onclick = function(event){
    var cont = document.getElementsByClassName('cont');

    for (var x = 0; x < cont.length; x++){
        if (cont[x].style.display == 'flex'){
            cont[x].style.display = 'none';
        }
    }
    var menu_img = document.getElementById('menu_img');
    menu_img.style.display = 'flex';
}

let slide_no = 0;
auto_slides();
//creates an automatic slideshow
function auto_slides(){
    var slides = document.getElementsByClassName('myslides');
    //set display to none
    for (var i = 0; i < slides.length; i++){
        slides[i].style.display = 'none';
    }
    //show the first slide
    slides[slide_no].style.display = 'flex';
    
    slide_no++;
    //reset the slideindex to loop the slideshow
    if (slide_no >= slides.length){
        slide_no = 0;
    }
    //call the function after 1s to show next slide
    setTimeout(auto_slides, 2000);
}
//show and hide the radio list for services
function radio_list(){
    var list = document.getElementById('radio_list');
    if (list.style.display == 'none'){
        list.style.display = 'flex';
    }
    else{
        list.style.display = 'none';
    }
}