console.log("hi")

function toggleMenu() {
  let filter = document.getElementById("filter")
  let menu = document.getElementById("menu")
  filter.classList.toggle("hidden")
  menu.classList.toggle("hidden")
}

function profileNext(currId, nextId) {
  if (!nextId) {
    window.location = "index"
    return
  }
  let currForm = document.getElementById(currId)
  let nextForm = document.getElementById(nextId)
  console.log(currForm, nextForm)
  currForm.classList.toggle("hidden")
  nextForm.classList.toggle("hidden")
  return
}

