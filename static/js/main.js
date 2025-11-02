// get DOM elements
const startBtn = document.getElementById("start-btn");
const homeScreen = document.getElementById("home-screen");

// add click listener to Start Quiz button
startBtn.addEventListener("click", (e) => {
  e.preventDefault(); // prevent default link behavior

  // play fade-out animation
  homeScreen.classList.add("fade-out");

  // after animation completes, redirect to quiz page
  setTimeout(() => {
    window.location.href = "quiz.html";
  }, 800); 
});