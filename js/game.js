let socket = new WebSocket("ws://" + window.location.host + "/ws");

let mySymbol = null;
let currentTurn = null;

function updateStatus(boardStr) {
    if (!mySymbol) return;

    if (mySymbol === "S") {
      document.getElementById("turn").innerHTML = "C'est le tour du joueur (" + currentTurn + ")";
    }
    else {
      if (currentTurn === mySymbol) {
          document.getElementById("turn").innerHTML = "C'est votre tour";
      } else {
          if(boardStr === ",,,,,,,,") document.getElementById("turn").innerHTML = "En attente du joueur ( " + currentTurn + " )...";
          else document.getElementById("turn").innerHTML = "C'est le tour de votre adversaire";
      }
    }

    document.getElementById("user-msg").innerHTML = "Vous jouez: " + mySymbol;
}

function board_update(msg) {
  // Normal board update
  let [boardStr, current] = msg.split("|");
  currentTurn = current;
  updateStatus(boardStr);

  let cells = boardStr.split(",");
  let boxDivs = document.querySelectorAll(".cell");

  boxDivs.forEach((box, i) => {
      box.innerHTML = cells[i];
  });
}

socket.addEventListener("message", (event) => {
    let msg = event.data;

    // Assignation du symbole par le serveur.
    if (msg.startsWith("YOU|")) {
        mySymbol = msg.split("|")[1];
        document.getElementById("user-msg").innerHTML = "Vous êtes: " + mySymbol;
        return;
    }

    // Réception du message serveur en cas de déconnection.
    if (msg.startsWith("DISC|")) {
        disconnect = msg.split("|")[1];
        alert(disconnect);
        window.location.href = "http://" + window.location.host + "/";
        return;
    }

    // Réception du message serveur pour le gagnant.
    else if (msg.startsWith("WIN|")) {
        let winner = msg.split("|")[1];

        if(mySymbol === "X" || mySymbol === "O") {
          if (winner === mySymbol) {
              document.getElementById("result_value").value = "🎉 You avez GAGNÉ!";
          } else {
              document.getElementById("result_value").value = "You avez perdu… 💀";
          }

        }
        else {
          document.getElementById("result_value").value = "Le joueur " + winner + " à GAGNÉ! 🎉";
        }

        document.getElementById("result_form").submit();

        return;
    }

    // Partie nulle.
    else if (msg === "DRAW") {
        document.getElementById("result_value").value = "😐 Partie nulle!";
        document.getElementById("result_form").submit();
        return;
    }

    board_update(msg);
});

document.getElementById("board").addEventListener("click", function (e) {
    if (e.target.classList.contains("cell")) {
        const index = parseInt(e.target.dataset.index);
        if (!mySymbol) return;
        socket.send(index.toString());
    }
});
