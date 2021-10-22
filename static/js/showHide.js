 myFunction = () => {
    var x = document.getElementById("side-menu");
    if (x.style.display === "none") {
      x.style.display = "block";
      x.classList.add("animate__backInLeft")
      console.log(x)
    } else {
      x.style.display = "none";

    }
}