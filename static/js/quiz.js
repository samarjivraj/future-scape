const startBtn = document.getElementById("start-btn");
const homeScreen = document.getElementById("home-screen");
const quizScreen = document.getElementById("quiz-screen");
const questionEl = document.getElementById("question");
const optionsEl = document.getElementById("options");
const backBtn = document.getElementById("back-btn");

// transition from home → quiz
startBtn.addEventListener("click", () => {
  homeScreen.classList.add("fade-out");
  setTimeout(() => {
    homeScreen.classList.remove("active");
    quizScreen.classList.add("active", "fade-in");
    loadQuestion();
  }, 800);
});

// quiz questions (same as before)
const quizData = [
  {
    name: "meat_dairy",
    question: "How often do you eat meat or dairy products?",
    options: [
      { value: "less_20", label: "Every day" },
      { value: "20_50", label: "A few times per week" },
      { value: "50_100", label: "Rarely" },
      { value: "over_100", label: "Never (plant-based)" }
    ]
  },
  {
    name: "transport",
    question: "What is your main mode of daily transport?",
    options: [
      { value: "car_petrol", label: "Car (petrol/diesel)" },
      { value: "car_electric", label: "Car (electric/hybrid)" },
      { value: "public", label: "Public transport" },
      { value: "walk_cycle", label: "Walking or cycling" },
      { value: "home", label: "Work/study from home" }
    ]
  },
  {
    name: "flights",
    question: "How many flights do you take per year (return trips)?",
    options: [
      { value: "none", label: "None" },
      { value: "short", label: "1–2 short flights" },
      { value: "long", label: "1–2 long flights" },
      { value: "3plus", label: "3+ flights" }
    ]
  },
  {
    name: "home_energy_source",
    question: "How is your home mainly powered or heated?",
    options: [
      { value: "renewable", label: "Electricity from renewable sources" },
      { value: "mixed", label: "Electricity from mixed grid" },
      { value: "gas_oil", label: "Gas or oil heating" },
      { value: "unsure", label: "Unsure" }
    ]
  },
  {
    name: "home_efficiency",
    question: "How energy efficient is your home?",
    options: [
      { value: "very", label: "Very efficient" },
      { value: "some", label: "Some improvements made" },
      { value: "not_very", label: "Not very efficient" },
      { value: "not_sure", label: "Not sure" }
    ]
  },
  {
    name: "recycling",
    question: "How often do you recycle household waste?",
    options: [
      { value: "always", label: "Always" },
      { value: "often", label: "Often" },
      { value: "sometimes", label: "Sometimes" },
      { value: "rarely", label: "Rarely" }
    ]
  },
  {
    name: "sustainable_shopping",
    question: "Do you regularly buy second-hand or sustainable products?",
    options: [
      { value: "most", label: "Yes, most of the time" },
      { value: "occasionally", label: "Occasionally" },
      { value: "rarely", label: "Rarely" },
      { value: "never", label: "Never" }
    ]
  },
  {
    name: "carbon_awareness",
    question: "How much do you think about your carbon footprint?",
    options: [
      { value: "high", label: "Always" },
      { value: "medium", label: "Sometimes" },
      { value: "low", label: "Rarely" }
    ]
  },
  {
    name: "device_usage",
    question: "How many hours per day do you use electronic devices?",
    options: [
      { value: "less_2", label: "Less than 2 hours" },
      { value: "2_5", label: "2–5 hours" },
      { value: "5_8", label: "5–8 hours" },
      { value: "8plus", label: "8+ hours" }
    ]
  },
  {
    name: "food_waste",
    question: "How much food ends up being thrown away each week?",
    options: [
      { value: "almost_none", label: "Almost none" },
      { value: "a_little", label: "A little" },
      { value: "some", label: "Some" },
      { value: "a_lot", label: "A lot" }
    ]
  }
];

let currentQuestion = 0;
let answers = {};

function loadQuestion() {
  const current = quizData[currentQuestion];
  questionEl.textContent = current.question;
  optionsEl.innerHTML = "";

  current.options.forEach(opt => {
    const btn = document.createElement("button");
    btn.textContent = opt.label;
    btn.classList.add("option");

    btn.addEventListener("click", () => {
      answers[current.name] = opt.value;
      nextQuestion();
    });

    optionsEl.appendChild(btn);
  });

  backBtn.style.display = currentQuestion > 0 ? "inline-block" : "none";
}

function nextQuestion() {
  if (currentQuestion < quizData.length - 1) {
    currentQuestion++;
    loadQuestion();
  } else {
    submitQuiz();
  }
}

backBtn.addEventListener("click", () => {
  if (currentQuestion > 0) {
    currentQuestion--;
    loadQuestion();
  }
});

function submitQuiz() {
  // create a form dynamically to send POST request
  const form = document.createElement("form");
  form.method = "POST";
  form.action = "/calculate";

  for (const [key, value] of Object.entries(answers)) {
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = key;
    input.value = value;
    form.appendChild(input);
  }

  document.body.appendChild(form);
  form.submit();
}
