// Elements
const chat = document.getElementById("chat");
const startBtn = document.getElementById("startBtn");
const endBtn = document.getElementById("endBtn");

// Web Speech Recognition
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let rec = SR ? new SR() : null;

let autoListen = false;
let busy = false;
let speaking = false;
let started = false;


// ---------- UI ----------
function addMessage(text, who) {
  const typing = document.getElementById("typing");
  if (typing) typing.remove();

  const div = document.createElement("div");
  div.className = who;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function showTyping() {
  const row = document.createElement("div");
  row.id = "typing";
  row.className = "typing";
  row.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span> Listening…`;
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
}

function playChime() {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const o = ctx.createOscillator();
  const g = ctx.createGain();
  o.type = "sine";
  o.frequency.value = 660;
  o.connect(g);
  g.connect(ctx.destination);
  g.gain.setValueAtTime(0.0001, ctx.currentTime);
  g.gain.exponentialRampToValueAtTime(0.07, ctx.currentTime + 0.03);
  g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.30);
  o.start();
  o.stop(ctx.currentTime + 0.32);
}


// ---------- Speech Recognition ----------
function startListening() {
  if (!rec || speaking || busy) return;
  try { rec.start(); } catch {}
}

function stopListening() {
  if (!rec) return;
  try { rec.stop(); } catch {}
}

if (rec) {
  rec.lang = "en-IN";
  rec.continuous = true;
  rec.interimResults = false;

  rec.onresult = (ev) => {
    if (speaking || busy) return;
    for (let i = ev.resultIndex; i < ev.results.length; i++) {
      if (ev.results[i].isFinal) {
        const text = ev.results[i][0].transcript.trim();
        if (text.length < 2) return; // prevent empty triggers
        addMessage(text, "user");
        sendMessage(text);
      }
    }
  };

  rec.onend = () => {
    if (autoListen && !speaking && !busy) startListening();
  };
}


// ---------- Send to Server ----------
async function sendMessage(message) {
  busy = true;
  stopListening();
  showTyping();
  playChime();

  const res = await fetch("/send_message", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ message })
  });

  const data = await res.json();
  addMessage(data.response, "bot");

  speaking = true;

  if (data.audio) {
    const audio = new Audio("data:audio/mp3;base64," + data.audio);
    audio.play();
    audio.onended = () => { speaking = false; busy = false; startListening(); };
  } else {
    speaking = false;
    busy = false;
    startListening();
  }
}


// ---------- Start / End Session ----------
startBtn.onclick = async () => {
  if (started) return;
  started = true;
  autoListen = true;
  startBtn.disabled = true;
  endBtn.disabled = false;

  const res = await fetch("/send_message", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ message: "__WELCOME__" })
  });

  const data = await res.json();
  addMessage(data.response, "bot");

  if (data.audio) {
    const audio = new Audio("data:audio/mp3;base64," + data.audio);
    speaking = true;
    audio.play();
    audio.onended = () => { speaking = false; startListening(); };
  } else {
    startListening();
  }
};

endBtn.onclick = () => {
  autoListen = false;
  started = false;
  stopListening();
  startBtn.disabled = false;
  endBtn.disabled = true;
  addMessage("Call ended.", "bot");
};

