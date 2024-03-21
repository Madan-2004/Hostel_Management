var side_bar = document.querySelector(".side-bar");
var ham = document.querySelector(".ham p");
var closes = document.getElementById("close");

ham.addEventListener("click", ()=>{
    side_bar.classList.toggle("show-side");
});

closes.addEventListener("click", ()=>{
    side_bar.classList.toggle("show-side");
});

var nav1 = document.querySelector("div.nav1");
var nav2 = document.querySelector("div.navbar2");
var val;

window.onscroll = function(){
    if(document.documentElement.scrollTop > 20){
        nav1.classList.add("sticky");
        nav2.classList.add("sticky");
    }
    else{
        nav1.classList.remove("sticky");
        nav2.classList.remove("sticky");
    }
}