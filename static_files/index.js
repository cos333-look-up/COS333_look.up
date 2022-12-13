console.log('index.js working')
function toggleUserMenu() {
  let menu = document.getElementById("user-menu")
    if (menu.style.display !== "none") {
      menu.style.display = "none";
    } else {
      menu.style.display = "block"
    }
  }

function toggleMenu() {
  let filter = document.getElementById("filter")
  let menu = document.getElementById("menu")
  filter.classList.toggle("hidden")
  menu.classList.toggle("reveal")
}

function cloudsMove() {
  let cloud1 = document.getElementById("cloud1")
  let cloud2 = document.getElementById("cloud2")

  let i = 0;
  setInterval(function () {
    let temp1 = parseInt(cloud1.style.left.slice(0, -1))
    let temp2 = parseInt(cloud2.style.left.slice(0, -1))
    cloud1.style.left = (temp1 + 1) + "%"
    cloud2.style.left = (temp2 + 1) + "%"
    i = i + 1;
  }, 600);

}

function chevron() {
  let chevron = document.getElementById("chevron")
  let dropdown = document.getElementById("dropdown")
  chevron.classList.toggle("rotated")
  dropdown.classList.toggle("hidden")
  return
}
